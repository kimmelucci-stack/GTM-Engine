# GTM Engine — Modulo 06: GTM Execution Planning

**Versione:** 1.0 — Scope funzionale consolidato  
**Data:** 24 ottobre 2026  
**Stato:** **100% dei requisiti funzionali concordati specificati**; implementazione, benchmark, integrazioni e validazione empirica **non eseguiti**.  
**Dipendenze:** Project Brief, output Moduli 01–05, `docs/00_PROJECT/KNOWLEDGE_BASE.md`.

**Stack approvato:** React/TypeScript/Vite su Vercel; Python/FastAPI/Pydantic e worker separato su Render; Supabase Postgres/Storage; OpenAI Responses/Structured Outputs; deck python-pptx e preview LibreOffice headless. Decisioni in [architettura](../00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Restano da implementare e collaudare, non da selezionare. Gate 1A DataForSEO riprodotto nel repository il 25 ottobre 2026 con limiti di copertura; registro nell’audit. Altri provider non collaudati.

## 1. Obiettivo e confini

Trasformare la strategia del Modulo 05 in **un piano GTM eseguibile e motivato**, con combinazione di canali, attività essenziali, budget Paid, costi separati, capacità richieste, lacune, KPI e roadmap di esecuzione. L'agente **pianifica**, non avvia campagne, non invia outreach e non produce automaticamente piani editoriali dettagliati.

**Vincolo centrale:** la scelta strategica dipende da **mercato, ICP, domanda, obiettivi, evidenze e budget pubblicitario**, **non** dalle competenze già presenti nell'azienda. Il team viene valutato **dopo**, per identificare cosa manca e quando servono freelance, agenzie o fornitori. Una competenza assente non autorizza a inventare un piano meno efficace solo per adattarlo al personale.

La qualità del modulo non coincide con la quantità di attività generate: produrre poche azioni ad alto impatto, con dipendenze e obiettivi chiari.

## 2. Input e formulario minimo

L'agente eredita `Project Brief`, fino a 3 ICP, bisogni e buying context, canali raccomandati, domanda misurata, positioning/messaging **solo se prodotto disponibile**, fonti e playbook pertinenti.

Chiede soltanto ciò che manca:

| Campo UI | Significato | Regola |
|---|---|---|
| **Obiettivo** | Esito GTM da investigare/misurare, es. richieste qualificate, meeting, acquisti, validazione del bisogno | Obbligatorio se non definito nel brief; specificare metrica primaria |
| **Durata** | Orizzonte del piano e del test | Obbligatoria se non nota |
| **Budget pubblicitario Paid (€ / mese)** | **Solo spesa per inserzioni** Google, Meta, LinkedIn ecc. | Esplicito; può essere **0**. Non include software, freelance o agenzie |
| **Persone disponibili** | Numero complessivo, senza attribuire job title o responsabilità | Per l'analisi delle risorse |
| **Ore totali disponibili / settimana** | Capacità complessiva di tutte le persone, non ore per ruolo | Per l'analisi delle risorse |
| **Competenze disponibili** | Capacità che il team è in grado di svolgere autonomamente | Selezione semplice; approfondimenti **solo se pertinenti** ai canali |

Categorie iniziali e relativi esempi nell'help contestuale: **SEO & Content Strategy** (strategia di ricerca e contenuti); **Gestione social** (canali/community); **Campagne Ads** (configurazione/ottimizzazione); **Analytics & Tracking** (eventi e misurazione); **Grafica** (asset statici); **Foto e video** (riprese/montaggio); **Automazioni CRM / Email** (flussi, trigger e integrazioni). Le competenze SEO tecniche si indagano solo quando indispensabili. Le categorie non equivalgono a ruoli organizzativi o job title; una persona può coprirne più di una.

**UX:** schermata compatta, campi già noti precompilati, spiegazioni solo espandibili; competenze opzionali non pertinenti **non visualizzate**. Se manca un dato indispensabile, chiedere il minimo necessario; non inventarlo.

## 3. Workflow — sei step, un agente

| Step interno | Operazione | Risultato |
|---|---|---|
| **01 — DEFINE OBJECTIVES** | Legge strategia approvata, ICP, obiettivo, periodo, budget Paid, modalità prodotto e playbook. Esplicita metrica primaria e precondizioni. | `ExecutionContext` |
| **02 — DESIGN ACTIVITIES** | Propone soltanto i *work package* essenziali per canale (es. asset, landing, configurazione, contenuto, raccolta segnali, tracking). | `ActivityPackages` |
| **03 — ORCHESTRATE** | Collega canali, trigger **osservabili**, touchpoint, sequenze e dipendenze; non simula automazioni già attive. | `GTMOrchestration` |
| **04 — ALLOCATE RESOURCES** | Stima il **budget Paid minimo motivabile**, distingue costi software/servizi/supporto esterno, analizza competenze e ore, identifica gap e outsourcing. | `BudgetAndResourceGap` |
| **05 — DEFINE MEASUREMENT** | Definisce KPI, baseline disponibili, eventi da misurare, condizioni di stop/apprendimento e test qualitativi/quantitativi appropriati. | `MeasurementPlan` |
| **06 — BUILD ROADMAP** | Ordina attività, dipendenze e milestone, segnala condizioni non soddisfatte e produce il piano e le lacune. | `ExecutionPlan` |

Il workflow interno resta stabile; nella UI si visualizzano etichette brevi: **Obiettivi → Attività → Collegamenti → Investimento → Misurazione → Piano**. Mostrare stati effettivi (`queued`, `running`, `waiting_for_user`, `completed`, `partial`, `failed`), non percentuali inventate.

## 4. Regola di calcolo del budget Paid minimo

L'agente deve dichiarare **il minimo stimato per un test osservabile e interpretabile**, **mai il budget che garantisce clienti, vendite o ROI**. "Risultato reale" significa un **evento effettivamente misurato**, non un risultato commerciale assicurato. Il livello di evidenza condiziona quanto possiamo dire.

**Procedura obbligatoria per ogni canale Paid candidato:**

1. **Obiettivo del test:** definire *prima* la metrica primaria osservabile (visite pertinenti, lead, richieste, vendite, ecc.), il periodo e le condizioni di misurazione; distinguere **test di erogazione/traffico** da **test di conversione**.
2. **Costi unitari verificati:** usare CPC, CPM, preventivi e forecast pertinenti a *canale, territorio, periodo e tipo di pubblico*; fonte e data obbligatorie. Per Search, integrare volumi/CPC del Modulo 01 e, se disponibile, previsioni della piattaforma. Per Meta e altri canali, non trasferire i CPC Search. Non usare tassi medi di conversione senza fonte e comparabilità.
3. **Dimensione informativa del test:** definire le osservazioni necessarie **in funzione della domanda da verificare**. Se esistono baseline e obiettivo statistico, calcolare un campione appropriato. In assenza di baseline, **non presentare un numero arbitrario di click/lead come campione statisticamente valido**: costruire uno *scenario esplorativo*, dichiarando espressamente che non è una prova di efficacia.
4. **Stima:** per modello CPC, `spesa_media_stimata = CPC_applicabile × clic_pianificati`; per modello CPM, `spesa_media_stimata = CPM_applicabile × impression_pianificate / 1000`. Sono **stime condizionali**, soggette a inventory, offerte e targeting. Il minimo Paid coincide con la spesa necessaria per il **test definito e motivato**, se i dati consentono una stima difendibile; altrimenti `budget_minimo = non determinabile`, con dati mancanti e prossimo test necessario.
5. **Fattibilità:** confrontare `paid_minimo` con `budget_paid_disponibile`. Se insufficiente, quantificare il deficit; **non** ridurre automaticamente il test fino a renderlo privo di significato. Se nessun canale Paid è credibile per quel budget, segnalarlo ed eventualmente raccomandare attività non Paid coerenti con l'obiettivo.

La stima deve sempre presentare **fonte, range/scenario, assunzioni e limite**. Una previsione di click/impression non è una previsione di clienti. Quando l'obiettivo è vendite ma non disponiamo di tassi di conversione attendibili, dichiarare **non stimabile il budget minimo per ottenere una vendita**; può comunque essere stimato un budget esplorativo per apprendere.

**Fonti tecniche di riferimento:** Google Ads Keyword Planner distingue storico e previsioni, che dipendono da budget, offerte e qualità degli annunci: https://support.google.com/google-ads/answer/3022575?hl=it ; Google Ads Keyword Planner: https://support.google.com/google-ads/answer/7337243?hl=it . Da verificare nell'implementazione la disponibilità effettiva via API/provider e la compatibilità geografica.

## 5. Risorse: gap analysis senza organigrammi

**L'agente non assegna job title al team.** Stima i *work package* necessari al piano scelto e, per ciascuno, registra `competenza_necessaria`, `ore_settimanali_stimate`, `durata`, `criticità` (`critica`, `importante`, `accessoria`) e `evidenza/assunzione della stima`.

1. Incrocia i work package con le **competenze dichiarate** dal team; la checkbox indica disponibilità presunta, non certifica esperienza o produttività. Competenze non dichiarate → **gap di capacità** oppure dato da confermare.
2. Somma le ore dei pacchetti **potenzialmente svolgibili internamente** e le confronta con le **ore complessive disponibili**, senza simulare un organigramma. Se le ore sono insufficienti, identifica il carico residuo o una parte delegabile. Evitare doppi conteggi fra attività simultanee o dipendenze.
3. Se una **competenza critica** non è coperta, segnala **supporto esterno necessario** anche quando le ore interne sono sufficienti; il solo tempo non sostituisce la competenza.
4. Propone solo le attività da esternalizzare e la modalità più semplice (freelance, agenzia o servizio), con **costo stimato e fonte/preventivo** quando disponibile. Se il costo non è noto: `da quotare`, non €0.
5. Produce una **Gap List ordinata per criticità e dipendenza**, indicando precisamente cosa manca per poter eseguire la strategia. **Non cambia la strategia perché manca una competenza**; se la realizzazione è condizionata a esternalizzazioni, segnala chiaramente tale condizione.

**Economie separate, mai mescolate:**

| Voce | Definizione |
|---|---|
| `paid_media_budget` | Investimento in inserzioni: unico importo confrontato con il campo **Budget pubblicitario Paid** |
| `software_and_data` | Software, API, dati e servizi digitali necessari |
| `external_support` | Freelancer, agenzia, produzione o assistenza esterna necessaria |
| `internal_hours_per_week` | Ore lavorative interne stimate; **non trasformate in costo monetario** salvo richiesta |
| `total_external_cash_requirement` | **Paid + software/dati + supporto esterno**; mostrare totale, senza presumere che il budget Paid finanzi le altre voci |

Se una voce essenziale è sconosciuta, il totale monetario è **parziale**, non fittiziamente completo. In mancanza di un budget complessivo per i costi non Paid, l'agente non dichiara l'intero piano "finanziariamente coperto".

## 6. Pianificazione, orchestrazione e KPI

- Selezionare attività soltanto per canali già giustificati dal Modulo 05; ogni attività ha obiettivo, canale, ICP, dipendenza, trigger (se osservabile), deliverable e metrica.
- **Paid e organic insieme quando necessario**, senza equiparare organic a gratuito né attribuire al Paid una capacità di generare risultati certa.
- **Signal-based:** descrivere fonte/criterio del segnale, possibilità reale di rilevazione, nesso con il bisogno e azione prevista; un'ipotesi di segnale non è una trigger automation operativa.
- Usare KPI congruenti: delivery/visibilità, engagement qualificato, richieste/lead, conversioni e pipeline soltanto se tracciabili. Evidenziare quelli che richiedono un evento o una configurazione non ancora presenti. Google Analytics documenta ad esempio `generate_lead`, `qualify_lead` e `purchase`: https://support.google.com/analytics/answer/9267735?hl=it .
- Definire un piano minimo di apprendimento: cosa misurare, quando controllare, quali condizioni inducono a iterare, fermare o acquisire ulteriori dati. Non usare soglie di successo universali.
- La roadmap è **di attivazione GTM**, non la roadmap tecnica di sviluppo del GTM Engine. Ordina milestone e dipendenze senza produrre automaticamente un piano editoriale, testi di campagne o una piattaforma di esecuzione.

## 7. Due modalità di prodotto

**Offerta disponibile:** utilizzare positioning e messaggi approvati dal Modulo 04, senza creare nuove promesse; piano finalizzato a test, acquisizione o crescita in base all'obiettivo.

**Prodotto/servizio in sviluppo:** nessuna UVP, claim, promessa o copy promozionale. Pianificare attività di ricerca di mercato e validazione del bisogno/interesse, con KPI pertinenti (interviste, feedback, evidenze di domanda, partecipazione a test). Se si ipotizzano asset/canali Paid per reclutare partecipanti alla ricerca, descrivere neutralmente la ricerca senza attribuire al prodotto funzionalità future non dimostrate.

## 8. Delivery e schema concettuale

**Schermata principale minimalista**, massimo cinque sezioni visibili: **Strategia**, **Budget Paid**, **Cosa serve**, **Cosa manca**, **Piano e KPI**. L'utente apre fonti, costi, ipotesi e work package quando interessato; nessun muro di testo, nessun organigramma. Evidenziare quando il piano è `actionable`, `conditional` o `not_feasible`, con motivazione leggibile.

`ExecutionPlan` contiene almeno:

- `project_id`, `run_id`, `source_versions`, `icp_ids`, `objective`, `time_horizon`, `product_state`.
- `recommended_channels`, `activity_packages`, `dependencies`, `observable_triggers`.
- `paid_media_budget_available`, `paid_media_test_minimum` (valore/range o `unknown`), `paid_test_objective`, `paid_cost_assumptions` e `evidence_refs`.
- `software_and_data_cost`, `external_support_cost`, `total_external_cash_requirement` (stato `complete/partial`), `internal_hours_required`, `internal_hours_available`.
- `skills_required`, `skills_available`, `critical_gaps`, `outsourcing_actions`, `gap_priority`.
- `measurement_events`, `primary_kpi`, `secondary_kpis`, `learning_milestones`, `stop_or_review_conditions`.
- `uncertainties`, `limitations`, `decision_status`, `user_approval`, `deck_payload`.

L'output è una **raccomandazione tecnica e strategica controllabile**, non l'avvio automatico di una campagna.

## 9. QA e test di accettazione (obbligatori prima di dichiarare il modulo funzionante)

| Test | Condizione di accettazione |
|---|---|
| **Budget Paid insufficiente** | Mostra deficit e stato condizionato/non fattibile; non promette risultati né riduce il test senza criterio |
| **CPC/CPM o conversioni assenti** | Nessun budget minimo di vendita inventato; scenario esplicitamente esplorativo o `unknown` |
| **Competenze assenti ma budget disponibile** | **La strategia resta invariata**; output indica gap e supporto esterno necessario |
| **Ore insufficienti** | Mostra ore totali mancanti/delegabili senza attribuire job title o duplicare carico |
| **Competenze critiche mancanti** | Segnala gap anche se le ore interne sono sufficienti |
| **Costo esterno ignoto** | `da quotare`, totale di cassa parziale; non dichiara piano coperto |
| **Organic senza budget Paid** | Piano non-Paid ammissibile se strategicamente giustificato; ore e servizi comunque indicati |
| **KPI non tracciabile** | Indica evento/configurazione necessari; non presenta KPI come misurato |
| **B2B microimpresa / B2C familiare** | Nessun organigramma interno artificiale; ICP/buyer mapping adeguato a monte |
| **Prodotto in sviluppo** | Zero UVP/claim/messaging promozionale in piano, UI e deck |
| **Anti-AI-slop** | Azioni specifiche, precondizioni, trade-off, evidenze; no raccomandazioni genericamente intercambiabili |
| **Riproducibilità** | Stessi input, fonti, versioni e parametri → budget/costi deterministici; valutazioni LLM documentate |

**Collaudo strategico:** test su casi simulati con vincoli diversi e almeno un caso reale; revisione esperta per verificare se la strategia è sensata, non solo se i calcoli tornano. Nessun test è dichiarato già eseguito.

## 10. Questioni tecniche rimandate al PRD/TDD

- Schema completo di `Project Brief`, persistenza dei campi e richieste di approvazione.
- Raccolta effettiva di benchmark attuali, accessi API/prezzi fornitori e regole per non confrontare geografie/canali incompatibili.
- Stime delle ore per work package e processo di revisione dei relativi presupposti.
- Implementazione contratti e logging su API/worker Render, Supabase Postgres/Storage e deck python-pptx; le scelte sono definitive, gli accessi e il deploy da collaudare.
- Struttura dei test automatizzati e dataset dei casi di collaudo; nessuna promessa di accuratezza quantitativa prima di misurarla.

---

**Decisione di scope:** tutti i requisiti funzionali del Modulo 06 sono specificati. Lo stato "100%" si riferisce **alla copertura dello scope concordato**, non all'implementazione, all'attivazione di integrazioni o all'efficacia commerciale validata.
