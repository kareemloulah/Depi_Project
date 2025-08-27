import os
from urllib.parse import urlparse
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from prometheus_client import Counter

import requests
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

endpoints = ['/','/analytics/<shortId>','/<shortId>']
metrics = PrometheusMetrics(app, group_by_endpoint=True,
                             path_prefix='url_shortener_',
                             buckets=(0.1, 0.3, 0.5, 0.7, 1, 1.5, 2, 3, 5, 7, 10),
                             default_labels={'app_name': 'url_shortener'},
                             excluded_endpoints=[])



short_urls_created = Counter(
    'url_shortener_created_total',
    'Number of short URLs created',
    ['app_name']
)
short_urls_redirected = Counter(
    'url_shortener_redirects_total',
    'Number of redirects served',
    ['app_name']
)


def _normalize_and_validate_url(raw_url: str):
    """
    Normalize (add http:// if scheme missing) and
    validate that URL has http/https
    and a network location (netloc).
    Returns normalized URL string or None if invalid.
    """

    if not raw_url:
        return None
    raw_url = raw_url.strip()
    # If user omitted scheme, assume http
    if "://" not in raw_url:
        candidate = "http://" + raw_url
    else:
        candidate = raw_url
    parsed = urlparse(candidate)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return candidate
    return None


@app.route("/", methods=["GET","POST"])
def index():
    """
    Render the home page.
    - GET: Shows the form
    - POST: Validates user URL and sends it to the API
    """
    response_text = None

    # getting the instance public DNS
    token_url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    token = requests.put(token_url, headers=headers, timeout=2).text
    metadata_url = "http://169.254.169.254/latest/meta-data/public-hostname"
    headers = {"X-aws-ec2-metadata-token": token}
    Dns = requests.get(metadata_url, headers=headers, timeout=2)

    if request.method == "POST":
        user_url = request.form.get("url")
        normalized = _normalize_and_validate_url(user_url)
        if not normalized:
            response_text = (
                "Invalid URL. Please provide "
                "a valid http:// or https:// address."
            )
        else:
            try:
                resp = requests.post(
                    os.environ.get("API_POST_URL"), json={"url": normalized}
                )
                resp.raise_for_status()

                data = resp.json()
                response_text = data.get("id")
                short_urls_created.labels(app_name="url_shortener").inc()
            except Exception as exception:
                response_text = f"Error: {exception}"

    return (render_template("index.html", response=response_text, dns=Dns.text), {"status": "ok"})


@app.route("/<shortId>")
def go(shortId):
    """
    Redirect to the original URL given its shortId.
    Returns 404 if not found.
    """
    try:
        resp = requests.get(f"{os.environ.get('API_GET_URL')}/{shortId}")
        resp.raise_for_status()

        data = resp.json()
        redirect_url = data.get("redirectUrl")
        if redirect_url:
            short_urls_redirected.labels(app_name="url_shortener").inc()
            return redirect(redirect_url, code=302)
        else:
            return "URL not found", 404
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/analytics/<shortId>")
def Analytics(shortId):
    """
    Show analytics for a given shortId (number of visits).
    Returns 404 if the URL does not exist.
    """
    try:
        resp = requests.get(f"{os.environ.get('API_GET_ANALYTICS')}/{shortId}")
        resp.raise_for_status()

        resp = resp.json()
        print(resp)

        NumberOfVisits = len(resp.get("visitHistory"))
        if resp:
            if NumberOfVisits:
                return render_template(
                    "analytics.html",
                    NumberOfVisits=NumberOfVisits)
            else:
                return render_template(
                    "analytics.html",
                    NumberOfVisits="0")
        else:
            return (
                render_template(
                    "analytics.html",
                    NumberOfVisits="URL not found"),
                404,
            )
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    
    app.run(host="client", port=80)
