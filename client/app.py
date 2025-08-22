from flask import Flask, render_template_string, request , redirect
import requests
import os
app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Shortner</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f6f9;
            color: #2c3e50;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        .container {
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 500px;
            width: 100%;
        }

        h1 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #34495e;
        }

        form {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        input[type=text] {
            width: 100%;
            max-width: 400px;
            padding: 12px;
            margin-bottom: 15px;
            border: 1px solid #dcdcdc;
            border-radius: 8px;
            box-sizing: border-box;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        input[type=text]:focus {
            border-color: #007BFF;
            box-shadow: 0 0 6px rgba(0, 123, 255, 0.4);
            outline: none;
        }

        button {
            padding: 12px 25px;
            background-color: #007BFF;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s ease, transform 0.2s ease;
        }

        button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }

        .response-box {
            margin-top: 25px;
            padding: 18px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            background: #ecf5ff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
            text-align: left;
        }

        .response-box strong {
            display: block;
            margin-bottom: 10px;
            font-size: 1rem;
            color: #2c3e50;
        }

        .response-box pre {
            background: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #dcdcdc;
            overflow-x: auto;
            font-size: 0.95rem;
            margin: 8px 0;
        }

        a {
            color: #007BFF;
            text-decoration: none;
            font-weight: 500;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>URL Shortner</h1>
        <form method="POST">
            <input type="text" name="url" placeholder="Enter URL" required>
            <button type="submit">Submit</button>
        </form>
        {% if response %}
        <div class="response-box">
            <strong>Response:</strong>
            <pre>http://{{ ip }}/{{ response }}</pre>
            <p><a href="/{{ response }}">Shortened Link</a></p>
            <p>Here is the analytics link: <a href="/analytics/{{ response }}">Analytics</a></p>
        </div>
        {% endif %}
    </div>
</body>
</html>

"""


analytics = """
<!DOCTYPE html>
<html>
<head>
    <title>URL Analytics</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 0; 
            background: #f4f6f9; 
            color: #333; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
        }

        .container {
            background: #fff;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 400px;
            width: 100%;
        }

        h1 {
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 15px;
        }

        h2 {
            font-size: 3rem;
            color: #3498db;
            margin: 10px 0;
        }

        input[type=text] { 
            width: 80%; 
            padding: 10px; 
            border: 1px solid #ccc; 
            border-radius: 8px;
            margin-top: 15px;
            outline: none;
            transition: 0.3s;
        }

        input[type=text]:focus {
            border-color: #3498db;
            box-shadow: 0 0 5px rgba(52,152,219,0.5);
        }

        button { 
            margin-top: 15px;
            padding: 10px 20px; 
            background: #3498db; 
            color: white; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 1rem;
            transition: background 0.3s ease;
        }

        button:hover { 
            background: #2980b9;
        }

        .response-box { 
            margin-top: 20px; 
            padding: 12px; 
            border: 1px solid #e0e0e0; 
            border-radius: 8px;
            background: #ecf5ff; 
            font-size: 0.95rem; 
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Number of Link Visits</h1>
        <h2>{{ NumberOfVisits }}</h2>
    </div>
</body>
</html>

"""

@app.route("/", methods=[ "GET" , "POST"])
def index():
    response_text = None
    token_url = "http://169.254.169.254/latest/api/token"
    headers = {"X-aws-ec2-metadata-token-ttl-seconds": "21600"}
    token = requests.put(token_url, headers=headers, timeout=2).text

    # Step 2: Query metadata with the token
    metadata_url = f"http://169.254.169.254/latest/meta-data/public-hostname"
    headers = {"X-aws-ec2-metadata-token": token}
    DNS = requests.get(metadata_url, headers=headers, timeout=2)
    if request.method == "POST":
        user_url = request.form.get("url")
        try:
            resp = requests.post(os.environ.get("API_POST_URL"), json={"url": user_url})
            resp.raise_for_status()
            data = resp.json()              
            response_text = data.get('id') 
        except Exception as e:
            response_text = f"Error: {e}"

    return render_template_string(TEMPLATE, response=response_text ,ip = DNS.text)



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
