"""Verify PASETO v4.public access tokens (same format as auth_service / Node `paseto` package)."""

from __future__ import annotations

import json
from functools import lru_cache

import pyseto
from pyseto import Key

from src.core.config import settings


@lru_cache(maxsize=1)
def _public_key() -> Key:
    raw = (settings.paseto_public_key or "").strip()
    if not raw:
        raise RuntimeError("PASETO_PUBLIC_KEY is not set.")
    return Key.from_paserk(raw)


def verify_access_token(token: str) -> dict:
    """
    Validate a v4.public token and return the JSON payload (e.g. `sub` = user id string).
    Raises on invalid signature, expiry, or malformed token.
    """
    token = token.strip()
    pk = _public_key()
    decoded = pyseto.decode(pk, token, deserializer=json)
    return decoded.payload if isinstance(decoded.payload, dict) else {}
