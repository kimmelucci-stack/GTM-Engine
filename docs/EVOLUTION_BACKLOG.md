# GTM Engine — Evolution Backlog

**Versione:** 0.1  
**Data:** 24 ottobre 2026  
**Scopo:** tenere traccia delle evolutive deliberate ma non ancora incluse nell'implementazione corrente. Le voci non sono funzionalità già sviluppate o schedulate.

## KB-001 — Verifica periodica delle fonti (45 giorni)

- **Stato:** proposta approvabile per MVP leggero; implementazione da pianificare nella Development Roadmap.
- **Obiettivo:** controllare se le fonti registrate della Marketing Knowledge Base sono cambiate o non sono più raggiungibili, senza riscrivere automaticamente la conoscenza approvata.
- **Ambito iniziale:** sole fonti inserite nel registro ufficiale della knowledge base; non crawling indiscriminato del web.
- **Cadenza:** ogni 45 giorni dall'ultima verifica effettiva per fonte.
- **Procedura minima:** leggere il registro; eseguire richieste HTTP condizionali (ETag/Last-Modified quando disponibili) o confronto hash normalizzato; registrare `last_checked_at`, esito, cambiamenti e link; mostrare un rapporto sintetico.
- **Strumenti candidati:** Python e GitHub Actions. Per intervalli esatti di 45 giorni, una schedulazione giornaliera può avviare il solo controllo delle fonti la cui data `last_checked_at` abbia superato 45 giorni; evitare di interrogare tutte le fonti ogni giorno.
- **Esclusioni:** nessun aggiornamento automatico dei playbook; nessuna nuova fonte inserita senza qualifica; nessuna reindicizzazione automatica indiscriminata.
- **Criterio d'accettazione:** rapporto di link modificati/non raggiungibili; nessuna modifica non approvata ai documenti ufficiali; costi API e quote visibili.
- **Nota costi:** controlli HTTP di poche decine di URL possono avere costo incrementale nullo entro le quote di GitHub Actions; parsing con AI, ricerca web a pagamento e nuove indicizzazioni si valutano separatamente. Non è possibile garantire un costo fisso senza volumi misurati.

## KB-002 — Ingestione e aggiornamento automatici della Knowledge Base

- **Stato:** evolutiva rinviata; non inclusa nell'MVP.
- **Obiettivo:** trovare nuove fonti, valutarne metodologia/pertinenza, proporre modifiche ai playbook, ottenere approvazione e riallineare l'indice RAG.
- **Dipendenze:** registro e qualità delle fonti, test strategici, revisione umana, audit/versionamento.
- **Vincolo:** la Source of Truth rimane nel repository; i documenti aggiornati automaticamente non possono diventare approvati senza il controllo previsto.

## Regole di gestione del backlog

1. Ogni nuova evolutiva avrà ID, valore, priorità, dipendenze, costo stimato e criterio d'accettazione.
2. Nessuna voce è implementata per il solo fatto di essere presente qui.
3. Le voci approvate per una release passano alla Development Roadmap, mantenendo il riferimento all'ID originale.

## Riferimenti tecnici (consultati 24 ottobre 2026)

- GitHub Actions, eventi schedulati: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- GitHub Actions, utilizzo e fatturazione: https://docs.github.com/en/actions/concepts/billing-and-usage
- OpenAI API pricing (File Search e modelli): https://developers.openai.com/api/docs/pricing
