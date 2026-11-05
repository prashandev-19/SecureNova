"""Demo API. /chat needs scope read:ai-data, /admin needs write:admin.
Valid token -> 200, missing scope -> 403, expired/invalid token -> 401.
Run: python api_server.py  (API docs page: /docs)"""

import jwt
import uvicorn
from fastapi import Depends, FastAPI , HTTPException
from fastapi.security import HTTPAuthorizationCredentials , HTTPBearer
from jwt import PyJWKClient

import config
app =FastAPI(title="SecureNova AI API")
bearer=HTTPBearer(auto_error=False)
ISSUER=f"https://{config.DOMAIN}"
_jwks = PyJWKClient(f"https://{config.DOMAIN}/.well-known.jwks.json") if config.DOMAIN
else None


def get_key(token):
    """ Get Auth0's public key that matches this token (so we can check its signature)."""
    return _jwks.get_signing_key_from_jwt(token).key


def require_scope(scope):
    def check(cred: HTTPAuthorizationCredentials = Depends(bearer)):
        if cred is None:
            raise HTTPException(status_code=401, detail="missing token")
        try:
            #Checks signature(RS256)
            claims = jwt.decode(creds.credentials, get_key(creds.credentials),algorithms=["RS256"],audience=config.AUDIENCE,
                                issuer=ISSUER)
        except jwt.PyJWTError:
            raise HTTPException(status_code=401,detail="invalid or expired token")

        if scope not in claims.get("scope","").split():
            raise HTTPException(status_code=403,detail=f"missing scope {scope}")

        return claims
    return check

@app.get("/chat")
def chat(claims: dict= Depends(require_scope("read:ai-data"))):
    return {"reply":"Hello form the AI chat API"}

@app.get("/admin")
def admin(claims: dict= Depends(require_scope("write:admin"))):
    return {"message":"Admin action done"}

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=5000)


