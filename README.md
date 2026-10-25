# GTM Engine

Piattaforma GTM a sette moduli. Specifiche in [docs/README.md](docs/README.md), regole in [AGENTS.md](AGENTS.md), stato in [handoff](docs/00_PROJECT/HANDOFF_TO_CODEX.md).

Agentic Go To Market Tool.

Progetto pubblico per portfolio, attualmente alla foundation: frontend React/TypeScript/Vite, API FastAPI/Pydantic e ingresso worker. Gate 0 verificato; Moduli 01–07 definiti funzionalmente, nessun modulo operativo end-to-end. Backend e worker previsti su Render, dati/storage su Supabase, deck modificabile via python-pptx. Nessun invio automatico di campagne nell'MVP.

La documentazione segue le decisioni definitive. Gate 1A DataForSEO riprodotto nel repository: accessibilità superata con limiti, 0,31847 USD spesi; Trends insufficiente. Prove precedenti e attuali sono distinte nell'audit. KB-001, controllo fonti ogni 45 giorni, è assegnato al Gate 2 con test e verifica prima della release.

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

Connettore e runner testati offline e con dati reali. **Gate 1A PASS_WITH_LIMITATIONS**, 13 campioni e una SERP supplementare PAA; 15 richieste dati, costo totale 0,31847 USD. Autenticazione/tariffe verificate con una richiesta gratuita separata. Serie Trends: 2/54 valori non null, non utilizzabile per stagionalità. Il report separa esito del gate da qualità parziale del dataset. Cap del proprietario: **5 USD per l'intero pilota**, mantenuto nelle continuazioni. Prodotto completo: obiettivo 10 USD, massimo 15 USD per run; fattibilità ancora da misurare.

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

Per le recensioni: scegliere prima un'identità pubblica verificata tra i candidati Maps del report privato. `--start-reviews --review-place-id IDENTIFICATIVO` avvia il solo task recensioni una volta, usando budget residuo e tariffe del pilota; il valore deve appartenere ai candidati salvati. `--resume-reviews` recupera il task salvato con soli GET, senza reinviarlo. `--check-paa` esegue una sola query supplementare pertinente e conserva l'assenza PAA della query iniziale. Le continuazioni richiedono `--live --rate-card`, condividono ledger/cap e non sono ripetute automaticamente. Il pilota già eseguito rimane disponibile privatamente: non cancellarlo per riavviare. Un blocco o crash richiede riconciliazione.

## Gate 1B — Siti competitor

Crawler HTTP con BeautifulSoup/trafilatura, fallback Playwright su HTML povero di testo. CLI locale, non esposta dall'API: quattro pagine per sito, solo HTTPS e dominio iniziale/con variante www, robots.txt verificato, timeout, tetto richieste e 2 MB per risposta. Nessun login, aggiramento anti-bot o invio di form. Ogni estratto conserva URL, data UTC, riferimento raw e natura osservata: un claim pubblicato non è un risultato dimostrato. Prezzi e casi non trovati sono `unavailable_in_sample`, non zero o assenza sull'intero sito.

```powershell
.\.venv\Scripts\python.exe -m pip install -e './backend[dev,crawl]'
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) 'artifacts/private/playwright'
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe -m gtm_engine.gate1b --url https://example.com
```

Il comando mostra il piano senza rete. Per il pilota aggiungere `--live --confirmed-sample --browser` solo dopo conferma dei cinque siti da parte del proprietario. Raw HTML e report normalizzato sono salvati esclusivamente nella cartella ignorata `artifacts/private/web`, creata una sola volta per evitare sovrascritture. Nuovi tentativi richiedono una nuova cartella privata e mantengono le prove precedenti. Non vengono lette credenziali. Nessun costo API; costo del calcolo locale non misurato.

**Stato:** componente implementato e testato su fixture sintetiche; il primo campione è stato rifiutato dal proprietario. Nuova selezione da motivare rispetto a offerta del pilota, domanda e mercato locale, distinguendo pertinenza commerciale e visibilità organica; nessuna classifica basata su notorietà presunta. Gate 1B non superato finché non risultano cinque crawl reali con evidenze. Controllo DNS prima di ciascuna richiesta, senza pinning socket: prima di esporre URL arbitrari tramite API servono protezioni egress contro DNS rebinding. Risorse esterne, URL con query e WebSocket bloccati nel fallback; pagine che li richiedono possono restare partial/unavailable.

Il [metodo canonico di selezione](docs/02_MARKET_INTELLIGENCE/SCOPE.md) è `competitor-selection-v1` (§4.4–4.7): analisi per offerta/bisogno/pubblico/territorio, discovery ampia, concorrenti diretti e sostitutivi distinti da intermediari/editori, presenza organica/Maps/paid separata, cinque proposti con motivazioni e revisione. I contratti Python in `backend/src/gtm_engine/domain/competitors.py` verificano coerenza dello screening e della proposta, esclusione cliente/duplicati, separazione offerte e dati mancanti. Non sono un algoritmo di ranking né un workflow AI già operativo: raccolta automatica, proposta dell'agente e UI del Modulo 02 restano al Gate 4. Nessun punteggio competitivo nuovo o modifica allo scoring v1.1.
