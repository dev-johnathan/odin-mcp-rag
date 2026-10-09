"""Autenticação simples para o Odin usando JWT.

A autenticação principal é por chaves de API, mas quando o ambiente define
JWT_SECRET, o backend também aceita tokens assinados em padrão JWT.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from odin_rag_mcp.config import settings


def _get_secret() -> str:
    secret = os.getenv("JWT_SECRET") or settings.jwt_secret
    if not secret:
        raise ValueError("JWT_SECRET is not configured.")
    return secret


def create_access_token(payload: dict[str, Any], expires_minutes: int = 60) -> str:
    """Cria um token JWT para um sujeito autenticado."""
    to_encode = dict(payload)
    expiry = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expiry
    return jwt.encode(to_encode, _get_secret(), algorithm=settings.jwt_algorithm)


def verify_access_token(token: str) -> dict[str, Any]:
    """Valida e retorna o payload do JWT."""
    return jwt.decode(token, _get_secret(), algorithms=[settings.jwt_algorithm])
