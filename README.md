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

**Stato:** Gate 1B PASS_WITH_LIMITATIONS dopo crawl reale di cinque siti del campione tecnico scelto su delega del proprietario: 15 GET, otto pagine disponibili e una risorsa esclusa perché non HTML. Evidenze con fonte e hash verificati; browser abilitato ma non necessario, quindi non validato live. Il primo campione rifiutato e lo screening restano storici. Non è approvazione della shortlist commerciale né validazione di ranking o intero Modulo 02. Controllo DNS prima di ciascuna richiesta, senza pinning socket: prima di esporre URL arbitrari tramite API servono protezioni egress contro DNS rebinding. Risorse esterne, URL con query e WebSocket bloccati nel fallback; pagine che li richiedono possono restare partial/unavailable.

**Screening leggero riprodotto il 25 ottobre:** nove domini candidati delle due offerte, una pagina per sito; 17 GET totali, otto pagine con evidenze e un HTTP 403 su robots.txt. Nessun aggiramento o fallback sul sito bloccato. Prezzi osservati su due pagine dopo correzione del parser e rielaborazione degli stessi raw senza rete. Report e dati specifici del pilota solo nella cartella privata, registro aggregato nell'audit. Lo screening non certificava ranking, fit commerciale o approvazione; è seguito dal crawl tecnico sopra riportato.

Modalità riutilizzabile: `python -m gtm_engine.gate1b --screen --url https://example.com` mostra il piano senza rete; aggiungere `--live --output artifacts/private/web-screening/NOME_RUN_UNICO` per lo screening HTTP. Da uno a sedici domini distinti, una pagina e al massimo dieci richieste per sito, incluse robots e redirect, senza browser. Non combinabile con `--confirmed-sample` o `--browser`; nessuna raccolta approfondita o approvazione implicita. L'output deve essere ignorato da Git e non esistere già. Costi API zero, calcolo locale non misurato. Conservare report originale e raw; una nuova estrazione con `web-extract-v2` conserva URL/data originali e registra la data della trasformazione separatamente.

Il [metodo canonico di selezione](docs/02_MARKET_INTELLIGENCE/SCOPE.md) è `competitor-selection-v1` (§4.4–4.7): analisi per offerta/bisogno/pubblico/territorio, discovery ampia, concorrenti diretti e sostitutivi distinti da intermediari/editori, presenza organica/Maps/paid separata, cinque proposti con motivazioni e revisione. I contratti Python in `backend/src/gtm_engine/domain/competitors.py` verificano coerenza dello screening e della proposta, esclusione cliente/duplicati, separazione offerte e dati mancanti. Non sono un algoritmo di ranking né un workflow AI già operativo: raccolta automatica, proposta dell'agente e UI del Modulo 02 restano al Gate 4. Nessun punteggio competitivo nuovo o modifica allo scoring v1.1.

## Anteprima approvazione competitor

Avviare il frontend con `pnpm dev`: si apre direttamente la **proposta SaaS v03**, con dati sintetici espliciti. Workspace con navigazione delle sette fasi, offerte separate, tabella competitor, ricerca e filtri, scheda laterale (drawer su mobile), aggiunta URL in dialogo e riepilogo di conferma visibile durante la revisione. Checkbox per confermare/sostituire i cinque e fino a tre aggiunte da verificare. Conferma solo in memoria, azzerata cambiando offerta o ricaricando; nessuna analisi, chiamata provider o persistenza simulata. Le altre fasi sono disabilitate, non collegate a pagine fittizie. La schermata reale attende proposte e salvataggio server; raccolta e verifica automatica dei nuovi siti, Supabase e worker ancora da collegare.

Direzione vincolata dal proprietario: [app Attio](https://attio.com/help/reference/attio-101/introduction-to-navigating-attio), tabella continua e neutra con controlli compatti; CTA **senza frecce**. Rimossi hero, stepper decorativo e CTA viola della proposta v02. Font **Inter variabile**, verificato sulla pagina pubblica `app.attio.com` il 25 ottobre 2026 e incluso localmente in `frontend/public/fonts/InterVariable.woff2` con [licenza OFL](frontend/public/fonts/Inter-OFL.txt). SHA-256 `8af7bd5b545567adffb3dfceb5bedb353a522d7bf1b3a2b8af7b6064156babc0`, file originale non modificato. Il sito marketing Attio usa anche Inter Display/Tiempos: non sono il riferimento per questa UI operativa. Fonte e font consultabili da **Direzione di design**. Nessun font remoto a runtime o nuovo servizio. Layout originale, non copia del marchio o dei contenuti di Attio. Il primo layout è rifiutato; questa revisione resta una proposta da valutare.

`domain/approvals.py` contiene le guardie pure per conferma esplicita, versione della proposta, massimo cinque base più tre aggiunte qualificate, cliente/duplicati e blocco degli ID non approvati. Non è un servizio di autenticazione né un endpoint pubblico: il server dovrà salvare l'approvazione del proprietario autenticato prima del job. Test browser opt-in: frontend su `127.0.0.1:5173`, Chromium locale, `GTM_UI_TEST=1`; con `GTM_BROWSER_TEST=1` si include anche il rendering del crawler. Screenshot sintetici solo in `artifacts/private/review-ui/`.


## Gate 1C — Meta: controllo preliminare

`python -m gtm_engine.gate1c` controlla offline la configurazione e mostra solo nomi mancanti/stati: nessuna richiesta o verifica di permessi. `--output artifacts/private/meta/NOME_UNICO` conserva un report privato. Per inserire valori nascosti usare `.venv/Scripts/python.exe scripts/configure_meta.py` nel terminale interattivo locale. Non incollare credenziali in chat o nella riga di comando. Il setup conserva le altre impostazioni, non crea account/app. `META_IG_USER_ID` identifica il proprio account professionale interrogante; versione Graph da verificare sulle fonti ufficiali prima del test. Stato locale: configurazione mancante. Prova separata nel browser autenticato: permessi concessi, Ads Library negata (codice 10), nessun IG ID restituito; Business Discovery non interrogato. Gate 1C non superato, nessun fallback attivato.


## Gate 1E — Fonti pubbliche

`python -m gtm_engine.gate1e` mostra il piano offline. Per tre richieste anonime limitate agli endpoint ufficiali: `python -m gtm_engine.gate1e --live --output artifacts/private/public-sources/NOME_RUN_UNICO`. Non legge credenziali; massimo 10 MB/risposta, timeout 25 secondi, niente retry o redirect automatico. Output nuovo e ignorato da Git, raw e normalizzati separati con hash/query/UTC.

Prova reale: 3.257 codici ATECO importati da XLSX ufficiale, una cella Eurostat per Torino NUTS 3/2023 e tre record OpenAlex. ESCO temporaneamente non disponibile (307 alla pagina sorry), quindi Gate 1E PARTIAL. OpenAlex dichiara 0,001 USD di costo tecnico; addebito effettivo non verificato, nessun account o servizio acquistato. Dati di contesto e bibliografici, non domanda commerciale o buyer dimostrati. Gate 1C in attesa su istruzione del proprietario; Gate 1D non eseguito senza chiave e cap Openapi.


## Foundation — aggiornamento fonti ogni 45 giorni

KB-001 disponibile a richiesta: `python -m gtm_engine.source_refresh --registry PERCORSO_REGISTRO --output artifacts/private/source-refresh/NOME_UNICO`. Controllo calendario senza rete per default; `--live` abilita solo fonti approvate e scadute. Conserva ETag/Last-Modified/hash, tentativi ed errori separati, e scrive un nuovo report/registro senza modificare playbook o file di input. Registro reale da approvare; nessun monitor schedulato o deploy attivo. Dettagli e limiti in `docs/00_PROJECT/KNOWLEDGE_BASE.md`. Gate 2 avviato, non completato.


## Supporto storico: funzioni operative e governance

[Consulta le 60 funzioni operative nei 12 reparti](docs/03_UVP_ICP_INTELLIGENCE/BUSINESS_FUNCTION_DIRECTORY.md). Dati canonici in `backend/src/gtm_engine/domain/business_functions.v1_1.json`; disponibili da API con `GET /reference/business-functions` e filtro opzionale `department_id` (es. people). Nessun account o dato cliente esposto.

Nel precedente contratto di supporto reparto, funzione e ruolo di acquisto erano distinti e il job title facoltativo. Questo contratto è superato per il buyer mapping; ora è obbligatorio il titolo concreto. Nel solo supporto storico, il contratto Python rifiuta associazioni reparto/funzione incoerenti e stato Observed senza fonte. Sono riferimenti, non identificazione automatica di buyer reali; workflow del Modulo 03 ancora da implementare. ESCO non necessario: il runner pubblico v2 lo interroga soltanto con `--include-esco`. Le prove storiche e il relativo esito PARTIAL restano conservati.

La directory corrente v1.1 comprende anche quattro organi/strutture collegiali e 25 ruoli di proprietà, governo e vertice (Owner, soci, Founder, Presidente, consiglieri, AD, CEO, direttore generale e direzioni funzionali). Cariche cumulabili, nessuna autorità di acquisto dedotta. API: `?version=business-functions-v1` per la versione storica; default v1.1. Buyer reference può indicare solo cariche/organi se la funzione operativa non è verificata. Nessuna migrazione o assegnazione a clienti eseguita.


## Directory principale: job title del buying committee

[251 job title nei 12 reparti](docs/03_UVP_ICP_INTELLIGENCE/BUYER_JOB_TITLE_DIRECTORY.md), inclusi manager, coordinatori, specialisti, buyer, referenti tecnici e assistenti, oltre al board. API `GET /reference/buyer-job-titles`, filtri `department_id` e `q` (italiano/inglese/varianti). La precedente directory funzioni/governance è supporto storico: il nuovo contratto richiede un titolo concreto per ogni membro. CommitteeMember e BuyingCommittee separano titolo, ruolo di acquisto ed evidenze; ApproachStep collega obiettivi e prove ai membri proposti. Non è ancora un workflow AI end-to-end. Nessuna autorità o appartenenza a un comitato reale dedotta dalla sola directory.


## Foundation — loader KB e regole di budget

Loader selettivo in `knowledge.py`: Markdown approved per fase, con versione/hash/fonti; un file cambiato richiede revisione. Nessuna libreria reale auto-approvata. `domain/run_budget.py`: prenotazioni e consuntivi USD trasversali, obiettivo 10/cap massimo 15; richieste incerte mantengono il massimale, costi mancanti non diventano zero. Sono componenti testati localmente, ancora da collegare a Postgres, worker e adapter prima di controllare un’esecuzione reale. Nessuna nuova spesa o connessione cloud implicita.
