# GTM Engine — Modulo 01: Demand Intelligence

**Versione:** 0.3 — Scope funzionale + Knowledge Base condivisa  
**Data:** 20 ottobre 2026  
**Stato:** scope definito; accessi DataForSEO riprodotti al Gate 1A con limiti di qualità nell'audit. Modulo non implementato end-to-end.

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Gate 1A DataForSEO riprodotto nel repository il 25 ottobre 2026 con limiti di copertura; registro nell’audit. Per crawler e altri accessi, stato e limiti nella [matrice canonica](../00_PROJECT/PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md).

## 1. Scopo

Misurare e interpretare la domanda espressa attraverso le ricerche online relative a un prodotto o servizio, comprendendo anche **come gli utenti formulano i propri bisogni**. Identificare cluster di ricerca, intenzioni, volumi disponibili, trend, stagionalità e primi soggetti visibili nelle SERP.

Il modulo alimenta data visualization, analytics e presentazione GTM finale. Il suo compito non è ancora l'analisi competitiva completa né la scelta definitiva dei canali di investimento.

## 2. Input e interfaccia — configurazione concordata / proposta

| Campo | Specifica | Stato |
|---|---|---|
| Prodotto/servizio | Descrizione dell'offerta; il modulo legge il brief | Previsto |
| Target | **Non si reinserisce nel modulo**; proviene dal Project Brief | Decisione espressa |
| Keyword iniziali | Facoltative, aggiunte alle seed create dall'AI | Previsto |
| Geografia | **Radio button mutuamente esclusivi:** `Città` / `Regione` / `Nazione` | Decisione espressa |
| Geografia fuori Italia | Disponibile **solo `Nazione`** | Decisione espressa |
| Selettore geografico | Dopo la scelta radio, selezione del luogo coerente; evitare input libero non validato | Proposta da specificare |
| Raggio chilometrico | **Escluso** dalla configurazione | Decisione espressa |
| Modalità di analisi | `Exploratory`, `Standard`, `Deep` con descrizione nell'interfaccia | Decisione espressa; contenuti sotto proposti |
| Esecuzione API | Preferenza esplicita per **LIVE**, senza attese di code batch | Requisito; fattibilità per endpoint da verificare |

**Accortezza tecnica geografica:** la disponibilità del selettore città/regione non garantisce di per sé che l'endpoint richiesto fornisca volumi a quella granularità. Prima di avviare ogni richiesta, il backend deve confrontare la località con quelle supportate da quell'endpoint. Se non disponibile, non deve mostrare dati nazionali come fossero locali; deve esplicitare il problema o richiedere una scelta alternativa.

**Internazionale:** selezione per nazione; eventuali più nazioni vanno analizzate e identificate separatamente. La disponibilità di lingua e località deve essere validata.

### Descrizione proposta delle modalità

- **Exploratory:** discovery keyword, prima misurazione, cluster tematici essenziali.
- **Standard:** Exploratory + intent, linguaggio delle ricerche/domande, trend/stagionalità.
- **Deep:** Standard + espansione iterativa, SERP selezionate e prima competitor discovery.

Le modalità rappresentano livelli di profondità, non fasce di prezzo. Il loro perimetro preciso rimane da testare e approvare. I dati disponibili da Autocomplete/People Also Ask/Related Searches/Trends devono essere raccolti nelle modalità che li prevedono, conservati e clusterizzati per analytics e visualizzazioni.

## 3. Flusso operativo dell'agente — sei passaggi

### 01 — Understand: comprensione del prodotto
L'agente legge il brief, identifica cosa viene venduto, a chi, quale problema risolve e quali alternative potrebbe cercare il cliente.

**Output:** categorie di bisogno, segmenti, ipotesi di ricerca e seed keyword.

### 02 — Discover: espansione delle keyword
L'agente combina keyword formulate dall'AI, varianti recuperate tramite DataForSEO e keyword facoltative fornite dall'utente. Include ricerche per sinonimi, bisogni e formulazioni più lunghe.

**Output:** universo di keyword candidate con provenienza (`AI hypothesis`, `user`, `DataForSEO observed`).

### 03 — Validate: misurazione
Python interroga DataForSEO per recuperare le metriche realmente disponibili: volumi, CPC, competizione, serie mensili. I dati mancanti rimangono marcati come mancanti, non inventati o convertiti arbitrariamente a zero.

**Output:** dataset quantitativo delle keyword, con perimetro e metadati del provider.

### 04 — Classify: clustering e intent
Pulizia, deduplicazione e classificazione per bisogno, categoria prodotto, tema e intenzione di ricerca. Le metriche aggregate non devono introdurre doppi conteggi ingiustificati, né essere presentate come totale di utenti unici.

**Output:** cluster e metriche, con assegnazioni e classificazioni verificabili.

### 05 — Investigate: approfondimento automatico
L'agente cerca aree incomplete, interroga formulazioni simili ad AnswerThePublic (quando fornite da sorgenti reali), controlla trend, seleziona SERP rappresentative e approfondisce dove opportuno. Limiti di iterazione, timeout e cap economico confermato seguono l'architettura approvata; le modalità restano livelli di profondità, non fasce di prezzo.

**Output:** evidenze di approfondimento, copertura effettiva e prima lista di domini/inserzionisti osservati.

### 06 — Synthesize: interpretazione
L'agente sintetizza quantità e articolazione della domanda, bisogni, linguaggio usato nelle ricerche, trend/stagionalità, distribuzioni e primi elementi di concorrenza osservata.

**Output:** dataset strutturati, visualizzazioni/metriche preparate per dashboard e sezioni del deck.

## 4. Search Language Intelligence (stile AnswerThePublic)

**Requisito:** non limitarsi a un elenco di keyword; identificare come gli utenti verbalizzano il bisogno.

Fonti candidate tramite DataForSEO, soggette a test per endpoint, disponibilità e limiti:
- Google Autocomplete;
- elementi People Also Ask presenti nelle SERP;
- Related Searches dalle SERP;
- Keyword Ideas / Suggestions;
- query correlate e trend, quando restituiti dagli endpoint pertinenti.

Organizzazione dei risultati per categorie: domande (`come`, `dove`, `quanto`, ecc.), confronti, alternative, problemi/bisogni, prezzi e ricerche locali. La tassonomia è una **proposta**, non ancora un elenco chiuso.

**Regole:**
- Preservare la **frase originale** restituita dall'API e la sua provenienza.
- Tenere distinta una formulazione osservata da una frase ipotizzata dall'AI.
- Non attribuire automaticamente volumi a suggerimenti Autocomplete o PAA: chiedere separatamente le metriche, quando disponibili.
- Autocomplete e PAA non costituiscono un campione statisticamente rappresentativo dell'intera domanda.

## 5. Competitor Discovery — perimetro iniziale

La Demand Intelligence può identificare soggetti presenti nelle SERP pertinenti: risultati organici, annunci osservati e local pack quando disponibili. Questa fase produce **candidati competitor** e *search competitors*, non un censimento completo del mercato.

La classificazione deve distinguere almeno:
- concorrenti commerciali diretti o indiretti, **solo se sostenuti da evidenze sufficienti**;
- siti che competono per visibilità organica (editori, directory, portali inclusi);
- inserzionisti osservati su query specifiche.

L'approfondimento di offerte, messaggi, posizionamento e confronto strategico rimane nella futura **Market & Competitive Intelligence**.

Una SERP isolata non dimostra la continuità della spesa pubblicitaria di un'azienda, né consente di ricavare con affidabilità il suo budget.

## 6. Fonti e integrazioni — da testare

**Provider principale approvato:** DataForSEO; accessibilità effettiva da riprodurre nel Gate 1A.

Famiglie di dati da verificare con la documentazione corrente e una prova integrata reale:
- Google Ads Search Volume e metriche associate;
- Labs Keyword Ideas / Suggestions / Related Keywords / Search Intent, dove applicabili;
- Google SERP, incluse funzionalità e tipi di elementi effettivamente restituiti;
- Google Autocomplete;
- Google Trends Explore e query/trend associati;
- possibilità di SERP geolocalizzate e limiti delle location Google Ads.

**Importante:** il fatto che DataForSEO documenti una famiglia di endpoint non costituisce prova che tutti supportino gli stessi parametri, paesi, profondità o modalità LIVE. L'implementazione deve fare un test di compatibilità per ciascun endpoint selezionato. Non si promettono risultati PAA, local pack o trend per ogni keyword.

## 7. Modello dati concettuale

Record suggeriti (schema tecnico da finalizzare nel TDD):

- `Project / AnalysisRun`: riferimento al progetto, configurazione, modalità, stato, data, geografia, lingua.
- `Keyword`: testo originale e normalizzato, origine, relazione alla seed e stato validazione.
- `KeywordMetric`: metrica, valore, unità, periodo, località, fonte, timestamp, disponibilità.
- `SearchExpression`: frase/domanda, classe linguistica, sorgente, keyword/tema di origine.
- `Cluster`: etichetta, definizione, metodo di assegnazione, keyword associate.
- `TrendSeries`: keyword/argomento, periodo, valori e tipo di scala (assoluta o relativa).
- `SerpObservation`: query, località, momento di ricerca, tipo di risultato, URL/dominio, posizione quando disponibile.
- `Insight`: osservazione, interpretazione, evidenze collegate, caveat.
- `RawApiResponse`: risposta originale, endpoint, parametri essenziali, timestamp, stato/errori.

**Separare dati originali, dati normalizzati e risultati derivati.** I numeri Google Trends (scala relativa) non vanno sommati ai volumi assoluti Google Ads.

## 8. Output del modulo

1. **Keyword Universe:** query scoperte, origine, cluster, metriche quando disponibili.
2. **Search Language Map:** domande, confronti e formulazioni degli utenti, distinguendo dati osservati e ipotesi.
3. **Demand Landscape:** domanda misurata, distribuzioni, intent, trend, stagionalità e vincoli geografici.
4. **Competitor Discovery:** siti e inserzionisti osservati nelle SERP selezionate, con evidenza a supporto.
5. **Insights strutturati:** conclusioni motivate, ambiguità e limiti.
6. **Dati per dashboard e deck:** grafici e contenuti generabili dai dati, senza ricreare numeri nei testi del modello AI.

## 9. Architettura e ruolo dell'agente

**Scelta approvata:** un Demand Intelligence Agent coordina strumenti specializzati, senza agenti per ogni micro-operazione. Orchestrazione Python e OpenAI Responses nel worker Render; nessun n8n nell'MVP.

Stack approvato: FastAPI/Pydantic, React/TypeScript/Vite su Vercel, Supabase Postgres/Storage e worker Render. Preferire LIVE dove supportato; per endpoint TASK mostrare lo stato asincrono reale. Le prove di deploy e accesso restano necessarie.

## 10. Caso pilota

**Prodotto/servizio:** eventi aziendali e team building  
**Target del Project Brief:** aziende, HR Manager, Office Manager  
**Territorio:** Torino, Italia  
**Geografia UI:** `Città`  
**Seed facoltative:** `team building aziendale`; `location eventi aziendali`  
**Modalità:** Deep  

La precedente richiesta di **raggio 25 km è stata rimossa**: non va reintrodotta né tradotta in presunta precisione geografica. Le due seed restano ipotesi relative a bisogni distinti. L'audit storico riporta campioni Torino/Piemonte, non riprodotti qui e non estendibili all'intero universo keyword.

## 11. Vincoli di affidabilità e criteri per considerarlo funzionante

- Dati quantitativi derivati dall'API, mai fabbricati dall'AI.
- Marcatura esplicita delle query/ipotesi generate e di quelle osservate.
- Parametri e perimetri geografici effettivi visibili.
- Differenza fra valori nulli, zero ed errore API.
- Provenienza e timestamp per ogni metrica/risultato importante.
- Memorizzazione di raw e processed data.
- Possibilità di ricostruire i grafici dai dataset.
- Reporting distinto tra domanda osservata e interpretazioni.
- Esecuzione automatica end-to-end su almeno un caso pilota con controlli sui risultati.

## 12. Questioni aperte prima del PRD/TDD

1. Definire con precisione l'insieme di strumenti ed endpoint per ciascuna modalità Exploratory / Standard / Deep.
2. Validare la copertura effettiva di città, regioni e nazioni italiane e internazionali per ciascun endpoint richiesto.
3. Verificare le capacità LIVE, i tempi reali e gli eventuali casi in cui un endpoint non lo consente.
4. Implementare regole di selezione/iterazione per evitare cicli e rumore, rispettando limiti e cap economici confermati.
5. Confermare tassonomia linguistica e intent; gestire keyword associate a più bisogni.
6. Definire gli schemi dati, i controlli QA e le visualizzazioni del modulo.
7. Specificare layout e contenuti della sezione Demand Intelligence nel deck finale.

---

*La stesura originaria dello scope non eseguiva chiamate API. Successivamente Gate 1A ha riprodotto nel repository i campioni DataForSEO; verifiche, geografie e limiti sono nell'audit. Campioni riusciti non certificano copertura universale o modulo end-to-end.*


## 13. Aggiornamento trasversale 24 ottobre 2026 — modalità e workflow visibile

- Il Project Brief indica se l'offerta è disponibile o ancora in sviluppo. La **Demand Intelligence resta attiva in entrambi i casi**, utilizzando descrizione dell'idea/bisogno anche se non esiste una UVP; non inventa capacità del prodotto.
- La schermata principale mostra solo gli step brevi: **Comprendere → Esplorare → Misurare → Organizzare → Approfondire → Risultati**. I nomi tecnici *Understand / Discover / Validate / Classify / Investigate / Synthesize* restano interni.
- Per ogni step: stato effettivo, avanzamento osservato, eventuale richiesta d'intervento; dataset/fonti e limiti solo in pannelli di dettaglio. Nessuna percentuale di completamento ricavata arbitrariamente dalla generazione AI.
- UX minimale, niente spiegazioni lunghe nella schermata principale e nessuna perdita dei metadati di fonte nei dettagli/deck.

Questi vincoli integrano lo scope originario senza modificarne le sei fasi e la configurazione geografica.


## 14. Knowledge Base condivisa — decisione trasversale

Il Demand Intelligence Agent può leggere **playbook pertinenti** della Knowledge Base generale (metodologia keyword, search intent, interpretazione dei volumi, limiti geografici e SERP) tramite selezione di documenti Markdown e caricamento Python. Il Source of Truth è GitHub; **nessun RAG/indice vettoriale nella prima versione**.

I playbook guidano il metodo, ma **non sostituiscono i dati rilevati da DataForSEO**: volumi, CPC e SERP devono provenire da fonti effettive. I contenuti della KB non vengono automaticamente aggiornati in base a una singola analisi di progetto. Vedere `docs/00_PROJECT/KNOWLEDGE_BASE.md`.
