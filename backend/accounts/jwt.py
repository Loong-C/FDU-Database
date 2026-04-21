from datetime import datetime, timedelta
from uuid import uuid4

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework import exceptions

from accounts.models import RefreshToken


def _utc_now() -> datetime:
    return timezone.now()


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise exceptions.AuthenticationFailed("Token is invalid or expired.") from exc

    if payload.get("type") != expected_type:
        raise exceptions.AuthenticationFailed("Token type is invalid.")
    return payload


def build_access_token(user) -> tuple[str, datetime]:
    issued_at = _utc_now()
    expires_at = issued_at + timedelta(minutes=settings.JWT_ACCESS_MINUTES)
    payload = {
        "sub": str(user.pk),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return _encode(payload), expires_at


def build_refresh_token(user) -> tuple[str, datetime, str]:
    issued_at = _utc_now()
    expires_at = issued_at + timedelta(days=settings.JWT_REFRESH_DAYS)
    jti = str(uuid4())
    payload = {
        "sub": str(user.pk),
        "type": "refresh",
        "jti": jti,
        "iat": int(issued_at.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return _encode(payload), expires_at, jti


def issue_token_pair(user) -> dict:
    access_token, access_expires_at = build_access_token(user)
    refresh_token, refresh_expires_at, jti = build_refresh_token(user)
    RefreshToken.objects.create(
        user=user,
        jti=jti,
        token_hash=RefreshToken.hash_token(refresh_token),
        expires_at=refresh_expires_at,
    )
    return {
        "access_token": access_token,
        "access_expires_at": access_expires_at,
        "refresh_token": refresh_token,
        "refresh_expires_at": refresh_expires_at,
        "token_type": "Bearer",
        "user": {
            "id": user.pk,
            "username": user.username,
            "role": user.role,
            "display_name": user.display_name,
        },
    }


def rotate_refresh_token(refresh_token: str) -> dict:
    payload = decode_token(refresh_token, expected_type="refresh")
    token_hash = RefreshToken.hash_token(refresh_token)
    try:
        token_record = RefreshToken.objects.select_related("user").get(
            token_hash=token_hash,
            jti=payload["jti"],
        )
    except RefreshToken.DoesNotExist as exc:
        raise exceptions.AuthenticationFailed("Refresh token is not recognized.") from exc

    if not token_record.is_active:
        raise exceptions.AuthenticationFailed("Refresh token has been revoked.")

    token_record.mark_used()
    user = token_record.user
    access_token, access_expires_at = build_access_token(user)
    new_refresh_token, refresh_expires_at, new_jti = build_refresh_token(user)
    RefreshToken.objects.create(
        user=user,
        jti=new_jti,
        token_hash=RefreshToken.hash_token(new_refresh_token),
        expires_at=refresh_expires_at,
    )
    token_record.revoke(replaced_by_jti=new_jti)
    return {
        "access_token": access_token,
        "access_expires_at": access_expires_at,
        "refresh_token": new_refresh_token,
        "refresh_expires_at": refresh_expires_at,
        "token_type": "Bearer",
        "user": {
            "id": user.pk,
            "username": user.username,
            "role": user.role,
            "display_name": user.display_name,
        },
    }


def revoke_refresh_token(refresh_token: str) -> None:
    payload = decode_token(refresh_token, expected_type="refresh")
    token_hash = RefreshToken.hash_token(refresh_token)
    try:
        token_record = RefreshToken.objects.get(token_hash=token_hash, jti=payload["jti"])
    except RefreshToken.DoesNotExist as exc:
        raise exceptions.AuthenticationFailed("Refresh token is not recognized.") from exc
    token_record.revoke()
