# GTM Engine — Handoff operativo a Codex

Data: 25 ottobre 2026. Questo registro distingue progettazione, codice locale e servizi verificati. Le specifiche originali restano invariate.

## A. Stato iniziale verificato

All'ingresso: sola cartella `docs/`, nessun codice applicativo, nessuna directory `.git`; `git status --short` restituisce «not a git repository». Nessuno ZIP da estrarre. Non risultano fixture raw delle precedenti prove, script crawler/Instagram, playbook KB o configurazioni di deployment. L'esistenza di account esterni non è stata accertata.

Tutti i sette moduli sono progettati: Demand; Market & Competitive; UVP & ICP; Value Proposition & Positioning; Channel & GTM Strategy; Execution Planning; Strategy Deck. Lo scoring v1.1 è una specifica sperimentale, non un modello empiricamente validato. Nessuna percentuale storica misura sviluppo effettivo.

Stack approvato: React/TypeScript/Vite su Vercel; Python 3.12+/FastAPI/Pydantic con API e worker separati su Render; Supabase Postgres e Storage; OpenAI Responses/Structured Outputs; DataForSEO; crawler Python; Meta ufficiale e Openapi Company condizionati agli accessi. KB GitHub/Markdown selettiva senza vettori; python-pptx con preview e verifica visiva. Codex sviluppa frontend e backend.

### Prove API ereditate, non riprodotte qui

Il registro aggiornato iniziale di `DATA_ACCESS_AUDIT_2026-10-24.md` riporta 12 prove DataForSEO: catalogo città, volumi/CPC Torino, volumi/CPC Piemonte, keyword ideas, intent, autocomplete, SERP organica, Maps, reviews TASK POST→GET, Trends, advertiser discovery e Ads Search. Esempi documentati: 10 recensioni, 18 advertiser e 19 creatività. Trends contiene solo 3 valori non null su 53: dato insufficiente. PAA e copertura nazionale restano da provare. Questi sono resoconti della sessione precedente, senza fixture locali: non costituiscono PASS del Gate 1A.

Da collaudare in questo runtime: tutti i provider, crawler su cinque siti, Meta Ads UE, Instagram Business Discovery, Openapi su tre società e un bilancio, ISTAT/Eurostat/ESCO/OpenAlex, OpenAI, Supabase, hosting e PPTX. Nessuna chiamata autenticata eseguita durante l'inizializzazione.

### Consolidamento documentale del 25 ottobre 2026 — dieci incoerenze chiuse

| Riferimento | Riscontro | Regola operativa per l'avvio |
|---|---|---|
| Project Scope: moduli e campagne | Stati funzionali e confine MVP allineati | 01–07 definiti, nessun invio automatico; chiuso |
| Stack negli scope 01–07 | Indicazioni tecniche superate sostituite | Render API/worker, Supabase e python-pptx definitivi; chiuso |
| Priorità provider | Registro attuale allineato alla matrice | DataForSEO Google; Meta ufficiale UE prima; fallback condizionati; chiuso |
| Cronologia prove API | Registro aggiornato e prima stesura separati | Evidenze precedenti conservate integralmente nell'archivio non normativo; nessun PASS locale inventato; chiuso |
| Ads Modulo 02 | Rimosso requisito di verifica assistita obbligatoria | Raccolta automatica oppure partial/unavailable motivato; chiuso |
| Backlog duplicato v0.1 | Contenuto confrontato con canonico | Canonico v0.3 in `docs/00_PROJECT/`, riferimento pricing storico recuperato; duplicato rimosso, storia in Git; chiuso |
| Legenda matrice | Accessibilità, disponibilità e inferenze separati | Tre assi, ambiente/data/fixture espliciti; chiuso |
| KB-001 | Inserito nella roadmap e nella KB | Implementazione/test Gate 2; verifica operativa prima della release Gate 8; chiuso, non implementato |
| README/handoff/rimandi | Stato aggiornato e duplicati scope consolidati | File con vecchi nomi 06–07 solo rimandi ai canonici, contenuti originali in Git; chiuso |
| AGENTS | Riferimenti e precedenze consolidati | Solo documenti canonici; archivio non normativo; chiuso |

Bonifica autorizzata dal proprietario: nessun requisito funzionale approvato modificato, nessun servizio aggiunto e nessuna evidenza storica API eliminata. Scoring v1.1 invariato. Restano dettagli implementativi e prove reali, non conflitti di stack: geografie/feature endpoint, permessi Meta, identità societarie, calibrazione empirica CCI, contratti tecnici e qualità strategica da collaudare.

Il proprietario richiede repository pubblica per portfolio. Pubblicazione limitata a codice/documentazione e campioni pubblici o sintetici revisionati; secret e dati cliente esclusi, inclusa la storia Git. L'impostazione privata prima del primo caricamento è una precauzione storica, non l'audience finale richiesta.

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
| 2 Foundation | Prove accesso, Supabase, Render, Vercel | Adapter, evidenze/raw, REST→job→worker→storage, retry/fail/timeout, cap, KB loader e KB-001 con test 45 giorni |
| 3 Demand | Foundation e dati utilizzabili | Pilota Torino, 20 keyword e tre cluster validati dal proprietario |
| 4 Competitive | Demand e fonti con stati espliciti | Cinque aziende, tre scorecard riviste, regressioni scoring v1.1 e missing data |
| 5 UVP/ICP/Positioning | Output 01–02 e input/prove proprietario | B2B/B2C e offerta disponibile/in sviluppo; approvazioni, nessun claim falso |
| 6 Channels/Execution | Strategia e risorse dichiarate | Budget insufficiente, ore/skill gap e costi separati; revisione strategica |
| 7 Deck | Snapshot approvati, template approvato | PPTX nativo editabile, render senza overflow e prova di modifica |
| 8 Release | Gate precedenti e consenso owner | E2E, failure provider, smoke produzione, KB-001 verificato operativamente, costi e accettazione firmata |

Ogni PASS richiede i campi QA della roadmap: comando/data/versione/provider/endpoint/input/status/campione/copertura/costo/raw/limiti e approvazione se prevista. Test automatici non sostituiscono validazione business o prova live.

### Avvio locale realizzato

- `AGENTS.md`: istruzioni permanenti.
- `backend/`: healthcheck FastAPI tipizzato, test API e ingresso worker `--check` (nessuna coda o persistenza).
- `frontend/`: shell React minimale, stato preparazione e fonti espandibili. Non è un modulo funzionante né collegato all'API.
- `.env.example`, `.gitignore`, workflow CI senza secret o chiamate provider.
- Repository Git collegato a `https://github.com/kimmelucci-stack/GTM-Engine`, ramo `main`, preservando il commit iniziale. Prima del primo caricamento era stata resa privata; ora pubblica su richiesta esplicita del proprietario, dopo scansione di contenuti e cronologia. Autenticazione tramite credential manager senza token negli URL.
- Guardia credenziali locale pre-commit e CI: controllo dei blob Git senza stampa dei valori, esclusione file sensibili, test con credenziali sintetiche. Non sostituisce la corretta gestione dei secret.
- Esiti di installazione e controlli: vedere `GATE_0_VALIDATION.md`.

Gate 0 **PASS e riconfermato dopo bonifica**: healthcheck e guardia credenziali (5 test), ruff, ingresso worker e build/typecheck frontend riusciti; repository pubblica collegata e push effettuato. CI secrets/backend/frontend Success anche sul consolidamento `5276c77`: https://github.com/kimmelucci-stack/GTM-Engine/actions/runs/40178552216 . Nessuna prova browser/E2E dell'applicazione. Non sono avviati gate applicativi successivi.

Prossimo task dopo Gate 1A: Gate 1B, crawler su cinque siti con riuso di eventuali script del proprietario e verifica evidenze per claim. Gli accessi DataForSEO sono stati riprodotti come da registro finale sotto; continuazioni mantengono il ledger, senza azzerare costi o riutilizzare automaticamente tutti i dati come validati.

## C. Attività del proprietario

| Fase | Cosa devo fare | Account/servizio | Credenziali o materiali necessari | Obbligatorio o condizionale | Stato |
|---|---|---|---|---|---|
| 0 | Indicare/creare repository e consentire collegamento | GitHub | URL repo e accesso autorizzato | Obbligatorio | Accesso verificato; repository pubblica per portfolio, senza secret versionati |
| 0, poi AI | Configurare API e limite spesa | OpenAI API | OPENAI_API_KEY server-side e budget | Obbligatorio per agenti | Non verificato; nessuna prova live |
| 1A | Configurare accesso API e limite richieste/costo | DataForSEO | Secret solo server-side, credito, cap USD | Obbligatorio per Search | Configurato privatamente; Gate 1A eseguito entro 5 USD |
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
| Pronto per lo sviluppo | Bonifica e Gate 0 PASS; Gate 1A PASS_WITH_LIMITATIONS | Prossimo Gate 1B, nessuna riprogettazione |
| Da verificare tecnicamente | Accessi provider nel runtime, crawler, geografie, PAA, fonti pubbliche, Structured Outputs e preview PPTX | Prove riproducibili con evidenze e limiti; build/test foundation già riusciti |
| In attesa di credenziali | Meta, Openapi, OpenAI; Supabase/hosting ai gate pertinenti | DataForSEO configurato e verificato; nessun altro accesso presunto |
| In attesa di approvazione economica | Cap richieste provider, Openapi/bilancio, API AI, Render e altri costi cloud | Importo/limite autorizzato prima della spesa |
| Non accessibile o limitato | Trends pilota 3/53; spesa Ads privata, reach privata competitor, WTP non studiata, performance commerciali private | Mantenere unavailable/partial; nuova prova può aggiornare lo stato, mai riempimento inventato |
| Collegamento proprietario — RISOLTO | GitHub assente nella cartella iniziale | Repository fornita dal proprietario, accesso e remote verificati; pubblica dopo revisione e scansione |

Rischi: copertura geografica scarsa, omonimie società/brand, autorizzazioni Meta insufficienti, costi/task duplicati, CCI non calibrato, assenza di playbook approvati e qualità strategica da validare con persone. Nessuno di questi impedisce di preparare la struttura locale; impediscono invece di dichiarare conclusi i rispettivi gate.

## Gate 1A — cronologia avvio sviluppo, 25 ottobre 2026

**Stato storico all'avvio: codice pronto; accesso GATED.** Proprietario: 5 USD totali per il pilota, prodotto completo 10–15 USD per run. Inizialmente cap preparato e credenziali mancanti, nessuna chiamata. Configurazione e collaudo sono stati poi completati come nel registro finale sotto; questa cronologia non descrive il blocco attuale.

Implementati `backend/src/gtm_engine/providers/dataforseo.py`, runner `backend/src/gtm_engine/gate1a.py` e configurazione locale a campi nascosti `scripts/configure_dataforseo.py`. Tredici campioni: catalogo IT; volumi città/regione/nazione; ideas; intent; autocomplete; organic/PAA; Maps; Trends; advertiser discovery; Ads Search; reviews POST/GET. Per reviews selezione di identità realmente osservata in Maps, avvio una sola volta e ripresa GET del task. Budget e journal persistiti prima dell'invio; nessuna riesecuzione automatica di POST dall'esito incerto. Nessun dato privato o fixture reale nel repository pubblico.

Verifica offline: pytest 43 test PASS (36 casi sintetici provider/pilota, 6 guardia credenziali e 1 healthcheck), ruff PASS. Copertura: credenziali oscurate, cap e prenotazioni, prezzi ignoti/superati, errori HTTP/rate limit/redirect, timeout senza duplicazioni, null distinto da zero, geografia errata, Trends sintetico 3/53, PAA assente, ripresa senza reset budget e singolo POST recensioni. Guardia corretta per distinguere un'annotazione SecretStr senza valore da un'assegnazione letterale, con test positivi/negativi. Questi test non provano accessibilità, correttezza dei dati live o qualità strategica.

Documentazione ufficiale consultata il 25 ottobre 2026: [volumi](https://docs.dataforseo.com/v3/keywords_data/google_ads/search_volume/live/), [Ads Search](https://docs.dataforseo.com/v3/serp/google/ads_search/live/advanced/), [reviews POST](https://docs.dataforseo.com/v3/business_data/google/reviews/task_post/), [reviews GET](https://docs.dataforseo.com/v3/business_data/google/reviews/task_get/), [Trends](https://docs.dataforseo.com/v3/keywords_data/google_trends/explore/live/). Confermati percorso GET reviews senza suffisso advanced, profondità campione 10 reviews e 40 Ads Search; nessuna tariffa numerica attuale dichiarata verificata. Listini dinamici da verificare prima di generare il rate card privato: altro prerequisito per l'esecuzione pagata, non un compito richiesto al proprietario.

Prossimo intervento del proprietario: configurare login/password API nel terminale locale con campi nascosti come da README. Poi Codex verifica tariffe, prepara riserve compatibili con 5 USD, esegue le prove e aggiorna matrice/audit con ambiente/data/campioni/costi/fixture/limiti effettivi. Nessun gate successivo avviato.

Codice iniziale `4058ad7`, CI **Success**: https://github.com/kimmelucci-stack/GTM-Engine/actions/runs/40179619707 . Le sole prove offline non superavano Gate 1A; le successive prove live sono distinte sotto.

## Gate 1A — esito live nel repository, 25 ottobre 2026

**PASS_WITH_LIMITATIONS di accessibilità; qualità dati complessiva partial.** Tredici campioni, compresa nazione, più una query PAA supplementare: dati reali ottenuti, reviews POST 20100→GET 20000 con 10 recensioni. SERP iniziale senza PAA; query mirata con un blocco PAA. Trends solo 2 valori non null su 54: nessuna stagionalità inferita. Maps un'attività, Ads discovery 18 elementi e Ads Search 19 creatività; nessun censimento o spesa competitor dedotta.

Spesa API 0,31847 USD (15 richieste dati); autenticazione/tariffe con endpoint gratuito a costo 0, senza divulgare dettagli account. Riserva conservativa 0,74644 USD, cap 5 USD. Fixture, tariffa e report solo nella cartella privata ignorata da Git; riepilogo pubblico nell'audit. Dataset sintetici e 47 test automatici PASS; ruff PASS. Nessun modulo applicativo end-to-end né altro provider collaudato. La misura del pilota non certifica ancora il target 10–15 USD del percorso completo. Prossimo gate: 1B, crawl cinque siti e verifiche delle fonti web.
