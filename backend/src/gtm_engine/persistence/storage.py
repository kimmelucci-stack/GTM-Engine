"""Bounded private Storage HTTP operations. No public/signed URLs or automatic retries."""

import hashlib
import json
import os
import re
from urllib.parse import urlsplit

import httpx

BUCKET = "gtm-evidence"
MAX_BYTES = 6 * 1024 * 1024
CONTENT_TYPES = frozenset({"application/json", "text/plain", "text/html", "image/png",
                           "image/jpeg",
                           "application/vnd.openxmlformats-officedocument.presentationml.presentation"})
KEY = re.compile(r"[0-9a-f-]{36}/[0-9a-f-]{36}/[0-9a-f]{64}\Z")


class StorageError(Exception):
    """Only stable safe codes may leave this boundary."""


class PrivateStorage:
    def __init__(self, base: str, secret: str, *, transport: httpx.BaseTransport | None = None):
        parsed = urlsplit(base)
        if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                or parsed.path not in ("", "/") or parsed.query or parsed.fragment or not secret):
            raise StorageError("storage_not_configured")
        self._base, self._secret, self._transport = base.rstrip("/"), secret, transport

    @classmethod
    def configured(cls) -> "PrivateStorage":
        # Dedicated server setting: never read from frontend settings or a user request.
        return cls(os.environ.get("SUPABASE_URL", ""),
                   os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))

    def _request(self, method: str, path: str, *, maximum: int = MAX_BYTES, **kwargs
                 ) -> tuple[int, bytes]:
        headers = {"apikey": self._secret}
        # Legacy service_role JWTs require Bearer; modern secret keys use apikey alone.
        if not self._secret.startswith("sb_secret_"):
            headers["Authorization"] = "Bearer " + self._secret
        headers.update(kwargs.pop("headers", {}))
        try:
            with (
                httpx.Client(timeout=httpx.Timeout(30, connect=10), follow_redirects=False,
                             trust_env=False, transport=self._transport) as client,
                client.stream(method, self._base + "/storage/v1/" + path,
                              headers=headers, **kwargs) as response,
            ):
                chunks, size = [], 0
                for chunk in response.iter_bytes():
                    size += len(chunk)
                    if size > maximum:
                        raise StorageError("storage_response_too_large")
                    chunks.append(chunk)
                return response.status_code, b"".join(chunks)
        except httpx.HTTPError:
            raise StorageError("storage_request_uncertain") from None

    def ensure_private_bucket(self) -> None:
        status, body = self._request("GET", "bucket/" + BUCKET, maximum=16384)
        if status == 404 or (status == 400 and self._error_code(body) == "NoSuchBucket"):
            status, _ = self._request("POST", "bucket", maximum=16384, json={
                "id": BUCKET, "name": BUCKET, "public": False,
                "file_size_limit": MAX_BYTES, "allowed_mime_types": sorted(CONTENT_TYPES)})
            if status not in (200, 201):
                raise StorageError("storage_bucket_create_failed")
            status, body = self._request("GET", "bucket/" + BUCKET, maximum=16384)
        if status != 200:
            raise StorageError("storage_bucket_unavailable")
        try:
            bucket = json.loads(body)
            valid = (bucket["id"] == BUCKET and bucket["public"] is False
                     and 0 < int(bucket["file_size_limit"]) <= MAX_BYTES
                     and bool(bucket["allowed_mime_types"])
                     and set(bucket["allowed_mime_types"]).issubset(CONTENT_TYPES))
        except (ValueError, TypeError, KeyError):
            valid = False
        if not valid:
            raise StorageError("unsafe_storage_bucket")

    @staticmethod
    def _error_code(body: bytes) -> str | None:
        try:
            value = json.loads(body)
            return value.get("code") if isinstance(value, dict) else None
        except ValueError:
            return None

    @staticmethod
    def _key(key: str) -> None:
        if not KEY.fullmatch(key):
            raise StorageError("invalid_storage_key")

    def download(self, key: str, *, expected_size: int, digest: str) -> bytes:
        self._key(key)
        if not 0 < expected_size <= MAX_BYTES:
            raise StorageError("invalid_artifact_size")
        status, body = self._request("GET", "object/authenticated/" + BUCKET + "/" + key,
                                     maximum=expected_size)
        if status != 200:
            raise StorageError("storage_download_failed")
        if len(body) != expected_size or hashlib.sha256(body).hexdigest() != digest:
            raise StorageError("artifact_integrity_failed")
        return body

    def upload_verified(self, key: str, body: bytes, content_type: str) -> None:
        self._key(key)
        if (not 0 < len(body) <= MAX_BYTES or content_type not in CONTENT_TYPES
                or hashlib.sha256(body).hexdigest() != key.rsplit("/", 1)[1]):
            raise StorageError("invalid_artifact_content")
        self.ensure_private_bucket()
        status, response = self._request("POST", "object/" + BUCKET + "/" + key, maximum=16384,
                                  content=body, headers={"Content-Type": content_type,
                                                         "x-upsert": "false"})
        # Existing objects must match exactly; never replace them. Timeout is left pending.
        duplicate = (status in (400, 409) and self._error_code(response)
                     in {"ResourceAlreadyExists", "KeyAlreadyExists"})
        if status not in (200, 201) and not duplicate:
            raise StorageError("storage_upload_failed")
        self.download(key, expected_size=len(body), digest=key.rsplit("/", 1)[1])
