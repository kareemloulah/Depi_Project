from flask import Flask, request, redirect, render_template
import requests
import os
from urllib.parse import urlparse

app = Flask(__name__)


def _normalize_and_validate_url(raw_url: str):
    """
    Normalize (add http:// if scheme missing) and validate that URL has http/https
    and a network location (netloc). Returns normalized URL string or None if invalid.
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


@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None

    # getting the instance public DNS
    token_url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    token = requests.put(token_url, headers=headers, timeout=2).text
    metadata_url = f"http://169.254.169.254/latest/meta-data/public-hostname"
    headers = {"X-aws-ec2-metadata-token": token}
    DNS = requests.get(metadata_url, headers=headers, timeout=2)

    if request.method == "POST":
        user_url = request.form.get("url")
        normalized = _normalize_and_validate_url(user_url)
        if not normalized:
            response_text = (
                "Invalid URL. Please provide a valid http:// or https:// address."
            )
        else:
            try:
                resp = requests.post(
                    os.environ.get("API_POST_URL"), json={"url": normalized}
                )
                resp.raise_for_status()

                data = resp.json()
                response_text = data.get("id")
            except Exception as e:
                response_text = f"Error: {e}"

    return render_template("index.html", response=response_text, dns=DNS.text)


@app.route("/<shortId>")
def go(shortId):
    try:
        resp = requests.get(f"{os.environ.get('API_GET_URL')}/{shortId}")
        resp.raise_for_status()

        data = resp.json()
        redirect_url = data.get("redirectUrl")
        if redirect_url:
            return redirect(redirect_url, code=302)
        else:
            return "URL not found", 404
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/analytics/<shortId>")
def Analytics(shortId):
    try:
        resp = requests.get(f"{os.environ.get('API_GET_ANALYTICS')}/{shortId}")
        resp.raise_for_status()

        resp = resp.json()
        print(resp)

        NumberOfVisits = len(resp.get("visitHistory"))
        if resp:
            if NumberOfVisits:
                return render_template("analytics.html", NumberOfVisits=NumberOfVisits)
            else:
                return render_template("analytics.html", NumberOfVisits="0")
        else:
            return render_template("analytics.html", NumberOfVisits="URL not found"), 404
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)