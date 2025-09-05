import os
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

import requests
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

endpoints = ['/', '/analytics/<shortId>', '/<shortId>']
metrics = PrometheusMetrics(
            app,
            group_by_endpoint=True,
            path_prefix='url_shortener_',
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5),
            default_labels={'app_name': 'url_shortener'},
            excluded_endpoints=[],
            )

short_urls_created = Counter(
    'url_shortener_created_total', 'Number of short URLs created',
    ['app_name']
)

short_urls_failed_redirects = Counter(
    'url_shortener_failed_redirects', 'Number of short URLs created',
    ['app_name']
)

short_urls_redirected = Counter(
    'url_shortener_redirects_total',
    'Number of failed redirects',
    ['app_name']
)


@app.route("/", methods=["GET", "POST"])
def index():
    """
    Render the home page.
    - GET: Shows the form
    - POST: Validates user URL and sends it to the API
    """
    response_text = None
    # preserves the real host From nginx
    # will be localhost if ran Locally or public IP of server
    host = request.headers.get("Host")
    base_url = f"https://{host}"

    if request.method == "POST":
        user_url = request.form.get("url")
        try:
            resp = requests.post(
                os.environ.get("API_POST_URL"), json={"url": user_url}
            )
            resp.raise_for_status()

            data = resp.json()
            response_text = data.get("id")
            short_urls_created.labels(app_name="url_shortener").inc()
        except Exception as exception:
            response_text = f"Error: {exception}"
    return (render_template(
        "index.html",
        response=response_text,
        base_url=base_url),
        200
        )


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
            short_urls_failed_redirects.labels(app_name="url_shortener").inc()
            return "URL not found", 404
    except Exception as e:
        short_urls_failed_redirects.labels(app_name="url_shortener").inc()
        return f"Error: {e}", 404


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
                return (
                    render_template
                    ("analytics.html", NumberOfVisits=NumberOfVisits),
                    200
                    )
            else:
                return (
                    render_template
                    ("analytics.html", NumberOfVisits="0"),
                    200
                  )
        else:
            return (
                render_template
                ("analytics.html", NumberOfVisits="URL not found"),
                404,
            )
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=os.environ.get('PORT'))
