# Istruzioni operative Codex — GTM Engine

## Missione e fonti autorevoli
Sviluppare frontend e backend della piattaforma GTM a sette moduli già progettata, con risultati tracciabili e PowerPoint nativo modificabile. Non riprogettare lo scope. Questo file governa Codex, non gli agenti AI del prodotto.

Leggere nell'ordine: `docs/README.md`, poi in `docs/00_PROJECT/` `PROJECT_SCOPE.md`, `PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md`, `TECHNOLOGY_STACK_AND_ARCHITECTURE.md`, `DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md`, `DATA_ACCESS_AUDIT_2026-10-24.md`, `KNOWLEDGE_BASE.md`; quindi gli `SCOPE.md` dei Moduli 01–07, `docs/02_MARKET_INTELLIGENCE/SCORING_MODEL.md` e `docs/00_PROJECT/EVOLUTION_BACKLOG.md`.

Le istruzioni esplicite del proprietario prevalgono. Per stack/provider usare le decisioni definitive di architettura e matrice e l'aggiornamento iniziale dell'audit; per comportamento funzionale gli scope aggiornati; per formule esclusivamente scoring v1.1. Segnalare conflitti sostanziali prima di modificare documenti approvati; non risolverli riscrivendo tacitamente requisiti. I duplicati storici sono registrati in `docs/00_PROJECT/HANDOFF_TO_CODEX.md`.

## Architettura e convenzioni
- React/TypeScript/Vite in `frontend/` → Vercel; Python 3.12+, FastAPI/Pydantic in `backend/` → Render API e processo worker separato; Supabase PostgreSQL/Storage privato. Niente Lovable.
- Separare `agents` (orchestrazione per modulo), `providers` (API/crawler), `domain` (normalizzazione/calcoli deterministici), `persistence` (DB/storage), API e frontend. Creare componenti quando necessari al gate, senza servizi speculativi.
- OpenAI Responses con output strutturati; un agente per modulo. KB Markdown selettiva e versionata; niente RAG vettoriale, embeddings o File Search nell'MVP.
- Worker futuro: job persistiti su Postgres, stati/heartbeat/timeout/retry limitati. Non simulare persistenza o connessioni. No n8n, Redis, Celery o nuovi servizi senza necessità documentata e approvazione.
- Python tipizzato, Pydantic ai confini, funzioni pure per scoring e pianificazione; TypeScript strict. Testi UI in italiano semplice, pochi campi, dettagli espandibili, stati reali.

## Regole di prodotto bloccanti
- Mai inventare metriche, performance, prezzi o prove. Distinguere osservato, derivato e ipotesi; dato mancante diverso da zero.
- Supportare B2B e B2C senza stereotipi. In sviluppo: nessuna UVP, claim, positioning promozionale o messaging in API, UI e deck; imporre il vincolo nei validator oltre che nei prompt.
- Modulo 02: scoring v1.1 invariato, parametri versionati, CCI4/CCI6 distinti, Valid/Partial/Unavailable; nessuna rinormalizzazione dei pesi per dati mancanti.
- Modulo 06: Paid solo media; software e outsourcing separati; persone, ore TOTALI settimanali e competenze senza organigramma. Le skill identificano gap, non impoveriscono la strategia.
- Modulo 07: snapshot approvati, main cover, section cover opzionali, due famiglie contenuto; testi/tabelle/grafici nativi con python-pptx. Render e verifica visiva obbligatori quando si implementa il deck.
- Nessun invio automatico di campagne nell'MVP. Modifiche sostanziali a brief/UVP/modalità segnalano output obsoleti, senza riesecuzioni silenziose.

## Evidenze, accessi e costi
- Separare raw, normalizzato e derivato. Ogni risultato significativo porta fonte/endpoint, query, timestamp UTC, geografia richiesta/effettiva, periodo, raw reference, stato e limiti; derivazioni includono metodo/versione. Registrare playbook effettivamente usati.
- Riprodurre gli accessi nel runtime corrente prima di dichiararli tested: T/T_LIMITED storici non sono test locali. HTTP 200 o status 20000 non bastano: controllare campi, copertura, campione e pertinenza.
- DataForSEO primario anche Google Ads Transparency; Meta ufficiale prima per Ads UE e Business Discovery, con permessi separati. Fallback solo dopo gap dimostrato e approvazione; niente acquisti duplicati.
- Chiamate limitate da timeout, numero massimo, budget confermato, cache e backoff. Per task fatturabili non ripetere automaticamente POST dall'esito incerto; riconciliare il task. Su errore/limite/costo esporre partial/unavailable e causa, senza dati sintetici sostitutivi.
- Credenziali solo secret o variabili d'ambiente server-side; `.env.example` contiene solo nomi/valori vuoti. Mai secret nel frontend, Git, fixture, log o documenti. Redigere fixture e metadati prima del versionamento.
- Mai stampare valori delle credenziali o elencare l'ambiente. Autenticazione Git tramite credential manager, mai token nell'URL. Prima di ogni commit eseguire `scripts/check_secrets.py`; attivare gli hook con `git config core.hooksPath .githooks`. Il controllo è euristico e non sostituisce la revisione. Errori futuri di provider devono essere redatti prima di log/API/UI.

## Esecuzione, test e consegna
- Controllare stato Git e istruzioni locali prima di modificare; preservare lavoro esistente. Un gate alla volta secondo roadmap; non passare al successivo senza richiesta.
- Eseguire pytest/ruff, typecheck/build frontend e test pertinenti; test negativi per dati assenti, errori/costi e modalità prodotto. Mock separati da prove live; test provider live opt-in, mai in CI ordinaria.
- Per ogni gate registrare comando, data, versione, input, provider/endpoint, esito, campione/copertura, costo, fixture e limiti; usare N/A motivato dove non pertinente. Non segnare PASS se manca una condizione richiesta.
- Aggiornare handoff/stato con risultati osservati, task successivo e blocchi; non usare percentuali arbitrarie. Aggiornare README per cambi operativi, senza duplicare gli scope.
- Richiedere intervento solo per credenziali/account, cap economici, ambiguo match societario o decisioni business/approvazioni previste. Richiedere approvazione per nuovi servizi/spese, cambi sostanziali alle decisioni, pubblicazione/deploy e rilascio. Proseguire autonomamente sulle attività locali autorizzate e indipendenti.
