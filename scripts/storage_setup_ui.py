"""Single-use local masked Storage credential setup, reusing the hardened HTTP boundary."""

import json
import secrets
from html import escape
from http.server import HTTPServer
from threading import Thread
from urllib.parse import parse_qs

from database_setup_ui import CSS, ROOT, SCRIPT
from database_setup_ui import Handler as DatabaseHandler
from gtm_engine.persistence.storage import PrivateStorage
from run_backend import local_settings


def configure(secret: str) -> None:
    if not secret.startswith("sb_secret_") or any(c.isspace() for c in secret):
        raise ValueError("invalid_storage_secret")
    settings = local_settings()
    PrivateStorage(settings.get("SUPABASE_URL", ""), secret)
    path = ROOT / ".env"
    # Preserve existing settings; never print values. Replace only this allowlisted key.
    lines = [line for line in path.read_text(encoding="utf-8-sig").splitlines()
             if line.partition("=")[0].strip() != "SUPABASE_SERVICE_ROLE_KEY"]
    lines.append("SUPABASE_SERVICE_ROLE_KEY=" + json.dumps(secret))
    temporary = ROOT / ".env.storage.tmp"
    try:
        temporary.write_text("\n".join(lines) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def page(nonce: str) -> str:
    return f"""<!doctype html><html lang="it"><meta charset="utf-8">
    <title>Archivio privato · GTM Engine</title><style>{CSS}</style><header>GTM Engine</header>
    <main><h1>Collega l’archivio privato</h1>
    <p>La chiave resta sul computer, esclusa da Git. Nessun dato viene mostrato in chat.</p>
    <div id="setup-status" class="message" hidden role="status"></div>
    <form action="submit" method="post" autocomplete="off">
    <input type="hidden" name="csrf" value="{escape(nonce)}">
    <label for="storage_secret">Chiave server Supabase</label>
    <input id="storage_secret" name="storage_secret" type="password" required
      autocomplete="new-password" maxlength="4096">
    <button type="submit">Collega archivio privato</button></form></main>
    <script nonce="{escape(nonce)}">{SCRIPT}</script></html>"""


class StorageServer(HTTPServer):
    def __init__(self, address, provision=configure):
        self.nonce, self.completed, self.provision = secrets.token_urlsafe(32), False, provision
        super().__init__(address, Handler)

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class Handler(DatabaseHandler):
    server: StorageServer

    def do_GET(self) -> None:
        prefix = "/" + self.server.nonce + "/"
        if not self.allowed_host() or self.path not in {prefix, prefix + "font"}:
            self.respond(404, b"Not found", "text/plain")
        elif self.path.endswith("/font"):
            self.respond(200, (ROOT / "frontend/public/fonts/InterVariable.woff2").read_bytes(),
                         "font/woff2")
        else:
            self.respond(200, page(self.server.nonce).encode())

    def do_POST(self) -> None:
        if (not self.allowed_host() or self.path != "/" + self.server.nonce + "/submit"
                or self.headers.get("Origin") != self.server.origin or self.server.completed):
            self.reject_post(403, b"Forbidden")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if (not 0 < size <= 8192 or self.headers.get("Content-Type", "").split(";")[0]
                    != "application/x-www-form-urlencoded"):
                self.reject_post(400, b"Invalid request")
                return
            fields = parse_qs(self.rfile.read(size).decode(), max_num_fields=2, strict_parsing=True)
            if (set(fields) != {"csrf", "storage_secret"}
                    or any(len(v) != 1 for v in fields.values())
                    or not secrets.compare_digest(fields["csrf"][0], self.server.nonce)):
                self.respond(403, b"Forbidden", "text/plain")
                return
            self.server.provision(fields["storage_secret"][0])
            self.server.completed = True
        except Exception:  # noqa: BLE001 -- no input or provider exception reaches response/log
            self.server.completed = False
        message = ("Archivio privato collegato. Configurazione salvata." if self.server.completed
                   else "Configurazione non completata. Torna in chat senza inviare la chiave.")
        self.respond(200 if self.server.completed else 400,
                     json.dumps({"ok": self.server.completed, "message": message}).encode(),
                     "application/json")
        if self.server.completed:
            Thread(target=self.server.shutdown, daemon=True).start()


if __name__ == "__main__":
    with StorageServer(("127.0.0.1", 0)) as server:
        print(server.origin + "/" + server.nonce + "/", flush=True)
        server.serve_forever()
