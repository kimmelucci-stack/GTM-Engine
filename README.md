# GTM Engine

Piattaforma GTM a sette moduli. Specifiche in [docs/README.md](docs/README.md), regole in [AGENTS.md](AGENTS.md), stato in [handoff](docs/00_PROJECT/HANDOFF_TO_CODEX.md).

Agentic Go To Market Tool.

Progetto pubblico per portfolio, attualmente alla foundation: frontend React/TypeScript/Vite, API FastAPI/Pydantic e ingresso worker. Gate 0 verificato; Moduli 01–07 definiti funzionalmente, nessun modulo operativo end-to-end. Backend e worker previsti su Render, dati/storage su Supabase, deck modificabile via python-pptx. Nessun invio automatico di campagne nell'MVP.

La documentazione è consolidata sulle decisioni definitive. Le prove DataForSEO del precedente ambiente sono conservate come evidenze storiche: non certificano l'accesso del repository corrente. KB-001, controllo fonti ogni 45 giorni, è assegnato al Gate 2 con test e verifica operativa prima della release.

## Credenziali

Non salvare utenze provider, chiavi o token nei file versionati, nel frontend o nei log. Usare secret server-side e Git Credential Manager per l'accesso GitHub; nessun token negli URL. Pubblicare solo codice, documentazione e campioni sintetici o pubblici revisionati; dati cliente e raw privati restano esclusi anche dalla cronologia. Il nome dell'account GitHub e l'attribuzione dei commit sono metadati pubblici del portfolio, non credenziali di accesso.

Attivare il controllo locale dopo ogni clone:

```powershell
git config core.hooksPath .githooks
```

L'hook controlla i contenuti effettivamente preparati per il commit; la CI ricontrolla i file versionati. Il controllo blocca formati comuni di token, password assegnate e file sensibili senza stamparne i valori. È una protezione euristica: configurare i secret correttamente e verificare i cambi resta necessario. Non incollare credenziali in chat.

Prima di cambiare visibilità: `python scripts/check_secrets.py --tracked --history` controlla anche tutti i commit raggiungibili. `python scripts/check_docs.py` verifica riferimenti interni ed espressioni tecniche superate, escludendo solo l'archivio storico esplicitamente non normativo.

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

## Gate 1A — DataForSEO

Connettore e runner pilota implementati con test sintetici; **nessuna prova live ancora eseguita**. Il piano copre le 12 prove storiche e aggiunge il volume nazionale. Cap autorizzato dal proprietario: **5 USD per l'intero pilota**, mantenuto anche nella ripresa delle recensioni. Per il prodotto completo: obiettivo 10 USD, massimo 15 USD per run; fattibilità da misurare.

Configurazione privata, dal terminale nella root del progetto:

```powershell
.\.venv\Scripts\python.exe scripts/configure_dataforseo.py
```

Login e password API sono richiesti con campi nascosti e salvati solo nel `.env` locale ignorato da Git. Non incollarli in chat né passarli come argomenti. Nessuna chiamata API durante la configurazione. Il sistema carica solo le tre impostazioni DataForSEO necessarie; le variabili di processo hanno precedenza.

```powershell
.\.venv\Scripts\python.exe -m gtm_engine.gate1a
.\.venv\Scripts\python.exe -m gtm_engine.gate1a --plan
```

Questi comandi verificano configurazione e piano senza rete. Per prove pagate serve anche una tariffa massima revisionata per ciascun campione, mai valori inventati: file privato `artifacts/private/dataforseo/rates.json`, con `checked_at` UTC (entro 7 giorni), `currency` USD, `source_url` al listino ufficiale, `plan` uguale al piano stampato, `ceilings_usd` per tutti i 13 ID e `reviews_poll`. Il manutentore verifica i prezzi correnti prima di prepararlo. Un plafond locale basato su tariffe verificate non sostituisce un limite di fatturazione imposto dal provider: costo ignoto o superiore al previsto interrompe le richieste e richiede riconciliazione.

```powershell
.\.venv\Scripts\python.exe -m gtm_engine.gate1a --live --rate-card artifacts/private/dataforseo/rates.json
```

Il runner usa la cartella privata unica `artifacts/private/dataforseo/pilot/` e non sovrascrive/ripete un pilota esistente. Risposte redatte delle credenziali, journal, budget e report rimangono privati; nessun raw caricato nel portfolio. Errori/timeout non ripetono POST fatturabili. Le prenotazioni di costo non vengono rimborsate automaticamente; nessun retry di pagamento incerto.

Per le recensioni: scegliere prima un'identità pubblica verificata tra i candidati Maps del report privato. `--start-reviews --review-place-id IDENTIFICATIVO` avvia il solo task recensioni una volta, usando budget residuo e tariffe del pilota; il valore deve appartenere ai candidati salvati. `--resume-reviews` recupera il task salvato con soli GET, senza reinviarlo. Entrambe le opzioni richiedono `--live --rate-card` come sopra. Polling e richieste totali limitati; un blocco o crash richiede revisione dello stato, mai cancellazione automatica del budget.
