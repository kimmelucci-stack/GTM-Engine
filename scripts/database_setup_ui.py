"""Temporary loopback-only credential entry; no secret values in responses or logs."""

import io
import re
import secrets
from contextlib import redirect_stdout
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import parse_qs, quote

from configure_database import configure

ROOT = Path(__file__).resolve().parents[1]
CSS = """
@font-face{font-family:Inter;src:url('font') format('woff2');font-weight:100 900}
*{box-sizing:border-box}body{margin:0;background:#fafafa;color:#242529;
font:14px Inter,system-ui,sans-serif}header{height:64px;padding:22px 32px;
border-bottom:1px solid #e6e7e9;background:#fff;font-weight:600}
main{max-width:540px;margin:64px auto;padding:0 24px 48px}h1{font-size:25px;
letter-spacing:-.7px;font-weight:600;margin:14px 0}p{color:#6b6d73;line-height:1.65}
.eyebrow{font-size:12px;color:#777b82}form{margin-top:30px}label{display:block;
font-weight:500;margin:24px 0 9px}input{width:100%;padding:12px;border:1px solid #d9dbe0;
border-radius:7px;background:#fff;font:inherit}input:focus{outline:2px solid #92969d;
outline-offset:2px}small{display:block;font-size:12px;color:#74777e;line-height:1.6;margin-top:8px}
button{margin-top:28px;border:1px solid #292a2e;border-radius:7px;background:#292a2e;
color:white;font:500 14px Inter,system-ui;padding:11px 18px;cursor:pointer}
.note{border-top:1px solid #e6e7e9;margin-top:30px;padding-top:18px;font-size:12px}
.message{padding:16px;border:1px solid #dedfe3;border-radius:7px;background:#fff;margin:24px 0}
"""


def page(nonce: str, message: str = "", complete: bool = False) -> str:
    form = "" if complete else f"""
    <form method="post" action="submit" autocomplete="off">
      <input type="hidden" name="csrf" value="{escape(nonce)}">
      <label for="administrative">Connessione PostgreSQL</label>
      <input id="administrative" name="administrative" type="password" required
        autocomplete="new-password" spellcheck="false" maxlength="8192">
      <small>Dal pannello Supabase, Connect: connessione del progetto con la password.
      Usa Session pooler se la rete non supporta IPv6.</small>
      <label for="db_password">Password del database</label>
      <input id="db_password" name="db_password" type="password"
        autocomplete="new-password" maxlength="1024">
      <small>Compila questo campo se la connessione contiene ancora YOUR-PASSWORD.
      La password verrà inserita nella connessione automaticamente.</small>
      <label for="auth_url">URL del progetto Supabase</label>
      <input id="auth_url" name="auth_url" type="password" required
        autocomplete="new-password" spellcheck="false" maxlength="512">
      <label for="public_key">Publishable key</label>
      <input id="public_key" name="public_key" type="password" required
        autocomplete="new-password" spellcheck="false" maxlength="4096">
      <small>La chiave publishable del progetto, non una service role key.</small>
      <button type="submit">Configura accesso riservato</button>
    </form>"""
    notice = f'<div class="message" role="status">{escape(message)}</div>' if message else ""
    return f"""<!doctype html><html lang="it"><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Accesso riservato · GTM Engine</title><style>{CSS}</style>
    <header>GTM Engine</header><main><div class="eyebrow">CONFIGURAZIONE LOCALE</div>
    <h1>Collega il database</h1><p>Inserisci i dati una sola volta, in questa scheda.
    I valori restano nascosti e vengono inviati soltanto al processo sul tuo computer.</p>
    {notice}{form}<p class="note">La credenziale amministrativa serve a creare due accessi
    separati per API e worker e non viene salvata. Le connessioni generate restano nel file
    locale escluso da Git. Nessun invio in chat o servizio di analisi esterno.</p></main></html>"""


class SetupServer(HTTPServer):
    def __init__(self, address, provision=configure):
        self.nonce = secrets.token_urlsafe(32)
        self.provision = provision
        self.completed = False
        super().__init__(address, Handler)

    @property
    def origin(self) -> str:
        return f"http://127.0.0.1:{self.server_port}"


class Handler(BaseHTTPRequestHandler):
    server: SetupServer

    def log_message(self, *args) -> None:
        pass

    def setup(self) -> None:
        super().setup()
        self.connection.settimeout(15)

    def respond(self, status: int, body: bytes, content_type="text/html; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'none'; style-src 'unsafe-inline'; "
                         "font-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def allowed_host(self) -> bool:
        return self.headers.get("Host") == f"127.0.0.1:{self.server.server_port}"

    def do_GET(self) -> None:
        prefix = "/" + self.server.nonce + "/"
        if not self.allowed_host() or self.path not in {prefix, prefix + "font"}:
            self.respond(404, b"Not found", "text/plain")
            return
        if self.path.endswith("/font"):
            self.respond(200, (ROOT / "frontend/public/fonts/InterVariable.woff2").read_bytes(),
                         "font/woff2")
            return
        self.respond(200, page(self.server.nonce, complete=self.server.completed).encode())

    def do_POST(self) -> None:
        if (not self.allowed_host() or self.path != "/" + self.server.nonce + "/submit"
                or self.headers.get("Origin") != self.server.origin or self.server.completed):
            self.respond(403, b"Forbidden", "text/plain")
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if (not 0 < length <= 32768 or self.headers.get("Content-Type", "").split(";")[0]
                    != "application/x-www-form-urlencoded"):
                self.respond(400, b"Invalid request", "text/plain")
                return
            fields = parse_qs(self.rfile.read(length).decode("utf-8"), max_num_fields=5,
                              strict_parsing=True)
            expected = {"csrf", "administrative", "auth_url", "public_key"}
            if (not expected.issubset(fields) or set(fields) - expected - {"db_password"}
                    or any(len(v) != 1 for v in fields.values())
                    or not secrets.compare_digest(fields["csrf"][0], self.server.nonce)):
                self.respond(403, b"Forbidden", "text/plain")
                return
            administrative = fields["administrative"][0].strip()
            provided_value = fields.get("db_password", [""])[0]
            placeholder = r"\[YOUR[-_ ]PASSWORD\]"
            if re.search(placeholder, administrative, re.IGNORECASE):
                if not provided_value:
                    raise ValueError("missing_database_password")
                administrative = re.sub(placeholder, lambda match: quote(provided_value, safe=""),
                                        administrative, flags=re.IGNORECASE)
            elif provided_value:
                raise ValueError("connection_already_has_password")
            with redirect_stdout(io.StringIO()):
                result = self.server.provision(administrative, fields["auth_url"][0].strip(),
                                               fields["public_key"][0].strip())
        except Exception:  # noqa: BLE001 -- never return request bodies or connection exceptions
            result = 2
        self.server.completed = result == 0
        message = ("Configurazione salvata. Puoi tornare alla chat per la verifica del collegamento."
                   if self.server.completed else
                   "Configurazione non completata. Verifica i dati del progetto e riprova; "
                   "se il problema persiste, torna in chat senza inviare credenziali.")
        self.respond(200 if self.server.completed else 400,
                     page(self.server.nonce, message, self.server.completed).encode())
        if self.server.completed:
            Thread(target=self.server.shutdown, daemon=True).start()


def main() -> None:
    with SetupServer(("127.0.0.1", 0)) as server:
        print(server.origin + "/" + server.nonce + "/", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()
