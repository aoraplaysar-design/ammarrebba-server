
import os
import secrets
from urllib.parse import urlencode

import requests
from flask import Flask, redirect, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

CLIENT_ID = "1546207967643439224"
CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET", "")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
REDIRECT_URI = f"{BASE_URL}/discord/callback"

AUTHORIZE_URL = "https://discord.com/oauth2/authorize"
TOKEN_URL = "https://discord.com/api/oauth2/token"
USER_URL = "https://discord.com/api/users/@me"


@app.route("/")
def index():
    return redirect("/link")


@app.route("/link")
def link():
    return r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#050000">
<title>AMMAR REBBA</title>
<style>
*{box-sizing:border-box}
body{margin:0;min-height:100vh;background:#030303;color:white;
font-family:Arial,sans-serif;overflow:hidden}
body:before{content:"";position:fixed;inset:-30%;
background:radial-gradient(ellipse,rgba(170,0,0,.3),transparent 60%);
animation:fog 5s ease-in-out infinite alternate}
.intro{position:fixed;inset:0;z-index:5;background:#020202;
display:flex;flex-direction:column;align-items:center;justify-content:center;
padding:18px;text-align:center;animation:leave 1s ease 7s forwards}
.glow{position:absolute;width:230px;height:230px;border-radius:50%;
background:#650000;filter:blur(85px);animation:pulse 2s infinite}
.person{position:relative;width:190px;height:250px;margin-bottom:30px;
opacity:0;animation:appear 1.5s ease 1.5s forwards;
filter:drop-shadow(0 0 22px red)}
.hood{position:absolute;top:0;left:38px;width:114px;height:125px;
background:linear-gradient(120deg,#450000,#080808,#260000);
clip-path:polygon(50% 0,92% 18%,100% 75%,75% 100%,25% 100%,0 75%,8% 18%)}
.face{position:absolute;top:23px;left:65px;width:60px;height:75px;
border-radius:50%;background:#010101}
.eye{position:absolute;top:58px;width:15px;height:4px;background:red;
box-shadow:0 0 14px 5px red;animation:blink 1s infinite alternate}
.e1{left:72px}.e2{left:104px}
.body{position:absolute;top:88px;left:18px;width:154px;height:160px;
background:linear-gradient(90deg,#200000,#050505,#260000);
clip-path:polygon(35% 0,65% 0,82% 15%,100% 100%,0 100%,18% 15%)}
h2{position:relative;z-index:2;margin:0;font-size:clamp(19px,5vw,34px);
opacity:0;animation:title 1s ease 3.7s forwards;
text-shadow:0 0 8px red,0 0 25px #a00000}
.sub{position:relative;z-index:2;margin-top:16px;color:#a77;
font-size:10px;letter-spacing:5px;opacity:0;
animation:title 1s ease 5s forwards}
.main{position:relative;z-index:1;min-height:100vh;display:flex;
align-items:center;justify-content:center;padding:20px;
opacity:0;animation:show 1s ease 7.7s forwards}
.card{width:100%;max-width:420px;padding:35px 25px;text-align:center;
background:rgba(12,6,6,.96);border:1px solid #650000;border-radius:15px;
box-shadow:0 0 40px #260000}
.logo{width:72px;height:72px;margin:0 auto 20px;border:1px solid red;
border-radius:50%;display:grid;place-items:center;font-size:32px;font-weight:bold;
text-shadow:0 0 15px red;box-shadow:0 0 25px #400000}
h1{font-size:27px;letter-spacing:3px;text-shadow:0 0 15px #900}
p{color:#b5a0a0;line-height:1.8;font-size:14px;margin:20px 0 27px}
a{display:block;padding:16px;border:1px solid #ff3535;border-radius:8px;
background:linear-gradient(90deg,#580000,#bd0000,#580000);
color:white;text-decoration:none;font-weight:bold;letter-spacing:1px;
transition:.25s}
a:hover{box-shadow:0 0 25px red;transform:translateY(-2px)}
.small{margin-top:20px;color:#715555;font-size:10px;letter-spacing:2px}
@keyframes fog{to{transform:translate(5%,3%) scale(1.1)}}
@keyframes pulse{50%{opacity:.4;transform:scale(1.25)}}
@keyframes appear{0%{opacity:0;transform:translateY(35px) scale(.7)}
70%{opacity:1;transform:scale(1.05)}100%{opacity:1;transform:scale(1)}}
@keyframes blink{to{opacity:.45;box-shadow:0 0 20px 7px red}}
@keyframes title{to{opacity:1}}
@keyframes leave{to{opacity:0;visibility:hidden;pointer-events:none}}
@keyframes show{to{opacity:1}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation-duration:.01ms!important;animation-delay:0ms!important}}
</style>
</head>
<body>
<section class="intro">
  <div class="glow"></div>
  <div class="person" aria-hidden="true">
    <div class="hood"></div>
    <div class="face"></div>
    <div class="eye e1"></div>
    <div class="eye e2"></div>
    <div class="body"></div>
  </div>
  <h2>☠️ 𝘼𝙈𝙈𝘼𝙍 𝙎𝙏𝙊𝙈𝙋𝙎 𝙃𝙔𝙋𝙀𝙍 ☠️</h2>
  <div class="sub">THE SHADOW HAS ARRIVED</div>
</section>

<main class="main">
  <div class="card">
    <div class="logo">A</div>
    <h1>AMMAR REBBA</h1>
    <p>Enter the darkness.<br>Link your Discord account to continue.</p>
    <a href="/discord/login">☠ &nbsp; CONTINUE WITH DISCORD</a>
    <div class="small">SECURE AUTHENTICATION</div>
  </div>
</main>
</body>
</html>
"""


@app.route("/discord/login")
def discord_login():
    if not BASE_URL or not CLIENT_SECRET:
        return "BASE_URL or DISCORD_CLIENT_SECRET is not configured.", 500

    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state

    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "identify email",
        "state": state
    }
    return redirect(AUTHORIZE_URL + "?" + urlencode(params))


@app.route("/discord/callback")
def discord_callback():
    if request.args.get("error"):
        return "Discord authorization was cancelled.", 400

    code = request.args.get("code")
    state = request.args.get("state")
    saved_state = session.get("oauth_state")

    if not code or not state or not saved_state:
        return "Missing or expired OAuth parameters.", 400

    if not secrets.compare_digest(saved_state, state):
        return "Invalid OAuth state.", 400

    session.pop("oauth_state", None)

    try:
        response = requests.post(
            TOKEN_URL,
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI
            },
            timeout=15
        )
        if response.status_code != 200:
            return "Discord token exchange failed.", 400

        token = response.json().get("access_token")
        if not token:
            return "Discord access token missing.", 400

        response = requests.get(
            USER_URL,
            headers={"Authorization": f"Bearer {token}"},
            timeout=15
        )
        if response.status_code != 200:
            return "Could not retrieve Discord account.", 400

        user_id = response.json().get("id")
        if not user_id:
            return "Discord user ID missing.", 400

    except requests.RequestException:
        return "Could not contact Discord.", 502

    return redirect("ammarrebba://auth?" + urlencode({"oid": user_id}))


@app.route("/health")
def health():
    return {"status": "ok", "service": "ammarrebba", "discord": True}


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "4000"))
    )
