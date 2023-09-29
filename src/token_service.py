import uuid
from datetime import datetime

import jwt

JWT_RESERVED_CLAIMS = ("iss", "sub", "aud", "exp", "nbf", "iat", "jti")

HASH_ALGORITHM = "HS256"


def generate_token(payload: dict, secret_key: str, expires_at: datetime) -> str:
    payload = payload.copy()
    payload["exp"] = expires_at
    payload["iat"] = datetime.utcnow()
    payload["jti"] = str(uuid.uuid4())
    return jwt.encode(payload, secret_key, algorithm=HASH_ALGORITHM)


def validate_token(access_token: str, secret_key: str) -> dict:
    return jwt.decode(access_token, secret_key, algorithms=[HASH_ALGORITHM])


def get_token_payload(access_token: str) -> dict:
    payload = jwt.decode(access_token, options={"verify_signature": False})

    payload = {
        key: value for key, value in payload.items() if key not in JWT_RESERVED_CLAIMS
    }
    return payload


def get_token_identity(access_token: str) -> str:
    payload = jwt.decode(access_token, options={"verify_signature": False})

    return payload.get("jti")
