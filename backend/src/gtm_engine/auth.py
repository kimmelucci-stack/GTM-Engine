"""Validate access tokens with Supabase Auth, never trust an unverified JWT body."""

import os
from typing import Annotated
from uuid import UUID

import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

bearer = HTTPBearer(auto_error=False)


def verified_owner(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer)],
) -> UUID:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(401, "Accesso richiesto")
    base = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if not base.startswith("https://") or not key:
        raise HTTPException(503, "Autenticazione non configurata")
    try:
        with httpx.Client(timeout=10, follow_redirects=False, trust_env=False) as client:
            response = client.get(base + "/auth/v1/user", headers={
                "apikey": key, "Authorization": "Bearer " + credentials.credentials,
            })
        if response.status_code in (401, 403):
            raise HTTPException(401, "Sessione non valida")
        response.raise_for_status()
        user = response.json()
        if not isinstance(user, dict):
            raise TypeError("invalid_auth_response")
        if user.get("is_anonymous") is not False:
            raise HTTPException(401, "Accesso con account richiesto")
        return UUID(user["id"])
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(503, "Verifica sessione non disponibile") from None
