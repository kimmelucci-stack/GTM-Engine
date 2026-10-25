# GTM Engine

Piattaforma GTM a sette moduli. Specifiche in [docs/README.md](docs/README.md), regole in [AGENTS.md](AGENTS.md), stato in [handoff](docs/00_PROJECT/HANDOFF_TO_CODEX.md).

Agentic Go To Market Tool.

## Credenziali

Non salvare utenze provider, chiavi o token nei file versionati, nel frontend o nei log. Usare secret server-side e Git Credential Manager per l'accesso GitHub; nessun token negli URL. Il nome pubblico della repository resta visibile a chi ha accesso, ma non contiene credenziali.

Attivare il controllo locale dopo ogni clone:

```powershell
git config core.hooksPath .githooks
```

L'hook controlla i contenuti effettivamente preparati per il commit; la CI ricontrolla i file versionati. Il controllo blocca formati comuni di token, password assegnate e file sensibili senza stamparne i valori. È una protezione euristica: configurare i secret correttamente e verificare i cambi resta necessario. Non incollare credenziali in chat.

## Avvio locale — Gate 0

Richiede Python 3.12+, Node 22+ e pnpm 11.25.0. Le dipendenze vengono installate nel progetto; nessuna credenziale è necessaria per healthcheck e build.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e './backend[dev]'
.\.venv\Scripts\python -m pytest backend
.\.venv\Scripts\python -m ruff check backend
.\.venv\Scripts\python -m gtm_engine.worker --check
.\.venv\Scripts\python -m uvicorn gtm_engine.api:app --host 127.0.0.1 --port 8000
```

`GET http://127.0.0.1:8000/health` verifica solo il processo API, non database o provider. Il worker espone soltanto un controllo d'ingresso; il processamento persistente è previsto al Gate 2.

In un secondo terminale:

```powershell
cd frontend
pnpm install --frozen-lockfile
pnpm build
pnpm dev
```

La UI è una shell iniziale: nessuna analisi avviata o connessione simulata. Il frontend non contiene credenziali e non è ancora collegato al backend.

`.env.example` elenca i secret futuri. Il Gate 0 non li carica né esegue chiamate provider. Configurare i secret solo quando necessari al gate relativo. CI esegue verifiche locali; prove live opt-in e deployment richiedono i gate della roadmap.
