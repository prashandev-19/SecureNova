"""Short-lived M2M token: works now (200), rejected after it expires (401).
Start api_server.py first. API token lifetime must be 60 seconds."""
import datetime, time

import requests

import config


def say(msg):
    print(f"[{datetime.datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}", flush=True)


data = requests.post(f"https://{config.DOMAIN}/oauth/token", json={
    "grant_type": "client_credentials", "client_id": config.M2M_CLIENT_ID,
    "client_secret": config.M2M_CLIENT_SECRET, "audience": config.AUDIENCE}).json()
if "access_token" not in data:
    raise SystemExit(f"Token request failed: {data}")
headers = {"Authorization": "Bearer " + data["access_token"]}
say(f"Got M2M token, expires_in = {data['expires_in']} seconds")

say(f"Call /chat with fresh token -> {requests.get(config.API_URL + '/chat', headers=headers).status_code} OK")
say("Waiting 65 seconds for the token to expire...")
time.sleep(65)
say(f"Replay expired token on /chat -> {requests.get(config.API_URL + '/chat', headers=headers).status_code} Unauthorized")
