# Gate 0 — Registro verifiche

Data: 25 ottobre 2026. Versione applicazione 0.1.0. Repository del proprietario collegata, commit iniziale remoto conservato. Stato: controlli locali PASS; CI remota da verificare dopo push.

## Ambiente osservato

Windows/PowerShell. Python di sistema non eseguibile (alias WindowsApps); npm non disponibile. Usati Python 3.12.14 e Node 24.19.0 del runtime locale, pnpm 11.25.0. Ambiente Python dedicato `.venv/`, dipendenze frontend in `frontend/node_modules/`, entrambi ignorati da Git.

## Esiti

| Verifica | Comando / input | Esito e limiti |
|---|---|---|
| Stato iniziale | `git status --short` | Nessun repository esistente; sola documentazione |
| Repository | `git fetch origin`, collegamento al ramo `main` esistente | PASS: accesso verificato tramite credential manager; remote HTTPS senza credenziali incorporate |
| Visibilità | Impostazioni GitHub | PASS: privata prima del caricamento del progetto |
| Guardia credenziali | `scripts/check_secrets.py --tracked` e hook pre-commit | Scansione prima del commit, valori mai stampati; formati comuni/file sensibili, controllo euristico |
| Test guardia | `pytest backend` | PASS: 5 test totali, inclusi blocco token e credenziali assegnate, file sensibili e template vuoto ammesso |
| Install frontend | `pnpm install --frozen-lockfile` in `frontend/` | PASS dopo autorizzazione script esbuild nella configurazione; lockfile versionato |
| Frontend | `pnpm build` | PASS: TypeScript strict e Vite, 28 moduli trasformati; nessuna prova browser/E2E |
| Install backend | Runtime Python: `-m pip --python .venv/Scripts/python.exe install -e './backend[dev]'` | PASS; FastAPI 0.162.0, Pydantic 2.14.1, Uvicorn 0.54.0, pytest 9.1.1, httpx 0.28.1, ruff 0.17.2 |
| API healthcheck | `.venv/Scripts/python -m pytest backend` | PASS: 1 test, GET `/health` → HTTP 200, risposta tipizzata. Una deprecation warning Starlette/httpx; nessun DB o provider verificato |
| Lint backend | `.venv/Scripts/python -m ruff check backend` | PASS |
| Worker ingresso | `.venv/Scripts/python -m gtm_engine.worker --check` | PASS; nessun job eseguito, persistenza non implementata |
| Secret/artifact esclusi | `git check-ignore .venv/ frontend/node_modules/ frontend/dist/ .env` | Controllo locale; `.env.example` contiene solo valori vuoti |
| CI | `.github/workflows/ci.yml` | Predisposta, non eseguita su GitHub |
| Provider/DB/storage | Nessuna chiamata | NON TESTATI nel runtime; nessun PASS ereditato dall'audit |

Gli errori iniziali di installazione erano locali: bootstrap pip della venv non disponibile e restrizione realpath per pnpm; installazioni ripetute con runtime disponibile e accesso autorizzato. Un primo test era partito prima della fine dell'installazione (import mancanti); rieseguito dopo installazione completa. Il test API limitato dal sandbox è stato rieseguito con accesso autorizzato: PASS. Nessuna spesa provider richiesta.

Provider/endpoint/status rete/campione/copertura/raw fixture: N/A per build e test locali; non sono prove di acquisizione dati. Costo API: nessuna chiamata effettuata. Le fixture live saranno prodotte ai gate di accesso e redatte prima del versionamento.

L'esecuzione remota della CI rimane da osservare dopo il primo push. Non iniziare Gate 1A automaticamente. Test frontend comportamentali/E2E saranno aggiunti con i flussi applicativi; nessuna verifica visuale browser eseguita per la shell.
