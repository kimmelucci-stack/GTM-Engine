# GTM Engine — Modulo 05: Channel & GTM Strategy

**Versione:** 1.0 — Scope funzionale consolidato  
**Data:** 24 ottobre 2026  
**Stato:** progettazione funzionale definita; fonti operative, benchmark, PRD/TDD e test strategici ancora da completare  
**Dipendenze:** Project Brief, Moduli 01–04, `docs/00_PROJECT/KNOWLEDGE_BASE.md`.

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Prove provider storiche nell’audit del 24 ottobre; nessuna riprodotta nel repository attuale.

## 1. Obiettivo e perimetro

Definire **quali canali di acquisizione utilizzare, per quali ICP, per intercettare quale domanda e perché**, distinguendo canali prioritari, complementari e non raccomandati. La strategia deve integrare marketing digitale, social, contenuti, performance, Search, inbound, outbound e approcci **signal-based** quando pertinenti, senza consigliare automaticamente tutti i canali.

**Non appartiene al Modulo 05:** eseguire campagne, inviare email, fare prospecting, produrre liste di aziende o contatti, programmare sequenze operative dettagliate, inventare CPC/CPL/CAC o scegliere software finali. Budget operativo dettagliato, tool, sequenze, KPI e roadmap di esecuzione spettano al **Modulo 06**.

L'analisi è possibile sia per prodotti disponibili sia per idee **in fase di sviluppo**, in quest'ultimo caso con attività di esplorazione del mercato e validazione dell'interesse, **senza claim, UVP o messaging promozionale**.

## 2. Decisioni approvate

1. **Un solo Channel & GTM Strategy Agent** per la macrofase, con strumenti Python deterministici e accesso ai dati delle fasi precedenti.
2. **Marketing Knowledge Base condivisa fra tutti gli agenti**, su Markdown/GitHub; Python seleziona e legge i soli playbook pertinenti. **Nessun RAG vettoriale, embeddings o File Search per la prima versione.**
3. **Un canale prioritario, fino a due complementari** quando giustificati; è valido raccomandarne uno soltanto oppure non dichiarare alcun canale idoneo con i dati disponibili. Questi limiti riguardano le **raccomandazioni**, non i canali candidati analizzati.
4. Canale, tattica e segnale sono oggetti distinti: esempio `LinkedIn` / `outreach personalizzato` / `espansione delle sedi`. Un segnale è utilizzato come trigger soltanto se osservabile e pertinente, non perché ipotizzato dall'AI.
5. Prioritizzazione **qualitativa, motivata e verificabile**; **nessuno score 0–100** non calibrato. L'agente deve motivare anche le esclusioni.
6. **Nessun benchmark inventato:** quando un costo, conversione, disponibilità di targeting o copertura non è verificato, dichiarare l'incertezza e non fare previsioni puntuali di CPL, CAC o risultati.
7. **B2B:** buyer roles = job title reali recuperati dal Modulo 03. **B2C:** unità decisionale individuale/relazionale/familiare quando pertinente. Nessuna generalizzazione automatica da uno all'altro.
8. **UX minimale** con workflow comprensibile e stato reale; rationale, metadati, scenari e fonti solo nei dettagli.

## 3. Input strutturati

| Fonte | Informazioni | Utilizzo e limite |
|---|---|---|
| Project Brief | Offerta o idea, area/lingua, tipo cliente, vincoli, obiettivo GTM, budget **se disponibile**, stato di sviluppo | Se budget/obiettivo mancano: chiedere solo dati essenziali oppure dichiarare valutazione economica parziale; non inventare valori |
| Modulo 01 | Volumi e intent osservati, domanda espressa, keyword, CPC quando disponibile, trend, SERP | Search demand ≠ numero di buyer unici né conversioni |
| Modulo 02 | Canali, ads, contenuti e offerte dei competitor; evidenze disponibili e limiti di copertura | Competitor presente su un canale ≠ prova che quel canale renda |
| Modulo 03 | Fino a 3 ICP, need, buying triggers, buyer roles e fonti | Le ipotesi sul buying process non diventano dati certi |
| Modulo 04 | Positioning, messaggi e TOV **solo se prodotto disponibile**; altrimenti gap/opportunità analitiche | Non usare claim per un prodotto in sviluppo |
| KB generale | Playbook approvati di Search, Social, Content, Performance, Brand, B2B/B2C, measurement | Regole decisionali, non verità automatiche sul caso specifico |
| Verifiche esterne | Documentazione ufficiale delle piattaforme, studi pertinenti e dati correnti quando necessari | Prezzi e capacità devono essere verificati nel contesto e nel momento della valutazione |

## 4. Workflow dell'agente — sei step

| Step interno | Attività | Output | Gate |
|---|---|---|---|
| **01 — ANALYZE** | Recupera brief, ICP, ruoli, offerta/idea, vincoli, dati Demand/Market e positioning dove disponibile. Legge i playbook necessari. | `GTMContext` con gap informativi | Non assumere UVP o budget inesistenti |
| **02 — DISCOVER CHANNELS** | Formula una rosa di canali candidati includendo inbound, outbound, paid, organic, social, content e percorsi signal-based pertinenti. | `ChannelCandidates` e possibili tattiche/segnali distinti | Nessuna lista standard uguale per tutti |
| **03 — VALIDATE** | Controlla raggiungibilità dell'ICP, intento/buying journey, possibilità effettive di targeting, segnali osservabili, disponibilità dei canali. | `QualifiedChannels` con evidenze | Fonti originali e limiti attuali; platform capability ≠ efficacia |
| **04 — EVALUATE** | Confronta fattibilità, intensità della domanda, economie **solo se documentabili**, vincoli di budget/risorse, rischi e trade-off. | `ChannelComparison` con alternative scartate | Nessun CAC/CPL o conversion rate inventato |
| **05 — DESIGN STRATEGY** | Definisce ruolo dei canali, possibili combinazioni inbound/outbound/signal-based, relazione con fasi di acquisto e ICP. | `GTMChannelStrategy` con opzioni e dipendenze | Evitare piani multicanale sproporzionati |
| **06 — PRIORITIZE & DELIVER** | Seleziona un primario e fino a due complementari, motiva scelte/esclusioni, verifica evidenze, prepara output per Modulo 06 e deck. | `ChannelRecommendation` approvabile | Esplicitare incognite decisive; niente ranking artificiale |

### 4.1 Sotto-processo di qualificazione e priorità (all'interno degli step, non nuovo agente)

Per ciascun canale candidato: 

1. **Audience Fit:** il nostro ICP può essere raggiunto in modo plausibile e concretamente disponibile? Il targeting va verificato; esistenza di un pubblico non implica accesso automatico ai suoi dati.
2. **Buying Journey Fit:** il canale intercetta bisogno espresso, domanda latente, scoperta o validazione secondo i comportamenti documentati?
3. **Demand & Signals:** volumi/search intent o segnali pubblicamente osservabili danno una ragione di utilizzo? Il segnale deve avere nesso col bisogno e accessibilità verificabile.
4. **Economics:** ci sono costo, intensità competitiva e budget **pertinenti e misurati** sufficienti a valutare un test sostenibile? Se mancano, non dichiarare sostenibilità dimostrata.
5. **Execution Feasibility:** strumenti, contenuti, asset, capacità organizzativa e limiti tecnici rendono fattibile il canale nella fase di progetto?

Esito per ciascun canale: `Suitable`, `Conditional`, `Excluded` o `InsufficientEvidence`, con **motivazione e fonte**. Queste etichette non esprimono probabilità di successo.

**Regola di scelta:** privilegiare un canale con rapporto credibile tra ICP raggiungibile, ruolo nel buyer journey e fattibilità, tenendo conto delle alternative. In assenza di evidenza economica, classificare la raccomandazione come **condizionata a un test**, non come ROI previsto.

### 4.2 Ruolo della Knowledge Base e fonti

La KB è un **sistema condiviso di metodologia**, non un catalogo di risultati garantiti. Gli agenti recuperano via Python playbook per la disciplina pertinente; nessuna indicizzazione vettoriale v1. La **Source of Truth** è GitHub/Markdown. La documentazione approvata resta versionata; nessuna riscrittura autonoma dei playbook.

- **Principi e ricerche strategiche:** ricerche originali/metodologie pubblicamente consultabili e pertinenti al mercato (es. evidenze IPA, Ehrenberg-Bass, ricerche B2B con metodi trasparenti). Non estrapolare percentuali universalmente.
- **Piattaforme:** documentazione ufficiale Google Ads/Search, Meta, LinkedIn e provider utilizzati. È attendibile per funzionamento e limitazioni **ma non costituisce confronto imparziale di efficacia fra canali**.
- **Dati del caso:** ricerca osservata e metriche dei Moduli 01–02; bisogni e buyer roles dei Moduli 03–04. I fatti del progetto non devono essere sostituiti da opinioni generali dei playbook.
- **Validazione di fonti esterne:** fonte originale, data, metodo quando applicabile, territorio, campione, conflitti/interessi e limiti. Non basare una scelta su un solo report promozionale.

**Verifica della libreria ogni 45 giorni:** un controllo leggero di URL/versioni per fonti già registrate, con rapporto di cambiamento; non implica automaticamente aggiornare la KB. Dettagli in `docs/00_PROJECT/KNOWLEDGE_BASE.md`.

## 5. Output in interfaccia e verso il Modulo 06

**Interfaccia:** una vista sintetica con canale prioritario, fino a due complementari e stato della raccomandazione. Ogni scheda mostra ruolo del canale e ICP associati; fonti, motivazioni e ipotesi solo su espansione. Workflow visibile in linguaggio semplice: **Contesto → Canali → Verifica → Confronto → Strategia → Priorità**. Stati reali: `queued/running/waiting_for_user/completed/partial/failed`, nessuna percentuale inventata.

Ogni `ChannelRecommendation` include:

- `icp_ids`, `channel_name`, `channel_role` (primario/supporto), `strategy_goal`, `buying_stage`.
- `candidate_tactics` e `observed_signals` come oggetti separati (se disponibili).
- `audience_fit`, `demand_evidence`, `economics_evidence`, `execution_constraints`, `rationale`.
- `source_refs`, `evidence_status`, `assumptions`, `unknowns`, `excluded_alternatives`.
- `validation_plan` con domande da verificare mediante successivi esperimenti, senza inventare un outcome numerico.

Il Modulo 06 riceve canali, ruoli, priorità, vincoli, dati verificati e incognite; **non** un piano già eseguibile o un budget allocato dall'AI senza input. Il Modulo 07 riceve visualizzazioni e motivazioni sintetiche, con evidenze disponibili su richiesta.

## 6. Comportamento con prodotto in sviluppo

La selezione di canali serve a **ricerca qualitativa, test di domanda e apprendimento sul mercato**. Non presumere caratteristiche future né generare UVP, claim, positioning statement o copy commerciali. I canali possono essere discussi come modalità per raggiungere potenziali utilizzatori per feedback e discovery, sempre motivandone la scelta. Evitare di trattare il numero di interazioni come vendite attese.

## 7. Criteri di accettazione e casi di test

Il modulo sarà considerato funzionante se:

1. Ogni canale raccomandato ha **ICP, finalità, razionale, evidenza e vincoli** espliciti.
2. Gli agenti recuperano un sottoinsieme pertinente di playbook approvati, con ID/versioni registrati nell'esecuzione; nessun RAG vettoriale richiesto.
3. Non attribuisce budget, CPC, CPL, CAC, conversioni o ROI non documentati come fatti.
4. Distingue categoria canale, tattiche specifiche e segnali osservati/ipotizzati.
5. Seleziona un primario e fino a due complementari **solo se sostenibili**; può segnare nessuna raccomandazione quando l'evidenza è insufficiente.
6. Spiega almeno una esclusione rilevante e le condizioni che potrebbero modificarla, quando emergono alternative plausibili.
7. Distingue B2B e B2C usando job title vs ruoli familiari; nessun organigramma inventato.
8. In modalità prodotto in sviluppo non genera claim né messaggi non autorizzati.
9. UI mostra progressione reale e non sovraccarica l'utente di testi.
10. Un test pilota end-to-end confronta le raccomandazioni con revisione umana, incluse controevidenze e casi in cui la scelta corretta è **non raccomandare un canale**.

**Casi pilota proposti** *(non eseguiti)*: B2B servizi eventi aziendali su Torino con domanda Search misurata e budget dichiarato; B2C con unità decisionale familiare; prodotto in sviluppo con UVP disattivata.

## 8. Questioni da risolvere nel PRD/TDD (senza riaprire lo scope)

- Schema preciso di Project Brief per budget/obiettivo/asset e trattamento dei campi mancanti.
- Catalogo dei canali candidati, evidenze minime per il loro utilizzo e condizioni di stop.
- Caricamento selettivo dei playbook via Python, convenzione metadati e test degli agenti.
- Capacità correnti delle piattaforme e condizioni d'accesso: non considerate già collaudate.
- Contratto dati verso il Modulo 06, stato dei job, archiviazione e output deck.
- Collaudo API e worker Render, persistenza Supabase, autorizzazioni e costi; hosting e libreria PPTX sono già approvati nell'architettura.

**Conclusione:** lo scoping funzionale del Modulo 05 è definito. Nessuna strategia è stata ancora verificata su campagne reali, e nessun servizio esterno è dichiarato connesso o operativo.
