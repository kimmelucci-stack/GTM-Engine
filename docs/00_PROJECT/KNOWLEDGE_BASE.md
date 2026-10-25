# GTM Engine — Marketing Knowledge Base & Source of Truth

**Versione:** 1.0 — Decisioni architetturali funzionali  
**Data:** 24 ottobre 2026  
**Stato:** impostazione approvata; KB-001 implementato come controllo Python a richiesta e testato su fixture. Registro reale, schedulazione e verifica operativa restano da completare; libreria e loader non ancora implementati. Non è una Knowledge Base già popolata.

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
- Implementazione KB-001 al Gate 2: script Python con GitHub Actions o a richiesta; controllo giornaliero **solo del calendario**, HTTP esclusivamente sulle fonti scadute dopo 45 giorni. Verifica e test di accettazione obbligatori prima della release al Gate 8. Errori/tentativi non aggiornano la data dell'ultima verifica riuscita.
- **Output:** report delle fonti cambiate/non raggiungibili/da riesaminare. **Mai** sovrascrivere automaticamente i framework e i playbook.
- Scadenze, test e verifica operativa sono definiti nella `DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md`; permessi, quote e costi effettivi vanno collaudati. Il costo può essere nullo entro quote disponibili, ma non è garantito. Nessun monitor schedulato è attivo. Il comando a richiesta è disponibile, con test descritti sotto.

## 6. Controllo qualità della competenza strategica

Per ciascun agente predisporre casi di test realistici e confrontare raccomandazioni, esclusioni e motivazioni con valutazione umana: fondatezza delle fonti, coerenza col contesto, applicazione dei playbook, comprensione dei trade-off, assenza di metriche inventate. La sola disponibilità della KB non certifica competenza da senior strategist.

## 7. Evolutive espressamente escluse dalla v1

Ingestione automatica indiscriminata dal web, riscrittura autonoma dei playbook, RAG vettoriale, embeddings, indice semantico e database vettoriale personalizzato. Considerarli soltanto se la ricerca semplice sui file mostra limiti concreti. Tracciamento: `docs/00_PROJECT/EVOLUTION_BACKLOG.md`.


## Stato implementazione KB-001 — Gate 2 avviato

`domain/source_refresh.py` definisce registro tipizzato e scadenza; `source_refresh.py` produce report e un registro successivo separato, senza sovrascrivere input o playbook. Registro JSON con i metadati sopra: solo status approved può essere interrogato. L’approvazione nel file è un dato amministrato dal responsabile, non viene assegnata dal checker e non sostituisce futura autenticazione/persistenza. Nessun registro reale approvato è stato creato automaticamente.

Comando: `python -m gtm_engine.source_refresh --registry PERCORSO_REGISTRO --output artifacts/private/source-refresh/NOME_UNICO`. Senza `--live` controlla solo il calendario, senza HTTP/DNS. Con `--live` verifica soltanto fonti scadute e approvate: massimo 20 GET predefiniti (cap configurabile 1–100), timeout 20 secondi, 2 MB per risposta, niente redirect/retry automatici; destinazioni HTTPS senza credenziali/query e controllo DNS pubblico. CLI locale, non API per URL arbitrari; controllo DNS senza pinning socket.

ETag/Last-Modified, 304 con precedente hash verificabile, confronto SHA-256 dei byte; hash diverso richiede revisione, non dimostra modifica semantica. Errori/rate limit mantengono last_checked_at e aggiornano separatamente last_attempted_at/last_error. Fonti non scadute o non approvate non generano richieste. Non misura costi di esecuzione/quote esterne: report con costi nullable.

27 test offline pertinenti superati: confini 44/45/46 giorni, prima verifica, clock UTC, 200/304, hash iniziale/invariato/modificato, timeout/429/errori/redirect, pagina challenge, cap byte/richieste, DNS privato e URL con credenziali vietati. Comando CLI verificato su registro sintetico: zero richieste. Gate 8: registro reale approvato, verifica HTTP osservata e schedulazione ancora da collaudare prima della release.
