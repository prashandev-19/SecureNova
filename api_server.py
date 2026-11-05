"""Demo API. /chat needs scope read:ai-data, /admin needs write:admin.
Valid token -> 200, missing scope -> 403, expired/invalid token -> 401.
Run: python api_server.py"""
import functools

import jwt
from flask import Flask, jsonify, request
from jwt import PyJWKClient

import config

app = Flask(__name__)
ISSUER = f"https://{config.DOMAIN}/"
_jwks = PyJWKClient(f"https://{config.DOMAIN}/.well-known/jwks.json") if config.DOMAIN else None


def get_key(token):
    return _jwks.get_signing_key_from_jwt(token).key


def require_scope(scope):
    def wrap(fn):
        @functools.wraps(fn)
        def inner():
            token = request.headers.get("Authorization", "")[7:]
            try:
                claims = jwt.decode(token, get_key(token), algorithms=["RS256"],
                                    audience=config.AUDIENCE, issuer=ISSUER)
            except jwt.PyJWTError:          # includes expired tokens
                return jsonify(error="unauthorized"), 401
            if scope not in claims.get("scope", "").split():
                return jsonify(error="forbidden", required=scope), 403
            return fn()
        return inner
    return wrap


@app.route("/chat")
@require_scope("read:ai-data")
def chat():
    return jsonify(reply="Hello from the AI chat API")


@app.route("/admin")
@require_scope("write:admin")
def admin():
    return jsonify(message="Admin action done")


if __name__ == "__main__":
    app.run(port=5000)
