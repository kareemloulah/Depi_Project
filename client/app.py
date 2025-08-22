from flask import Flask, render_template_string, request , redirect
import requests
import os
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Sender</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        input[type=text] { width: 300px; padding: 8px; }
        button { padding: 8px 16px; }
        .response-box { margin-top: 10px; padding: 10px; border: 1px solid #ccc; background: #f9f9f9; }
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
        <p> </p>
        <a href="/{{ response }}">Link</a>
        <p> </p>
        here is the analytics link:
        <a href="/analytics/{{ response }}">Analytics</a>
        
    </div>
    {% endif %}
</body>
</html>
"""


analytics = """
<!DOCTYPE html>
<html>
<head>
    <title>URL analytics</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; }
        input[type=text] { width: 300px; padding: 8px; }
        button { padding: 8px 16px; }
        .response-box { margin-top: 10px; padding: 10px; border: 1px solid #ccc; background: #f9f9f9; }
    </style>
</head>
<body>
    <h1>Number of Link Visits</h1>
    <h2>{{ NumberOfVisits }}</h2>
</body>
</html>
"""

@app.route("/", methods=[ "GET" , "POST"])
def index():

    print(requests.get("http://checkip.amazonaws.com").text)
    response_text = None
    if request.method == "POST":
        user_url = request.form.get("url")
        try:
            resp = requests.post(os.environ.get("API_POST_URL"), json={"url": user_url})
            resp.raise_for_status()
            data = resp.json()              
            response_text = data.get('id') 
        except Exception as e:
            response_text = f"Error: {e}"

    return render_template_string(TEMPLATE, response=response_text ,ip = requests.get("http://checkip.amazonaws.com").text)



@app.route("/<shortId>")
def go(shortId):
    try:
        resp = requests.get(f"{os.environ.get("API_GET_URL")}/{shortId}")
        resp.raise_for_status()
        data = resp.json()  
        redirect_url = data.get('redirectUrl')  
        if redirect_url:
            return redirect(redirect_url, code=302)
        else:
            return "URL not found", 404
    except Exception as e:
        return f"Error: {e}", 500


@app.route("/analytics/<shortId>")
def Analytics(shortId):
    try:
        resp = requests.get(f"{os.environ.get("API_GET_URL")}/{shortId}")
        resp.raise_for_status() 
        resp=resp.json()
        NumberOfVisits = len(resp.get('visitHistory'))
        if NumberOfVisits:
            return render_template_string(analytics, NumberOfVisits=NumberOfVisits)
        else:
            return "URL not found", 404
    except Exception as e:
        return f"Error: {e}", 50


if __name__ == "__main__":
    app.run(ssl_context='adhoc',host='0.0.0.0', port=443 , debug=True)

