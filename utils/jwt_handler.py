from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from utils.settings import ACCESS_TOKEN_EXPIRE_MINUTES,SECRET_KEY


# Creating JWT Token
def create_token(user_id: str):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY)
    return token

# Verifying JWT Token
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
