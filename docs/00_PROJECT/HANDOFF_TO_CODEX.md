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

## Gate 1B — implementazione locale, 25 ottobre 2026

Versione `gate1b-v1`: `providers/web.py`, runner `gtm_engine.gate1b` e test sintetici. Nessuno script crawler precedente trovato nel repository; nessuna riscrittura di script ricevuti. HTTP anonimo, BeautifulSoup/trafilatura, fallback Chromium/Playwright solo per HTML scarso; tetto quattro pagine/sito, timeout 20 s HTTP/30 s navigazione, massimo 2 MB/risposta, ritardo almeno un secondo e robots.txt fail-closed (404 ammesso). Redirect controllati, soli HTTPS/domini campione, nessuna credenziale o form. Destinazioni DNS private e WebSocket bloccati; DNS non pinned: CLI locale soltanto, egress da irrobustire prima dell'esposizione API. Query e risorse esterne bloccate: limite esplicito del fallback.

Test: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-gate1b-browser` con `GTM_BROWSER_TEST=1` e `PLAYWRIGHT_BROWSERS_PATH` sulla cartella privata: **65 PASS**, incluso Chromium reale su pagina dinamica sintetica; ruff PASS, frontend typecheck/build PASS, worker check PASS, 22 Markdown/84 riferimenti senza errori. CI ordinaria esclude il solo test Chromium opt-in, senza crawl live. Fixture HTML sintetiche in `backend/tests/test_web.py`; raw temporanei nella cartella privata ignorata. Input: pagine statiche/dinamiche sintetiche, robots disallow, redirect privato, DNS pubblico/privato misto, timeout, oversize, challenge e dati mancanti. Provider HTTP simulato: nessun codice HTTP reale attribuito ai siti, costo API 0, calcolo locale non misurato. Fonte e data per ogni estratto; claim del publisher non promossi a fatti verificati. Prezzi assenti mai valorizzati a zero. Cache in memoria per evitare richieste duplicate, log richieste e robots salvati soltanto nelle fixture private.

**Gate non superato:** il campione iniziale (`madeinteam.it`, `teambuildingitaly.com`, `teambuilding.it`, `teamworking.it`, `sunnywayteambuilding.com`) è stato **rifiutato dal proprietario**. Non riutilizzarlo come default approvato. Richiesta una nuova discovery coerente con il cliente pilota e la domanda nel mercato locale; dettagli del cliente e ricerca specifica restano privati. Chiarire offerta effettiva e identità del cliente, così da escluderlo dai concorrenti. Confrontare competitive fit e organic visibility separatamente, distinguere concorrenti diretti e sostitutivi e motivare i cinque prima dell'approvazione. La consultazione preliminare tramite strumento web non è una prova live del connettore né un benchmark di ranking Google geolocalizzato. Nessun sito contato come crawl superato; nessuna shortlist commerciale approvata implicitamente. Prossimo task: selezione motivata, conferma campione, runner opt-in e registrazione copertura/campi/cause reali nell'audit. Non passare al Gate 1C.

**Successiva precisazione del proprietario:** identità del cliente ricevuta, esclusa dai concorrenti; analizzare separatamente offerta del club e offerta eventi aziendali. Brief, fonti ufficiali e due campioni motivati di cinque candidati salvati solo in `artifacts/private/web-discovery/screening.json`, ignorato da Git. Nove siti distinti per sovrapposizione di un operatore tra segmenti; nessuna fusione dei mercati o dei dataset. Proposte distinguono città e comuni vicini, concorrenti diretti e sostituti; omonimi fuori territorio esclusi. Nessuna quota di mercato, volume di domanda, classifica SEO geolocalizzata o indipendenza societaria certificati dalla sola discovery web. Conferma dei nuovi campioni ancora richiesta; vecchio campione resta rifiutato. Al momento nessun nuovo crawl live e nessuna spesa API aggiuntiva. Il costo del vecchio pilota Search non misura il nuovo segmento del club. CI del crawler `e0d4f3d`: Success.

## Metodo competitivo riutilizzabile — richiesta del proprietario, 25 ottobre 2026

La discussione sul pilota richiede un metodo del prodotto, non una lista settoriale costruita per un cliente. Canonico: Modulo 02 `SCOPE.md` v0.4 §4.4–4.7, `competitor-selection-v1`. Unità offerta/bisogno/pubblico/territorio, longlist da almeno due percorsi, screening qualificato, diretti/sostitutivi e intermediari/editori separati, organic/Maps/paid indipendenti con stati ignoti espliciti. Proposta di cinque con razionali e copertura, nessuna quota fissa o score arbitrario. Il proprietario rivede la proposta prima delle estrazioni approfondite; massimo tre aggiunte per analisi come già previsto. Offerte diverse mantengono analisi separate; fonti riusabili senza duplicare richieste e senza mescolare i contesti.

Contratti Python e test sintetici in `domain/competitors.py` e `tests/test_competitors.py`: esclusione cliente/duplicati di dominio, alternative commerciali con fonti/identità/pubblico/territorio, publisher non ammesso per sola visibilità, intermediario ammesso solo se vende un'alternativa, assenza nel campione distinta da ignoto, motivazioni per inclusioni/esclusioni e classi omesse, proposta distinta da approvazione. Non certificano il merito delle valutazioni AI o l'indipendenza societaria. Non implementati orchestrazione AI, acquisizione multi-query, persistenza, UI o ranking automatico; applicazione completa e QA strategica al Gate 4. Scoring v1.1 invariato, nessun nuovo servizio o modulo. Gate 1B resta aperto; le precedenti rose private sono provvisorie e da rivalutare applicando il metodo, non approvate. Nessuna nuova chiamata provider o spesa.

Verifiche locali del metodo: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-method-final` con `GTM_BROWSER_TEST=1` e browser nella cartella privata: **75 PASS**, inclusa regressione Chromium sintetica. Ruff, worker check e typecheck/build frontend PASS; 22 Markdown/85 riferimenti interni senza errori. Prove sintetiche separate dalle prove provider; nessuna efficacia strategica o selezione reale dichiarata validata. Il solo warning Starlette/httpx già presente non blocca i test.

## Approvazione con checkbox — implementazione parziale autorizzata, 25 ottobre 2026

Richiesta esplicita del proprietario: procedere con la revisione tramite checkbox. Scope §4.3 precisato; componente React `CompetitorReview.tsx` con cinque base, alternative, diretti/indiretti, motivazioni e fonti espandibili, campione parziale, fino a tre URL manuali con stato pendente e blocco conferma; proposte versionate e reset componente per nuova analisi/revisione. Conferma asincrona con errore esplicito e conservazione selezione. Schermata iniziale vuota, esempio interattivo sintetico opt-in, conferma soltanto in memoria: nessun cliente reale, salvataggio finto o analisi avviata. Nuovi siti non vengono automaticamente verificati. Guardie Python in `domain/approvals.py` legano consenso/versione/ID e impediscono raccolte con approvazione assente, obsoleta, ID non approvati o candidati non qualificati; funzioni pure non ancora collegate al crawler, API o worker. Nessun endpoint che accetti approvazioni autocertificate dal browser.

Test: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-approval-ui`, frontend su `127.0.0.1:5173`, `GTM_UI_TEST=1`, `GTM_BROWSER_TEST=1`, Chromium nella cartella privata: **80 PASS**. Browser reale: sostituzioni, numero selezionati, blocco eccesso, URL non HTTPS, aggiunta pendente/rimozione, conferma di prova, invalidazione modificando selezione, reset al reload, nessuna POST e nessun errore JS. Screenshot desktop/mobile in `artifacts/private/review-ui/`, verificati visivamente, niente overflow orizzontale a 390 px. Provider/costo: N/A per test sintetici locali, nessuna chiamata pagata. UI ordinaria in CI: test browser opt-in esclusi. Resta da collegare approvazione autenticata persistita su Supabase e job; nessun Gate 2/4 dichiarato completo, Gate 1B ancora aperto.

## Revisione UX/UI richiesta dal proprietario — proposta SaaS v02

Il proprietario ha rifiutato il primo layout verticale di selezione e richiesto reference e progettazione SaaS professionale. Il vincolo è registrato nello scope Modulo 02 §4.3; il layout precedente non è un riferimento approvato. Reference primarie consultate il 25 ottobre 2026: Linear Projects e Display options (struttura progetto/viste), Attio (gestione dati), Clay (ricerca aziende). Scelta proposta: workspace analitico con sidebar, breadcrumb e fase, offerte separate, tabella confrontabile con filtri/ricerca, inspector laterale e drawer su mobile, dialogo per URL e azione di conferma persistente a schermo. Alternativa discussa: revisione guidata a scheda singola, meno adatta al confronto simultaneo. Nessuna estensione delle funzionalità o provider; asset SVG/CSS originali, nessun servizio acquistato.

`Workspace.tsx`, `Icon.tsx` e nuovo layout `CompetitorReview.tsx`; root apre direttamente la proposta, senza «Apri esempio interattivo». Sidebar delle fasi non implementate disabilitata. Progetti, nomi, relazioni e motivazioni sintetici dichiarati; metriche assenti restano «da verificare». Riferimenti anche nel pannello «Direzione di design». Nessun dato del cliente nel frontend. Proposta da valutare, non approvazione ricevuta né release. Consenso, limiti e guardie backend invariati; nessuna analisi o persistenza simulata. Le prove browser precedenti sono state adattate alla nuova UX e comprendono filtri, ricerca vuota, scheda, dialogo, offerte e tastiera; screenshot desktop/mobile/drawer privati verificati visivamente. Gate 1B resta aperto.

Verifica v02: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-saas-final`, frontend locale e `GTM_UI_TEST=1`/`GTM_BROWSER_TEST=1`: **80 PASS**, ruff PASS, typecheck/build PASS, 22 Markdown/85 riferimenti senza errori. Controllato confronto visibile su mobile a 390 px, drawer, reset al cambio offerta/reload e tab da tastiera; nessun errore JS o POST applicativa. Immagini private `review-ui/saas-proposal.png`, `saas-add-dialog.png`, `desktop.png`, `mobile.png`, `mobile-detail.png`; nessun raw cliente pubblicato. Colori e layout sono una proposta originale, ancora in revisione.

## Attio e font verificati — revisione v03, 25 ottobre 2026

Indicazione esplicita: MAI frecce nelle CTA; Attio riferimento prioritario, con gli stessi font dell'app. Vincolo permanente in AGENTS, Project Scope e Modulo 02. La v02 è stata giudicata insufficiente dal proprietario; non considerarla approvata. Ispezione anonima delle fonti pubbliche ufficiali: `app.attio.com` calcola `Inter, sans-serif` e carica Inter variabile 100–900; `attio.com` usa Inter per testo, Inter Display per titoli e registra anche Tiempos/JetBrains Mono. L'app è il riferimento scelto; nessun accesso autenticato rivendicato. Screenshot ufficiale della navigazione esaminato tramite Help Center, copia di ispezione solo privata.

Inter prima era soltanto dichiarato nel CSS senza file: poteva essere sostituito dal font di sistema. Ora font WOFF2 originale Inter dell'app pubblica in `frontend/public/fonts/InterVariable.woff2`, 345588 byte, SHA-256 `8af7bd5b545567adffb3dfceb5bedb353a522d7bf1b3a2b8af7b6064156babc0`; licenza SIL OFL da upstream ufficiale `rsms/inter` inclusa in `Inter-OFL.txt`. Nessun font a pagamento o servizio nuovo. Rimossi CTA con frecce, icone di freccia sulle azioni, freccia nel marchio provvisorio, hero, stepper e palette viola. Tabella continua con bordi di cella sottili, densità compatta, tipografia reale, controlli neutrali e CTA scura; dati sintetici e limitazioni operative invariati. Niente copia del logo o dei dati di Attio. Proposta v03 da valutare, non release o design già approvato.

Test browser esteso: font Inter effettivamente caricato e font computato, nessun asset runtime esterno, nessuna freccia nelle CTA, filtri/ricerca/dialogo, revisione consenso e selezione anche delle ultime righe su mobile. Test automatici restano distinti dal giudizio UX del proprietario. Nessuna nuova raccolta cliente o spesa provider; Gate 1B ancora aperto.

Verifica v03: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-attio-final`, frontend locale e due flag opt-in browser: **80 PASS**. Ruff e typecheck/build PASS; 22 Markdown/86 riferimenti senza errori. Screenshot corrente privato `artifacts/private/review-ui/attio-v03-proposal.png`. Font copiato anche nel build statico; nessun collegamento a CDN font nel prodotto.

## Ripresa motore dati — screening web reale, 25 ottobre 2026

Su richiesta di proseguire lo sviluppo e rinviare le rifiniture visuali, aggiunta modalità CLI `--screen --live`: da uno a sedici domini distinti, una pagina HTTP e al massimo dieci richieste/sito incluse robots/redirect, nessun browser o conferma implicita. Mutualmente incompatibile con `--confirmed-sample`/`--browser`. Doppioni tra offerte deduplicati prima della rete, raw/report privati nuovi senza sovrascrittura. Lo screening commerciale leggero precede la conferma, come previsto dal metodo; non avvia l'approfondimento e non supera automaticamente il Gate 1B.

Eseguiti nove domini reali della longlist privata, 17 GET, otto pagine con evidenze e un HTTP 403 su robots.txt; sul dominio bloccato nessun fetch della pagina o aggiramento. Registro nell'audit e matrice canonica; stato sincronizzato negli scope tramite rimando canonico. Originale `artifacts/private/web-screening/20261025T115336Z/report.json`; dopo correzione del parser per prezzi in blocchi HTML/celle e paragrafi CMS lunghi, nuova trasformazione `web-extract-v2` in `extraction-v2.json`, senza rete e senza alterare l'originale. Otto pagine disponibili, 106 estratti (66 dichiarazioni del publisher, 29 CTA, 11 estratti di prezzo da due pagine); nessun case study nel campione, nessuna deduzione sulla sua assenza generale. Fit commerciale, visibilità nei canali e shortlist ancora da validare. Costo API aggiuntivo zero, calcolo locale non misurato; ledger DataForSEO invariato.

Integrità: digest originali del testo HTML verificati per tutte le otto catture, tenendo conto della conversione newline eseguita da `write_text` su Windows; `integrity.json` privato conserva anche i digest dei byte effettivamente salvati e il metodo di ricostruzione. Nessuna modifica ai raw originali. Nuove catture con `write_bytes` UTF-8 per corrispondenza esatta del digest del file su Windows/Linux, testata.

Verifiche: `.venv/Scripts/python.exe -m pytest backend -q --basetemp=artifacts/private/pytest-web-screening-final`, due flag opt-in browser e frontend locale: **85 PASS**; dopo correzione newline, test web mirati 22 PASS/un test browser escluso (già verificato nella suite completa). Ruff PASS, worker check PASS, piano CLI senza rete PASS, 22 Markdown/93 riferimenti senza errori. Frontend invariato in questa ripresa, nessuna rifinitura estetica. Prossimo lavoro: qualificare le alternative dei due mercati con evidenze e campioni di domanda, proporre la shortlist per revisione, quindi crawl approfondito autorizzato. Nessun Gate 1C o successivo avviato.

## Qualificazione esplorativa e guardie identità — 25 ottobre 2026

Eseguite otto query web esplorative, quattro per ciascuna delle due offerte, con percorsi per categoria e bisogno più ampio. Raw privati `artifacts/private/web-discovery/search-round-2.json` e `search-round-2b.json`; proposta privata con cinque candidati per offerta, fonti, motivazioni, riserve e limiti in `proposal-round-2.json`. Nessuna classifica dei migliori, nessuna posizione Google geolocalizzata o misura ADV attribuita a questa ricerca. Le aperture di pagine tramite ricerca web non sono prove del crawler HTTP del repository. Due ulteriori verifiche di pagina non riuscite restano tali, senza promozione a tested. Nessuna chiamata DataForSEO aggiuntiva; eventuali costi del tool di ricerca non misurati nel ledger API.

Contratto Python esteso con `exploratory_web` separato dai tre canali misurati e `represents_client`: una scheda cliente su dominio terzo non è selezionabile come competitor. Sono guardie deterministiche su classificazioni fornite, non risoluzione automatica di identità, discovery orchestrata o autenticazione. Nessuna modifica allo scoring o alla UI. Verificati anche i casi negativi per schede cliente e la separazione dei canali. Suite backend: **85 PASS, 2 test browser opt-in esclusi**; Ruff PASS; documentazione 22 file/93 riferimenti senza errori. La suite browser precedente non è stata ripetuta, frontend invariato. Gate 1B aperto: proposta da approvare prima del crawl approfondito; Gate successivi non iniziati.


## Gate 1B tecnico completato con limiti — 25 ottobre 2026

Il proprietario ha limitato il pilota a eventi aziendali/team building e delegato la scelta per i test. Eseguito il campione di cinque siti: `artifacts/private/web-detailed/20261025T121857Z/report.json`, 15 GET, otto pagine disponibili su nove tentativi, una risorsa `not_html`, 95 estratti con fonti, otto hash verificati. Gate 1B **PASS_WITH_LIMITATIONS**; dettaglio e comando nell’audit canonico. Browser abilitato ma mai necessario: non dichiararlo collaudato live. Nessuna approvazione commerciale implicita o nuova spesa API; dati privati ignorati da Git. La precedente analisi club B2C è esclusa dal pilota attivo e conservata soltanto come ricerca storica. Prossimo gate nella roadmap: 1C Meta, subordinato ad accessi e prove reali; non eseguito in questa sessione.

Controlli della sessione: 85 test backend PASS, due browser opt-in esclusi; Ruff e typecheck/build frontend PASS. Controllo documentale: 22 file/93 riferimenti, zero errori. Ricerca globale degli stati precedenti: rimangono solo nelle registrazioni storiche dell'handoff e dello screening, superate dal presente aggiornamento; intestazioni correnti allineate. Controllo segreti sui file tracciati e su 17 commit/172 blob PASS prima del commit documentale. Nessun raw, dominio del campione o dato cliente incluso nelle modifiche pubbliche.


## Gate 1C avviato — configurazione mancante, 25 ottobre 2026

Preflight offline alle 12:41:32 UTC: token Meta, App ID, IG user ID interrogante e versione Graph mancanti. Report privato `artifacts/private/meta/preflight-20261025/report.json`; zero richieste API. Nessun connettore live Meta implementato o accesso collaudato. Aggiunti controllo ripetibile `gate1c.py`, quattro test sintetici e setup a input nascosto `scripts/configure_meta.py`; `.env.example` esteso con nomi vuoti. 89 test PASS, due browser opt-in esclusi, Ruff PASS. Frontend invariato.

Le pagine ufficiali sviluppatori Ads Archive e Business Discovery hanno restituito HTTP 429 nel tool web; non si tratta di errori di autenticazione API. Onboarding ufficiale Ads Library consultabile; versione e requisiti da confermare prima delle prove live. Necessari account/app e autorizzazioni effettive del proprietario; mai chiedere valori in chat. Nessun fallback o spesa attivato. Gate 1C NOT_TESTED con causa needs_configuration; gate successivi non avviati.


## Gate 1C — riscontri effettivi nel browser autenticato

25 ottobre: app esistente confermata; Graph API Explorer v25.0. Quattro query logiche con risposta: permessi (9 granted), due varianti me/accounts (una pagina senza campi Instagram), ads_archive (OAuthException codice 10, autorizzazione richiesta). Prova UI, non adapter Python; token non copiato in locale e nessuna nuova autorizzazione concessa. Business Discovery non eseguito in assenza di IG ID utilizzabile. Audit aggiornato, riepilogo privato senza credenziali/ID/cursori in `artifacts/private/meta/browser-probe-20261025/report.json`. Nessun media/annuncio raccolto o fallback attivato. Gate NOT_PASSED; prossimo intervento: verificare abilitazione Ads Library e disponibilità/permessi del collegamento IG del proprio account. Non affermare che il collegamento sia inesistente. Nessun codice applicativo modificato in questa prova.

Ulteriore riscontro UI: il collegamento ufficiale Facebook.com/ID apre `/id/hub/`, che richiede ulteriori informazioni per confermare l’identità e presenta Get started. Nessuna informazione identitaria acquisita o inviata; nessun documento/biometria o consenso gestito. Questo riscontro indica un percorso incompleto, senza dimostrare che sia l’unica causa dell’errore Ads Library. Scheda lasciata al proprietario per completamento personale.


## Prosecuzione autorizzata: Meta in attesa e fonti pubbliche

Il proprietario ha richiesto di lasciare il Gate 1C in attesa della revisione Meta e continuare sulle attività indipendenti. Nessun nuovo accesso o documento identitario richiesto. Gate 1D: sola verifica booleana della chiave Openapi, assente; nessun budget specifico o richiesta fatturabile. Gate 1E implementato con runner opt-in e normalizzatori riutilizzabili: import ATECO XLSX (3.257 codici), Eurostat JSON-stat (una cella con dimensioni/etichette/anno/unità) e OpenAlex (tre record bibliografici) verificati live; ESCO HTTP 307 alla pagina sorry, stato unavailable. Gate 1E PARTIAL.

Run `artifacts/private/public-sources/20261025T131025Z/`, raw/hash/normalizzati e verifica privata, comando/limiti nell’audit. Originali preservati, annotazione del costo tecnico OpenAlex 0,001 USD separata da addebito non verificato. Nessuna nuova dipendenza, servizio, deploy, profilo utente o campagna. Suite 98 PASS/2 browser opt-in esclusi; Ruff PASS. Frontend invariato, Gate 2 non ancora implementato. ESCO da riprovare solo con nuovo run privato quando disponibile; Openapi richiede chiave/cap, Meta resta in attesa.


## Gate 2 Foundation avviato — KB-001 a richiesta

Su richiesta di proseguire durante le attese provider, implementati registro tipizzato, calendario 45 giorni e checker HTTP condizionale. Nuovi file `domain/source_refresh.py`, `source_refresh.py`, `tests/test_source_refresh.py`. Solo fonti approvate e scadute; niente richieste in modalità calendario, limite GET/byte/timeout, errori separati dalle verifiche riuscite, output nuovo ignorato da Git. Non modifica framework/playbook o approvazioni. Nessun servizio o dipendenza aggiunti.

Verifica: 125 test backend PASS, due browser opt-in esclusi; 27 test specifici KB-001. Ruff e typecheck/build frontend PASS. CLI offline su registro sintetico in `artifacts/private/kb001/offline-command-check/report.json`: zero richieste. Nessun registro reale KB approvato/schedulato né prova HTTP operativa KB-001, costi non misurati. DB, worker persistente, storage, loader KB e budget trasversale restano da implementare: Gate 2 non completo. Gate 1C rimane in attesa, Gate 1D non eseguito, Gate 1E parziale.


## Directory delle funzioni operative B2B — richiesta del proprietario

25 ottobre 2026: sostituire la dipendenza da un catalogo delle professioni con una directory interna delle funzioni operative coerenti ai reparti. Creati dati canonici business-functions-v1: 12 reparti, 60 funzioni con responsabilità descritta, ID stabili e appartenenze condivise esplicite. Vista leggibile nel Modulo 03. API di riferimento `/reference/business-functions`, filtro reparto, dati inclusi nel packaging backend. Contratto BuyerFunctionReference: job title facoltativo, ruoli di acquisto separati e non dedotti; associazioni incoerenti o Observed senza fonte rifiutati. Nessuna inferenza di buyer reali o autorità, nessun contatto nominativo, nessun organigramma imposto.

Scope 00/03/04/05, matrice, roadmap e AGENTS aggiornati alla nuova decisione esplicita. Ruoli relazionali B2C e competenze del team nel Modulo 06 invariati. ESCO non è necessario al buyer mapping; runner Gate 1E v2 esclude ESCO salvo flag esplicito, senza riscrivere prove storiche. Non eseguite nuove richieste provider. Directory e API non completano il workflow ICP end-to-end.

Verifiche: 134 test backend PASS, due browser opt-in esclusi; Ruff e frontend typecheck/build PASS. Pacchetto wheel costruito e presenza del JSON canonico al suo interno verificata; strumenti build setuptools/wheel predisposti nel solo ambiente locale. Piano CLI Gate 1E senza rete: tre fonti predefinite, quattro soltanto con flag ESCO. 23 Markdown/98 riferimenti senza errori. Nessun dato cliente o credenziale aggiunto alla directory pubblica; nessun deploy effettuato.


## Board, proprietà e ruoli di vertice — directory v1.1

Su richiesta esplicita del proprietario, estesa la directory mantenendo le 60 funzioni/12 reparti: quattro organi/strutture collegiali (CdA, assemblea soci, comitato esecutivo, advisory board) e 25 ruoli/posizioni di proprietà, fondazione, governo, direzione e coordinamento. Dati canonici correnti `business_functions.v1_1.json`; v1 preservata e interrogabile con versione esplicita, nessuna conversione silenziosa di riferimenti storici. AD/CEO/Owner/Founder/Presidente distinti, cariche cumulabili, nessuna equivalenza o potere di firma/budget inferito.

Contratto buyer esteso con riferimenti di governance separati; funzione/reparto possono essere assenti quando è noto soltanto l’organo o la carica. Controlli per ID ignoti/duplicati, organo scambiato per ruolo, riferimenti tra versioni e fonti per assegnazioni Observed. API di riferimento con filtro reparto e versione, non discovery di persone. Fonte consultata per le distinzioni: Codice Corporate Governance 2020 (società quotate) e guida IoD, riferimenti nella vista leggibile; indicazioni non universalizzate a ogni paese o assetto societario. Nessuna nuova raccolta o pubblicazione di dati cliente.

Verifica v1.1: 145 test backend PASS, due browser opt-in esclusi; Ruff e frontend typecheck/build PASS. Wheel verificato con directory corrente e storica incluse. Controlli negativi per riferimenti di governance orfani, ruoli duplicati o confusi con organi, autorità non dedotta e lettura della versione precedente. Nessun deploy o integrazione del workflow ICP completo; nessun nominativo o dato account nel catalogo.


## Correzione vincolante: buying committee per job title, non funzioni

Il proprietario ha rifiutato la directory delle attività come output buyer e richiesto job title in ogni reparto, inclusi interlocutori con influenza/valutazione anche minima, non solo board/C-level. Creato catalogo buyer-job-titles-v1: 251 titoli/posizioni nei 12 reparti, denominazioni italiane/inglesi e varianti, appartenenze condivise; vista leggibile BUYER_JOB_TITLE_DIRECTORY.md. Le directory precedenti restano supporto storico, non contratto principale. Nessun catalogo universale esaustivo o potere certo promesso.

Aggiunti API ricercabile/filtrabile e contratti CommitteeMember, BuyingCommittee e ApproachStep. Ogni membro richiede titolo da directory o estensione esplicita, reparto coerente, motivazione e stato; Observed richiede fonti. Ruolo di acquisto non assegnato dal titolo. Approccio eventuale con destinatari riferiti ai membri, obiettivo, sequenza e prove, senza messaggi o invii automatici. Scope 00/03/04/05, AGENTS e matrice aggiornati; B2C invariato. Nessuna raccolta di persone o comitato cliente pubblicato; nessuna orchestrazione AI/persistenza/UI ICP certificata.

Verifiche della correzione: 155 test backend PASS, due browser opt-in esclusi; Ruff, frontend typecheck/build e costruzione wheel PASS. Verificata inclusione dei 251 titoli nel pacchetto. 24 Markdown/100 riferimenti senza errori. Nessuna richiesta provider o dato cliente nella directory; nessuna UI ICP o selezione automatica del comitato reale dichiarata operativa.


## Foundation: loader KB e budget trasversale

Prosecuzione autorizzata: controllo di sola presenza per OpenAI e Supabase, nessun valore mostrato. OpenAI configurato, DB/storage non configurati; nessuna chiamata AI, deploy o nuova spesa. Implementati knowledge.py e domain/run_budget.py. Loader di Markdown approvati per fase, versioni/hash/fonti, confini percorsi e limiti; nessuna libreria reale auto-approvata o istruzione KB spacciata per dato cliente.

Budget USD unico di dominio: prenotazioni cross-provider, riconciliazione idempotente, incertezza senza rilascio, errori di sottostima conservati e blocco, tetto 15/obiettivo 10, costi mancanti o componenti non riconciliate impediscono la dichiarazione di conformità. Componente in memoria, non transazionale, non ancora collegato agli adapter né al worker; rimane da persistere in Postgres con lock. Gate 2 non completo. Nessuna modifica alla selezione per job title o al frontend; Meta in attesa.

Verifiche: 175 test backend PASS, due browser opt-in esclusi; 20 test aggiunti per loader/budget. Ruff e frontend typecheck/build PASS. Dati di test sintetici, nessun dato cliente pubblicato. Il costo complessivo reale del GTM resta non dimostrato.

## Foundation — progetto Supabase e prima migrazione privata

25 ottobre 2026: organizzazione confermata dal proprietario tramite connettore; progetto dedicato GTM Engine creato in eu-central-1, ACTIVE_HEALTHY, preventivo 0 USD/mese Free. Nessun altro progetto modificato; nessuna chiave recuperata e nessun dato account registrato nel repository. Tabelle applicative inizialmente assenti. Documentazione corrente e changelog Supabase consultati; CLI ufficiale 2.122.0 usata per generare la migrazione, poi versione del file allineata alla cronologia remota MCP: 20261025142253_foundation_private_queue.

Schema interno gtm con projects/runs/jobs, owner riferito ad auth.users, vincoli/indici e RLS attiva/forzata. Accesso negato ad anon, authenticated e service_role; nessuna policy permissiva o funzione SECURITY DEFINER. Questo blocco è intenzionale finché non esistono ruolo backend e autorizzazione per proprietario. Nessuna integrazione applicativa dichiarata operativa.

Prova live MCP execute_sql con `supabase/tests/foundation_private_queue.sql`: insert/read sintetico amministrativo, modulo invalido, job orfano e retry oltre limite rifiutati; SELECT effettivi negati ai tre ruoli su tutte le tabelle, privilegi verificati. Transazione rollback, successiva verifica projects/runs/jobs tutti a zero. Provider Supabase/Postgres, campione un progetto/un run/un job sintetici; nessuna richiesta commerciale o costo provider aggiuntivo. Advisor security/performance: zero ERROR/WARN; INFO RLS senza policy su tre tabelle e quattro indici non usati, coerenti con database chiuso e nuovo. Remediation ufficiali: https://supabase.com/docs/guides/database/database-linter?lint=0008_rls_enabled_no_policy e https://supabase.com/docs/guides/database/database-linter?lint=0005_unused_index.

Gate 2 ancora aperto: seguono accesso server riservato con autorizzazione, API di persistenza, worker con claim atomico/heartbeat/retry, ledger budget transazionale e Storage privato. Nessun deploy, storage o percorso frontend end-to-end collaudato. Prove storiche precedenti conservate; lo stato corrente del database supera le note precedenti di mancata creazione.

## Foundation — accessi separati, API progetti e worker a singolo passaggio

Aggiornamento UX setup: su richiesta del proprietario predisposto database_setup_ui.py, modulo temporaneo nel browser integrato, loopback e campi password, senza credenziali in URL/log/risposta, verifica Host/Origin/CSRF, limite payload e nessuna risorsa esterna; chiusura dopo successo. Riutilizza configure() estratta dal setup nascosto. Tre test HTTP sintetici PASS (mascheramento/header, richieste esterne/CSRF respinte, nessun valore ripetuto e chiusura dopo successo); provisioning e collegamento reale non certificati da questi test. Il lancio precedente tramite PowerShell incontrava un prompt attendibilità PSReadLine; nessuna policy o attendibilità modificata. Il percorso browser evita quel terminale.

Semplificazione ulteriore: parametri disponibili trasferiti dall'interfaccia Supabase al modulo locale senza riportarne i valori nella conversazione. Connessione ancora con segnaposto: aggiunto quarto campo mascherato per la sola password, sostituzione del segnaposto con percent-encoding e rifiuto di una password aggiuntiva se la connessione ne contiene già una. Quattro test del modulo, inclusi caratteri speciali senza echo. Pannello reset preparato per l'inserimento personale del proprietario; nessuna password cambiata dall'agente, nessun invio del setup o accesso runtime dichiarato verificato.

Correzione setup dopo segnalazione Forbidden: configurazione runtime ancora assente. Il modulo combinava Referrer-Policy no-referrer con controllo Origin esatto, incompatibili per POST form nativi che possono inviare Origin null. Header corretto in same-origin: nessun referrer a destinazioni esterne, controllo Host/Origin e CSRF invariati, richieste Origin null/esterne ancora rifiutate nei test. Causa coerente con documentazione https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Origin; header della richiesta utente originale non registrato, nessuna password dedotta come errata. Test HTTP del modulo PASS; istanza riavviata sullo stesso indirizzo e parametri disponibili ripristinati. La prova con un browser su un endpoint diagnostico vuoto separato è stata bloccata dal client, senza usare credenziali; nessun aggiramento. Il nuovo invio reale resta da eseguire dal proprietario, senza reset ulteriore della password.

25 ottobre 2026: Francoforte mantenuta su indicazione del proprietario di gestire autonomamente l'hosting UE; sede server distinta dalla geografia del pilota. Nessun progetto spostato o servizio aggiunto. Migrazioni worker_leases e owner_policy_initplan applicate via MCP, versioni locali allineate alla cronologia remota. Skill Supabase/Postgres applicate; documentazione corrente ruoli consultata. PostgreSQL driver psycopg[binary] 3.3.6 fissato e installato localmente.

Ruoli server NOLOGIN gtm_api/gtm_worker, senza superuser/BYPASSRLS; API solo INSERT/SELECT progetti con owner verificato e contesto transazionale locale, worker solo SELECT/UPDATE job. Funzioni SECURITY INVOKER nello schema privato, EXECUTE revocato ai client e service_role. Claim atomico FOR UPDATE SKIP LOCKED, tentativi incrementati, UUID token, heartbeat e scadenza, completamento subordinato a token valido. Scadenza => failed/outcome_unknown senza retry automatico; retry esplicito solo handler dichiarato sicuro e tentativi residui. Nessun ledger sostituito dal cap di modulo.

Python: connessioni brevi con TLS verify-full/system CA, rifiuto login privilegiati ed errori redatti. POST/GET progetti protetti con verifica server Supabase Auth, nessuna fiducia nel payload JWT decodificato localmente, account anonimi esclusi. Worker --once con heartbeat e solo handler locale catalog.validate; nessun provider/AI/analisi a pagamento abilitato. Stato run aggregato, enqueue autenticato e workflow analitici non implementati. Deadline interrompe il rinnovo e invalida il completamento, non uccide fisicamente handler bloccati: timeout provider restano necessari. Nessun worker continuo o deploy.

Prove: supabase/tests/worker_leases.sql via MCP, due proprietari sintetici, tre job iniziali più caso retry, vincoli e isolamento, owner spoof rifiutato, worker escluso dai brief, API esclusa dalle funzioni worker, token errato/scaduto e completamento ripetuto rifiutati. Test separato due query MCP parallele, una trattenuta tre secondi nella transazione: due job distinti; transazioni amministrative per la sola prova concorrenza, permessi worker verificati nello script SQL. Due tentativi di pulizia multi-statement hanno restituito invalid_request_state; pulizia riuscita con CTE mirate, controllo finale projects/runs/jobs tutti zero. Nessun dato cliente. Nessuna richiesta fatturabile aggiuntiva. Advisor: due WARN iniziali initplan corretti in migrazione separata; controllo successivo performance soltanto INFO indice runs non usato, security INFO runs senza policy perché chiusa. Remediation: https://supabase.com/docs/guides/database/database-linter?lint=0003_auth_rls_initplan.

Suite locale: 197 test backend PASS, due browser opt-in esclusi; frontend typecheck/build PASS. Warning Starlette/httpx preesistente. Setup configure_database.py con input nascosto e login separati predisposto; verificato rifiuto non interattivo, provisioning NON eseguito. run_backend.py legge solo quattro impostazioni server da .env ignorato; check mostra booleani tutti false. Worker non configurato esce senza mostrare connessioni. Mancano DATABASE_URL, WORKER_DATABASE_URL, SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY nel runtime; il connettore gestisce SQL ma non fornisce la credenziale da usare nel processo Python. Non chiedere o pubblicare password in chat: usare setup nascosto con la connessione amministrativa del solo progetto dedicato, non salvata dal setup. Prova reale Python/TLS/Auth/API→DB→worker ancora da eseguire, distinta dai test SQL live e dai mock HTTP. Gate 2 resta aperto; seguono configurazione runtime e prova completa, ledger trasversale e Storage privato.
