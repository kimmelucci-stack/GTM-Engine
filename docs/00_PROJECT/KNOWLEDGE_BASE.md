# GTM Engine — Marketing Knowledge Base & Source of Truth

**Versione:** 1.0 — Decisioni architetturali funzionali  
**Data:** 24 ottobre 2026  
**Stato:** impostazione approvata; libreria, funzioni Python, monitor e test da realizzare. Non è una specifica TDD né una Knowledge Base già popolata.

## 1. Scopo e distinzioni

La **Source of Truth (SoT)** è il repository GitHub di contenuti, metodologie e playbook **approvati e versionati**, che stabilisce quali regole siano valide. La **Knowledge Base (KB)** comprende framework, playbook, ricerche e registri delle fonti consultabili dagli agenti. Il **RAG** è un'architettura di recupero contestuale: non è sinonimo di Knowledge Base e non richiede sempre embeddings.

**Decisione v1:** nessun RAG vettoriale, embeddings, OpenAI File Search, pgvector o servizio dedicato di indicizzazione. Python seleziona e legge dal filesystem del repository i soli file Markdown necessari all'agente. Questa scelta riduce infrastruttura e complessità, non elimina il controllo di qualità delle fonti.

## 2. Regole di accesso condivise

- **Tutti gli agenti** possono accedere alla KB; ogni agente riceve **solo i playbook e i principi pertinenti** alla sua macrofase e all'attività in corso. Nessun prompt monolitico con l'intera biblioteca.
- Repository: **GitHub + Markdown**; il progetto operativo con Codex usa una copia locale sincronizzata. Obsidian è un editor locale opzionale, **non necessario**.
- **Python** carica i file dal percorso relativo alla root, selezionandoli per ID, disciplina e tipo di attività (mappatura configurata), controlla la versione e registra i file effettivamente usati nell'`AnalysisRun`.
- Gli agenti distinguono tra **regola metodologica**, **fatto esterno supportato da una fonte**, **dato dell'esecuzione GTM** e **ipotesi di interpretazione**. Una KB non è prova che una conclusione sul cliente sia vera.
- Gli LLM **non apprendono permanentemente** dai file consultati: i documenti entrano nel contesto della richiesta. Non vengono modificati pesi o neuroni del modello.
- Un aggiornamento approvato del documento nel repository sostituisce la fonte ufficiale; i risultati già prodotti mantengono la versione dei file consultata e non vengono modificati silenziosamente.

## 3. Libreria iniziale: minima e verificabile

Al rilascio iniziale prevedere una **piccola raccolta curata**, non un crawler di siti indiscriminato. Le categorie sono: principi di marketing; segmentazione/buyer research; positioning/TOV; Search/SEO; Social; Content; Performance; GTM B2B/B2C; metriche e sperimentazione.

Ogni playbook deve rispondere almeno a: **quando applicare il metodo; quando escluderlo; quali dati servono; cosa NON si può dedurre; quali alternative valutare; KPI appropriati; fonti/versione**. Il motore può adottare prima pochi playbook sufficienti per i test pilota, poi ampliarli. Non è necessario coprire ogni disciplina con un volume prefissato di file.

### Fonti candidate da curare (non accessi già integrati)

| Tipologia | Esempi pertinenti | Uso corretto |
|---|---|---|
| Manuali/ricerca fondativa | Libri e materiali legittimamente disponibili, ricerca accademica originale, studi metodologicamente trasparenti | Principi e modelli, contestualizzati al caso |
| Efficacia e strategia | Pubblicazioni IPA/Ehrenberg-Bass, ricerche buyer/B2B con metodologia chiara | Regole e limiti, non leggi universali |
| Documentazione piattaforme | Google Search/Ads, Meta, LinkedIn, provider dati | Come funziona una piattaforma; **non** prova imparziale che sia il canale migliore |
| Evidence di progetto | Dataset versionati di Moduli 01–04 e risultati osservati | Valutazione del caso corrente; **non** trascrivere automaticamente nella SoT generale |

I documenti protetti o non disponibili possono essere rappresentati nel registro da metadati, URL, sintesi autonome e note metodologiche; non presumere di possederne il testo integrale.

## 4. Percorso tecnico v1

```text
GTM_ENGINE/
├── docs/             # scope/architettura/decisioni
└── knowledge/
    ├── core/         # principi trasversali approvati
    ├── playbooks/    # competenze per disciplina e attività
    └── sources/      # registro fonti e riferimenti originali
```

L'implementazione minima può essere una configurazione del tipo `phase → [playbook_ids]`. Un loader Python legge i file Markdown approvati, ne conserva gli identificativi e passa il contenuto all'LLM con istruzioni che distinguono metodologia, dati osservati e ipotesi. Non richiede un server separato, né API per fare embeddings.

**Metadati minimi** per ogni playbook: `id`, `title`, `discipline`, `version`, `status` (`approved/draft/deprecated`), `source_references`, `last_reviewed_at`. Per ogni fonte: `source_id`, `title`, `url`, `publisher`, `publication_date` se disponibile, `last_checked_at`, `methodology_notes`, `applicability`, `status`. Se i documenti sono molto lunghi, si possono creare versioni concise approvate prima di introdurre un indice semantico.

## 5. Governance minima e verifica ogni 45 giorni

- **I file ufficiali sono approvati dall'utente o dal responsabile del progetto**, non riscritti autonomamente dall'agente.
- Verifica leggera **ogni 45 giorni** per le fonti già registrate, senza rielaborare ogni documento con AI: stato URL, eventuale `ETag`/`Last-Modified` o impronta contenuto quando accessibile, esito e ultima verifica. Siti dinamici/anti-bot possono richiedere verifica manuale; una modifica non è automaticamente un cambiamento sostanziale delle conclusioni.
- Implementazione proposta: piccolo script Python eseguibile con GitHub Actions o a richiesta; se la pianificazione a intervalli di 45 giorni non è disponibile direttamente, un controllo quotidiano **solo del calendario/scadenze** può eseguire gli HTTP check esclusivamente sulle fonti scadute.
- **Output:** report delle fonti cambiate/non raggiungibili/da riesaminare. **Mai** sovrascrivere automaticamente i framework e i playbook.
- I dettagli di deploy, permessi, costi reali e periodicità sono da formalizzare nella Development Roadmap. Il costo può essere nullo entro quote disponibili, ma **non** è garantito senza misurazioni.

## 6. Controllo qualità della competenza strategica

Per ciascun agente predisporre casi di test realistici e confrontare raccomandazioni, esclusioni e motivazioni con valutazione umana: fondatezza delle fonti, coerenza col contesto, applicazione dei playbook, comprensione dei trade-off, assenza di metriche inventate. La sola disponibilità della KB non certifica competenza da senior strategist.

## 7. Evolutive espressamente escluse dalla v1

Ingestione automatica indiscriminata dal web, riscrittura autonoma dei playbook, RAG vettoriale, embeddings, indice semantico e database vettoriale personalizzato. Considerarli soltanto se la ricerca semplice sui file mostra limiti concreti. Tracciamento: `docs/00_PROJECT/EVOLUTION_BACKLOG.md`.
