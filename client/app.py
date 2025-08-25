from flask import Flask, render_template_string, request , redirect ,render_template
import requests
import os

app = Flask(__name__)

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

    return render_template("index.html", response=response_text ,ip = DNS.text)



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
        resp = requests.get(f"{os.environ.get("API_GET_ANALYTICS")}/{shortId}")
        resp.raise_for_status() 
        resp=resp.json()
        print(resp)
        NumberOfVisits = len(resp.get('visitHistory'))
        if resp:
            if NumberOfVisits:
                return render_template_string(analytics, NumberOfVisits=NumberOfVisits)
            else:
                return render_template_string(analytics, NumberOfVisits="0")
        else:
            return render_template("analytics", NumberOfVisits="URL not found" ) , 404
    except Exception as e:
        return f"Error: {e}", 500


if __name__ == "__main__":
    app.run(ssl_context='adhoc',host='0.0.0.0', port=443)
