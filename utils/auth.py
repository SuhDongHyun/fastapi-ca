from typing import Annotated
from dataclasses import dataclass
from enum import StrEnum
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = "THIS_IS_SUPER_SECRET_KEY"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


class Role(StrEnum):
    USER = "USER"
    ADMIN = "ADMIN"


@dataclass
class CurrentUser:
    user_id: str
    role: Role


def create_access_token(
    payload: dict,
    role: Role,
    expires_delta: timedelta = timedelta(hours=6),
):
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"role": role, "exp": expire})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> CurrentUser:
    payload = decode_access_token(token)
    user_id = payload.get("user_id")
    role = payload.get("role")
    if user_id is None or role is None or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return CurrentUser(user_id=user_id, role=role)


def get_admin_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> CurrentUser:
    payload = decode_access_token(token)
    role = payload.get("role")
    if role is None or role != Role.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return CurrentUser(user_id="ADMIN_USER_ID", role=role)
