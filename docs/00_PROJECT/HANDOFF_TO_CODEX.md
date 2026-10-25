# GTM Engine — Handoff operativo a Codex

Data: 25 ottobre 2026. Questo registro distingue progettazione, codice locale e servizi verificati. Le specifiche originali restano invariate.

## A. Stato iniziale verificato

All'ingresso: sola cartella `docs/`, nessun codice applicativo, nessuna directory `.git`; `git status --short` restituisce «not a git repository». Nessuno ZIP da estrarre. Non risultano fixture raw delle precedenti prove, script crawler/Instagram, playbook KB o configurazioni di deployment. L'esistenza di account esterni non è stata accertata.

Tutti i sette moduli sono progettati: Demand; Market & Competitive; UVP & ICP; Value Proposition & Positioning; Channel & GTM Strategy; Execution Planning; Strategy Deck. Lo scoring v1.1 è una specifica sperimentale, non un modello empiricamente validato. Nessuna percentuale storica misura sviluppo effettivo.

Stack approvato: React/TypeScript/Vite su Vercel; Python 3.12+/FastAPI/Pydantic con API e worker separati su Render; Supabase Postgres e Storage; OpenAI Responses/Structured Outputs; DataForSEO; crawler Python; Meta ufficiale e Openapi Company condizionati agli accessi. KB GitHub/Markdown selettiva senza vettori; python-pptx con preview e verifica visiva. Codex sviluppa frontend e backend.

### Prove API ereditate, non riprodotte qui

Il registro aggiornato iniziale di `DATA_ACCESS_AUDIT_2026-10-24.md` riporta 12 prove DataForSEO: catalogo città, volumi/CPC Torino, volumi/CPC Piemonte, keyword ideas, intent, autocomplete, SERP organica, Maps, reviews TASK POST→GET, Trends, advertiser discovery e Ads Search. Esempi documentati: 10 recensioni, 18 advertiser e 19 creatività. Trends contiene solo 3 valori non null su 53: dato insufficiente. PAA e copertura nazionale restano da provare. Questi sono resoconti della sessione precedente, senza fixture locali: non costituiscono PASS del Gate 1A.

Da collaudare in questo runtime: tutti i provider, crawler su cinque siti, Meta Ads UE, Instagram Business Discovery, Openapi su tre società e un bilancio, ISTAT/Eurostat/ESCO/OpenAlex, OpenAI, Supabase, hosting e PPTX. Nessuna chiamata autenticata eseguita durante l'inizializzazione.

### Audit documentale: conflitti e duplicati conservati

| Riferimento | Riscontro | Regola operativa per l'avvio |
|---|---|---|
| `PROJECT_SCOPE.md` §§3/5/10 e ultima nota §12 | Moduli 06–07 ancora aperti, stack proposto, hosting da scegliere, perimetro campagne indeciso | Richiesta del proprietario, stack definitivo, roadmap e scope aggiornati chiudono queste scelte; nessuna campagna inviata |
| Scope 01/02 e altre sezioni tecniche degli scope | «Test mai eseguiti», runtime/deck da scegliere | Sono stati funzionali storici; audit aggiornato distingue le prove successive e architettura fissa lo stack |
| Corpo storico dell'audit e sua tabella integrazioni | SearchAPI primaria Google/Meta, reviews non raccolte, regione non provata | L'aggiornamento iniziale sostituisce esplicitamente queste affermazioni: DataForSEO Google, Meta ufficiale prima; reviews e Piemonte testati nel precedente ambiente |
| Scope 02, fallback manuale Ads | Verifica assistita proposta storicamente | Matrice aggiornata: nessuna ricerca manuale obbligatoria; partial/unavailable se manca connettore verificato |
| `docs/EVOLUTION_BACKLOG.md` v0.1 | Duplicato divergente: riferimento a riallineamento RAG | Canonico `docs/00_PROJECT/EVOLUTION_BACKLOG.md` v0.2, senza vettori MVP |
| Modulo 06 `06_GTM_EXECUTION_PLANNING_SCOPE.md` e `SCOPE.md` | SHA256 identici | Canonico `SCOPE.md`; copia conservata |
| Modulo 07 `SCOPE_MODULO_07.md` e `SCOPE.md` | SHA256 identici | Canonico `SCOPE.md`; copia conservata |
| Matrice: riga buyer `D/I` | `I` non compare nella legenda principale della matrice; audit lo usa per inferenze | Non confondere accessibilità provider e natura epistemica; definire campi distinti al Gate 2 |
| Backlog KB-001 | Controllo leggero 45 giorni previsto ma non assegnato a un gate | Collocazione da concordare prima della release; nessuna automazione attivata ora |

Non sono stati eliminati duplicati o riscritti documenti approvati. Le priorità esplicite già disponibili consentono il Gate 0; eventuali ulteriori conflitti sostanziali richiedono segnalazione prima di una modifica normativa.

## B. Piano operativo e dipendenze

Seguire `DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md`, un gate alla volta.

| Gate | Dipendenze | Criterio di uscita sintetico |
|---|---|---|
| 0 Repository | Toolchain locale, GitHub proprietario | Repo collegato, healthcheck, build React, pytest, configurazione API/worker/env/CI |
| 1A DataForSEO | Credenziali e cap confermato | Riprodurre 12 prove, aggiungere verifica nazione, QA copertura, raw e costi |
| 1B Web | Cinque siti campione, eventuali script precedenti | Cinque crawl, URL/timestamp per claim e unavailable espliciti |
| 1C Meta/IG | App/token/permessi distinti Ads e IG | Due advertiser IT con due pagine; due account professionali fino a 50 media ove disponibili, copertura o blocco motivato |
| 1D Company | Token Openapi, cap, aziende e bilancio | Tre match verificati, dati con anno, confronto un bilancio |
| 1E Pubbliche | Accesso rete e condizioni correnti | Download/query reale per ISTAT, Eurostat, ESCO, OpenAlex con query/versione/data |
| 2 Foundation | Prove accesso, Supabase, Render, Vercel | Adapter, persistenza evidenze/raw, REST→job→worker→storage, retry/fail/timeout, cap e KB loader |
| 3 Demand | Foundation e dati utilizzabili | Pilota Torino, 20 keyword e tre cluster validati dal proprietario |
| 4 Competitive | Demand e fonti con stati espliciti | Cinque aziende, tre scorecard riviste, regressioni scoring v1.1 e missing data |
| 5 UVP/ICP/Positioning | Output 01–02 e input/prove proprietario | B2B/B2C e offerta disponibile/in sviluppo; approvazioni, nessun claim falso |
| 6 Channels/Execution | Strategia e risorse dichiarate | Budget insufficiente, ore/skill gap e costi separati; revisione strategica |
| 7 Deck | Snapshot approvati, template approvato | PPTX nativo editabile, render senza overflow e prova di modifica |
| 8 Release | Gate precedenti e consenso owner | E2E, failure provider, smoke produzione, costi e accettazione firmata |

Ogni PASS richiede i campi QA della roadmap: comando/data/versione/provider/endpoint/input/status/campione/copertura/costo/raw/limiti e approvazione se prevista. Test automatici non sostituiscono validazione business o prova live.

### Avvio locale realizzato

- `AGENTS.md`: istruzioni permanenti.
- `backend/`: healthcheck FastAPI tipizzato, test API e ingresso worker `--check` (nessuna coda o persistenza).
- `frontend/`: shell React minimale, stato preparazione e fonti espandibili. Non è un modulo funzionante né collegato all'API.
- `.env.example`, `.gitignore`, workflow CI senza secret o chiamate provider.
- Repository Git collegato a `https://github.com/kimmelucci-stack/GTM-Engine`, ramo `main`, preservando il commit iniziale del proprietario. Visibilità cambiata da pubblica a privata prima del caricamento; autenticazione tramite credential manager senza token negli URL.
- Guardia credenziali locale pre-commit e CI: controllo dei blob Git senza stampa dei valori, esclusione file sensibili, test con credenziali sintetiche. Non sostituisce la corretta gestione dei secret.
- Esiti di installazione e controlli: vedere `GATE_0_VALIDATION.md`.

Gate 0: healthcheck e guardia credenziali (5 test), ruff, ingresso worker e build/typecheck frontend riusciti; repository GitHub collegato. Esito CI remoto registrato in `GATE_0_VALIDATION.md`. Nessuna prova browser/E2E. Non sono avviati gate applicativi successivi.

Prossimo task: verificare CI sul primo push, poi su richiesta avviare Gate 1A con credenziali DataForSEO e cap esplicito. Prima delle chiamate consultare documentazione ufficiale corrente, definire campioni e registro costi; salvare raw redatti, senza trasferire ciecamente risultati numerici dell'audit.

## C. Attività del proprietario

| Fase | Cosa devo fare | Account/servizio | Credenziali o materiali necessari | Obbligatorio o condizionale | Stato |
|---|---|---|---|---|---|
| 0 | Indicare/creare repository e consentire collegamento | GitHub | URL repo e accesso autorizzato | Obbligatorio | Accesso verificato; repository privata collegata |
| 0, poi AI | Configurare API e limite spesa | OpenAI API | OPENAI_API_KEY server-side e budget | Obbligatorio per agenti | Non verificato; nessuna prova live |
| 1A | Configurare accesso API e limite richieste/costo | DataForSEO | DATAFORSEO_LOGIN/PASSWORD, credito, cap USD | Obbligatorio per Search | Da configurare/confermare nel runtime |
| 1B | Confermare cinque siti e fornire script se esistono | Siti campione | URL competitor; crawler/reviews preesistenti | Campione obbligatorio; script facoltativi | Campione non confermato, script assenti |
| 1C | Ottenere accessi Ads UE e IG separatamente | Meta Developer | App ID, token e permessi effettivi; script IG eventuale | Per Social/Meta ufficiale | Non verificato; autorizzazioni da provare |
| 1D | Configurare token e approvare micro-spesa | Openapi Company | API key, tre società/P.IVA e bilancio di confronto | Per dati societari automatici | Non verificato; cap non confermato |
| 1E | Fornire eventuali studi interni | Fonti pubbliche/proprietarie | Materiali posseduti; eventuale chiave se richiesta dalla policy corrente | Materiali facoltativi | Accesso pubblico da verificare |
| 2 | Creare progetto DB e storage privato | Supabase | DATABASE_URL, URL e service role key solo server | Obbligatorio | Non verificato |
| 2 | Predisporre frontend e approvare deploy | Vercel | Account/progetto collegato al repo | Obbligatorio per hosting | Non verificato; nessun deploy |
| 2 | Predisporre API/worker e autorizzare costo | Render | Account, servizi, variabili secret, cap | Obbligatorio per hosting | Non verificato; nessun deploy |
| Solo gap dimostrato | Autorizzare un fallback pertinente | SearchAPI / Apify / SerpApi | Token e budget del solo provider necessario | Condizionale | Non richiesto, non attivato |
| 3–4 | Validare keyword, cluster, identità e scorecard | GTM Engine | Feedback su dati reali | Obbligatorio come quality gate | Non avviato |
| 5–6 | Fornire brief, prove, obiettivi, durata e risorse | GTM Engine | UVP se applicabile; Paid, persone, ore totali, skill | Obbligatorio secondo modalità | Non avviato |
| 7 | Approvare template e verificare editabilità | PowerPoint | Branding/font licenziati opzionali | Approvazione obbligatoria; asset facoltativi | Non avviato |
| 8 | Accettare pilota, spese e pubblicazione | Servizi cloud | Consenso esplicito al rilascio | Obbligatorio | Non avviato |

Non inserire credenziali nella chat o nei documenti: usare variabili d'ambiente o secret manager. Nessuna richiesta di acquisto alternativo prima di dimostrarne la necessità.

## D. Registro dei blocchi

| Categoria | Elementi | Come si chiude |
|---|---|---|
| Pronto per lo sviluppo | Gate 0 locale, scope 01–07, stack, modello scoring e contratti concettuali | Eseguire solo attività del gate corrente; progettazione non equivale a implementazione |
| Da verificare tecnicamente | Build/test locali, tutti gli accessi nel runtime, crawler, geografie, PAA, fonti pubbliche, Structured Outputs e preview PPTX | Comandi/prove riproducibili con evidenze e limiti |
| In attesa di credenziali | DataForSEO, Meta, Openapi, OpenAI; accessi Supabase e hosting ai gate pertinenti | Configurazione privata e prova riuscita; disponibilità account non presunta |
| In attesa di approvazione economica | Cap richieste provider, Openapi/bilancio, API AI, Render e altri costi cloud | Importo/limite autorizzato prima della spesa |
| Non accessibile o limitato | Trends pilota 3/53; spesa Ads privata, reach privata competitor, WTP non studiata, performance commerciali private | Mantenere unavailable/partial; nuova prova può aggiornare lo stato, mai riempimento inventato |
| Collegamento proprietario — RISOLTO | GitHub assente nella cartella iniziale | Repository fornita dal proprietario, accesso Git verificato e remote configurato; visibilità privata |

Rischi: copertura geografica scarsa, omonimie società/brand, autorizzazioni Meta insufficienti, costi/task duplicati, CCI non calibrato, assenza di playbook approvati e qualità strategica da validare con persone. Nessuno di questi impedisce di preparare la struttura locale; impediscono invece di dichiarare conclusi i rispettivi gate.
