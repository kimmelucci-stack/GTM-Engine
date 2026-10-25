# GTM Engine — Project Scope

**Versione:** 0.6 — Consolidamento documentale del 25 ottobre 2026
**Data delle decisioni funzionali:** 24 ottobre 2026
**Stato:** Moduli 01–07 definiti; stack approvato; Gate 0 verificato e Gate 1A DataForSEO PASS_WITH_LIMITATIONS. Gate 1B PASS_WITH_LIMITATIONS sul campione tecnico di cinque siti; nessun modulo end-to-end e Meta in attesa, Openapi non collaudato e fonti pubbliche Gate 1E parzialmente verificate. Stato operativo in `docs/00_PROJECT/HANDOFF_TO_CODEX.md`.

## 1. Visione

Costruire un framework/software modulare per automatizzare quanto più possibile le analisi e le attività di strategia Go-To-Market relative a prodotti o servizi, riutilizzabile per clienti, settori e territori differenti senza riprogrammare il sistema per ogni progetto.

Il sistema deve raccogliere dati da fonti identificabili, eseguire analisi riproducibili, interpretare i risultati mediante agenti AI coordinati e produrre **sempre una presentazione/deck finale**. Il deck deve essere basato su risultati strutturati e tracciabili, non soltanto su testo generato liberamente.

## 2. Obiettivi di prodotto

1. Configurare un progetto GTM per prodotto/servizio, cliente e mercato di riferimento.
2. Avviare una pipeline modulare di analisi e strategia, anche articolata in più fasi.
3. Ridurre attività manuali mediante agenti AI e funzioni deterministiche.
4. Registrare risultati intermedi, metriche, fonti, limiti e interpretazioni.
5. Visualizzare dataset, cluster e insight in interfaccia.
6. Generare un deck finale riutilizzando gli output di ciascuna fase.
7. Consentire l'adattamento a nuovi clienti tramite configurazioni, non modifiche ad hoc del codice.

## 3. Macrofasi definite

| ID | Macrofase | Obiettivo / output indicativo | Stato |
|---|---|---|---|
| 01 | Demand Intelligence | Domanda di ricerca, linguaggio degli utenti, keyword, trend, prime evidenze sui competitor | Scope funzionale disponibile |
| 02 | Market & Competitive Intelligence | Scenario di mercato, competitor, offerte e posizionamento | Scope funzionale e scoring sperimentale disponibili |
| 03 | UVP & ICP Intelligence | Working UVP, segmentazione, profili ICP e Buying Committee | Scope funzionale disponibile |
| 04 | Value Proposition & Positioning | Alternative, differenziazione, fit, posizionamento e messaging; modalità in sviluppo analitica | Scope funzionale disponibile |
| 05 | Channel & GTM Strategy | Scelta e priorità dei canali per ICP, combinazioni inbound/outbound/signal-based | Scope funzionale disponibile |
| 06 | GTM Execution Planning | Attività, priorità, KPI, budget Paid e gap operativi | Scope funzionale definito |
| 07 | GTM Strategy Deck | Presentazione finale basata sulle evidenze prodotte | Scope definito; PPTX modificabile obbligatorio |

**Confine MVP approvato:** analisi, strategia e pianificazione GTM; nessun avvio automatico di campagne, prospecting o outreach. Il Modulo 06 progetta l'esecuzione, non la effettua.

## 4. Modello operativo

- **Project Brief:** configurazione trasversale comune alle fasi (prodotto/servizio o idea, cliente, target inizialmente ipotizzato, geografia, lingua/mercato e vincoli). Il target iniziale non equivale all’ICP validato nel Modulo 03. Flag visibile **«Il prodotto o servizio è ancora in fase di sviluppo?»**: se Sì, la UVP del Modulo 03 è saltata e il Modulo 04 produce soltanto analisi di opportunità, senza proposition/claim/messaggi promozionali.
- **Agente per macrofase:** scelta progettuale condivisa; un agente non deve essere creato per ogni singola operazione. Gli agenti coordinano strumenti specializzati.
- **Knowledge Base condivisa:** framework e playbook Markdown approvati in GitHub, caricati selettivamente via Python a seconda del compito. Le evidenze specifiche del cliente e i dataset di esecuzione non diventano automaticamente conoscenza generale. Dettagli in `docs/00_PROJECT/KNOWLEDGE_BASE.md`.
- **Esecuzione controllata:** il modello AI interpreta e sceglie strumenti; codice tradizionale esegue API, trasformazioni e controlli. Le chiamate devono essere osservabili e riproducibili.
- **Output interoperabili:** dati strutturati e versionati con fonti, località, date, parametri e limitazioni. Le revisioni sostanziali di offerta/UVP/target devono segnalare gli output precedenti potenzialmente obsoleti e consentire una rivalutazione o riesecuzione esplicita.
- **Analytics e deck:** dati grezzi e derivati vengono conservati separatamente per permettere nuovi cluster e visualizzazioni senza dover necessariamente ripetere ogni interrogazione.

## 5. Architettura approvata MVP

| Livello | Tecnologie/orientamento | Stato |
|---|---|---|
| Frontend | React + TypeScript + Vite | Approvato |
| Hosting frontend | Vercel | Scelto; piano e limiti da verificare in fase di deploy |
| Backend | Python 3.12+ + FastAPI + Pydantic su Render | Approvato; deploy da collaudare |
| Agenti | OpenAI Responses API, Structured Outputs e tool calling, orchestrazione Python per modulo | Approvato; integrazione da collaudare |
| Elaborazione dati | Python deterministico per normalizzazione, scoring e pianificazione | Approvato |
| Database applicativo | **Supabase (PostgreSQL)** | Scelta architetturale di riferimento; piano e integrazione da verificare |
| Orchestrazione | Worker Python separato su Render, job persistiti e polling su Postgres | Approvato; niente n8n/Redis/Celery nell'MVP |
| Storage | Supabase Storage privato per raw e deliverable | Approvato; accessi da collaudare |
| Repository e Source of Truth KB | GitHub + Markdown | Scelto: documenti approvati, framework e playbook condivisi |
| Knowledge Base agenti | File Markdown selezionati e letti da Python | Scelto per la prima versione: **senza RAG vettoriale, embeddings o File Search** |
| Sviluppo | Codex desktop e PyCharm, cartella locale condivisa | Scelto come workflow |
| Deck | PPTX nativo modificabile via python-pptx; LibreOffice headless per preview/QA | Approvato; implementazione da verificare |
| Hosting backend/job | Render API e background worker separati | Approvato; piano/costi/deploy da verificare |

**Topologia:** Vercel ospita il frontend; Render ospita API e worker; Supabase persiste dati e artefatti. Dettagli e contratti in `docs/00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md`; le scelte non equivalgono a connessioni operative.

## 6. Requisiti trasversali di qualità

- **Vincolo economico del proprietario (25 ottobre 2026):** percorso GTM completo per prodotto/servizio, dall'acquisizione dati al contenuto analitico/strategico e deck, obiettivo 10 USD ed estremo massimo 15 USD per run. Misurare provider, AI e altri costi attribuibili all'esecuzione; non dichiarare il target raggiunto senza prova. Il solo pilota Gate 1A ha autorizzazione separata di 5 USD complessivi, non per richiesta.
- Nessuna metrica inventata dal modello AI.
- Separazione tra dato osservato e interpretazione/inferenza.
- Ogni dataset include fonte, timestamp, località, lingua e parametri rilevanti.
- Gestione esplicita di errori, risposte mancanti, limiti degli endpoint e copertura incompleta.
- Possibilità di ispezionare risultati intermedi e risalire alle evidenze del deck; nessuna affermazione strategica presentata come prova senza fonte. Revisioni sostanziali del brief/flag/UVP segnalano gli output dipendenti potenzialmente obsoleti.
- Configurabilità per nuovi clienti e progetti.
- Interfaccia accessibile via web, **pulita e minimalista**: indicatore di workflow visibile in linguaggio comprensibile, etichette brevi, stati reali, output sintetici; dettagli/fonti/razionali apribili su richiesta, non testi invasivi. Hosting delle componenti operative da verificare.

## 7. Output del progetto

1. Applicazione web con interfaccia per configurare e avviare le analisi.
2. Motore di analisi e agenti per ciascuna macrofase.
3. Archiviazione di raw data, risultati elaborati, cluster e insights.
4. Dashboard di analisi.
5. **Deck GTM finale**, generato dagli output strutturati delle fasi.
6. Documentazione funzionale, tecnica e istruzioni del repository per Codex.

## 8. Documentazione e sviluppo

La documentazione approvata è nel repository, accessibile a Codex e PyCharm. Setup locale in `README.md`, istruzioni permanenti in `AGENTS.md`, gate e attività del proprietario nella roadmap. Origine: progettazione nel precedente ambiente ChatGPT; prove storiche conservate nell'audit.

Documenti previsti:
- Project Scope (questo documento).
- Dettagli implementativi dei contratti, senza riaprire le macrofasi approvate.
- PRD dettagliato per macrofase (prima Demand Intelligence).
- TDD e schemi dati/API, dopo le decisioni funzionali.
- Istruzioni operative per Codex e guida setup/deployment.

## 9. Tempistiche — stime preliminari, non impegni

- Obiettivo discusso: circa 20 ore per un prototipo end-to-end *fortemente limitato*.
- Stima preliminare proposta per un tool multi-fase: **100–180 ore**, a forte incertezza e dipendente da perimetro, affidabilità attesa, integrazioni, hosting e complessità del deck.
- Queste sono stime storiche, non una pianificazione vigente; la roadmap richiede una stima basata sui risultati effettivi del Gate 1. Macrofasi e confine MVP sono definiti.

## 10. Decisioni / questioni aperte

**Scelte e indirizzi già espressi**
- Documentazione nel progetto ChatGPT, poi repository locale GitHub per sviluppo in Codex.
- Frontend React ospitato su Vercel.
- Un AI Agent per ciascuna macrofase, con orchestrazione Python e senza n8n nell'MVP.
- Output finale sempre costituito da un **deck modificabile**.
- Target iniziale registrato nel Project Brief e riutilizzato dai moduli; il Modulo 03 produce ICP motivati da evidenze e può suggerire revisioni delle ipotesi iniziali.

**Dettagli di implementazione e collaudo, non decisioni di stack aperte**
- Perimetro fissato: strategia e piano senza invio automatico; applicare il vincolo ai Moduli 05–06.
- Documentare nel PRD l’interfaccia di configurazione budget/obiettivi per il Modulo 05; in mancanza di valori non produrre stime economiche arbitrarie.
- Schemi tecnici del Project Brief, usando i campi e i confini funzionali già approvati.
- Implementare dipendenze e approvazioni previste dagli scope e dalla roadmap.
- Implementare python-pptx con Main Cover, Section Cover opzionali e due famiglie contenuto del Modulo 07; verificare layout ed editabilità.
- Implementare worker Render e persistenza Supabase secondo architettura approvata.
- Gestione di versioni e ri-esecuzioni parziali.

---

*Questo documento è deliberatamente uno scope: non descrive come implementare ogni endpoint né dichiara già testate funzionalità ancora da validare.*


## 11. Regole globali aggiornate — modalità, buyer mapping e UX

**Due modalità, selezionate nel Project Brief**

- **Prodotto/servizio disponibile:** Modulo 03 con sezione `UVP` e chat; Modulo 04 con differenziazione, positioning e messaging condizionati alla presenza di prove.
- **Prodotto/servizio in sviluppo:** Modulo 03 **salta UVP** e individua ICP da bisogno/domanda + competitor + ricerca; Modulo 04 restituisce alternative, gap, opportunità e requisiti potenziali, **senza UVP, claim, statement o messaging**, anche nel deck. L'analisi di domanda e concorrenza dei Moduli 01–02 non cambia. L'assenza di unicità in un prodotto disponibile *non* attiva automaticamente questa modalità.

**Target B2B/B2C:** nel B2B l’output principale è il **buying committee per job title concreti**, selezionati da tutti i reparti pertinenti, non solo board/C-level. Includere possibili promotori, influenzatori, valutatori, coordinatori, referenti tecnici, specialisti, assistenti e utilizzatori coinvolti, oltre a decisori/acquisti/budget. Reparti e funzioni operative sono attributi di supporto, non sostituti del titolo. Autorità e ruolo di acquisto non sono certi dal solo titolo. Directory interna versionata ed estensibile; ESCO non necessario. L’eventuale approccio descrive punto d’ingresso, sequenza e prove da presentare, senza invii automatici. Nel B2C l'unità d'analisi può essere il consumatore singolo oppure il nucleo/household: coppia, famiglia nucleare, monoparentale, allargata/multigenerazionale e altre configurazioni pertinenti; i ruoli relazionali e la dinamica di scelta non devono essere stereotipati. Non generare contatti nominativi. Gli ATECO, **massimo tre esempi** per ICP business italiano, non sono classificazioni applicabili alle famiglie B2C.

**Regola UX unica per tutti i moduli:** workflow visibile in italiano semplice, senza gergo tecnico; mostrare **fase corrente, stato reale, output chiave e azione necessaria**. Dettagli e fonti apribili (progressive disclosure). Non mostrare percentuali fittizie o step non pertinenti alla modalità. Messaggi e TOV naturali, **soprattutto in italiano**, con controllo anti-copy generico.

**Vincoli visuali successivi del proprietario:** riferimento prioritario all'app Attio per tipografia e struttura operativa, Inter variabile caricato localmente con licenza OFL, gerarchia sobria e viste dati confrontabili. **Mai frecce nelle CTA**, né glifi né icone direzionali decorative nei pulsanti/link d'azione. Non confondere font del sito marketing con quelli dell'app, né una dichiarazione CSS con un font effettivamente caricato. Proposte UX/UI da valutare prima di estenderle; nessuna approvazione implicita del design.

**Stato di maturità:** tutti gli scope sono documenti funzionali. Nessuna integrazione, workflow AI o formula di scoring è dichiarata empiricamente validata. Il deck modificabile resta obbligatorio in entrambe le modalità, ma segue i vincoli di output applicabili.


## 12. Decisioni aggiuntive — Modulo 05 e Knowledge Base

- **Modulo 05 approvato a livello funzionale:** leggere contesto dei Moduli 01–04 e scegliere una strategia di acquisizione, **un canale primario e fino a due complementari**, solo quando sostenibili. Canale ≠ tattica ≠ segnale; confronto qualitativo motivato, **nessuno score arbitrario 0–100**, nessun CAC/CPL/conversion rate inventato. Specifica: `docs/05_CHANNEL_GTM_STRATEGY/SCOPE.md`.
- **Marketing Source of Truth:** repository GitHub di framework/playbook/versioni approvati; **Knowledge Base:** insieme più ampio di conoscenze e fonti consultabili. Agenti leggono via Python solo i file pertinenti, sulla base dei metadati e delle regole del compito. **Non implementare RAG vettoriale, embeddings, pgvector o OpenAI File Search nella prima versione.**
- **Marketing Knowledge Base trasversale:** accessibile a tutti gli agenti, con regole generali e playbook specifici. Avere documenti non equivale ad avere decisioni corrette: prevedere test strategici con valutazione umana. Fonte e metodologia vanno tracciate.
- **Controllo fonti KB:** controllo leggero delle fonti registrate **ogni 45 giorni**, KB-001: implementazione al Gate 2, test di accettazione e verifica operativa al Gate 8 prima della release. Solo rilevazione modifiche/link e report, nessuna riscrittura dei playbook. Evolutive complesse nel backlog canonico.
- **Per Codex:** `AGENTS.md` e Gate 0 sono realizzati; verificare la foundation dopo il consolidamento, poi procedere ai gate di accesso secondo roadmap. Le prove API del precedente ambiente non certificano il runtime corrente.
- **Stato realizzativo:** nessun agente applicativo, connettore o source-monitor è dichiarato operativo. Render ospiterà backend/worker; Supabase persiste job/dati/storage. Sono scelte definitive, non deploy già eseguiti.
