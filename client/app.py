from flask import Flask, render_template_string, request , redirect
import requests

app = Flask(__name__)

# HTML template (inline for simplicity)
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Sender</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        input[type=text] { width: 300px; padding: 8px; }
        button { padding: 8px 16px; }
        .response-box { margin-top: 20px; padding: 10px; border: 1px solid #ccc; background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Send URL</h1>
    <form method="POST">
        <input type="text" name="url" placeholder="Enter URL" required>
        <button type="submit">Submit</button>
    </form>

    {% if response %}
    <div class="response-box">
        <strong>Response:</strong>
        <pre>http://{{ ip }}/{{ response }}</pre>
    </div>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    response_text = None
    if request.method == "POST":
        user_url = request.form.get("url")
        try:
            # Send POST request to your backend
            resp = requests.post("http://server:8001/url", json={"url": user_url})
            resp.raise_for_status()
            data = resp.json()              # parse JSON
            response_text = data.get('id')  # extract only 'id'
        except Exception as e:
            response_text = f"Error: {e}"

    return render_template_string(TEMPLATE, response=response_text ,ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr))


@app.route("/<shortId>")
def go(shortId):
    # send Get request to the API to get the redirect URL
    try:
        resp = requests.get(f"http://server:8001/{shortId}")
        resp.raise_for_status()
        data = resp.json()  # parse JSON
        redirect_url = data.get('redirectUrl')  # extract 'url'
        if redirect_url:
            return redirect(redirect_url, code=302)
        else:
            return "URL not found", 404
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
