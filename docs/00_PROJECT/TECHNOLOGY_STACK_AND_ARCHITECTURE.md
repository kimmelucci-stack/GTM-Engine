# GTM Engine — Stack tecnologico e architettura (decisione MVP)
**24 ottobre 2026 · Specifica architetturale chiusa per implementazione, subordinata ai gate di accesso ai provider.** La completezza della scelta architetturale **non certifica** API o integrazioni senza test.

## Decisioni definitive: componenti e responsabile sviluppo
| Componente | Scelta unica MVP | Perché | Owner/azione utente |
|---|---|---|---|
| **Sviluppatore frontend e backend** | **Codex su repository GitHub** | Un solo code owner, frontend React e backend Python coerenti, debug/test con browser | Collegare GitHub e aprire progetto in Codex sull'account Pro |
| Lovable | **NON nello stack iniziale** | Prototipazione visuale possibile, ma non serve secondo generatore né repository parallelo | Nessun account Lovable necessario |
| Web frontend | React + TypeScript + Vite → Vercel | UI modulare minimale, progress reali, tabelle ed evidenze espandibili | Vercel account/progetto |
| API backend | Python 3.12+ FastAPI + Pydantic su Render | Adapter, contratti e stati job | Render account/servizio |
| Worker | Processo Python persistente separato da API, polling job su Postgres | Long tasks, scraping, LLM, PowerPoint senza Celery/Redis | Render background worker (spesa autorizzata) |
| AI | OpenAI Responses API con Structured Outputs/tool calls: 1 agente per modulo | Structured decision + tool Python deterministic | OpenAI API key con budget autonomo da ChatGPT Pro |
| Database | Supabase Postgres | Persistenza progetti, run, job, evidenze e decisioni | Supabase account/progetto |
| Raw data e deliverable | Supabase Storage | JSON, eventuali evidenze visive, PPTX | bucket privato/gestione server |
| Knowledge Base | Markdown versionati in GitHub, loader Python per moduli | No vettori/RAG nella v1 | Fornire/approvare fonti e playbook |
| Siti concorrenti | `httpx`, `BeautifulSoup4`, `trafilatura`; Playwright solo dove indispensabile | Gate 1B PASS_WITH_LIMITATIONS: cinque siti e otto pagine con evidenze; rendering live non necessario, non collaudato | Conferma shortlist prima dell'approfondimento; eventuali script esistenti |
| Keyword/SERP/Trends/Google Reviews | **DataForSEO** | Gate 1A riprodotto il 25 ottobre; Trends limitato nel campione | Credenziali private configurate; pilota entro 5 USD |
| **Google Ads Transparency competitor** | **DataForSEO Ads Search/Ads Advertisers**, riprodotti nel repository al Gate 1A | NO acquisto SearchAPI per Google finché DataForSEO basta | nessun token aggiuntivo |
| **Meta Ads competitor IT/UE** | **Meta Ad Library API ufficiale `ads_archive`**; fallback SearchAPI, poi Apify | Il mercato IT rientra nel perimetro annunci EU; auth ufficiale necessaria | Facebook/Meta Developer, identità/autorizzazione/token se ottenibile; fallback solo previa approvazione |
| Instagram competitor (fino 50 post) | Graph Business Discovery, poi Apify | Ufficiale ove account business/permessi supportati | script/permessi Meta, poi Apify solo se richiesto |
| LinkedIn ads | SearchAPI solo se richiesto dall'ICP/strategia | Non imporre terzo provider per tutti | trial key opzionale |
| Dati imprese Italia | Openapi Company, account commerciale | P.IVA, ATECO, ricavi, dipendenti con anno | Openapi key e limite spesa |
| Studi e codifiche | ISTAT ATECO2025, Eurostat SDMX, OpenAlex; ESCO opzionale | Fonti autoritative e automatizzabili | niente chiave di norma; confermare policy/limiti |
| PPTX | `python-pptx`, main cover + section cover opzionali + 2 content template | Oggetti Office modificabili; deck dinamico | branding/logo se presente |
| Preview PPTX | LibreOffice headless sul worker + controlli visuali | Render per QA, NON output finalizzato a immagini | pacchetto LibreOffice/font nell'hosting |
| Test & CI | pytest + contract/golden tests, ruff, frontend typecheck/test + Playwright E2E | Gate misurabili | fornire casi pilota/validazioni |

## Topologia e flusso
```
Frontend (Vercel React TypeScript)
    │ HTTPS REST: Project Brief, Runs, Decisions, Evidence, Deck
    ▼
FastAPI (Render web service) ── writes/reads ──► Supabase Postgres
    │                                               │
    └─ enqueue persisted jobs ───────────────────────┘
                                                 ▲
Worker Python (Render background) ────────────────┘
    ├─ Adapter DataForSEO ↔ LIVE + TASK POST/GET
    ├─ Adapter Meta API ↔ authorized Graph endpoints
    ├─ Adapter Social ↔ Business Discovery / fallback Apify
    ├─ Adapter Company ↔ Openapi
    ├─ Public downloads ↔ ISTAT/Eurostat/ESCO/OpenAlex
    ├─ Controlled crawl ↔ HTTP then Playwright fallback
    ├─ OpenAI Responses + Markdown KB loader
    ├─ Pure Python scoring/validation/resource planning
    └─ python-pptx + optional headless preview ↔ Supabase Storage
```

## Schemi minimi / contratti di prodotto
- `projects(id, title, offer_brief, product_in_development, geo, locale, created_at)`.
- `runs(id, project_id, module_no, mode, status, cost_cap, started_at, completed_at)`.
- `jobs(id, run_id, task_type, state, attempt, heartbeat_at, error_code, created_at, updated_at)`.
- `observations(id, run_id, field, value_json, source_id, status, observed_at, geo_requested, geo_effective, period)`.
- `sources(id, provider, endpoint, source_url, query_json, raw_storage_ref, fetched_at, provider_status, cost_record)`.
- `decisions(id, run_id, decision_type, payload_json, approved, supersedes_id)`.
- `artifacts(id, run_id, kind, storage_ref, created_at)`.
- `cost_events(id, run_id, provider, endpoint, units, provider_price, currency, observed_or_estimated)`.
- `provider_checks(id, provider, capability, status, sample_ref, checked_at, limitations)`.

Elenco concettuale MVP. Al Gate 2 implementate projects/runs/jobs e cost_events nello schema interno gtm, con budgets necessario a raggruppare il tetto dell'intera esecuzione GTM fra i moduli. runs.budget_id collega i moduli allo stesso budget; FK composite impediscono eventi su progetti/budget incoerenti. Le altre tabelle restano da implementare. RLS attiva/forzata e nessun accesso client; gtm_api crea/legge progetti e budget del proprietario, gtm_worker gestisce job e costi senza modifica cap o cancellazione storico. Connessioni runtime Python/TLS verificate il 26 ottobre; worker catalog.validate e API su database reale con identità sintetica collaudati, dati rimossi. Login utente/browser e moduli analitici end-to-end restano da implementare/collaudare. Dettagli nell'handoff, migrazioni in supabase/migrations.

## Stato job e comportamento UI
`queued → running → completed | partial | failed | cancelled` con heartbeat, timeout e tentativi limitati. Frontend legge da API lo stato persistito; **mai indicare progresso finto**. Ogni modulo mostra nome italiano corto, risultato consultabile e approfondimenti nascosti di default.

## Pipeline per un modulo
Input/Brief validato → select related KB playbooks → provider adapters con cap/caching → normalize + raw/source → evidence QA → deterministic metrics → orchestrator agent → independent challenge QA → user approval → persist outputs → downstream module.
Ogni decisione agentica salva rationale e lista source IDs. Mod.07 utilizza solo risultati approvati, non riscrive la strategia.

## Provider selection: evitare costi duplicati
1. DataForSEO per Search/Maps/Reviews/**Google Ads Transparency**: prove Gate 1A nel repository, con campioni e limiti nell'audit; non estendere l'esito a tutti i mercati/query.
2. Meta official per Ads Library EU e IG Business Discovery **quando possibile**; i due flussi richiedono autorizzazioni differenti, non dedurre l'uno dall'altro.
3. SearchAPI soltanto Meta fallback o LinkedIn Ads pertinente. Apify solo in fallback Instagram/Meta. Non attivare tutti questi abbonamenti per default.
4. Openapi solo per Companies dopo confronto dei dati; null/Unavailable non diventano zeri.
5. Dati pubblici scaricabili senza chiavi per studi/ATECO se il caso lo consente.

## Gate architetturali e qualità
- **Costo per run completo:** obiettivo 10 USD, massimo 15 USD secondo vincolo del proprietario del 25 ottobre 2026. Budget e rendicontazione trasversali su provider, AI, generazione deck e costi di esecuzione attribuibili; distinguere quote di costi fissi da costi variabili senza ometterli dal modello economico. Validare sul pilota, non promettere sostenibilità prima delle misure. Gate 1A: autorizzati 5 USD totali; nessuna autorizzazione implicita per acquisti o canoni.
- Ogni adapter implementa `retrieve(query, geo, limit, cost_cap) → data + evidence + cost + status` e test con mock/cassette; non utilizzare scraper interattivi non riproducibili come unica fonte.
- Bounded calls: numero massimo, timeout, backoff, costo per run e messaggio di blocco quando il tetto è raggiunto.
- Geo: `requested_geo` vs `effective_geo`; mai aggregare città e regione senza metodo/statistica validata.
- Copertura: non accettare API 200 con campi null come dato completo (Google Trends campione 2/54 valori non null).
- Mod.02 scoring per azienda indipendente dalla shortlist, CCI4/CCI6 e stati Valid/Partial/Unavailable secondo `docs/02_MARKET_INTELLIGENCE/SCORING_MODEL.md` immutato.
- Prodotti in sviluppo: vietati UVP/messaging promozionali e claim non supportati; enforcement nel JSON validator, non solo nel prompt.
- Mod.06: Paid = media/inserzioni; software/fornitori separati; risorse sono persone, ore TOTALI/sett., competenze (SEO & Content Strategy congiunta); nessun role chart; gap outsourcing senza cambiare strategia per mancanza di skill.
- Mod.07: testo/grafici/tabelle PPTX nativi, no image-only slide; section covers condizionali, non fisse 7; 2 template content.
- QA: test provider reali e di qualità strategica con casi positivi/negativi; E2E di rete e servizi al Gate 8, non segnare prima di averli osservati.

## Escalation / ownership
**Codex** implementa e fa test con tool autorizzati. **Utente** ottiene credenziali/attiva billing, sceglie cap, valida dati e approva deployment. Codex non crea account, compra servizi o presume accessi, non inserisce segreti in repo o documenti. L'account ChatGPT Pro e i crediti OpenAI API sono distinti.

## Decisioni di non-scopo MVP
Niente Lovable nello sviluppo primario; niente n8n/Redis/Celery/RAG vettoriale; niente campagne realmente inviate; niente scraping obbligatorio di dati non pubblici; niente percentuale falsa di accessibilità provider.

## Fonti
- Codex AGENTS/Repo: https://learn.chatgpt.com/docs/agent-configuration/agents-md
- Lovable Git sync e import limitations: https://docs.lovable.dev/integrations/git-sync-overview
- DataForSEO Google Ads Advertisers: https://docs.dataforseo.com/v3/serp/google/ads_advertisers/live/advanced/
- DataForSEO Google Ads Search: https://docs.dataforseo.com/v3/serp/google/ads_search/live/advanced/
- Meta Ad Library EU coverage e accesso: https://www.facebook.com/ads/library/api/
- Render: https://render.com/docs/background-workers
- Supabase: https://supabase.com/docs/guides/database ; https://supabase.com/docs/guides/storage


## Avanzamento Foundation: loader KB e budget di run

Loader selettivo approved/version/hash implementato in knowledge.py, test sintetici; libreria reale e passaggio dei record a AnalysisRun/LLM non ancora collegati. RunBudget in domain/run_budget.py implementa prenotazione di massimali e riconciliazione USD cross-provider, obiettivo 10 e cap massimo 15 per run. Prenotazioni incerte restano impegnate e lo stesso evento non può autorizzare una seconda richiesta; consuntivi sopra massimale sono conservati e fermano nuove prenotazioni. Costi mancanti non sono zero: la conformità non è dimostrata finché dati, AI, esecuzione (inclusa generazione deck) e costi fissi attribuiti non sono misurati e riconciliati. Una componente realmente gratuita può avere zero osservato esplicito.

La classe di dominio resta pura/in memoria. Il repository PostgresBudget persiste eventi e stato sotto SELECT FOR UPDATE sulla riga del budget, con READ COMMITTED e lock timeout, prima di restituire la prenotazione al chiamante. Sette run di modulo condividono un budget; un nuovo oggetto/worker rilegge lo stesso stato, senza copie concorrenti indipendenti. execute_budgeted esegue la chiamata fuori dalla transazione soltanto dopo il commit, conserva esiti incerti e rende riconciliabili i costi osservati quando il database non risponde. Undici test reali, inclusa concorrenza, superati senza provider fatturabili. Confine implementato, adapter dei moduli ancora da collegare; non esposto come API pubblica e non autorizza nuove spese. Budget Gate 1A invariato; costi completi effettivi non ancora misurati.
