import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    secrets.token_hex(32)
)

DISCORD_CLIENT_ID = "1546207967643439224"
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

DISCORD_AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token"
DISCORD_USER_URL = "https://discord.com/api/users/@me"

REDIRECT_URI = f"{BASE_URL}/discord/callback"


@app.route("/")
def index():
    return redirect("/link")


@app.route("/link")
def link():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Account Link</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: radial-gradient(
        circle at top,
        #252a40,
        #0b0c11 65%
    );
    font-family: Arial, sans-serif;
    color: white;
}

.card {
    width: 90%;
    max-width: 430px;
    padding: 36px 28px;
    text-align: center;
    border-radius: 20px;
    background: rgba(20,21,31,.96);
    box-shadow: 0 20px 60px rgba(0,0,0,.55);
}

.logo {
    width: 75px;
    height: 75px;
    margin: auto;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #5865f2;
    font-size: 34px;
    font-weight: bold;
}

h1 {
    margin: 22px 0 10px;
}

p {
    color: #aeb2c2;
    line-height: 1.6;
    margin-bottom: 28px;
}

.button {
    display: block;
    padding: 15px;
    border-radius: 12px;
    background: #5865f2;
    color: white;
    text-decoration: none;
    font-weight: bold;
}

.button:hover {
    background: #4752c4;
}

.small {
    margin-top: 20px;
    color: #666b7d;
    font-size: 12px;
}
</style>
</head>

<body>

<div class="card">

    <div class="logo">D</div>

    <h1>Account Link</h1>

    <p>
        Link your Discord account to continue.
    </p>

    <a class="button" href="/discord/login">
        Continue with Discord
    </a>

    <div class="small">
        Secure Discord authentication
    </div>

</div>

</body>
</html>
"""


@app.route("/discord/login")
def discord_login():

    if not BASE_URL:
        return "BASE_URL is not configured.", 500

    if not DISCORD_CLIENT_SECRET:
        return "DISCORD_CLIENT_SECRET is not configured.", 500

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "identify email",
        "state": state
    }

    return redirect(
        DISCORD_AUTHORIZE_URL + "?" + urlencode(params)
    )


@app.route("/discord/callback")
def discord_callback():

    if request.args.get("error"):
        return "Discord authorization was cancelled.", 400

    code = request.args.get("code")
    state = request.args.get("state")

    if not code or not state:
        return "Missing OAuth parameters.", 400

    saved_state = session.get("oauth_state")

    if not saved_state:
        return "OAuth session expired.", 400

    if not secrets.compare_digest(saved_state, state):
        return "Invalid OAuth state.", 400

    session.pop("oauth_state", None)

    token_data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    try:
        response = requests.post(
            DISCORD_TOKEN_URL,
            data=token_data,
            timeout=15
        )
    except requests.RequestException:
        return "Could not contact Discord.", 502

    if response.status_code != 200:
        return "Discord token exchange failed.", 400

    token = response.json().get("access_token")

    if not token:
        return "Discord access token missing.", 400

    try:
        response = requests.get(
            DISCORD_USER_URL,
            headers={
                "Authorization": f"Bearer {token}"
            },
            timeout=15
        )
    except requests.RequestException:
        return "Could not retrieve Discord account.", 502

    if response.status_code != 200:
        return "Could not retrieve Discord account.", 400

    user = response.json()
    oid = user.get("id")

    if not oid:
        return "Discord user ID missing.", 400

    callback = "ammarrebba://auth?" + urlencode({
        "oid": oid
    })

    return redirect(callback)


@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "ammarrebba",
        "discord": True
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "4000"))

    app.run(
        host="0.0.0.0",
        port=port
    )