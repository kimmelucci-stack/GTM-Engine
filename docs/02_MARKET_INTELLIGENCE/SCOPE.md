# GTM Engine — Modulo 02: Market & Competitive Intelligence

**Versione:** 0.3 — Scope funzionale + Knowledge Base condivisa  
**Data:** 20 ottobre 2026  
**Stato:** scoping approvato nelle sue linee funzionali; PRD/TDD e verifiche tecniche non ancora completati  
**Documento collegato:** `SCORING_MODEL.md` (specifica matematica sperimentale)

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Prove provider storiche nell’audit del 24 ottobre; nessuna riprodotta nel repository attuale.

## 1. Scopo e confini

Analizzare il panorama competitivo del prodotto/servizio definito nel **Project Brief** del GTM Engine; identificare i concorrenti commercialmente rilevanti, studiarne offerta e comportamento, raccogliere evidenze da fonti verificabili e produrre dati strutturati, analytics, confronti e insight utilizzabili nel **GTM Strategy Deck**.

**Non è compito di questo modulo:** dichiarare una quota di mercato o il fatturato attribuibile al prodotto sulla base della sola presenza web; garantire il budget pubblicitario di terzi; scegliere in via definitiva i canali GTM (fase successiva).

**Input principali:** brief di progetto (prodotto, benefici, mercato, target, geografia), output del Modulo 01 (keyword non-branded, cluster, SERP, domini, intent, trend), eventuali preferenze dell'utente.

**Output principali:** fino a 8 profili competitor (5 selezionati dal sistema + massimo 3 aggiuntivi), matrici e scorecard, evidenze per analytics e blocco della presentazione finale.

## 2. Decisioni già approvate

1. **Cinque competitor identificati automaticamente** mediante ricerca multi-fonte; l'utente può sostituirli prima dell'analisi approfondita.
2. **Fino a tre competitor aggiuntivi** inserendo il sito web; numero finale 5–8, salvo candidati non verificabili segnalati esplicitamente.
3. **Scraping approfondito** delle pagine rilevanti di ciascun sito: prodotti, servizi, prezzi pubblicati, value proposition, CTA, case study, testimonianze, recensioni presenti sul sito e altri contenuti commerciali accessibili. Riutilizzo degli script Python esistenti dopo revisione.
4. **Instagram principale**, fino a 50 post accessibili per competitor tramite Meta Graph API / Business Discovery, previo test delle autorizzazioni; l'utente può fornire/correggere il link dell'account. **Facebook secondario**, quando l'accesso ai contenuti è tecnicamente disponibile. **TikTok escluso dalla prima versione.**
5. **Advertising Intelligence**: Google Ads Transparency via DataForSEO Ads Advertisers/Ads Search LIVE; Meta Ad Library API ufficiale prima opzione per annunci UE. Fallback automatici solo per gap dimostrati, con accesso verificato e costo approvato; altrimenti `partial/unavailable`, senza ricerca manuale obbligatoria.
6. **Review Intelligence**: recupero e analisi di tutte le recensioni effettivamente accessibili dalle fonti integrate, con Google Reviews/DataForSEO tra i candidati principali, e script Python dedicato da valutare. Numero recuperato e copertura dichiarati.
7. **Company Intelligence**: dati societari di base, fatturato e dipendenti/addetti, quando reperibili. Per l'Italia valutare fonti camerali ufficiali e fornitori API; per l'estero fonti nazionali pertinenti. Dati mancanti = non disponibili, non zero.
8. **Competitive Scoring**: sei score per azienda, ciascuno 0–100 e calcolato autonomamente; aggregazione opzionale tramite due indici *distinti*, CCI₆ e CCI₄, secondo allegato v1.1. I parametri dipendenti dal mercato devono essere fissati e versionati prima dell'esecuzione.
9. **Un Market Intelligence Agent** coordina la fase tramite orchestrazione Python; n8n escluso dall'MVP.
10. **Servizi a pagamento:** DataForSEO e API OpenAI ammessi. Altri servizi, anche a pagamento, possono essere proposti **solo dopo verifica di copertura, utilità e costi**, senza acquisti o integrazioni assunti automaticamente.
11. I dati originali, normalizzati e derivati restano distinti; tutte le metriche e le analisi devono essere tracciabili fino alla fonte.

## 3. Workflow dell'agente

| Passo | Operazione | Output | Controllo |
|---|---|---|---|
| 01 — Discover | Incrocio dei domini del Modulo 01 con ricerca settoriale, Google SERP/Maps e alternative allo stesso bisogno | Lista candidati, link e motivazioni | Verifica commerciale, geografica e dell'offerta |
| 02 — Screen & Rank | Verifica essenziale delle pagine di offerta, deduplica delle aziende, Competitive Fit e Organic Visibility distinti | **5 competitor proposti** e alternative | Distinguere operatori commerciali da directory/editori |
| 03 — Human Review | Visualizzazione proposte e fonti | 5 confermati/sostituiti + fino a 3 URL manuali | Conferma utente prima delle estrazioni approfondite |
| 04 — Resolve Entities | Collegamento brand, dominio, ragione sociale, account Instagram/Facebook e advertiser | Identità competitor verificata o incerta | Richiedere conferma in caso di ambiguità |
| 05 — Collect | Sito, social, ads, recensioni, fonti societarie, posizionamento SEO | Raw datasets e metadati | Controlli di qualità, disponibilità e fonti |
| 06 — Analyze | Clustering, pattern temporali, offerta, sentiment, metriche e scoring Python | Sei dimensioni, indicatori, temi ricorrenti | Dato osservato distinto da interpretazione AI |
| 07 — Synthesize | Interpretazione dei punti di forza/debolezza e opportunità | Profili, confronti, insight e output per deck | Evidenze verificabili; limiti espliciti |

L'**AI Agent** decide approfondimenti consentiti, coordina strumenti e interpreta risultati. **Python** esegue estrazioni, pulizia, deduplica, calcoli e controlli. Nessun punteggio quantitativo viene calcolato liberamente dal modello linguistico.

## 4. Competitor Discovery: metodologia

### 4.1 Fonti e percorso operativo

- **Search competitors:** domini commerciali da SERP e keyword rilevanti del Modulo 01, mantenendo separati portali, media, directory e fornitori veri e propri.
- **Market competitors:** interrogazioni settoriali prodotte dall'agente a partire da categorie di offerta, sinonimi, target, territorio e intent; dati SERP/Google Maps/Business Listings quando accessibili.
- **Alternative competitors:** categorie di soluzioni sostitutive al bisogno, da validare tramite analisi delle pagine di offerta.

Per ogni candidato conservare query/fonte, URL, categoria di offerta, territorio e motivazione del collegamento al mercato. Eliminare duplicati di dominio, marchi e persona giuridica senza fondere soggetti diversi.

### 4.2 Valutazione e scelta dei cinque

La selezione utilizza **due assi separati**:

- **Competitive Fit:** sovrapposizione dell'offerta, del target, della geografia e sostituibilità commerciale.
- **Organic Visibility:** presenza organica sulle keyword *non-branded* pertinenti, distinta da fatturato e successo commerciale.

Il sistema tiene conto anche della **rappresentatività** di modelli di offerta diversi: non basta scegliere i primi cinque domini per ranking SEO. I pesi del Competitive Fit e la regola di selezione dei cinque sono da precisare nel PRD/TDD e collaudare sul pilota; nessun valore va spacciato per validato.

Il **Search Opportunity Gap** è un output analitico distinto: identifica domanda pertinente potenzialmente contendibile e non decide da solo chi sia un competitor.

### 4.3 Selezione UI

La schermata presenta cinque candidati con: nome, sito, tipologia, motivazione, fonti, fit e visibilità osservata. L'utente può **sostituire** un candidato ed **aggiungere fino a 3 competitor** tramite URL; può correggere il profilo Instagram di ciascuno. Prima dell'avvio del crawling approfondito il sistema controlla URL, duplicati e corrispondenza fra brand e sito.

## 5. Website Intelligence

**Raccolta:** homepage, pagine prodotto/servizio, pricing, landing commerciali, settori, case study, testimonianze, about e altre pagine pertinenti. Un crawler Python identifica e ordina le pagine per rilevanza; evita scansioni illimitate; adotta limiti tecnici, gestione errori e rispetto delle condizioni applicabili ai siti.

**Dati:** offerte e pacchetti, prezzi pubblicati, segmenti dichiarati, USP, claim, prove sociali, CTA, funnel/landing osservabili, eventuali loghi clienti, link social e dati per identificare la società.

**Analisi:** raggruppamento per prodotto/servizio, benefici dichiarati, target, pricing e modelli di vendita. Ogni affermazione rilevante conserva URL, snippet, data e classificazione `observed`/`inferred`.

**Script esistenti:** l'utente possiede crawler Python; prima di riscriverli, ispezionarne dipendenze, limiti, modalità di accesso ed estrazione.

## 6. Social Intelligence

**Canale principale:** Instagram, fino a **50 post accessibili per competitor**. Riutilizzare il metodo Meta Graph / Business Discovery già sperimentato dall'utente sui progetti precedenti, **dopo aver ricevuto e verificato gli script e le autorizzazioni correnti**.

**Dati quando disponibili:** data, URL/ID, caption, formato, like, commenti, follower osservati, media accessibili. Il link IG è recuperato dal sito ufficiale o inserito/corretto dall'utente. **Facebook** aggiunto solo se esiste una via tecnica legittima per recuperare i contenuti richiesti; indisponibilità dichiarata. Nessuna promessa su reach/impressions private dei competitor.

**Analisi:** frequenza, content pillars, promozioni, benefici e CTA, creatività ricorrenti, pattern editoriali, variazioni temporali, interazioni osservate per formato e potenziali cambiamenti di posizionamento. La classificazione dei visual può integrare le caption quando i media sono effettivamente disponibili.

**Qualità:** 50 è un tetto, non un numero garantito; dichiarare post recuperati, periodo coperto, campi assenti e limiti nella confrontabilità tra account.

## 7. Advertising Intelligence

**Fonti approvate:** DataForSEO Ads Advertisers e Ads Search LIVE per Google Ads Transparency; Meta ufficiale `GET /ads_archive` come prima opzione UE. Le prove DataForSEO del precedente ambiente sono nell'audit e vanno riprodotte al Gate 1A. Meta richiede Gate 1C con autorizzazioni proprie, distinte da Instagram. SearchAPI/Apify per Meta e SearchAPI/SerpApi per gap Google solo dopo necessità dimostrata e approvazione; nessun acquisto duplicato. Fonte non accessibile: `partial/unavailable`, senza raccolta manuale obbligatoria.

**Dati quando disponibili:** inserzionista, ID pagina/advertiser, annuncio, testo, formato, creatività, prodotto/servizio, landing page, date e piattaforme osservate, attributi UE/SEE disponibili nel dataset. L'identità inserzionista–competitor va verificata.

**Analytics:** annunci osservati e deduplicati, ricorrenza creativa, distribuzione per tema e CTA, durata e continuità **solo quando ricostruibili dai dati**, confronto messaggi paid/organici, variazioni nel periodo e opportunità di differenziazione.

**Spesa stimata:** indicatore **separato** da Advertising Activity. Mostrare un importo/intervallo soltanto in presenza di dati adatti (es. impression stimate e benchmark CPM giustificabili, con frequenza dove necessaria), ipotesi e incertezza. **Numero di annunci ≠ budget, ROAS o conversioni.** Se non sostenibile, segnare `not_estimable`.

## 8. Review Intelligence

**Raccolta:** tutte le recensioni effettivamente accessibili dalle fonti selezionate, con particolare attenzione a Google Reviews tramite DataForSEO; altre piattaforme solo quando pertinenti e accessibili. È previsto uno **script Python dedicato**; esaminare prima quelli già scritti dall'utente.

**Dati:** fonte, identificativo del punto/attività, timestamp, rating, testo, risposta aziendale ove disponibile, URL/riferimento e campi relativi al totale dichiarato dal provider.

**Analytics:** distribuzione 1–5 stelle, punteggio medio, sentiment, topic, aspetti apprezzati, criticità ricorrenti, evoluzione nel tempo e confronti su metriche omogenee. Evitare di attribuire al marchio recensioni di un'attività omonima o di una sede non pertinente.

**Limite tecnico:** per Google Reviews, l'endpoint DataForSEO precedentemente identificato è **Standard POST/GET**, non Live; numero massimo e paginazione devono essere confermati durante il test tecnico. L'interfaccia mostra progresso/stato e risultati non appena disponibili; non può promettere immediatezza API impossibile. **Tutte le recensioni accessibili non significa tutte quelle esistenti.**

## 9. Company Intelligence

**Campi:** denominazione, P. IVA/identificativo, ATECO/settore, sede, anno costituzione, fatturato con esercizio, dipendenti/addetti con definizione e riferimento temporale, eventuali altri bilanci disponibili.

**Fonte approvata Italia:** Openapi Company, con token, limite economico e match da verificare al Gate 1D. La scelta del provider non autorizza una sottoscrizione o spesa. Bilancio ufficiale per confronto del campione; per l'estero fonti nazionali pertinenti, senza assumere copertura Openapi universale.

**Identità:** associare correttamente dominio, brand e persona giuridica; il fatturato della società non equivale automaticamente al fatturato dello specifico prodotto/servizio analizzato. Se non verificabile, richiedere conferma o mostrare `unavailable`.

## 10. Scoring e Competitive Landscape

**Specifica di riferimento:** `SCORING_MODEL.md` (allegato, NON validato empiricamente).

Sei dimensioni calcolate **separatamente** da funzioni Python e configurazioni congelate:

1. Market Positioning
2. Organic Visibility
3. Social Performance
4. Advertising Activity
5. Customer Satisfaction
6. Company Scale

Ogni score valido appartiene a `[0,100]`. L'indice complessivo non è un giudizio libero dell'AI:

- **CCI₆:** sei dimensioni, tutte richieste disponibili secondo le regole del modello.
- **CCI₄:** indice Core separato su Positioning, SEO, Reviews e Scale.

I due indici **non sono intercambiabili**; non si ricalcolano automaticamente i pesi in funzione degli altri competitor. Aggiungere un competitor non modifica gli score esistenti, a parametri e dataset invariati. Gli stati `Valid`, `Partial`, `Unavailable` e le coperture vanno esplicitati.

**Limite:** formule presenti e test numerici simulati, ma coefficienti, rubriche e soglie restano sperimentali. Il pilota reale è necessario prima di dichiarare attendibile il modello come strumento decisionale.

## 11. Dati e output attesi

**Entità concettuali** (schema definitivo da progettare nel TDD):

- `CompetitorCandidate` (fonte discovery, evidenza, ragione selezione)
- `CompetitorIdentity` (brand, dominio, società, Instagram/Facebook, advertiser ID, verifica associazioni)
- `WebsitePage` / `WebsiteClaim`
- `SocialPost` / `SocialPattern`
- `AdObservation` / `CreativeCluster`
- `Review` / `ReviewTopic`
- `CompanyRecord` / `FinancialMetric`
- `KeywordVisibility` / `OrganicVisibilityMetric`
- `DimensionScore` / `CompositeIndex` / `ModelVersion`
- `Evidence` / `AnalysisRun` / `RawApiResponse` / `Insight`

**Output di fase:**

1. Profili dettagliati per ciascun competitor.
2. Tabella e dashboard di confronto per offerta, SEO, social, advertising, recensioni, dimensione aziendale.
3. Ricorrenze, pattern, trend, cambiamenti e gap osservati/inferiti con evidenze.
4. Scorecard con sei dimensioni e indici CCI₄/CCI₆ soltanto quando calcolabili.
5. Dataset esportabili e sezioni di grafici/testi per il **deck GTM finale**.

**Regola:** preservare dati raw, normalizzati e derivati separatamente e versionarli; valori relativi, stime, giudizi AI e misure osservate non devono essere mescolati.

## 12. Requisiti UX

- Schermata di selezione: 5 proposte modificabili, motivazioni e fonti, fino a 3 URL aggiuntivi, link IG opzionali/modificabili.
- Stato di avanzamento per singolo competitor e sorgente, anche con richieste esterne asincrone inevitabili.
- Schede fonte-dati con disponibilità, timestamp e limiti; dati parziali chiaramente distinguibili.
- Dashboard con metriche originali, trend, cluster, score e loro qualità; possibilità di ispezionare le evidenze.
- Input prodotto/target/geografia **ereditati dal Project Brief**, non duplicati inutilmente nel modulo.

## 13. Architettura approvata, implementazione da collaudare

- **Agent:** un solo orchestratore Market Intelligence con tool calling e output strutturati.
- **Worker Python Render:** discovery, scraper, adapter Meta/Ads/Reviews/Company, trasformazioni e scoring; niente n8n nell'MVP.
- **API applicativa:** FastAPI/Pydantic su Render.
- **Data layer:** Supabase Postgres e Storage privato, raw/versioni e normalizzati separati.
- **UI:** React; hosting frontend Vercel già scelto.
- **Deployment di job lunghi:** worker Python separato su Render, polling job su Postgres; implementazione al Gate 2.
- **Sviluppo:** Codex desktop, PyCharm e GitHub; riutilizzare gli script esistenti previa revisione.

La preferenza per chiamate **LIVE** resta in vigore ove l'endpoint la supporti. I limiti effettivi vanno verificati per ogni API; il sistema non deve dichiarare LIVE un flusso Standard/asincrono.

## 14. Criteri di accettazione e test pilota

Il modulo potrà essere considerato **funzionante** quando un caso pilota dimostrerà:

1. Scoperta di candidati da almeno due percorsi distinti, con evidenze e selezione motivata di cinque competitor.
2. Sostituzione di un candidato e inserimento fino a tre URL da UI senza modificare il codice.
3. Risoluzione dell'identità e segnalazione di ambiguità brand/dominio/società/social.
4. Scansione di pagine commerciali pertinenti e recupero di campi osservabili con URL e timestamp.
5. Recupero dei post Instagram permessi dalle autorizzazioni reali e gestione corretta dei campi mancanti.
6. Acquisizione automatica annunci mediante connettore verificato; fallback solo se approvato e collaudato, altrimenti `partial/unavailable` con causa e copertura.
7. Raccolta di recensioni tramite integrazione reale; copertura e limiti documentati.
8. Recupero di dati societari quando disponibili; corretta distinzione dei dati mancanti.
9. Calcolo Python delle sei dimensioni, CCI₄/CCI₆ solo quando validi e superamento dei test matematici della v1.1.
10. Report e visualizzazioni ricostruibili dai dataset; insight collegati alle evidenze; output utilizzabile dal deck.

**La validazione matematica e quella strategico-empirica dello scoring sono due verifiche differenti.** I test automatici non bastano per garantire che l'indice misuri la competitività reale. Il modello v1.1 resta congelato; eventuali calibrazioni richiedono nuova versione e approvazione.

## 15. Questioni operative ancora aperte (non nuove funzionalità)

- Specifiche dettagliate delle query di market discovery, soglie di screening, diversificazione dei cinque e policy di sostituzione.
- Verifica degli script Python dell'utente: crawler siti, Google Reviews, Meta Graph.
- Autorizzazioni e dati realmente ottenibili per Instagram Business Discovery, Facebook, Meta Ads Library e Google Ads Transparency; gestione dei casi non accessibili.
- Collaudo Openapi Company per Italia; verifica delle fonti pertinenti per l'estero, senza assumere accessi o costi.
- Implementazione finale e calibrazione dello scoring v1.1, inclusi parametri e soglie di qualità; prova dati reali prima dell'approvazione come indice affidabile.
- Limiti del crawling, politiche di refresh, job orchestration e persistenza; analisi comparativa dei costi dei servizi a pagamento.
- Definizione dei grafici finali e dei layout del blocco deck di questo modulo.

---

**Decisione di scoping:** il **Modulo 02 è definito a livello funzionale** e può passare al PRD e successivamente all'implementazione pilota. **Non** sono ancora verificati accessi API, scraping, disponibilità dati o validità empirica degli score. Nessuna funzionalità esterna non testata va presentata come già operativa.


## 16. Aggiornamento trasversale 24 ottobre 2026 — modalità e UX

- Il Modulo 02 resta utilizzabile anche se il prodotto/servizio è ancora in sviluppo: competitor diretti e sostitutivi vengono ricercati rispetto alla **categoria/idea e al bisogno**, non a capacità inesistenti.
- In modalità prodotto in sviluppo, nessuna affermazione sui presunti vantaggi dell'offerta o sui suoi claim viene dedotta dai punteggi competitivi.
- Workflow visibile: **Concorrenti → Selezione → Offerte → Marketing → Reputazione e dati → Confronto**. Le lavorazioni tecniche, richieste API e i log sono consultabili solo nelle viste di dettaglio.
- Il punto di approvazione della selezione di 5 competitor (con fino a 3 aggiunte manuali) deve essere evidente. Stato reale e fonti ispezionabili, senza sovraccarico testuale o progressi inventati.
- Il competitive scoring `SCORING_MODEL.md` resta **v1.1 sperimentale**: non ricalibrarlo tacitamente e non confondere un CCI alto con una superiorità dimostrata in acquisto o positioning.

Questi vincoli non alterano il perimetro di scraping, social, ads, reviews o company intelligence definito sopra.


## 17. Knowledge Base condivisa — decisione trasversale

Il Market Intelligence Agent accede via Python ai playbook verificati su competitor discovery, interpretazione di SEO/social/ads, review intelligence e limiti delle comparazioni. I playbook sono **metodologia**, non osservazioni sostitutive di crawling/API: uno score o un'affermazione sull'azienda richiede dati ed evidenze del progetto.

Archivio ufficiale: GitHub/Markdown; caricamento selettivo; nessun RAG vettoriale per il primo rilascio. Il modello di scoring resta v1.1 sperimentale **senza modifiche**. Riferimento: `docs/00_PROJECT/KNOWLEDGE_BASE.md`.
