# GTM Engine — Evolution Backlog

**Versione:** 0.3 — consolidamento del 25 ottobre 2026
**Origine:** decisioni del 24 ottobre 2026.
**Scopo:** registro canonico di evolutive e KB-001 assegnato alla roadmap. Nessuna voce implementata o attivata. La copia v0.1 precedentemente in `docs/` è rimossa; storia recuperabile da Git. Obiettivi e criteri utili erano già inclusi nella v0.2; il riferimento v0.1 a un indice RAG si riferisce esclusivamente a evolutive future KB-002/003, mai all'MVP.

## KB-001 — Verifica periodica delle fonti (45 giorni)

- **Stato:** controllo leggero assegnato al Gate 2; test e verifica operativa al Gate 8 prima della release, secondo `DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md`. Non ancora implementato né schedulato.
- **Obiettivo:** controllare se le fonti registrate della Marketing Knowledge Base sono cambiate o non sono più raggiungibili, senza riscrivere automaticamente la conoscenza approvata.
- **Ambito iniziale:** sole fonti inserite nel registro ufficiale della knowledge base; non crawling indiscriminato del web.
- **Cadenza:** ogni 45 giorni dall'ultima verifica effettiva per fonte.
- **Procedura minima:** leggere il registro; eseguire richieste HTTP condizionali (ETag/Last-Modified quando disponibili) o confronto hash normalizzato; registrare `last_checked_at`, esito, cambiamenti e link; mostrare un rapporto sintetico.
- **Strumenti:** Python e GitHub Actions/a richiesta, senza nuovi servizi. Schedulazione giornaliera del solo calendario, HTTP solo per fonti scadute a 45 giorni da una verifica riuscita. Tentativi/errori separati da `last_checked_at`; test dei confini e delle risposte HTTP nella roadmap.
- **Esclusioni:** nessun aggiornamento automatico dei playbook; nessuna nuova fonte inserita senza qualifica; **nessun RAG o reindicizzazione** nella prima versione.
- **Criterio d'accettazione:** rapporto di link modificati/non raggiungibili; nessuna modifica non approvata ai documenti ufficiali; costi API e quote visibili.
- **Nota costi:** controlli HTTP di poche decine di URL possono avere costo incrementale nullo entro le quote di GitHub Actions; parsing con AI, ricerca web a pagamento e nuove indicizzazioni si valutano separatamente. Non è possibile garantire un costo fisso senza volumi misurati.

## KB-002 — Ingestione e aggiornamento automatici della Knowledge Base

- **Stato:** evolutiva rinviata; non inclusa nell'MVP.
- **Obiettivo:** trovare nuove fonti, valutarne metodologia/pertinenza, proporre modifiche ai playbook e ottenere approvazione; un eventuale indice di ricerca potrà essere aggiunto solo se giustificato in futuro.
- **Dipendenze:** registro e qualità delle fonti, test strategici, revisione umana, audit/versionamento.
- **Vincolo:** la Source of Truth rimane nel repository; i documenti aggiornati automaticamente non possono diventare approvati senza il controllo previsto.

## KB-003 — Ricerca semantica / RAG vettoriale opzionale

- **Stato:** non previsto nella prima versione.
- **Trigger per rivalutare:** crescita significativa dei file, ricerca per metadati/manuale insufficiente o problemi dimostrati nel recupero dei playbook.
- **Alternative future:** ricerca full-text, retrieval ibrido o servizio RAG gestito; selezione solo dopo test su precisione, complessità e costi.
- **Vincolo:** non modificare i pesi del LLM e non confondere embeddings con fine-tuning; Source of Truth sempre nel repository.

## Regole di gestione del backlog

1. Ogni nuova evolutiva avrà ID, valore, priorità, dipendenze, costo stimato e criterio d'accettazione.
2. Nessuna voce è implementata per il solo fatto di essere presente qui.
3. Le voci approvate per una release passano alla Development Roadmap, mantenendo il riferimento all'ID originale.

## Riferimenti tecnici (consultati 24 ottobre 2026)

- GitHub Actions, eventi schedulati: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub Actions, utilizzo e fatturazione: https://docs.github.com/en/actions/concepts/billing-and-usage
- Architettura KB approvata: `KNOWLEDGE_BASE.md`. Nessun servizio File Search previsto in v1.
- Riferimento recuperato dal backlog v0.1, solo per eventuali valutazioni future: https://developers.openai.com/api/docs/pricing . Non implica uso o attivazione di File Search nell'MVP.
