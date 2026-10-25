# GTM Engine — Evolution Backlog

**Versione:** 0.2  
**Data:** 24 ottobre 2026  
**Scopo:** tenere traccia delle funzionalità rinviate e degli interventi opzionali da calendarizzare nella Development Roadmap. Nessuna voce è già sviluppata o attivata.

## KB-001 — Verifica periodica delle fonti (45 giorni)

- **Stato:** **previsto per la prima release solo come controllo leggero**, se semplice da implementare; dettaglio e collocazione nella Development Roadmap ancora da fissare.
- **Obiettivo:** controllare se le fonti registrate della Marketing Knowledge Base sono cambiate o non sono più raggiungibili, senza riscrivere automaticamente la conoscenza approvata.
- **Ambito iniziale:** sole fonti inserite nel registro ufficiale della knowledge base; non crawling indiscriminato del web.
- **Cadenza:** ogni 45 giorni dall'ultima verifica effettiva per fonte.
- **Procedura minima:** leggere il registro; eseguire richieste HTTP condizionali (ETag/Last-Modified quando disponibili) o confronto hash normalizzato; registrare `last_checked_at`, esito, cambiamenti e link; mostrare un rapporto sintetico.
- **Strumenti candidati:** Python e GitHub Actions. Per intervalli esatti di 45 giorni, una schedulazione giornaliera può avviare il solo controllo delle fonti la cui data `last_checked_at` abbia superato 45 giorni; evitare di interrogare tutte le fonti ogni giorno.
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
