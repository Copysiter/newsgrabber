from datetime import datetime, timedelta
from typing import Optional

from jose import jwt

from core.config import settings  # noqa


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {'exp': exp, 'nbf': now, 'sub': email},
        settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY,
                                   algorithms=[settings.JWT_ALGORITHM])
        return decoded_token['sub']
    except jwt.JWTError:
        return None
