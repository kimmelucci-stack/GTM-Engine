# GTM Engine — Modulo 04: Value Proposition & Positioning

**Versione:** 1.1 — Scoping funzionale + handoff Modulo 05  
**Data:** 24 ottobre 2026  
**Stato:** workflow funzionale concluso; implementazione, integrazioni e validazione ancora da svolgere  
**Dipendenze:** Project Brief, Moduli 01–03; linee guida UX in `docs/00_PROJECT/PROJECT_SCOPE.md`.

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Gate 1A DataForSEO riprodotto nel repository il 25 ottobre 2026 con limiti di copertura; registro nell’audit. Per crawler e altri accessi, stato e limiti nella [matrice canonica](../00_PROJECT/PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md).

## 1. Obiettivo

Stabilire **perché un cliente dovrebbe scegliere l'offerta rispetto alle alternative disponibili** e, soltanto quando l'offerta è sufficientemente definita, costruire posizionamento e architettura di messaging coerenti con i profili ICP. Non generare campagne, email o inserzioni: questi appartengono ai moduli successivi.

L'agente di macrofase **Value Proposition & Positioning Agent** coordina analisi e controlli. Non sono previsti agenti autonomi per ciascun micro-passaggio.

**Confini:** non ripetere la compilazione della UVP (Modulo 03), la ricerca completa sui competitor (Modulo 02) o la selezione degli ICP (Modulo 03). Riutilizzare prioritariamente dati, fonti e versioni già disponibili. Non usare punteggi CCI come prova automatica di superiorità di un'offerta.

## 2. Due modalità definite nel Project Brief

| Modalità | Condizione | Consentito | Vietato |
|---|---|---|---|
| **Offerta disponibile** | Flag «Il prodotto/servizio è ancora in sviluppo?» = **No** | Verificare capacità, differenziazione, Value–ICP Fit, posizionamento e messaggi, con evidenze e approvazione | Inventare vantaggi esclusivi o prove; fare claim non sostenuti |
| **Prodotto/servizio in sviluppo** | Flag = **Sì** | Analizzare alternative, bisogni non soddisfatti, opportunità e requisiti di valore da esplorare per ICP | Compilazione UVP, claim, positioning statement, Value Proposition commerciale, messaggi promozionali, argomentazioni commerciali e altre verbalizzazioni della proposition |

Nella seconda modalità si esegue una **Opportunity Analysis**: l'applicazione non suggerisce implicitamente che un prodotto ancora non disponibile abbia funzionalità, benefici o prestazioni dimostrate. I bisogni provengono dal Modulo 01, dalle evidenze del Modulo 02 e dalla ricerca ICP del Modulo 03: **non esclusivamente dai competitor**.

Un prodotto già disponibile **senza qualità uniche** resta nella prima modalità: la UVP può descrivere un valore funzionale reale, ma differenziazione e superiorità rimangono `Non dimostrate`. È lecito non produrre differenziatori verificati; non riempire artificialmente la scheda.

La modalità, la versione del brief e gli output che dipendono dal flag devono essere conservati per ogni esecuzione. Cambiare il flag segnala i risultati da rivalutare, senza rigenerazioni silenziose.

## 3. Input

- **Project Brief:** descrizione offerta o idea progettuale, stadio di sviluppo, ambito geografico, vincoli, lingua/mercato, informazioni di brand eventualmente disponibili.
- **Modulo 01 — Demand:** problemi, linguaggio della domanda, search intent, cluster, trend e relativi limiti; una query non dimostra l'intenzione di acquisto.
- **Modulo 02 — Market & Competitive:** alternative, offerte e capacità rilevate, prove, recensioni, prezzi/casi d'uso quando effettivamente osservati; dati e score non equivalgono a differenziazione dimostrata.
- **Modulo 03 — UVP & ICP:** Working UVP solo in modalità offerta disponibile, 1–3 ICP, bisogni, Evidence Matrix, buyer map B2B/B2C, criteri di acquisto e barriere.
- **Brand references:** materiali verificabili dell'azienda, esempi di comunicazione, preferenze editoriali e TOV esplicito quando forniti; se assenti, proporre il TOV e richiedere approvazione.

## 4. Workflow dell'agente — sei step

| Step interno | Procedura concreta | Output | Controllo |
|---|---|---|---|
| **01 — COMPETITIVE ALTERNATIVES** | Recupera concorrenti documentati e identifica soluzioni sostitutive, alternative interne, status quo. Valuta rilevanza dal punto di vista di ciascun ICP e ricerca soltanto lacune decisive. | `AlternativeMap` per ICP | SEO visibility ≠ alternativa commerciale; nessuna alternativa inventata |
| **02 — DIFFERENTIATION** | Estrae capacità dichiarate e osservabili; le confronta con alternative pertinenti, associa bisogni e prove, tenta di falsificare presunti vantaggi. | `DifferentiationMatrix`, fino a 3 differenziatori per ICP se fondati | Feature ≠ benefit ≠ differenziatore; è ammesso l'esito «nessuno verificato» |
| **03 — VALUE–ICP FIT** | Associa bisogno documentato → capacità dell'offerta → beneficio potenziale → differenza e prova; prioritizza secondo criteri d'acquisto supportati. | `ValueMap` per ICP | Se manca il collegamento, segnala il gap, non inventa benefici |
| **04 — POSITIONING** | Determina categoria/contesto competitivo, territorio strategico sostenibile, core positioning e declinazioni per ICP; stress test delle affermazioni. | `PositioningStrategy` | Un nucleo di brand coerente, senza tre identità incompatibili |
| **05 — MESSAGING** | Definisce/approva TOV, adatta argomentazioni agli specifici buyer roles, produce core message e supporting arguments, revisione editoriale e conversazionale. | `MessagingArchitecture` + `ToneOfVoice` | Italiano nativo credibile; niente brochure generica o promesse non provate |
| **06 — VERIFY & DELIVER** | Audit fonti → coerenza → qualità copy → pertinenza buyer → massimo un ciclo correttivo → consegna con conferma. | `PositioningPackage` approvabile, input del Modulo 05 e deck | Se restano blocchi strategici, esporli anziché approvare fittiziamente |

**Modalità in sviluppo — deviazione condizionale, non un nuovo agente:**
- Step 01: alternative reali e status quo.
- Step 02: **spazi di differenziazione da indagare**, non vantaggi già posseduti.
- Step 03: **Opportunity Map** (bisogni, gap e requisiti desiderabili), non Value–ICP Fit riferito a capacità non esistenti.
- Step 04: **territori di opportunità competitiva**, senza positioning statement.
- Step 05: **saltato**; nessun copy, claim o formulazione della proposition.
- Step 06: validazione e delivery **solo analitici**, senza verbalizzazioni promozionali.

### 4.1 Step 01 — Competitive Alternatives

La domanda è: «Che cosa sceglierebbe il cliente se la nostra offerta non esistesse?» Distinguere:
1. concorrenti diretti;
2. prodotti/servizi sostitutivi;
3. gestione interna o fai-da-te;
4. scelta di non acquistare (*status quo*).

Ogni alternativa ha: `type`, `relevance_to_icp`, `purchase_criterion`, `source`, `evidence_status`, `limitations`. Non promuovere un dominio presente nelle SERP a competitor commerciale senza verifica.

### 4.2 Step 02 — Differentiation

Per ogni ipotesi di differenza: **capacità specifica → bisogno ICP → alternativa di confronto → evidenza**. Validare specificità, pertinenza, distintività e prova; cercare controesempi presso alternative pertinenti. Prioritizzare **fino a tre**, anche zero. Non trattare «personalizzato», «innovativo» o «di qualità» come differenziatori senza contenuti concreti e confronto.

### 4.3 Step 03 — Value–ICP Fit

Prodotto esistente: costruire per ciascun ICP una `ValueMap` con `need`, `capability`, `potential_benefit`, `differentiation_status`, `supporting_evidence`, `gap`. Una capacità condivisa dal mercato può essere utile ma non differenziante.

Prodotto in sviluppo: produrre `OpportunityMap` con `documented_need`, `competitive_gap`, `possible_product_requirement`, `supporting_evidence`, `unknowns`. I requisiti futuri sono **ipotesi progettuali**, non caratteristiche già disponibili.

### 4.4 Step 04 — Positioning

Prodotto esistente: categoria di riferimento, alternative confrontate, territorio strategico e **un core positioning coerente**, eventualmente declinato per ciascun ICP. Dove il vantaggio non esiste, descrivere la categoria/valore senza simulare unicità.

Prodotto in sviluppo: limitarsi alla mappa delle opportunità/territori possibili; **non produrre statement formali o claim**.

### 4.5 Step 05 — Messaging e Tone of Voice

**Solo per prodotto disponibile.** Prima di scrivere, l'agente raccoglie e confronta esempi del brand, contesto locale e caratteristiche dei destinatari; propone un TOV iniziale **soggetto ad approvazione**. Un TOV di marca, non una personalità diversa per ogni ICP.

Output: messaggio centrale per ICP, argomentazioni di supporto, obiezioni e prove, variazioni per buyer role. Sono **architetture di messaggio**, non campagne, email o annunci pronti alla pubblicazione.

**Requisito anti-AI-slop, prioritario e testabile in revisione umana:**
- Italiano scritto con sintassi, ritmo e lessico naturali, **non traduzione letterale di copy inglese**; verificare la qualità per ciascuna lingua e mercato.
- Niente cliché («soluzioni innovative», «esperienze uniche», «partner a 360°»), frasi intercambiabili, superlativi gratuiti o benefici generici senza sostanza.
- **Test sostitutivo:** se un competitor può firmare il messaggio senza cambiarlo, non è abbastanza specifico.
- **Test del bisogno:** è evidente quale problema dell'ICP affronta e quale capacità lo rende pertinente?
- **Test probatorio:** le affermazioni sono osservate e fondate? Se non lo sono, non formulare risultati come garantiti.
- **Test TOV:** appropriatezza per lingua/brand/mercato/target, con revisione editoriale critica; AI non approva da sola il proprio output come prova di qualità.
- La chat consente di rivedere il messaggio; proposte di riscrittura ai campi strutturati **solo previo consenso dell'utente**.

**Buyer mapping corretto:** B2B mostra **job title reali** (es. CEO, HR Director, CFO, Office Manager) con funzione decisionale come attributo secondario; B2C mostra **ruoli individuali e relazionali** (es. individuo, partner, madre/padre, figli, nonni/tutori) coerenti con nucleo e dinamiche familiari, senza presumere gerarchie o stereotipi. Nessun contatto nominativo.

### 4.6 Step 06 — Verify & Deliver

Un ciclo editoriale/strategico automatico; se permangono contraddizioni o lacune essenziali, esito `NeedsReview`, non false conferme. L'utente può correggere o approvare la strategia. La versione approvata diventa l'unica sorgente autorizzata per il Modulo 05; le ipotesi restano visibili come tali.

## 5. Interfaccia utente — minimale, workflow visibile

La UI mostra **solo**: titolo modulo, un indicatore di avanzamento con etichette italiane brevi, output primario e una o due azioni contestuali. Razionali, fonti, fonti contrarie e versioni sono disponibili in pannelli espandibili; **non** riempiono la schermata principale.

| Step interno | Etichetta UI (prodotto disponibile) | Etichetta UI (in sviluppo) |
|---|---|---|
| Competitive Alternatives | Alternative | Alternative |
| Differentiation | Punti di forza | Opportunità |
| Value–ICP Fit | Valore per i clienti | Bisogni e gap |
| Positioning | Posizionamento | Territori possibili |
| Messaging | Messaggi | **Nascosto** |
| Verify & Deliver | Verifica | Verifica |

- ICP realmente disponibili tramite tab/card essenziali (mai mostrare ICP 02–03 fittizi).
- Stati reali: `Da avviare`, `In corso`, `Richiede conferma`, `Completato`, `Parziale`, `Non disponibile`, `Errore`; progresso **non simulato**. Nessuna percentuale inventata dagli LLM.
- Output sintetici per default, dettagli per espansione; *progressive disclosure* uniforme nei Moduli 01–04.
- Se serve approvazione, l'azione `Approva` o `Rivedi con l'agente` appare dove pertinente.
- In modalità in sviluppo, l'utente **non vede sezioni claim/messaging vuote o grigie**: sono escluse dal flusso e dal deck.
- Nessuna UI prolissa: evitare liste complete di log, descrizioni di ogni micro-task, gergo interno, emoji decorative o badge superflui.

## 6. Output strutturati e handoff

**Offerta disponibile:**
- `AlternativeMap` per ICP; `DifferentiationMatrix` con esiti e prove.
- `ValueMap` per ICP; `PositioningStrategy` centrale e declinazioni motivate.
- `ToneOfVoice` approvato; `MessagingArchitecture` per ICP e buyer role.
- `EvidenceLedger` con `claim_id`, `source`, `date`, `observed_or_inferred`, `limitations`, `version`; `ReviewStatus`, `Approval`.

**Prodotto in sviluppo:**
- `AlternativeMap`, `OpportunityMap`, `CompetitiveOpportunityTerritories`, requisiti di valore ipotizzati, fonti, limiti e approvazione dell'analisi.
- **Assenti per contratto:** `WorkingUVP`, `PositioningStatement`, `BrandClaim`, `MessagingArchitecture`, `PromotionalCopy`.

**Passaggio al Modulo 05:** priorità ICP, criteri decisionali, alternative, evidenze e, quando disponibili, posizionamento e messaggi approvati. In modalità in sviluppo, le raccomandazioni sui canali sono limitate a ricerca/validazione del mercato, non attivazione di promesse promozionali.

**Deck:** sempre **modificabile**; contiene solamente elementi coerenti con la modalità selezionata, fatti con fonte e ipotesi dichiarate. Non reinventare numeri o claim in fase di presentazione.

## 7. Criteri di accettazione e rischi

1. Nessuna duplicazione di full-scraping, segmentazione e raccolta già effettuati, salvo lacune decisive documentate.
2. Alternative valutate per ciascun ICP dal punto di vista del cliente; inclusi sostituti e status quo ove pertinenti.
3. Differenziatori mai imposti in numero fisso: zero è un risultato ammissibile.
4. Valore/benefici senza collegamento verificabile classificati come ipotesi, non fatti.
5. Modalità in sviluppo blocca effettivamente **tutti** gli output verbali della proposition, incluso il deck, e non richiede compilazione UVP.
6. Mapping B2B su **job title** e B2C su **ruoli relazionali e strutture familiari**, senza stereotipi.
7. TOV approvabile, adeguato alla lingua locale, con controllo specifico sul copy italiano e revisione anti-genericità.
8. Un solo ciclo automatico di correzione; criticità irrisolte restano esplicite.
9. UI minimale con workflow comprensibile, stati reali e approfondimenti opzionali.
10. Output strutturati, versionati e riutilizzabili dal Modulo 05 e dal deck.

**Rischi da verificare durante il pilota:** mancanza di evidenze su differenze reali, inferenze causali deboli, insufficiente qualità del copy italiano, errori di attribuzione del potere decisionale, incoerenze fra declinazioni per ICP. Servono valutazioni umane su campioni reali; non dichiarare qualità comprovata prima dei test.

## 8. Questioni tecniche aperte (non modificano lo scope)

Da dettagliare e collaudare: contratti API, versionamento, configurazione modelli OpenAI e test TOV multilingua, accesso fonti, refresh input e componenti UI. Le scelte tecniche sono definitive: Render API/worker, Supabase Postgres/Storage e PPTX python-pptx con preview LibreOffice; nessuna riapertura dello stack.


## 9. Knowledge Base condivisa e handoff verso Channel Strategy

Il Positioning Agent può consultare playbook Markdown approvati di positioning, differenziazione, messaging, revisione editoriale e Tone of Voice attraverso la selezione Python prevista per tutti gli agenti. **Non** utilizzare la Knowledge Base per inventare risultati dell'offerta o caratteristiche dei competitor.

Il Modulo 05 riceve: ICP e buyer roles concreti, messaggi/TOV **solo se offerta disponibile e approvati**, alternative, bisogni, evidence status, obiettivi e vincoli. In modalità **prodotto in sviluppo** riceve esclusivamente gap, bisogni e opportunità analitiche, non claim o argomentazioni promozionali. Riferimenti: `docs/00_PROJECT/KNOWLEDGE_BASE.md` e `docs/05_CHANNEL_GTM_STRATEGY/SCOPE.md`.
