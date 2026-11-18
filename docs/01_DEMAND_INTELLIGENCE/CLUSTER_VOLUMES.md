# Volumi comunali e prime dieci query per cluster

Decisione del proprietario, 18 novembre 2026: Demand deve presentare i volumi mensili per cluster di ricerca sul Comune selezionato e le dieci query con più ricerche mensili in ciascun cluster. La classifica riguarda query Google; i player SERP appartengono a una vista distinta.

## Metodo

1. Definire i cluster per bisogno/intento, mantenendo insieme le formulazioni broad e locali dello stesso bisogno. Non costruire gruppi per singolo modificatore né generare frasi per riempire dieci posizioni. Le assegnazioni correnti derivano dalla revisione salvata; una nuova vista non approva né modifica i gruppi.
2. Usare misure della stessa raccolta, Comune, lingua, rete Google senza partner e periodo. Il Comune deve essere verificato nel catalogo dell'endpoint. Il luogo scritto nella query è separato dal territorio della misura. Una misura provinciale conserva tale etichetta e non soddisfa il requisito comunale.
3. Deduplicare solo le identità lessicali già normalizzate. Una query appartiene a un solo cluster. Misure multiple ambigue, periodi diversi, dati simulati, valori invalidi e territori incompatibili sono esclusi dal calcolo. Le fonti originali restano immutabili.
4. Mostrare **somma lorda dei volumi disponibili** per cluster, unità **ricerche medie mensili stimate su Google**, copertura misurata/totale, periodo e stato. La somma include tutte le query misurate del cluster, anche oltre la decima. È un indicatore derivato del campione: le varianti vicine possono sovrapporsi. Non rappresenta persone uniche, ricerche deduplicate o domanda totale del mercato. Il totale corretto per sovrapposizioni rimane indisponibile senza prove del raggruppamento della fonte.
5. Ordinare le query con valore numerico per volume decrescente, poi testo normalizzato per gli ex aequo, e mostrare le prime dieci. Lo zero esplicitamente restituito è numerico; un valore assente rimane fuori classifica. La classifica descrive il campione misurato, senza affermare che siano le prime dieci dell'intero mercato.
6. Con meno di dieci misure, indicare quante sono disponibili e il requisito ancora aperto. I valori mancanti non diventano zero. Le ulteriori candidate richiedono pertinenza, approvazione e misurazione autorizzate; nessuna ricerca, spesa o nuova approvazione parte dalla lettura.

Questa regola introduce una proiezione quantitativa esplicitamente lorda. Supera il divieto generico di qualunque somma nelle sole viste per cluster; conserva il divieto di presentare la somma delle varianti come domanda unica. Le singole misure, le serie e gli snapshot approvati restano invariati.

## Contratto e superfici

`demand-cluster-metrics-v1` è una funzione deterministica condivisa. La lettura autenticata `/projects/{project_id}/demand/runs/{run_id}/classifications/{classification_id}/clusters` verifica proprietario, raccolta, classificazione e revisione. Non scrive dati né invoca provider.

In Demand > Evidenze: riepilogo per cluster, volume e copertura visibili; espansione per le dieci query e i valori, dettaglio separato per le assenze. L'etichetta geografica deriva dal catalogo originale; gruppi storici e non approvati sono segnalati.

Deck usa `deck_cluster_rows` della stessa proiezione. La fase Domanda espone cluster, classifica, unità, territorio e periodo; interpreta la copertura prima di raccomandare un canale. Vietati grafici o tabelle quantitative composti da sole assenze. Una classifica incompleta o provinciale lascia aperto il requisito comunale: la sola compilazione del software non chiude l'analisi.

## Definizioni delle fonti

- [Google Ads: metriche storiche](https://support.google.com/google-ads/answer/3022575?hl=en): media mensile della keyword e delle varianti vicine, dipendente da periodo, territorio e rete; valori arrotondati. Il tipo di corrispondenza di una campagna non trasforma la metrica storica in domanda broad complessiva.
- [DataForSEO: Search Volume](https://docs.dataforseo.com/v3/keywords_data-google_ads-search_volume-live/): endpoint di acquisizione, ambito geografico e campi della risposta. Il fornitore tecnico compare nelle note di provenienza; Google identifica la piattaforma osservata.

## Verifica

Test sintetici separati dalla qualità dei dati reali: ordinamento/top ten, intero totale del campione, null/zero, esclusività dei gruppi, duplicati, territorio, lingua, rete, periodi incompatibili e immutabilità. Il rilascio richiede build e controllo autenticato della versione online; non basta un test locale. Una nuova raccolta segue ledger, cap, riserve e autorizzazioni esistenti.
