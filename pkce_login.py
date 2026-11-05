"""Log in with Authorization Code + PKCE, print the token, then test the API.
  python pkce_login.py                 main app (Regular Web App)
  python pkce_login.py --client web2   second app (SSO check: no login screen should appear)
Works locally and in GitHub Codespaces (you open the link in your own browser).
Start api_server.py first."""
import argparse, base64, datetime, hashlib, json, secrets, urllib.parse

import requests

import config

ap = argparse.ArgumentParser()
ap.add_argument("--client", choices=["web", "web2"], default="web")
args = ap.parse_args()
cid, secret = ((config.WEB_CLIENT_ID, config.WEB_CLIENT_SECRET) if args.client == "web"
               else (config.WEB2_CLIENT_ID, config.WEB2_CLIENT_SECRET))


def now():
    return datetime.datetime.now().isoformat(sep=" ", timespec="seconds")


b64 = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=").decode()
verifier = b64(secrets.token_bytes(48))                      # PKCE secret
challenge = b64(hashlib.sha256(verifier.encode()).digest())  # sent to Auth0
state = secrets.token_urlsafe(16)

url = f"https://{config.DOMAIN}/authorize?" + urllib.parse.urlencode({
    "response_type": "code", "client_id": cid, "redirect_uri": config.CALLBACK,
    "scope": "openid profile email read:ai-data",            # user-level scope only
    "audience": config.AUDIENCE, "state": state,
    "code_challenge": challenge, "code_challenge_method": "S256"})

print("\n1) Open this link in YOUR browser and log in:\n\n" + url + "\n")
print("2) After login the browser shows 'This site can't be reached' on localhost:3000. That is expected.")
back = input("3) Copy the full address from the address bar and paste it here:\n> ").strip()
got = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(back).query).items()}
if "code" not in got or got.get("state") != state:
    raise SystemExit(f"Login failed or state mismatch: {got}")

tok = requests.post(f"https://{config.DOMAIN}/oauth/token", data={
    "grant_type": "authorization_code", "client_id": cid, "client_secret": secret,
    "code": got["code"], "redirect_uri": config.CALLBACK, "code_verifier": verifier}).json()
json.dump(tok, open("tokens.json", "w"), indent=2)
print(f"[{now()}] Login OK ({args.client}). Tokens saved in tokens.json - paste them into jwt.io")

for path in ("/chat", "/admin"):
    r = requests.get(config.API_URL + path, headers={"Authorization": "Bearer " + tok["access_token"]})
    print(f"[{now()}] GET {path} -> {r.status_code}")
