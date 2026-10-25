# GTM Engine — Modulo 07: GTM Strategy Deck

**Versione:** 1.0 — Scoping funzionale consolidato  
**Data:** 24 ottobre 2026  
**Stato:** requisiti funzionali approvati e documentati; implementazione, collaudo grafico ed export reale da sviluppare e validare.  
**Dipendenze:** `docs/00_PROJECT/PROJECT_SCOPE.md`, `docs/00_PROJECT/KNOWLEDGE_BASE.md`, output approvati dei Moduli 01–06.

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Prove provider storiche nell’audit del 24 ottobre; nessuna riprodotta nel repository attuale.

## 1. Obiettivo e perimetro

Convertire le evidenze e le decisioni strategiche dei Moduli 01–06 in un **GTM Strategy Deck professionale, sintetico, narrativamente coerente e realmente modificabile in PowerPoint (`.pptx`)**.

Il modulo agisce come **editor strategico e presentation designer**, non come un nuovo motore di ricerca o strategia. **Non inventa insight, KPI, risultati, differenziatori, budget o messaggi**. Se riscontra incoerenze o informazioni mancanti, le segnala e richiede una decisione, senza colmare i vuoti con contenuti plausibili ma non fondati.

**Fuori scope MVP:** creazione di campagne, invii, generazione di interi piani editoriali, collaborazione PowerPoint in tempo reale, editing grafico libero nel browser, generazione di una nuova identità visiva per ogni slide, export nativo Google Slides. Il PDF è eventuale formato secondario, non sostitutivo del PPTX editabile.

## 2. Sistema di template approvato

L'intera presentazione deriva da un sistema tipografico e di impaginazione coerente composto da:

1. **Main Cover:** copertina iniziale dedicata, con nome progetto, titolo del deck, data/versione e logo se fornito.
2. **Section Cover:** copertina di sezione ispirata alla Main Cover ma **visivamente distinguibile**, con titolo, numero/segnaposto e una breve frase di inquadramento. **È opzionale per ogni sezione**: non generare automaticamente sette copertine soltanto perché il software ha sette moduli.
3. **Content Template A — Insight / Analysis:** per domanda, dati, grafici, tabelle, confronti competitivi, ICP, risultati analitici e limiti di evidenza.
4. **Content Template B — Recommendation / Action:** per scelte, opportunità, positioning (quando ammissibile), priorità dei canali, orchestrazione, gap di risorse, budget, roadmap e KPI.

**Totale: 1 modello Main Cover + 1 modello Section Cover + 2 modelli contenuto.** I due modelli contenuto sono **famiglie di layout parametrizzabili**, non due immagini rigide: il generatore modifica dimensioni, spazi, combinazioni e presenza degli slot già previsti senza inventare stili grafici alternativi a ogni slide.

**Regola del template:** l'agente prima determina il messaggio della slide, poi seleziona A oppure B, infine adatta i contenuti agli slot consentiti. Se il contenuto non è leggibile, deve **sintetizzare, suddividere in due slide o spostare il dettaglio in appendice**; mai ridurre indiscriminatamente il font, sovrapporre oggetti o trasformare la slide in un'immagine piatta.

### 2.1 Slot minimi dei template

| Elemento | Main Cover | Section Cover | A: Insight / Analysis | B: Recommendation / Action |
|---|---|---|---|---|
| Titolo | Sì | Sì | Sì, preferibilmente una conclusione | Sì, preferibilmente una decisione |
| Sottotitolo / contesto | Opzionale | Breve | Opzionale | Opzionale |
| Corpo testuale | No | No | Sintesi e annotazioni | Sintesi, motivazione, trade-off |
| Visual | Elemento grafico editoriale, opzionale | Segno grafico di sezione | Grafico/tabella/confronto, ove utile | Sequenza/matrice/priorità, ove utile |
| Fonte / assunzioni | Non richiesta | Non richiesta | Riferimento sintetico / rimando all'appendice | Riferimento a evidenza / rimando all'appendice |
| Elementi editabili | Titolo, metadati, forme | Titolo, metadati, forme | Testo, grafici, tabelle, forme | Testo, forme, tabelle, sequenze |

Le visualizzazioni non necessarie sono omesse: niente grafici puramente decorativi.

## 3. Architettura narrativa e numero di slide

**Numero di slide variabile**, definito dalla quantità e importanza delle conclusioni; **10–15 è una stima orientativa, non un obbligo né un massimo**. Il deck non deve essere una trascrizione degli output tecnici e non richiede esattamente una slide per modulo.

Ordine narrativo di riferimento, riorganizzabile in funzione del progetto:

1. **Main Cover** e **Executive Summary**: decisioni strategiche, opportunity thesis, rischi e priorità.
2. **Demand & Market**: evidenze di domanda, ricerca, tendenze pertinenti e limiti.
3. **Competitive Landscape**: competitor, differenziazione fondata, posizionamenti e gap osservati; scoring soltanto dove valido e con dimensioni coperte dichiarate.
4. **ICP & Buyers**: segmenti raccomandati, bisogno e ruoli di acquisto (per B2B job title, per B2C ruoli relazionali se pertinenti).
5. **Positioning & Value**: per offerte già disponibili, solo UVP, proposta e messaggi approvati; per prodotti in sviluppo questa sezione diventa **opportunità da validare e implicazioni di prodotto**, senza copy commerciale.
6. **Channel Strategy**: canale prioritario, fino a due complementari se giustificati, esclusioni e motivazioni.
7. **GTM Execution Plan**: combinazione dei canali, attività essenziali e orchestrazione con trigger osservabili.
8. **Investment & Resource Gap**: Paid media separato da software/servizi, outsourcing, ore e competenze; budget minimo solo quando stimabile e motivato.
9. **Roadmap & Measurement**: milestone, dipendenze, KPI effettivamente misurabili e condizioni per iterare.
10. **Recommendations / Next Decisions**: scelte, precondizioni e prossimi passi.

**Le Section Cover vanno inserite per veri passaggi narrativi**, non automaticamente per ogni modulo. Possibile raggruppamento iniziale: *Market & Demand → ICP & Positioning → GTM Strategy → Execution & Measurement*. Le intestazioni di sezione sono adattabili: il lettore deve seguire una storia strategica, non leggere l'albero dei componenti software.

**Appendice (dinamica, se necessaria):** fonti, metodologia, assunzioni, esclusioni, scoring, definizioni e dati tabellari più dettagliati. Gli approfondimenti non devono appesantire le slide decisionali.

## 4. Workflow — cinque step, un agente

| Step interno | Attività | Artefatto |
|---|---|---|
| **01 — COLLECT** | Recupera snapshot **approvati** dei moduli 01–06, metadati, fonti, limiti, modalità prodotto e template/branding scelto. | `DeckSourceSnapshot` |
| **02 — SYNTHESIZE** | Estrae messaggi, insight e decisioni, separa osservazioni da interpretazioni e ipotesi, identifica lacune e contraddizioni. | `EditorialEvidenceMap` |
| **03 — STRUCTURE** | Costruisce outline narrativo con numero variabile di slide; decide cover di sezione, ordine, titolo-conclusione e template A/B. | `DeckOutline` |
| **04 — DESIGN** | Popola gli slot dei template, costruisce oggetti editabili e applica la griglia editoriale. | `DeckSlideSpec[]` e presentazione bozza |
| **05 — VALIDATE & EXPORT** | Controlla coerenza strategica, tracciabilità, anti-slop, layout, editabilità e approvazione; esporta `.pptx`. | `DeckQAReport`, `GTM_Strategy_Deck.pptx` |

Etichette UI brevi: **Raccoglie → Sintetizza → Organizza → Impagina → Verifica**. Progressi solo per stati reali (`queued`, `running`, `waiting_for_user`, `completed`, `partial`, `failed`), non percentuali simulate.

## 5. Contratti informativi e provenienza

Per ogni affermazione quantitativa o qualitativa sostanziale inserita nel deck è necessario un riferimento al materiale sorgente: `module_id`, `run_id`, `artifact_id`/`evidence_ref`, versione e stato (`observed`, `derived`, `hypothesis`, `unavailable`). L'agente può **riscrivere per sintesi**, ma non alterare significato, popolazione, geografia, periodo, livello di certezza o condizionalità.

**Regole bloccanti:**

- **Numeri e grafici** devono usare gli stessi valori approvati a monte, con unità, periodo, territorio e limiti coerenti.
- **Competitive Scoring**: mostrare l'indicatore corretto, la copertura di dimensioni valide e le limitazioni; mai sostituire dati mancanti con zero o presentare il prototipo come validato empiricamente.
- **Paid & risorse**: distinguere budget media, costi software/dati, costi di supporto esterno e ore interne; importi `da quotare` restano ignoti, non €0.
- **In sviluppo**: non generare UVP, claim, positioning promozionale o messaging; mantenere il carattere esplorativo delle opportunità.
- **Qualità fonti**: possibilità di risalire a evidenza e data; in slide citazione breve o marker, in appendice riferimento completo. Non citare fonti inesistenti.
- **Non approvato o parziale**: mostrare un avviso e non spacciare la conclusione per definitiva; se essenziale, sospendere o chiedere conferma.

La Knowledge Base supporta stile, narrative design e controllo metodologico ma **non prevale sulle evidenze specifiche** del progetto né giustifica l'invenzione di dati.

## 6. Regole editoriali e visuali

- **Direzione grafica:** editoriale, minimale, professionale, con prevalenza di tipografia e spazio bianco. Design system coerente con griglia, margini, stili dei titoli, palette limitata, formati di numero e allineamenti.
- **Titoli informativi:** dove appropriato, formulati come conclusioni, non semplici etichette generiche (es. evitare «Analisi del mercato» quando la slide dimostra un fatto più preciso).
- **Gerarchia:** un messaggio principale per slide; eventuali confronti o dati a supporto.
- **Contenuti:** no AI-slop, frasi vuote, icone casuali, gradienti gratuiti, fotografie stock non funzionali o visualizzazioni ornamentali.
- **Identità:** utilizzare logo/palette/font aziendali **solo se forniti** e compatibili; altrimenti un tema editoriale di default. Nessun logo inventato e nessuna richiesta obbligatoria di brand kit.
- **Griglie e grafici:** scegliere il visual più leggibile e fedele all'informazione. Usare diagrammi/forme native quando più appropriati dei grafici.
- **Leggibilità:** overflow, clipping, sovrapposizioni e dimensioni di testo illeggibili costituiscono errori; applicare una correzione verificabile, eventualmente dividendo la slide.

## 7. Modificabilità e formato

**Output primario MVP: file PowerPoint `.pptx`.** Ogni slide deve essere composta, nella misura applicabile, da **testi, forme, tabelle e grafici nativi editabili**. I grafici che richiedono dati devono conservare una struttura dati modificabile in PowerPoint, oppure utilizzare forme native con etichette editabili se la fedeltà del grafico nativo non è sufficiente. Loghi e fotografie forniti dall'utente possono rimanere immagini, in quanto asset fotografici e non elementi di testo/dati da modificare.

**Vietato:** esportare una slide intera come PNG/JPEG e inserirla in una presentazione presentandola come editabile. Per gli elementi complessi non supportati dal generatore, dichiarare il limite e preferire un layout nativo più semplice; non degradare silenziosamente l'editabilità.

Separare **contenuto strutturato**, **layout/template** e **renderer PPTX**: l'agente sceglie messaggio e famiglia di layout; il renderer deterministico applica le regole. L'architettura approva python-pptx, preview LibreOffice headless sul worker Render e Supabase Storage privato. Restano da implementare e verificare editabilità, compatibilità e layout.

## 8. Revisione e UX

- Visualizzare un **outline/indice** con numero di slide stimato, senza mostrare tutta la pipeline tecnica.
- Mostrare l'anteprima delle slide con evidenza dei contenuti incompleti o dei warning.
- Consentire **approvazione dell'intero deck** prima dell'esportazione.
- Consentire almeno **rigenerazione di una singola slide** o della sua sintesi/impaginazione senza rieseguire Moduli 01–06; riutilizzare snapshot approvato e template scelto.
- L'editing fine di testi, grafici, forme e layout è garantito **nel PPTX dopo l'export**. Un editor visuale PowerPoint completo nel browser non è requisito MVP.
- Rigenerazioni e modifiche di una slide non devono sovrascrivere dati/insight approvati dei moduli sorgenti.

L'utente deve poter distinguere facilmente **bozza**, **da rivedere**, **approvata**, **esportata**.

## 9. Quality Assurance e test di accettazione

| Test | Criterio di accettazione |
|---|---|
| **Slide count variabile** | Cambiando quantità di evidenze, cambia il numero di slide senza violare la narrativa o forzare un numero fisso |
| **Cover principale + section cover** | Main Cover presente; Section Cover coerente ma distinta e aggiunta solo se serve; nessuna cover automatica per ogni modulo |
| **Due template contenuto** | Tutte le slide informative usano solo le famiglie A e B con slot adattabili; non vengono introdotti nuovi stili casuali |
| **Editabilità PPTX** | Titoli, testi, forme, tabelle e grafici di test restano manipolabili come oggetti, non raster di pagina |
| **Overflow/layout** | Nessun clipping, testo fuori pagina o sovrapposizione di oggetti; si verifica anche su esempi densi |
| **Tracciabilità** | Numeri, citazioni, raccomandazioni e assunzioni rimandano ai run e alle fonti corrette |
| **Coerenza Moduli 05–06** | Canali, investimenti, gap e roadmap rimangono coerenti con gli output approvati |
| **Dati mancanti** | `unknown`, `partial` e `da quotare` non diventano valori numerici o certezze |
| **Prodotto in sviluppo** | Nessuna UVP, claim o proposta promozionale creata dal deck |
| **Anti-AI-slop** | Titoli specifici e linguaggio credibile, senza formulazioni ridondanti o decorative |
| **Rigenerazione locale** | Modificare una slide non ricalcola moduli a monte e non altera le altre slide senza scelta esplicita |
| **Apertura file** | PPTX apre in PowerPoint/strumento compatibile, con struttura valida e media/asset disponibili |

**Test visivo:** renderizzare tutte le slide in immagini per ispezione automatica e revisione manuale su casi campione; confrontare la leggibilità con il deck PPTX effettivo. Prevedere casi B2B, B2C, prodotto disponibile, prodotto in sviluppo, dati incompleti, competitor non comparabili e presentazione lunga.

**Stato test:** questi sono criteri progettati, **non test già superati**.

## 10. Schema concettuale dell'output

```text
DeckProject
  project_id, deck_id, run_id, source_versions, product_state
  deck_title, audience, language, branding, template_version
  status, approvals, warnings
  outline: Section[]
  slides: DeckSlideSpec[]
  evidence_index: EvidenceRef[]
  export: {format: "pptx", file_path, generated_at, validated}

DeckSlideSpec
  slide_id, section_id, role: main_cover|section_cover|content
  template: main_cover|section_cover|insight_analysis|recommendation_action
  title, subtitle?, key_message?
  content_blocks[], chart_specs?, table_specs?, footnotes[]
  evidence_refs[], limitations[], review_state
```

Il renderer associa i blocchi agli slot dei quattro layout approvati. Font, layout, tema e regole di overflow sono versionati: la riproducibilità grafica non deve dipendere da un prompt libero diverso a ogni esecuzione.

## 11. Implementazione e collaudo secondo architettura approvata

- Implementare python-pptx e verificare grafici realmente editabili.
- Implementare preview LibreOffice headless sul worker Render; verificare font e layout.
- Implementare Supabase Storage privato, versioning bozze, limiti file e job persistiti su Postgres.
- Schemi JSON validati e collegamento ai contratti di output dei Moduli 01–06.
- Strategia di test end-to-end su ambienti equivalenti a quelli di produzione.

---

**Decisione finale di scope:** il Modulo 07 è definito funzionalmente con **1 Main Cover, Section Cover opzionali e 2 famiglie di content template modificabili**, numero di slide dinamico, QA e output primario `.pptx`. La completezza dello scope **non implica** che la generazione o il rendering PPTX siano stati già implementati o collaudati.
