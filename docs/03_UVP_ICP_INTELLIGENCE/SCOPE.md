# GTM Engine — Modulo 03: UVP & ICP Intelligence

**Versione:** 0.4 — Scope funzionale + Knowledge Base condivisa  
**Data:** 24 ottobre 2026  
**Stato:** scoping funzionale consolidato; UX/form UVP da rifinire, PRD/TDD e validazione empirica da realizzare  
**Dipendenze:** `docs/00_PROJECT/PROJECT_SCOPE.md`, `docs/01_DEMAND_INTELLIGENCE/SCOPE.md`, `docs/02_MARKET_INTELLIGENCE/SCOPE.md`.

## 1. Obiettivo e perimetro

Individuare e raccomandare **profili di clienti ideali (ICP) B2B o B2C**, collegando la UVP quando disponibile, i bisogni, le evidenze di domanda, i comportamenti commerciali e le caratteristiche organizzative o familiari. Il modulo deve produrre una **raccomandazione da Marketing Strategist**, argomentata e verificabile, non una buyer persona narrativa inventata dal modello.

Per prodotti disponibili il modulo comprende **00 — UVP** con formulario e chat AI; per prodotti in sviluppo lo step UVP **non viene eseguito né mostrato** e l'agente parte dall'idea, dal bisogno, dal Project Brief e dalle evidenze dei Moduli 01–02.

**Confini espliciti**:
- **Non** genera liste di aziende, lead o contatti individuali; non esporta database di prospect.
- **Non** necessita di LinkedIn Sales Navigator né ne presume accesso.
- Non sovrappone la ricerca di ICP alla definizione del positioning e dei messaggi definitivi del **Modulo 04 — Value Proposition & Positioning**. La UVP formulata qui è una **Working UVP**, rivedibile alla luce dei segmenti.
- Nessun segmento viene presentato come mercato validato soltanto perché il problema generale è documentato.
- Un singolo case study non rappresenta automaticamente l'intero segmento; il volume di ricerca non equivale al numero di imprese intenzionate ad acquistare.

**Output principale:** un ICP prioritario, con possibilità di aggiungere fino a **due ulteriori ICP** distinti mediante pulsante `+` (massimo **3 profili complessivi**). È legittimo produrne uno solo, oppure nessuno se non esistono evidenze adeguate.

## 2. Decisioni funzionali consolidate

1. Nome ufficiale: **Modulo 03 — UVP & ICP Intelligence**; agente: **UVP & ICP Intelligence Agent**.
2. Sequenza interna: **00 UVP [solo offerta disponibile] → 01 DISCOVER → 02 RESEARCH → 03 VALIDATE → 04 CLASSIFY → 05 MAP BUYERS → 06 SYNTHESIZE**. Nessuna fase STP aggiuntiva: la terminologia STP non modifica il workflow.
3. **00 UVP** *(solo se offerta disponibile)*: l'utente compila campi guidati e interagisce con una **chat contestuale**; l'agente formula, critica e affina una Working UVP. L'utente approva le modifiche proposte.
4. **DISCOVER:** produce inizialmente **4–6 ipotesi di segmenti**. Non produce direttamente ICP definitivi.
5. **RESEARCH:** ricerca le evidenze pertinenti, prioritariamente riutilizzando i Moduli 01–02. Utilizza **al massimo un ciclo di approfondimento aggiuntivo** per lacune davvero decisive; nessuna ricerca illimitata.
6. **VALIDATE:** distingue obbligatoriamente **Problem Evidence**, **Solution/Purchase Evidence** e **Commercial/UVP Fit**. Esiti: `ADVANCE`, `INVESTIGATE`, `REJECT`, tutti motivati.
7. **CLASSIFY:** in B2B determina settori, geografia, dimensioni e caratteristiche aziendali; in B2C definisce contesto individuale o household pertinente. Per B2B italiano mostra **massimo 3 ATECO esemplificativi**, verificati; ATECO non equivale a bisogno.
8. **MAP BUYERS:** identifica **job title B2B** oppure **ruoli individuali/familiari B2C**; funzioni decisorie come attributi, non come nomi dei ruoli. Nessun nominativo; evidenze distinte da ipotesi.
9. **SYNTHESIZE:** seleziona l'ICP raccomandato con giudizio strategico motivato; il pulsante `+` genera profili distinti **riutilizzando la ricerca già effettuata**.
10. Nessun sistema di scoring numerico 0–100 in questo modulo. Le decisioni devono essere argomentate, con evidenze e limiti.
11. Ogni affermazione sostanziale del profilo è riconducibile a fonte, data, contesto e stato epistemico (`Observed`, `Inferred`, `Unverified`).

## 3. Input e output di sistema

### Input

| Sorgente | Dati richiesti | Limite da rispettare |
|---|---|---|
| Project Brief | Prodotto/servizio, contesto, geografia, vincoli commerciali, informazioni sul cliente | Non chiedere ripetutamente informazioni già presenti |
| Step 00 UVP | Solo in modalità offerta disponibile: dichiarazioni dell'utente, Working UVP, evidenze e assunzioni | In sviluppo: assente, non simulata |
| Modulo 01 — Demand Intelligence | Domande, cluster, search intent, keyword, SERP e trend con tracciabilità | Domanda di ricerca ≠ domanda d'acquisto |
| Modulo 02 — Market Intelligence | Offerte, casi d'uso, testimonianze, recensioni, segmenti dichiarati, pattern competitivi | Casi singoli ≠ comportamento tipico del mercato |
| Ricerca esterna | Studi originali, ricerche sui buyer, fonti settoriali, casi documentati, metodologie | Valutare pertinenza, data, geografia e attendibilità |

### Output

- `WorkingUVP` approvata, con versione, ipotesi e prove disponibili **solo in modalità offerta disponibile**; in sviluppo l’output è assente.
- `SegmentHypotheses` (4–6 iniziali) con criteri di inclusione e fonti che hanno originato l'ipotesi.
- `EvidenceMatrix` per segmento, riutilizzabile e verificabile.
- `SegmentDecision` con esito e razionale.
- `FirmographicProfile` (B2B) o `ConsumerHouseholdProfile` (B2C) e `BuyerMap` per i segmenti qualificati.
- `ICPStrategicProfile` prioritario + fino a due ulteriori profili su richiesta; sezioni per dashboard e deck.

## 4. Workflow completo dell'agente

Un solo **UVP & ICP Intelligence Agent** orchestra analisi, ricerca ed estrazione. Il modello AI pianifica ricerche e produce interpretazioni; codice e strumenti eseguono recupero fonti, parsing, normalizzazione, verifiche e gestione dello stato. I dati osservati non devono essere sostituiti con affermazioni inventate.

| Fase | Operazione | Output | Gate di controllo |
|---|---|---|---|
| **00 — UVP** *(solo offerta disponibile)* | Raccoglie informazioni guidate, conversa, identifica lacune, formula una Working UVP | UVP strutturata e approvata, oppure step non eseguito | Distinguere fatti, benefici dichiarati e ipotesi; in sviluppo non generare UVP |
| **01 — DISCOVER** | Analizza UVP se disponibile, altrimenti idea/bisogno, brief e moduli precedenti; formula 4–6 ipotesi di segmenti non ridondanti | Segment hypotheses | Nessuna UVP immaginaria, motivazione commerciale minima |
| **02 — RESEARCH** | Verifica bisogni, contesto d'acquisto e caratteristiche organizzative tramite evidenze pertinenti | Evidence Matrix | Fonti originali e pertinenti; un solo approfondimento mirato |
| **03 — VALIDATE** | Controlla le evidenze, il fit con la UVP **quando presente** o la coerenza con il bisogno in sviluppo, le alternative e le controprove; decide | ADVANCE / INVESTIGATE / REJECT | Problem ≠ purchase; decisione motivata e verificabile |
| **04 — CLASSIFY** | Traduce il segmento in attributi **firmografici B2B o individuali/household B2C**; ATECO solo se pertinente al B2B Italia | Segment Profile | Non attribuire numeri/soglie senza base documentata |
| **05 — MAP BUYERS** | Individua **job title B2B** oppure **ruoli relazionali B2C** e relativi processi decisionali | Buyer / Household Map | Attributi decisionali ≠ ruoli; niente organigrammi o stereotipi inventati |
| **06 — SYNTHESIZE** | Confronta i candidati, formula raccomandazione, controlla qualità e consegna | Primo ICP + max 2 su `+` | Unicità sostanziale; niente informazioni inventate |

### 4.1 Step 00 — UVP: formulario e chat

**Stato della progettazione:** bozza funzionale accettata, da perfezionare nella successiva revisione UX. Non cambiare autonomamente il nome in *Value Hypothesis*: l'etichetta di interfaccia è **UVP**.

Form a sinistra e chat contestuale con l'agente a destra su desktop; su mobile la chat può essere collocata sotto il form. La chat conosce i campi compilati, può fare domande mirate, individuare ambiguità, contestare affermazioni generiche, suggerire modifiche e aiutare a redigere una UVP formale. **Nessuna modifica automatica ai campi senza conferma dell'utente**.

| Campo | Dato raccolto | Indicazione |
|---|---|---|
| 01 — Prodotto/servizio | Cosa viene venduto e quali funzionalità/attività comprende | Essenziale |
| 02 — Destinatario ipotizzato | Per chi potrebbe essere utile, senza fissare l'ICP definitivo | Essenziale |
| 03 — Customer Job | Obiettivo/compito che il cliente vuole realizzare | Essenziale |
| 04 — Pains & Frictions | Problemi, inefficienze, costi, rischi e ostacoli | Essenziale |
| 05 — Desired Gains | Risultati e benefici attesi, qualitativi o misurabili | Essenziale |
| 06 — Value Mechanism | Come la soluzione produce concretamente il beneficio | Essenziale |
| 07 — Alternative attuali | Soluzioni concorrenti, processi interni, status quo | Facoltativo, da approfondire |
| 08 — Elementi distintivi | Ragioni di preferenza e vantaggi sostenibili | Facoltativo, da verificare |
| 09 — Evidence & Proof | Dati, casi, testimonianze e altre prove disponibili | Facoltativo; assenza evidenziata |

I sei campi *essenziali* abilitano una prima formulazione guidata; la compilazione non dimostra che il contenuto sia vero o completo. L'agente restituisce una **UVP sintetica**, una **UVP estesa** e un elenco di **evidenze/assunzioni**. La versione approvata alimenta DISCOVER. La UVP definitiva segment-specific appartiene al Modulo 04.

### 4.2 Step 01 — DISCOVER: ipotesi, non ICP

1. Leggere la UVP approvata **se prevista**, altrimenti descrizione dell’idea e del bisogno, brief e output dei due moduli precedenti.
2. Derivare problemi, risultati attesi, usi, condizioni e possibili trigger.
3. Generare **4–6 ipotesi iniziali di segmenti** con variazioni reali di bisogni e contesto organizzativo, non solo taglie differenti.
4. Collegare ogni ipotesi alle prime evidenze e alle lacune; escludere le ipotesi palesemente incompatibili.
5. Consegnare un elenco candidato con: segmento, need, trigger ipotizzato, razionale, evidenze disponibili e quesiti di ricerca.

Non selezionare qui i tre ICP e non associare codici ATECO prematuramente.

### 4.3 Step 02 — RESEARCH: investigazione commerciale

Per ogni segmento candidato, l'agente formula quesiti specifici:
- **Problem:** il problema esiste ed è rilevante per questa tipologia di organizzazione?
- **Purchase:** si osservano acquisti o utilizzi di soluzioni della stessa categoria?
- **Fit:** quali caratteristiche del segmento rendono plausibile l'utilità dell'offerta?
- **Process:** quali circostanze potrebbero attivare la domanda, e quali ostacoli emergono?

**Sequenza vincolante:**
1. Cercare prima nei dataset strutturati dei Moduli 01–02, senza ripetere analisi già svolte.
2. Generare query web mirate alle lacune, non ricerche generiche sul segmento.
3. Individuare e consultare la **fonte originale** quando disponibile: studio, documento tecnico, intervista primaria, caso documentato, rapporto di settore.
4. Verificare autore, metodologia, popolazione/campione, periodo, geografia, interessi della fonte e applicabilità al segmento.
5. Estrarre claim puntuali, riportando URL/riferimento, data, contesto, risultato e limiti.
6. Cercare, quando possibile, conferme indipendenti e controevidenze. Consentire **un solo ulteriore ciclo di ricerca mirato** per lacune decisive; poi dichiarare l'incertezza restante.

**Gerarchia funzionale delle fonti, non catalogo rigido:**
- **Domanda e ricerca del problema:** evidenze del Modulo 01.
- **Uso/acquisto di soluzioni analoghe:** casi di acquisto documentati, recensioni e offerta/benefici osservati nel Modulo 02; testimonianze commerciali non equiparate a indagini statistiche.
- **Contesto buyer e organizzativo:** ricerche originali verticali, indagini di settore, studi metodologicamente trasparenti, fonti istituzionali pertinenti.
- **Ricerca e recupero:** motore di ricerca/SERP, Python per documenti web/PDF; servizi bibliografici quando utili. Non presumere accesso al testo integrale tramite un servizio di soli metadati.

**Non utilizzare OCSE o ESOMAR come integrazioni software obbligatorie.** Possono ispirare criteri metodologici, non costituiscono automaticamente fonti pertinenti per ogni ICP. **InfoCamere non è parte della pipeline standard**, e **ISTAT non è fonte centrale di need intelligence**; ATECO ISTAT è usato nello step CLASSIFY.

**Evidence Matrix minima**:
`segment_id | claim | evidence_type | finding | original_source_url | author/publisher | publication_date | geography | methodology | applicability | limitations | epistemic_status`.

I claim derivati dalla ricerca sono classificabili come `Supported`, `Mixed` o `Unverified`; conservare sempre l'argomento e le fonti, non percentuali di attendibilità arbitrarie. Il **grado di supporto** (`Supported/Mixed/Unverified`) è distinto dalla **natura dell'affermazione** (`Observed/Inferred/Unverified`): non vanno confusi in un unico campo.

### 4.4 Step 03 — VALIDATE: decisione su evidenze disponibili

VALIDATE **non ripete tutta RESEARCH**. Usa la Evidence Matrix per distinguere rigorosamente:

1. **Problem Evidence:** esistenza e rilevanza del bisogno.
2. **Solution/Purchase Evidence:** utilizzo, valutazione o acquisto di soluzioni della categoria, quando documentato.
3. **Commercial / UVP Fit:** plausibilità del valore specifico dell'offerta rispetto al segmento e alle alternative.

Controllare inoltre triggering conditions, barriere, evidenze contrarie e lacune. Non trasformare un problema dimostrato in intenzione di spesa automaticamente. Valutare il fit senza assumere che la Working UVP sia vera per definizione.

**Esiti possibili:**
- `ADVANCE`: **Problem Evidence**, **Solution/Purchase Evidence** e **Commercial/UVP Fit** valutati separatamente, con almeno evidenze commerciali dirette oppure analogie specifiche e documentate; l’analogia deve rimanere indicata come tale. Un problema documentato, da solo, non basta. Nessun ostacolo determinante irrisolto.
- `INVESTIGATE`: ipotesi credibile, ma manca un elemento decisivo. Una ricerca supplementare è ammessa soltanto se non è già stato consumato il ciclo aggiuntivo consentito.
- `REJECT`: incompatibilità sostanziale o controevidenze sufficienti. **Scarsità di dati, da sola, non è motivo di REJECT.**

Ogni decisione registra: evidenze favorevoli, contrarie, valutazione di fit, lacune, motivazione e riferimenti. Se manca la prova di utilizzo/acquisto della categoria di soluzione, l'agente deve mantenere `INVESTIGATE`, salvo evidenze analoghe puntuali e chiaramente qualificate; non deve dedurre l'acquisto dal solo bisogno. **Nessuno score numerico arbitrario** e nessun numero minimo di fonti usato come surrogato di qualità.

### 4.5 Step 04 — CLASSIFY: caratterizzazione firmografica

Per ogni segmento `ADVANCE`, definire:
- **Industry:** settori e sottosettori pertinenti al need, anche trasversali a più classificazioni economiche.
- **Company Size:** intervalli plausibili di addetti; fatturato soltanto se giustificabile e utile.
- **Geography:** coerente con mercato, servizio e vincoli del Project Brief.
- **Organizational Attributes:** struttura multisede, crescita, complessità organizzativa, modalità di lavoro e altri attributi rilevanti quando sostenuti da evidenze.
- **Need / Trigger:** problema e condizioni che distinguono davvero il segmento.

**ATECO:** per gli ICP relativi all'Italia mostrare **al massimo tre esempi**, scelti in funzione dei settori descritti, con `codice | descrizione ufficiale ISTAT ATECO 2025 | ragione della pertinenza`. Verificare la classificazione vigente e le note di inclusione/esclusione, senza fabbricare codici o descrizioni. Gli ATECO sono **esempi e non un elenco esaustivo né il perimetro definitorio dell'ICP**. Per mercati esteri applicare, se utile, la classificazione ufficiale corrispondente senza forzare ATECO italiani.

Non inventare precisione: se il range di fatturato o addetti non è giustificabile, indicare **non determinato**, esplicitando il motivo.

### 4.6 Step 05 — MAP BUYERS: job title B2B o relazioni B2C, non contatti

Per ogni segmento qualificato, costruire una **Buyer Map** adattata al tipo di mercato. **Nel B2B l’output principale è una lista di job title concreti**; nel B2C sono ruoli individuali/relazionali, eventualmente nel nucleo familiare:

| Output principale | Esempi | Attributi secondari |
|---|---|---|
| **B2B — Job title** | CEO, HR Director, HR Manager, CFO, Procurement Manager, Office Manager | Chi avvia, influenza, utilizza, finanzia o approva la decisione; bisogni, criteri e obiezioni |
| **B2C — Ruolo nella scelta** | Individuo, partner, madre/padre, figlio, nonno/nonna, tutore | Partecipazione alla scelta, impatto, pagamento, influenze; configurazione della famiglia se pertinente |

**Configurazioni B2C da investigare quando rilevanti:** individuo, coppia, nucleo familiare, monoparentale, allargata/multigenerazionale; forme gerarchiche o patriarcali soltanto quando osservate, mai assunte come regola.

Per B2B: `job_title / buying_responsibility / needs / criteria / barriers / evidence / status`. Per B2C: `relationship_role / household_configuration / participation_in_choice / needs / barriers / evidence / status`. La funzione decisionale (*initiator, influencer, budget owner...*) è un **attributo** e non sostituisce il job title o il ruolo familiare.

Non tutti i ruoli sono necessariamente distinti. Nelle imprese piccole possono coincidere; in quelle maggiori è possibile un processo più articolato. **La responsabilità del problema non dimostra il controllo del budget.** Non inventare organigrammi, nominativi o passaggi di autorizzazione: indicare `Hypothesized` dove l'evidenza non è sufficiente.

Le fonti sono le evidenze pertinenti già raccolte, più eventuali fonti specifiche sul buying process del settore. Non utilizzare Sales Navigator né elenchi di contatti.

### 4.7 Step 06 — SYNTHESIZE: raccomandazione e profili ICP

1. Riunire i segmenti `ADVANCE` con Evidence Matrix, Firmographic Profiles e Buyer Maps.
2. Confrontare qualitativamente: bisogno, coerenza con UVP **quando presente** o con il problema esplorato, segnali di acquisto, accessibilità commerciale e barriere. Esplicitare trade-off e limiti.
3. Raccomandare **un ICP prioritario** soltanto se esistono elementi sufficienti; altrimenti mostrare ciò che manca e l'impossibilità di raccomandarne uno.
4. Generare un **ICP Strategic Profile strutturato**, con sintesi per la dashboard e contenuti derivati per il deck.
5. Verificare coerenza interna, fonti, terminologia e assenza di elementi inventati.
6. Il pulsante `+` richiede un ICP addizionale, sostanzialmente diverso da quelli già generati; **riutilizza analisi e ricerca esistenti** senza riavviare l'intera pipeline. Massimo due aggiunte e tre ICP totali.

Se solo uno o due segmenti risultano qualificati, non generare profili fittizi per raggiungere il limite massimo.

## 5. User Interface e delivery

### 5.1 Schermata di apertura — UVP (solo offerta disponibile)

- Form guidato a nove campi, suddiviso in **Offerta e destinatario**, **Customer Value**, **Meccanismo e differenziazione**. **Quando il flag in sviluppo è attivo, il form e le formulazioni UVP sono assenti, non disabilitati a schermo.**
- Chat AI contestuale accessibile durante tutta la compilazione; può proporre testi alternativi, richieste di chiarimento e verifiche.
- Anteprima UVP sintetica/estesa; evidenze e assunzioni; approvazione della Working UVP.
- Progresso di compilazione senza trattare la completezza formale come prova di validità.

### 5.2 Analisi e progressione

- Visualizzare il passaggio corrente (`DISCOVER` … `SYNTHESIZE`), eventuali lacune decisive e gli esiti della validazione, evitando report ridondanti.
- Consentire di consultare prove e fonti associate ai claim importanti.
- Un sistema di stati separa `Observed`, `Inferred`, `Unverified` e decisioni `ADVANCE`, `INVESTIGATE`, `REJECT`.

### 5.3 Workspace ICP

**Inizialmente un solo ICP raccomandato**; pulsante **`+ Nuovo ICP`** per creare il secondo e il terzo, se sostenibili. La generazione incrementale conserva la tracciabilità degli elementi già studiati. Un ICP deve essere distinguibile dagli altri per bisogno, contesto o dinamica di acquisto, non soltanto per una descrizione diversa dello stesso segmento.

Ogni scheda contiene:

| Sezione | Output richiesto |
|---|---|
| Identification | Nome descrittivo del segmento + sintesi |
| Industries | Settori e sottosettori coerenti |
| Company Size / Household Profile | B2B: addetti e fatturato se fondati. B2C: composizione del nucleo e attributi pertinenti, senza equivalenti aziendali artificiosi |
| Geography | Territorio di riferimento |
| Organizational / Household Attributes | B2B: struttura organizzativa; B2C: contesto individuale/familiare, se rilevante e documentabile |
| Needs & Pain Points | Problemi e priorità, collegati alle evidenze |
| Desired Outcomes | Risultati ricercati e relazione con la Working UVP, **solo se disponibile** |
| Buying Triggers | Situazioni favorevoli osservate o ipotizzate |
| Key Roles | B2B: **job title**; B2C: **ruoli individuali/familiari** |
| Decision Makers | B2B: job title con autorità; B2C: relazioni decisionali e pagatore se pertinente, mai presunti da età/genere |
| Purchase Criteria & Barriers | Fattori di scelta e ostacoli |
| ATECO examples | **Fino a 3 esempi** con descrizione ufficiale e razionale, **solo per profili di aziende italiane**; non applicabile ai nuclei B2C |
| Strategic Rationale | Perché questo ICP è raccomandato, trade-off e limiti |
| Sources & Evidence | Fonti cliccabili e collegamento claim → evidenza |

**Esclusi dal delivery:** elenchi di aziende, contatti, email, nominativi ricercati, dati non verificati presentati come fatti.

## 6. Qualità, affidabilità e criteri di accettazione

L'implementazione è accettabile solo se:

1. **Tracciabilità:** ogni affermazione importante ha riferimento a fonte o stato di ipotesi. I risultati dei Moduli 01–02 mantengono la propria provenienza.
2. **Pertinenza:** la fonte sostiene proprio il claim (non semplicemente un argomento correlato); geografia, periodo e popolazione sono confrontabili o i limiti sono dichiarati.
3. **Distinzione commerciale:** un bisogno documentato non viene presentato come evidenza di acquisto senza ulteriori prove.
4. **Gestione dell'incertezza:** dati assenti non sono zero e non giustificano automaticamente l'esclusione del segmento.
5. **Criteri decisionali:** ADVANCE/INVESTIGATE/REJECT sono riproducibili almeno nelle motivazioni e nei riferimenti, pur richiedendo test di coerenza dell'LLM.
6. **Efficienza:** DISCOVER produce 4–6 candidati; RESEARCH riusa dati disponibili; massimo **un approfondimento supplementare mirato** per le lacune decisive.
7. **Buyer Mapping:** separazione fra figure che vivono il problema e figure che decidono/autorizzano l'acquisto; nessuna persona inventata.
8. **ATECO:** non più di tre codici esemplificativi **per ICP aziendale italiano**; codici/titoli verificati; **non applicabile ai profili B2C**.
9. **UI:** chat UVP contestuale, suggerimenti con conferma, un ICP iniziale, pulsante `+` fino a tre; nuove generazioni senza rifare inutilmente il lavoro precedente.
10. **Output strutturato:** i profili possono alimentare Modulo 04, dashboard e deck senza dover rigenerare fatti con l'LLM.
11. **Comportamento negativo:** in caso di prove insufficienti l'agente non inventa un ICP raccomandato per riempire la schermata.
12. **Esecuzione pilota:** prova end-to-end con il caso del Project Brief, valutazione umana di fonti, decisioni e coerenza degli ICP. **Non ancora effettuata.**

## 7. Dati concettuali — da dettagliare nel TDD

- `UVPForm`, `WorkingUVP`, `UVPRevision`, `UVPChatMessage`.
- `SegmentHypothesis`, `ResearchQuestion`, `SourceDocument`, `EvidenceClaim`, `EvidenceMatrix`.
- `SegmentDecision` (esito, motivazioni, evidenze e contrarie, versione).
- `FirmographicProfile` (B2B) / `ConsumerHouseholdProfile` (B2C), `EconomicClassificationExample` (solo se applicabile), `BuyerRole`, `BuyerMap`.
- `ICPStrategicProfile`, `ICPGenerationRequest`, `ICPRecommendation`.

Ogni record rilevante include progetto/esecuzione, provenienza, data, stato, versione e collegamenti alle evidenze. Separare **documenti/fonti raw**, **informazioni estratte** e **giudizi dell'agente**.

## 8. Dipendenze e handoff

- **Modulo 01:** fornisce il linguaggio della domanda e i segnali di ricerca osservati; non determina automaticamente propensione all'acquisto.
- **Modulo 02:** fornisce casi d'uso, segmenti dichiarati e segnali competitivi, con limiti delle fonti.
- **Modulo 03:** definisce Working UVP, segmentazione, buyer mapping e 1–3 ICP documentati.
- **Modulo 04:** utilizza gli ICP e le evidenze per **Value Proposition & Positioning** specifici per segmento, evitando la duplicazione della Working UVP iniziale. Se la Working UVP o l'offerta cambia in modo sostanziale, i risultati dipendenti dei Moduli 01–02 devono essere segnalati come potenzialmente obsoleti; la rivalutazione avviene mediante richiesta esplicita, non automaticamente.
- **Deck:** utilizza i profili e le evidenze strutturate, mostrando chiaramente ipotesi e criticità.

## 9. Questioni tecniche aperte — non riaprire lo scope

1. Contratto dati/schema definitivo fra moduli e salvataggio dei risultati intermedi.
2. Implementazione della ricerca multi-fonte (query, SERP, accessibilità documenti web/PDF, deduplica, estrazione e citazioni).
3. Regole verificabili di qualità/retest per il giudizio dell'agente e confronti fra esecuzioni.
4. Parametri di stop legati a errori di accesso, dati scarsi e fonti non comparabili.
5. Esperienza della chat UVP e revisione dei nove campi nella fase di UX/PRD.
6. Layout definitivo della scorecard qualitativa e delle sezioni ICP nel deck.

**Non è stato eseguito alcun test end-to-end del Modulo 03 né verificato l'accesso a tutte le fonti qui descritte.** Il presente documento chiude lo **scoping funzionale**, non certifica l'affidabilità delle analisi future.


## 10. Aggiornamenti vincolanti 24 ottobre 2026 — modalità prodotto, B2C e UI

### Modalità prodotto in sviluppo

Il flag nel Project Brief **«Il prodotto o servizio è ancora in fase di sviluppo?»** determina un percorso senza UVP: step 00 non mostrato né richiesto; DISCOVER e le fasi successive costruiscono ICP a partire da problemi, domanda osservata, competitor, gap e altre evidenze. **Non generare UVP sintetica/estesa, claim o altre verbalizzazioni della proposition**, né inviarle al deck. I segmenti ottenuti sono ipotesi/opportunità da verificare, non una promessa di capacità del futuro prodotto.

### Buyer mapping effettivo

- **B2B:** l'unità mostrata è un **job title** concreto (es. HR Manager, HR Director, CEO, CFO, Procurement Manager); iniziatore, influencer, decisore, approvatore sono attributi eventuali. Non usare *Initiator/Champion* come se fossero job title.
- **B2C:** considerare consumatore individuale o **household decision unit**. Se l'acquisto è familiare, investigare coppia, famiglia nucleare, monoparentale, allargata/multigenerazionale, contesti patriarcali **solo se supportati dal caso e dalle evidenze**, e ruoli di partner, genitori, figli, nonni/tutori. Non presupporre chi paga o decide in base al genere o alla struttura del nucleo.
- Per B2C `Company Size`, fatturato e ATECO **non sono campi obbligatori** né si applicano a persone/famiglie. Il massimo di tre ATECO vale soltanto per gli **ICP aziendali italiani**, come esempi non esaustivi.

### UX essenziale e trasparenza

Workflow visibile: **UVP [se pertinente] → Segmenti → Ricerca → Verifica → Profilo → Chi decide → ICP**. Mostrare una sola riga compatta di step con stato reale; le schede principali rimangono pulite, razionali e fonti apribili su richiesta. Richieste di conferma esplicite per modifiche UVP e approvazioni. Stato in sviluppo: UI inizia da **Segmenti**. Non inventare percentuali di avanzamento.

### Compatibilità col Modulo 04

In modalità offerta disponibile, trasmettere Working UVP approvata e buyer mapping con ruoli concreti. In modalità sviluppo, trasmettere **solo bisogno, profili, buying roles, evidenze e opportunità**: nel Modulo 04 sono vietati claim, messaggi e positioning statement commerciali. Versionare lo stato del flag.


## 11. Knowledge Base condivisa — decisione trasversale

L'agente accede a playbook e framework di ricerca sui buyer, segmentazione, validazione qualitativa, definizione ICP e mappatura decisionale B2B/B2C tramite lettura selettiva di file Markdown. Le ricerche originali e le evidenze dei Moduli 01–02 mantengono priorità come **prova fattuale**: un playbook indica **come** valutare, non dimostra che un segmento acquisti.

Non usare RAG vettoriale nella prima versione; il caricamento è orchestrato da Python. Fonti e playbook hanno provenienza, versione e stato di approvazione. Vedere `docs/00_PROJECT/KNOWLEDGE_BASE.md`.
