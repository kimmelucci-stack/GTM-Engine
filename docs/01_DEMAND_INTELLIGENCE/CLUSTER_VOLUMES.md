# Ricerche annuali su Google e classifiche per bisogno

Decisione aggiornata del proprietario: rappresentare le ricerche su Google su base annuale. `demand-cluster-metrics-v2` somma dodici stime mensili consecutive per ciascuna query, conserva media originale, serie, territorio e periodo, e assegna pari merito ai valori uguali. Serie incomplete restano indisponibili. La somma lorda rimane un dettaglio contabile; il totale distinto del cluster è sconosciuto per sovrapposizioni e copertura. Fino a dieci posizioni per cluster, includendo eventuali pari merito alla soglia. I player organici e gli annunci sono osservazioni SERP separate dal volume delle ricerche. I contratti v1 e le loro impronte restano validi per lo storico. Nessuna nuova raccolta, costo o approvazione implicita.

## Che cosa misurano le fonti

Il volume proviene dalle statistiche storiche Google Ads Keyword Planner. Descrive ricerche su Google per termini e varianti vicine; non esistono due volumi separati, organico e pubblicitario, da sommare. Il connettore SERP rileva posizioni organiche, Local Pack e presenza di annunci. CPC e indice di concorrenza Ads riguardano gli inserzionisti; l'indice non misura difficoltà SEO né domanda unica.

Google restituisce stime arrotondate. L'endpoint Search Volume non offre una modalità broad/exact/phrase capace di trasformare una formulazione in tutte le ricerche del bisogno. L'etichetta broad del workflow è descrittiva. Il numero delle aziende residenti non verifica la frequenza di una query specifica. Assenza di stima, zero e errore tecnico rimangono tre stati distinti.

## Calcolo annuale

1. Usare una sola raccolta live, stesso territorio, lingua e rete Google senza partner. Comune e provincia mantengono etichette distinte; il luogo scritto nella query non sostituisce il target geografico.
2. Per ciascuna query richiedere esattamente dodici mesi unici e consecutivi con stime intere non negative. Duplicati, buchi, null e valori non validi impediscono il totale annuale. Lo zero esplicito resta valido.
3. Sommare le dodici stime. La media mensile arrotondata del provider moltiplicata per dodici non è un sostituto della serie. Conservare media originaria, valori mensili e riferimenti al raw; l'annuale è un derivato storico, non una previsione o un numero esatto di persone.
4. Classificare valori comparabili in ordine decrescente. A valori uguali assegnare la stessa posizione; alfabetico solo per visualizzare i pari merito. Includere l'intero pareggio alla decima posizione, dichiarandolo. Non inventare termini per completare dieci righe.
5. Non presentare la somma delle formulazioni come domanda unica del cluster. Varianti identiche nella serie sono un segnale di sovrapposizione, senza autorizzare una deduplicazione numerica arbitraria. Il totale distinto resta null con causa esplicita.
6. Serie con periodi diversi impediscono classifica e somma comune. Periodi e geografie sono verificati prima del confronto. Le metriche originali e gli snapshot approvati restano immutabili.

## Confronto gratuito con Keyword Planner

Confrontare identico elenco, periodo, territorio e rete; documentare ogni differenza di lingua o filtro. Un account che mostra fasce non permette la verifica di valori puntuali. Un valore numerico presente nell'export va confrontato con la fascia mostrata dall'interfaccia prima di interpretarlo: non trasformarlo automaticamente in una stima precisa. Conformità sulla presenza/assenza di misure e conformità numerica sono verifiche diverse. Nessuna attivazione di campagne o spesa per ottenere precisione maggiore senza autorizzazione.

## Tool e Deck

`annual_cluster_metrics` costruisce la proiezione v2 sopra il contratto mensile v1 immutato. Le route di lettura verificano proprietario, raccolta, versione e revisione. Il supplemento editoriale conserva e verifica prima l'impronta v1 salvata; solo dopo deriva l'annuale. Nessuna riscrittura del binding storico.

Demand > Evidenze mostra copertura e classifiche annuali; metodo, serie mensili, media originale, CPC, concorrenza Ads e somma lorda sono dettagli consultabili. Il totale unico del bisogno resta sconosciuto. La compatibilità geografica e lo stato della revisione restano visibili.

Deck presenta i valori per query nella fase Domanda, con unità e Comune espliciti. Il periodo esatto e la provenienza restano nelle note secondo la decisione editoriale del proprietario. Conclude la fase con lettura del campione, alternative plausibili e prescrizioni condizionate; nessuna equivalenza fra volume basso del campione e inesistenza del mercato.

## Fonti metodologiche

- [Google: metriche storiche](https://support.google.com/google-ads/answer/3022575?hl=it): stime, varianti vicine e arrotondamenti.
- [DataForSEO: Search Volume](https://docs.dataforseo.com/v3/keywords_data-google_ads-search_volume-live/): campi, geografia e serie della risposta.
- [DataForSEO: tipi di corrispondenza](https://dataforseo.com/help-center/sv-broad-exact-phrase-match): limite della distinzione broad/exact/phrase nei volumi.
- [DataForSEO: SERP organica](https://docs.dataforseo.com/v3/serp/google/organic/live/advanced/): osservazioni dei risultati, distinte dalla frequenza storica.

## Controlli e limiti

Test offline: somma della serie distinta da media per dodici, mesi incompleti/duplicati/null, zero, periodo, territorio, pareggi e immutabilità. La riproduzione del raw non certifica la precisione della fonte o l'intera copertura del mercato. Rilascio e prova autenticata richiesti prima di dichiarare la vista online.

I rifiuti tecnici del provider conservano raw e costo e rendono la raccolta partial; nessun riempimento con null validi e nessun retry automatico. Le richieste nuove restano soggette a cap, riserva, quota e autorizzazione.
