# Istruzioni operative Codex — GTM Engine

## Missione e fonti autorevoli
Sviluppare frontend e backend della piattaforma GTM a sette moduli già progettata, con risultati tracciabili e PowerPoint nativo modificabile. Non riprogettare lo scope. Questo file governa Codex, non gli agenti AI del prodotto.

Leggere nell'ordine: `docs/README.md`, `docs/00_PROJECT/PROJECT_SCOPE.md`, `docs/00_PROJECT/PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md`, `docs/00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md`, `docs/00_PROJECT/DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md`, `docs/00_PROJECT/DATA_ACCESS_AUDIT_2026-10-24.md`, `docs/00_PROJECT/KNOWLEDGE_BASE.md`; quindi gli `SCOPE.md` canonici dei Moduli 01–07 elencati in `docs/README.md`, `docs/02_MARKET_INTELLIGENCE/SCORING_MODEL.md` e `docs/00_PROJECT/EVOLUTION_BACKLOG.md`.

Le istruzioni esplicite del proprietario prevalgono. Stack e provider: architettura e matrice canoniche; comportamento: gli `SCOPE.md`; formule: scoring v1.1 invariato. Audit: registro prove del precedente ambiente e archivio storico esplicitamente superato, non fonte di scelte correnti. Segnalare nuovi conflitti prima di modificare requisiti approvati. L'handoff registra il consolidamento; le copie compatibili dei Moduli 06–07 rimandano ai soli `SCOPE.md` canonici.

## Architettura e convenzioni
- React/TypeScript/Vite in `frontend/` → Vercel; Python 3.12+, FastAPI/Pydantic in `backend/` → Render API e processo worker separato; Supabase PostgreSQL/Storage privato. Niente Lovable.
- Separare `agents` (orchestrazione per modulo), `providers` (API/crawler), `domain` (normalizzazione/calcoli deterministici), `persistence` (DB/storage), API e frontend. Creare componenti quando necessari al gate, senza servizi speculativi.
- OpenAI Responses con output strutturati; un agente per modulo. KB Markdown selettiva e versionata; niente RAG vettoriale, embeddings o File Search nell'MVP.
- Worker futuro: job persistiti su Postgres, stati/heartbeat/timeout/retry limitati. Non simulare persistenza o connessioni. No n8n, Redis, Celery o nuovi servizi senza necessità documentata e approvazione.
- Python tipizzato, Pydantic ai confini, funzioni pure per scoring e pianificazione; TypeScript strict. Testi UI in italiano semplice, pochi campi, dettagli espandibili, stati reali.
- UX/UI: riferimento prioritario all'app Attio, verificato sulle fonti ufficiali; Inter variabile caricato localmente con licenza OFL. Interfaccia operativa compatta e neutra, non landing page o questionario. **Mai frecce nelle CTA**, né caratteri né icone decorative/direzionali nei pulsanti o link d'azione. Non reintrodurle nei redesign. Nessun logo/font proprietario copiato; layout e identità del prodotto restano originali.

## Regole di prodotto bloccanti
- Mai inventare metriche, performance, prezzi o prove. Distinguere osservato, derivato e ipotesi; dato mancante diverso da zero.
- Supportare B2B e B2C senza stereotipi. In sviluppo: nessuna UVP, claim, positioning promozionale o messaging in API, UI e deck; imporre il vincolo nei validator oltre che nei prompt.
- Modulo 02: scoring v1.1 invariato, parametri versionati, CCI4/CCI6 distinti, Valid/Partial/Unavailable; nessuna rinormalizzazione dei pesi per dati mancanti.
- Buyer B2B: output principale = buying committee di **job title per ogni reparto**, inclusi responsabili, coordinatori, specialisti, referenti e assistenti con possibile influenza anche minima. Catalogo canonico `backend/src/gtm_engine/domain/buyer_job_titles.v1.json`, vista `docs/03_UVP_ICP_INTELLIGENCE/BUYER_JOB_TITLE_DIRECTORY.md`. Reparti e funzioni sono attributi di supporto, MAI sostituti dei job title. Ruolo di acquisto e autorità richiedono contesto/evidenze, non sono dedotti dal titolo. Strategia di approccio eventuale = punto di ingresso, sequenza e prove; nessun invio automatico. Le precedenti directory funzioni/governance sono supporto storico, non contratto principale del buyer mapping. Organi collettivi separati, ESCO non necessario, ruoli B2C e competenze esecutive invariati.
- Modulo 06: Paid solo media; software e outsourcing separati; persone, ore TOTALI settimanali e competenze senza organigramma. Le skill identificano gap, non impoveriscono la strategia.
- Modulo 07: snapshot approvati, main cover, section cover opzionali, due famiglie contenuto; testi/tabelle/grafici nativi con python-pptx. Render e verifica visiva obbligatori quando si implementa il deck.
- Nessun invio automatico di campagne nell'MVP. Modifiche sostanziali a brief/UVP/modalità segnalano output obsoleti, senza riesecuzioni silenziose.

## Evidenze, accessi e costi
- Separare raw, normalizzato e derivato. Ogni risultato significativo porta fonte/endpoint, query, timestamp UTC, geografia richiesta/effettiva, periodo, raw reference, stato e limiti; derivazioni includono metodo/versione. Registrare playbook effettivamente usati.
- Riprodurre gli accessi nel runtime corrente prima di dichiararli tested: T/T_LIMITED storici non sono test locali. HTTP 200 o status 20000 non bastano: controllare campi, copertura, campione e pertinenza.
- DataForSEO primario anche Google Ads Transparency; Meta ufficiale prima per Ads UE e Business Discovery, con permessi separati. Fallback solo dopo gap dimostrato e approvazione; niente acquisti duplicati.
- Chiamate limitate da timeout, numero massimo, budget confermato, cache e backoff. Per task fatturabili non ripetere automaticamente POST dall'esito incerto; riconciliare il task. Su errore/limite/costo esporre partial/unavailable e causa, senza dati sintetici sostitutivi.
- Credenziali solo secret o variabili d'ambiente server-side; `.env.example` contiene solo nomi/valori vuoti. Mai secret nel frontend, Git, fixture, log o documenti. Redigere fixture e metadati prima del versionamento.
- Repository pubblica per portfolio su istruzione del proprietario: solo codice, documentazione e campioni sintetici o pubblici già verificati; nessun dato cliente o raw privato in Git, inclusa la cronologia. Controllare l'intera cronologia prima di cambiare visibilità. La pubblicazione del codice non autorizza deploy, spese o pubblicazione di dati.
- Mai stampare valori delle credenziali o elencare l'ambiente. Autenticazione Git tramite credential manager, mai token nell'URL. Prima di ogni commit eseguire `scripts/check_secrets.py`; attivare gli hook con `git config core.hooksPath .githooks`. Il controllo è euristico e non sostituisce la revisione. Errori futuri di provider devono essere redatti prima di log/API/UI.

## Esecuzione, test e consegna
- Controllare stato Git e istruzioni locali prima di modificare; preservare lavoro esistente. Un gate alla volta secondo roadmap; non passare al successivo senza richiesta.
- Eseguire pytest/ruff, typecheck/build frontend e test pertinenti; test negativi per dati assenti, errori/costi e modalità prodotto. Mock separati da prove live; test provider live opt-in, mai in CI ordinaria.
- Per ogni gate registrare comando, data, versione, input, provider/endpoint, esito, campione/copertura, costo, fixture e limiti; usare N/A motivato dove non pertinente. Non segnare PASS se manca una condizione richiesta.
- Aggiornare handoff/stato con risultati osservati, task successivo e blocchi; non usare percentuali arbitrarie. Aggiornare README per cambi operativi, senza duplicare gli scope.
- Richiedere intervento solo per credenziali/account, cap economici, ambiguo match societario o decisioni business/approvazioni previste. Richiedere approvazione per nuovi servizi/spese, cambi sostanziali alle decisioni, pubblicazione/deploy e rilascio. Proseguire autonomamente sulle attività locali autorizzate e indipendenti.
