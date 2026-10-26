"""Server-only Supabase session exchange. Browser receives an encrypted HttpOnly cookie."""

import json
import os
import time
from urllib.parse import urlsplit

import httpx
from cryptography.fernet import Fernet, InvalidToken
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

COOKIE = "gtm_session"
MAX_AGE = 8 * 60 * 60
router = APIRouter(prefix="/auth")


def origin() -> str:
    value = os.environ.get("APP_ORIGIN", "http://127.0.0.1:5173")
    parsed = urlsplit(value)
    if (parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username
            or parsed.password or parsed.path or parsed.query or parsed.fragment
            or (parsed.scheme == "http" and parsed.hostname not in ("127.0.0.1", "localhost"))):
        raise HTTPException(503, "Accesso non configurato")
    return value


def check_origin(request: Request) -> None:
    if request.headers.get("origin") != origin():
        raise HTTPException(403, "Richiesta non consentita")


def cipher() -> Fernet:
    try:
        return Fernet(os.environ.get("SESSION_ENCRYPTION_KEY", ""))
    except (ValueError, TypeError):
        raise HTTPException(503, "Accesso non configurato") from None


def read_session(request: Request) -> dict:
    value = request.cookies.get(COOKIE, "")
    try:
        if not 0 < len(value) <= 3800:
            raise ValueError()
        data = json.loads(cipher().decrypt(value.encode(), ttl=MAX_AGE))
        if (set(data) != {"a", "r", "created"} or not isinstance(data["a"], str)
                or not isinstance(data["r"], str) or not isinstance(data["created"], int)
                or not 0 <= time.time() - data["created"] < MAX_AGE):
            raise ValueError()
        return data
    except (InvalidToken, ValueError, TypeError, KeyError):
        raise HTTPException(401, "Sessione scaduta. Accedi di nuovo.") from None


def auth_call(path: str, *, payload: dict | None = None, access: str | None = None) -> dict:
    base, key = os.environ.get("SUPABASE_URL", ""), os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
    if not base.startswith("https://") or not key:
        raise HTTPException(503, "Accesso non configurato")
    headers = {"apikey": key}
    if access:
        headers["Authorization"] = "Bearer " + access
    try:
        with httpx.Client(timeout=10, trust_env=False, follow_redirects=False) as client:
            response = client.post(base.rstrip("/") + "/auth/v1/" + path,
                                   json=payload, headers=headers)
        if response.status_code in (400, 401, 403, 422):
            raise HTTPException(401, "Accesso non riuscito. Verifica i dati e riprova.")
        if response.status_code == 429:
            raise HTTPException(429, "Troppi tentativi. Attendi prima di riprovare.")
        response.raise_for_status()
        return response.json() if response.content else {}
    except (httpx.HTTPError, ValueError):
        raise HTTPException(503, "Servizio di accesso temporaneamente non disponibile") from None


def set_session(response: Response, data: dict, created: int | None = None) -> None:
    try:
        access, refresh = data["access_token"], data["refresh_token"]
        if not isinstance(access, str) or not access or not isinstance(refresh, str) or not refresh:
            raise ValueError()
        value = cipher().encrypt(json.dumps({"a": access, "r": refresh,
                                             "created": created or int(time.time())}).encode()).decode()
        if len(value) > 3800:
            raise ValueError()
    except (ValueError, KeyError, TypeError):
        raise HTTPException(503, "Sessione non disponibile") from None
    response.set_cookie(COOKIE, value, max_age=MAX_AGE, httponly=True, samesite="strict",
                        secure=origin().startswith("https://"), path="/")
    response.headers["Cache-Control"] = "private, no-store"


class LoginInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: str = Field(min_length=3, max_length=320, pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: SecretStr

    @model_validator(mode="after")
    def valid_length(self) -> "LoginInput":
        if not 1 <= len(self.password.get_secret_value()) <= 1024:
            raise ValueError("invalid_login_input")
        return self


@router.post("/login", dependencies=[Depends(check_origin)])
def login(body: LoginInput, response: Response):
    cipher()  # Fail before contacting Auth if server encryption is missing.
    data = auth_call("token?grant_type=password",
                     payload={"email": body.email, "password": body.password.get_secret_value()})
    if data.get("user", {}).get("is_anonymous") is not False:
        raise HTTPException(401, "Accesso con account richiesto")
    set_session(response, data)
    return {"authenticated": True}


@router.post("/refresh", dependencies=[Depends(check_origin)])
def refresh(request: Request, response: Response):
    session = read_session(request)
    data = auth_call("token?grant_type=refresh_token", payload={"refresh_token": session["r"]})
    set_session(response, data, session["created"])
    return {"authenticated": True}


@router.post("/logout", dependencies=[Depends(check_origin)])
def logout(request: Request, response: Response):
    try:
        session = read_session(request)
        auth_call("logout?scope=global", access=session["a"])
    except HTTPException as error:
        if error.status_code != 401:
            raise
    response.delete_cookie(COOKIE, path="/", httponly=True, samesite="strict",
                           secure=origin().startswith("https://"))
    response.headers["Cache-Control"] = "private, no-store"
    return {"authenticated": False}
