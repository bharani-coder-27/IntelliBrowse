from fastapi import Depends, HTTPException, Request
from jose import jwt, JWTError, ExpiredSignatureError
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os

SECRET_KEY = os.getenv("SECRET_KEY", "IntelliBrowse")
ALGORITHM = "HS256"
OAUTH_SECRET_KEY = os.getenv("OAUTH_SECRET_KEY", "myoauthsecret")

def get_current_user(request: Request):
    token = request.cookies.get("intelli_session")

    if not token:
        raise HTTPException(status_code=401, detail="Token missing")

    print("🔹 Token from cookie:", token[:40])

    # Try JWT decode (email/password logins)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id:
            return int(user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError:
        pass

    # Try OAuth serializer fallback
    try:
        serializer = URLSafeTimedSerializer(OAUTH_SECRET_KEY)
        data = serializer.loads(token, max_age=60 * 60 * 24 * 7)
        return int(data.get("id"))
    except (BadSignature, SignatureExpired):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
