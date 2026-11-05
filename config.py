"""Reads settings from the .env file next to this script (works on Windows too)."""
import os
import pathlib


def _load_env():
    p = pathlib.Path(__file__).with_name(".env")
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()

DOMAIN = os.environ.get("AUTH0_DOMAIN", "")              # e.g. dev-abc123.us.auth0.com
AUDIENCE = os.environ.get("API_AUDIENCE", "https://api.securenova.local")
API_URL = os.environ.get("API_URL", "http://localhost:5000")

WEB_CLIENT_ID = os.environ.get("WEB_CLIENT_ID", "")
WEB_CLIENT_SECRET = os.environ.get("WEB_CLIENT_SECRET", "")
WEB2_CLIENT_ID = os.environ.get("WEB2_CLIENT_ID", "")    # second app, only for the SSO check
WEB2_CLIENT_SECRET = os.environ.get("WEB2_CLIENT_SECRET", "")
M2M_CLIENT_ID = os.environ.get("M2M_CLIENT_ID", "")
M2M_CLIENT_SECRET = os.environ.get("M2M_CLIENT_SECRET", "")

CALLBACK = "http://localhost:3000/callback"
