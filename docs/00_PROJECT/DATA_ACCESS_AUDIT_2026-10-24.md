# GTM Engine - Audit accessibilita dati: registro e archivio

Consolidamento e prove repository: 25 ottobre 2026. Le prove del 24 ottobre appartengono al precedente ambiente; sono conservate nelle sezioni storiche. Nessuna chiamata durante la bonifica documentale; successivamente Gate 1A eseguito nel repository come segue. Scelte correnti: [matrice](PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md) e [architettura](TECHNOLOGY_STACK_AND_ARCHITECTURE.md). Foundation locale/CI: [Gate 0](GATE_0_VALIDATION.md).

## Gate 1A — prove nel repository, 25 ottobre 2026

**Esito accessibilità: PASS_WITH_LIMITATIONS. Qualità complessiva dati: partial.** Tutti i tredici campioni previsti (dodici storici più volume nazionale) hanno restituito dati via richieste autenticate. HTTP 200 e codici task 20000 sui risultati; reviews task POST 20100 seguito da GET 20000. Un approfondimento SERP PAA separato è registrato con query distinta. Nessuna equivalenza tra successo di accesso e completezza/validità strategica del dato.

| Campione | Riscontro nel repository | Qualità / limite |
|---|---|---|
| Catalogo località IT | 10.862 record località; codice Torino presente | Numero di record, non conteggio certificato di sole città; catalogo può cambiare |
| Volume/CPC città | Un risultato su Torino, geografia richiesta/effettiva coincidente | Campione singola keyword, non validazione del mercato |
| Volume/CPC regione | Un risultato su Piemonte, geografia coincidente | Non estendere a tutte le regioni |
| Volume/CPC nazione | Un risultato su Italia, geografia coincidente | Non mescolare né sommare livelli geografici |
| Keyword ideas | 5 risultati | Campione ridotto |
| Search intent | Un risultato con probabilità | Classificazione modellistica, non acquisto osservato |
| Autocomplete | 15 suggerimenti | Nessun volume attribuito automaticamente |
| SERP organica iniziale | 9 risultati organici, PAA non presente | Feature non garantita per query |
| SERP PAA supplementare | Query «quanto costa un team building aziendale»: 1 blocco PAA e 9 organici | Prova distinta; non modifica la SERP originale |
| Maps | Una attività con sito, place_id e rating | Identità controllata tramite sito pubblico prima del task reviews; non censimento competitor |
| Google Reviews | 10 recensioni con date e rating via POST→GET | Campione parziale rispetto al totale esistente; nessun testo/nominativo pubblicato |
| Google Trends | 54 valori temporali, solo 2 non null | Serie insufficiente: non usare per stagionalità, non interpolare |
| Google Ads advertiser discovery | 18 elementi restituiti | Distinguere account/aggregazioni/domini, non 18 aziende validate |
| Google Ads Search | 19 creatività con identificativi | Attività osservata, nessuna stima di spesa/risultati competitor |

Esecuzione UTC: 09:21–09:23 del 25 ottobre 2026. Comandi: runner Gate 1A `--live --rate-card`, poi `--start-reviews` per identità osservata in Maps e `--check-paa` una sola volta; dettagli input/output e timestamp esatti nei file privati. Versione applicazione 0.1.0, codice base `4058ad7` con continuazione PAA e separazione accessibilità/qualità aggiunte durante il collaudo. Test offline aggiornati: 47 PASS; ruff PASS.

**Costi osservati:** 0,31847 USD complessivi per 15 richieste dati (incluse creazione/lettura reviews e SERP aggiuntiva); una richiesta gratuita preliminare a `/v3/appendix/user_data` per autenticazione e tariffe, costo 0. Cap autorizzato 5 USD; riserve conservative persistite 0,74644 USD, non spesa effettiva. Tariffe base verificate per l'account; supplementi non esposti da user_data coperti da margini conservativi e profondità minime del campione, senza opzioni a pagamento aggiuntive. Questa misura non dimostra il costo di un'intera strategia GTM o dei sette moduli.

Evidenze raw redatte delle credenziali, ledger, tariffa verificata e report esclusivamente in `artifacts/private/dataforseo/` (ignorato da Git); il repository pubblico contiene solo riepilghi aggregati e test sintetici. Riferimenti privati: `pilot/journal.jsonl`, `pilot/report.json`, `pilot/budget.json`, `account-pricing.json`, `rates.json`. Nessun risultato esteso o dato account pubblicato. Il report separa `gate_status` da `status` dei dati e preserva i limiti Trends/PAA. Altri provider non collaudati.


> **Aggiornamento successivo, 24 ottobre 2026 — priorità a questo registro.** La presente revisione sostituisce le scelte provider Google/Meta e integra i test effettivamente eseguiti dopo la prima stesura. Per il dettaglio dei gate consultare `PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md`.

## Registro del precedente ambiente — DataForSEO, 24 ottobre 2026
Tutti i risultati seguenti provengono da richieste autenticata al collegamento disponibile durante l'audit; il conto API e le credenziali **non sono automaticamente trasferiti** sull'account ChatGPT Pro.

| Requisito | Endpoint e campione | Riscontro | Giudizio |
|---|---|---|---|
| Località IT città | GET `/v3/keywords_data/google_ads/locations/IT` | 1462 città; Torino `1008857`, parent Piemonte `9053436` | TESTATO catalogo |
| Volume/CPC Torino | POST `/v3/keywords_data/google_ads/search_volume/live` Torino, `team building aziendale` | `search_volume=10`, `cpc=2.22`, `competition_index=68`, mesi restituiti | TESTATO, numerosità debole |
| Volume/CPC Piemonte | stesso POST con `location_code=9053436` | `search_volume=40`, `cpc=2.39`, `competition_index=70` | TESTATO sul singolo codice regione; non estendere a tutte senza campione |
| Keyword correlate | POST `/v3/dataforseo_labs/google/keyword_ideas/live`, IT, limite 5 | 5 risultati, con volume, CPC, intent dove disponibile | TESTATO |
| Intent | POST `/v3/dataforseo_labs/google/search_intent/live` | `transactional`, probabilità `0.576` per keyword pilota | TESTATO, classificazione modellistica |
| Autocomplete | POST `/v3/serp/google/autocomplete/live/advanced` Torino | 15 suggerimenti | TESTATO |
| SERP organica | POST `/v3/serp/google/organic/live/advanced` Torino | URL/domini e risultati organic | TESTATO |
| Maps competitor locali | POST `/v3/serp/google/maps/live/advanced` Torino | nome, URL, place_id, rating, review count e indirizzo di attività | TESTATO |
| Google recensioni | POST `/v3/business_data/google/reviews/task_post` + GET `.../task_get/{id}` su attività Torino | task creato, recuperate **10 recensioni** strutturate | TESTATO POST→GET; provare anche polling reale in codice |
| Trends | POST `/v3/keywords_data/google_trends/explore/live`, keyword pilota, IT, 12 mesi | 53 settimane, **soltanto 3 valori non null** | API TESTATA, **copertura dato INSUFFICIENTE** nel campione |
| Google Ads advertiser discovery | POST `/v3/serp/google/ads_advertisers/live/advanced`, `team building`, Italia | **18 inserzionisti** restituiti, inclusa un'azienda italiana | TESTATO |
| Google Ads Transparency per dominio | POST `/v3/serp/google/ads_search/live/advanced`, `target=madeinteam.it`, Italia | **19 creatività**, con `advertiser_id`, `creative_id`, URL, date e format | TESTATO |

**Modifica tecnica importante:** per Google Ads Transparency la fonte PRIMARIA diventa **DataForSEO già testato**, non SearchAPI. Non acquistare un altro provider per questa funzione senza evidenza che manchino dati necessari.

**Meta Ads Library ufficiale:** la documentazione Meta prevede annunci commerciali consegnati a UE/Regno Unito nell'ultimo anno, oltre alle categorie speciali. Per il mercato italiano è la **PRIMA opzione da collaudare** tramite `GET /ads_archive` su Graph API, con account Facebook idoneo, developer app e token. SearchAPI/Apify saranno FALLBACK solo se il percorso ufficiale non funziona o non copre casi necessari. Le spese dei normali annunci commerciali NON sono accessibili come importi effettivi. Fonte: https://www.facebook.com/ads/library/api/.

**Nota QA:** `status_code=20000` con `items=[]` o serie con valori null **non** equivale a copertura informativa valida. Ogni raccolta deve controllare presenza e qualità dei dati, non soltanto successo HTTP.

---


## Registro integrazioni e Gate per il codice
| Fonte | Copertura e scelta | Cosa deve dare l'utente | Prova tecnica necessaria prima di sviluppare il modulo |
|---|---|---|---|
| DataForSEO | **PRIMARIO**, collegamento già testato in chat | Credenziali API nell'ambiente Pro/Codex, credito/account API | Per nuovi endpoint fare uno smoke test con Italia/Torino/lingua it, JSON di esempio salvato |
| Python crawler | **PRIMARIO** per siti | URL eventuali di 3 competitor manuali e script esistenti da riutilizzare | 5 siti diversi, pages fetch/fallback dinamico e citazione pagina |
| Meta Instagram Graph | Priorità al metodo già usato dal proprietario | Script preesistente + app Meta/account professionale autorizzato + token/permessi (mai incollarli nel repository) | 50 post di competitor professionale, verifica campi esposti e percentuale media accessibile |
| Meta Ads UE | Prima opzione: API ufficiale `GET /ads_archive`; non testata qui | Developer app, token/permessi Ads specifici e cap | Due advertiser IT, due pagine, campi/creatività/copertura; altrimenti blocco motivato e valutazione fallback |
| Apify Instagram | Fallback automatico condizionato | Account Apify/token, scelta actor, approvazione costo | 5 competitor x 50 post (ove disponibili), verifica prezzi e success rate |
| SearchAPI | Fallback Meta dopo gap ufficiale; LinkedIn solo se pertinente; Google solo per gap DataForSEO dimostrato | Solo se necessario: account/API key e approvazione costo | Per la sola capacità necessaria verificare advertiser italiano, identificativo, date, creatività e paginazione |
| SerpApi | Solo gap Google Transparency non coperto da DataForSEO | Token solo dopo prova del gap e approvazione | Stessi criteri prova SearchAPI, evitare due provider duplicati |
| Openapi Company | Fonte approvata dati impresa Italia, accesso da collaudare | Configurare token privatamente e approvare micro-spesa | Match P.IVA a 3 società; ATECO, fatturato e anno, addetti e anno; confrontare 1 bilancio ufficiale |
| Istat/Eurostat/ESCO/OpenAlex | Fonti aperte istituzionali | Nessun token per endpoint pubblici, eventuale free key OpenAlex per limiti maggiori | Import ATECO2025; query dataset pertinenti; normalizzazione lingua/date |
| OpenAI API | Agenti, classificazioni e output strutturati | **Chiave API separata dal piano ChatGPT Pro** e limite di spesa | JSON schema, grounding/evidence, costi per run su dataset pilota |
| Supabase | Applicazione | Progetto, database URL, service key server-side | Migrazioni schema, upload artefatti e polling dei job |
| Vercel | Frontend | Account, repository GitHub, deployment project | Preview + endpoint backend esterno, no long-poll eseguito in browser |
| Render | API/worker per task lunghi | Account e autorizzazione spesa per servizio Python/worker | POST→job→worker→stato, callback task DataForSEO, generazione PPTX |
| GitHub | Source of Truth/version control | Repo o invito accesso a Codex nel conto Pro | CI test, secrets separati, loader Markdown KB |

## Bibliografia tecnica / URL primari e fornitori
- DataForSEO geolocalizzazione: https://docs.dataforseo.com/v3/keywords_data/google_ads/locations/ ; https://dataforseo.com/help-center/sv-for-city-or-coordinates
- DataForSEO volumi: https://docs.dataforseo.com/v3/keywords_data-google_ads-search_volume-live/
- DataForSEO Labs: https://docs.dataforseo.com/v3/dataforseo_labs/google/keyword_ideas/live ; https://docs.dataforseo.com/v3/dataforseo_labs/google/search_intent/live
- SERP: https://docs.dataforseo.com/v3/serp/google/organic/live/advanced/ ; https://docs.dataforseo.com/v3/serp-google-autocomplete-live-advanced/
- Google Trends: https://docs.dataforseo.com/v3/keywords_data-google-trends-explore-live/
- Forecast con limiti: https://docs.dataforseo.com/v3/keywords_data-google-ads-ad_traffic_by_keywords-live/
- Reviews: https://docs.dataforseo.com/v3/business_data-google-reviews-task_post/ ; https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_post/
- Google Places max 5 reviews: https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places
- Meta Business Discovery: https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-facebook-login/business-discovery
- Apify Instagram actor: https://apify.com/apify/instagram-post-scraper
- SearchAPI Meta: https://www.searchapi.io/docs/meta-ad-library-api ; https://www.searchapi.io/docs/meta-ad-library-page-search-api
- SearchAPI Google Transparency: https://www.searchapi.io/docs/google-ads-transparency-center-api
- SearchAPI LinkedIn Ads: https://www.searchapi.io/docs/linkedin-ad-library-api
- Openapi company: https://console.openapi.com/apis/company/documentation ; https://openapi.com/pricing ; https://openapi.com/products/italian-company-balance-sheet
- ISTAT ATECO2025: https://www.istat.it/classificazione/ateco-2025/
- ISTAT API: https://www.istat.it/classificazioni-e-strumenti/web-services-sdmx/
- Eurostat API: https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-introduction
- ESCO API: https://esco.ec.europa.eu/en/use-esco/use-esco-services-api
- OpenAlex API: https://help.openalex.org/api/

## Archivio storico - prima stesura, superata

Questa sezione conserva integralmente evidenze e valutazioni della prima stesura. NON e una specifica operativa corrente. Le affermazioni storiche su SearchAPI primario, recensioni non raccolte e regione non provata sono superate dal registro aggiornato qui sopra. I prezzi e le policy citati sono riferimenti storici, non verifiche attuali. Legenda T/D/C/I/X storica, non sostitutiva dei tre assi della matrice corrente.

<details>
<summary>Prima stesura storica del 24 ottobre 2026 (non normativa)</summary>

# GTM Engine — Audit accessibilità dati, 24 ottobre 2026

**Fonte di perimetro:** ZIP `docs(3).zip`, scope dei Moduli 01–07. **Ricerca:** documentazione tecnica online ufficiale e di provider commerciali; chiamate reali al connettore DataForSEO. **Questo documento certifica le vie tecniche documentate e i test effettivamente eseguiti, NON pretende che API di terzi prive di credenziali siano state collaudate.**

## Legenda evidenze
- **T = TESTATO ADESSO:** autentica chiamata all'API con risposta dati pertinenti.
- **D = DOCUMENTATO:** endpoint attivo descritto nella documentazione corrente, chiamata applicativa non ancora testata.
- **C = CONDIZIONATO:** automatizzabile previo token, acquisto, autorizzazione o verifica copertura specifica.
- **I = INFERENZA:** risultato AI/statistico derivato, mai presentato come campo osservato.
- **X = NON OSSERVABILE:** assenza di un canale verificato per il dato richiesto; nessun numero inventato.

**Metodi:** `LIVE` richiesta sincrona; `TASK` POST + poll/GET o webhook, **interamente automatizzabile**; `CRAWL` Python HTTP + parsing e, solo se necessario, browser controllato; `STATIC` file/dataset pubblici importati; `USER` dato che conosce solo l'utente. **Manuale** non è sinonimo di asincrono.

## Prova reale: DataForSEO
1. `GET /v3/keywords_data/google_ads/locations/IT` → HTTP applicativo status `20000`; catalogo di **1462 città italiane**; Torino `location_code=1008857`, `Turin,Turin,Piedmont,Italy`. Il GET generico `locations` mostrava soltanto 244 paesi in questo connettore; bisogna usare **`locations/IT` per le città**. La gerarchia regionale andrà ulteriormente verificata con gli identificativi supportati; NON sommare città e regioni.
2. `POST /v3/keywords_data/google_ads/search_volume/live`, una keyword `team building aziendale`, `location_code=1008857`, `language_code=it` → status **20000**, `search_volume=10`, `competition=HIGH`, `competition_index=68`, `cpc=2.22` (unità del provider da interpretare) e dodici osservazioni mensili. **È una prova di ritorno dati, non una validazione statistica dei valori.** CPC non è promessa di prezzo futuro. È stato eseguito un singolo campione e potrebbe comportare addebiti al conto API.
3. `POST /v3/serp/google/organic/live/advanced`, query `team building aziendale torino` geolocalizzata su Torino → status **20000**, elementi `organic` con URL/dominio/titolo e un elemento AI overview asincrono; questo dimostra accesso LIVE alle SERP, non l'affidabilità di tutti gli elementi per ogni query.
4. `GET /v3/business_data/google/reviews/tasks_ready` → status **20000** con lista vuota: autenticazione riuscita, **nessuna raccolta recensioni effettuata**. L'endpoint recensioni è documentato e usa TASK.

## Modulo 00 — Project Brief / contesto
| Dato richiesto | Fonte e metodo | Stato | Accesso richiesto / note |
|---|---|---|---|
| Descrizione prodotto, obiettivi, mercato, prodotto in sviluppo | Form utente e documenti forniti (`USER`) | USER | L'utente inserisce i dati, nessuna ricerca può sostituire la conoscenza dell'offerta |
| URL sito proprio, asset/logo, materiali approvati | Input URL e caricamenti | USER/CRAWL | URL e file dell'utente; crawler verifica il sito, non deduce le caratteristiche non pubblicate |
| Geografia e lingua | Catalogo DataForSEO `locations/{country}`, lingue endpoint | T per Torino; D altrove | Nessun token aggiuntivo per cataloghi; selezione città/regione/nazione con verifica esplicita del provider |

## Modulo 01 — Demand Intelligence
| Dato | Percorso automatico concreto | Stato | Limitazione / alternativa |
|---|---|---|---|
| Seed keyword | LLM da Project Brief + seed facoltative utente, salvare provenienza | I/USER | Ipotesi non sono ricerche osservate |
| Espansione semantica | DataForSEO Labs `google/keyword_ideas/live`; `google/keyword_suggestions/live`; `related_keywords/live` | D | Dataset Labs differente da volumi Ads; non presumere identica geografia |
| Volumi, CPC, competizione, 12 mesi | DataForSEO `keywords_data/google_ads/search_volume/live` | **T Torino, 1 keyword** | Metriche Ads approssimate, raggruppamenti Google e null possibili |
| Targeting città | `GET .../locations/IT` → `location_code 1008857` → keyword LIVE | **T** | Torino confermata, catalogo di città ma singole città potrebbero avere pochi dati |
| Targeting regione | Cataloghi geo DataForSEO / codici target; provare `location_code_parent`; fallimenti bloccare output regionale | C | **Non provato** che qualsiasi regione italiana produca volumi affidabili |
| Keyword intent | DataForSEO `dataforseo_labs/google/search_intent/live` o valore Labs | D | Probabilità/modello classificatorio, non intento osservato nel singolo buyer |
| Autocomplete | DataForSEO `serp/google/autocomplete/live/advanced` | D | Non attribuire search volume finché non interrogato separatamente |
| People Also Ask / Related Searches | `serp/google/organic/live/advanced`, filtro `items.type` | D; SERP base T | Presenza delle feature non garantita su una query |
| Trend / stagionalità | `keywords_data/google_trends/explore/live` | D | Scala 0–100 relativa, non volume assoluto; tipicamente 5 keyword per richiesta |
| SERP organiche e annunci osservati | `serp/google/organic/live/advanced` `organic`, `paid`, `local_pack` | **T organic**, D altri tipi | Una SERP non stima spesa mensile annunci |
| Domini SEO competitors / keyword overlap | Labs `ranked_keywords/live`, `serp_competitors/live` | D | Stime keyword DB non misure GSC proprietarie |
| Stima budget Search | CPC e domanda + `keywords_data/google_ads/ad_traffic_by_keywords/live` per scenari | D | Forecast task ora aggregato per campagna; `impressions`/`ctr` possono essere `null` per deprecated: NON basarsi su essi |

**Decisione raccolta Mod.01:** DataForSEO è il provider primario. **Non richiede Google Ads account diretto** (servizio rivenduto). La granularità di Torino è davvero funzionante; un confronto regione/nazione richiede test aggiuntivo. Nessuna ricerca manuale keyword prevista nell'MVP salvo correzione qualitativa volontaria.

## Modulo 02 — Market & Competitive Intelligence
| Dato | Percorso automatico concreto | Stato | Limiti / alternative |
|---|---|---|---|
| Competitor SEO/market | SERP DataForSEO LIVE + Google local pack/Maps via DataForSEO o provider Google Places; LLM verifica offerta e sostituibilità | T SERP; D Maps | Non confondere portali/editori con competitor commerciali |
| 5 competitor selezionati e fino a 3 extra | Raccolta automatica; approvazione utente (selezione commerciale) | USER su approvazione | La conferma è una scelta di prodotto, non un lavoro manuale di ricerca |
| Pagine, prodotti, listini, case study, claim | `httpx/requests` + `BeautifulSoup` + `trafilatura`, sitemap/schema.org; `Playwright` per JS | C/CRAWL | Pagine private, anti-bot, condizioni sito; limitare profondità; prezzo non pubblicato = `null` |
| Identity brand/dominio/società | Structured data sito, footer, note legali P.IVA + `Openapi /IT-search`, `/IT-advanced` | D/C | Match societario incerto richiede conferma, non assunzione |
| Instagram, profilo e fino 50 post concorrente | **Primaria:** Meta Instagram Graph Business Discovery (solo account idonei e autorizzazioni). **Fallback:** Apify `apify/instagram-post-scraper` o SearchAPI Instagram Profile/Post APIs | C | Meta Graph non garantisce account privati né tutti i media; provider terzi a consumo; non promettere insights privati dei concorrenti |
| Like, commenti, caption, formati post | Business Discovery quando visibili; Apify/SearchAPI pubblici | C | Copertura disomogenea e cambiamenti della piattaforma; non stimare reach organica non esposta |
| Facebook posts concorrenti | Pagine pubbliche tramite provider (es. SearchAPI Facebook Business Page) o crawler condizionato | C | API Meta per pagine altrui ha autorizzazioni/restrizioni; non garantito |
| Meta commercial ads concorrenti | **SearchAPI** `engine=meta_ad_library_page_search` → `page_id` → `engine=meta_ad_library` (paginato); fallback Apify attori Meta Ads Library | D/C | API ufficiale Meta Ad Library NON trattata come accesso universale alle campagne commerciali. Provider terzi da provare con brand italiani |
| Google ads creatività concorrenti | **SearchAPI** `engine=google_ads_transparency_center`, parametro `domain` o advertiser ID; alternativa SerpApi; annunci Search osservati anche in SERP DataForSEO | D/C | Nessuna API Google Transparency pubblica generica individuata; la presenza non quantifica investimento |
| LinkedIn ads concorrenti | **SearchAPI** `linkedin_ad_library` + `linkedin_ad_library_ad_details` per casi pertinenti | D/C | Campi impressions e targeting disponibili solo in alcuni mercati/ads, nessun budget concorrente |
| Spesa ADS effettiva competitors | Nessun API affidabile generale per spesa privata Meta/Google/LinkedIn | **X** | Conservare `ads_observed`, `first_seen`, numero creatività, NON inventare euro; eventuali stime esplicitamente non verificabili |
| Google Maps identità, rating, numero recensioni | DataForSEO `business_data/google/my_business_info/live`, Places Google o SERP local pack | D | API Places ufficiale restituisce **max 5 testi recensione**; usare DataForSEO per quantità |
| Google recensioni estese | `business_data/google/reviews/task_post` → `tasks_ready` / `task_get` o webhook | D (TASK; GET tasks_ready T) | Massimo Google osservabile fino a **4.490**, costi ogni 10; non equivale a tutte quelle esistenti |
| Trustpilot recensioni | DataForSEO `business_data/trustpilot/reviews/task_post` (TASK) | D | Solo se profilo Trustpilot associato al dominio e disponibile |
| Tripadvisor recensioni | Provider terzo/SearchAPI Tripadvisor Reviews o API DataForSEO se endpoint confermato per caso concreto | C | Pertinenza solo per settori rilevanti; non introdurre come prerequisito universale |
| Ragione sociale/P.IVA/ATECO/sede | `Openapi Company /IT-search` (da nome/geografia), `/IT-start`, `/IT-advanced` | D/C | Matching per dominio/brand va verificato; niente accesso Openapi configurato in questa sessione |
| Fatturato con esercizio, numero addetti | `Openapi /IT-advanced` (dichiara revenue, employees); per fonte ufficiale bilancio API `bilancio-ottico` | D/C | Copertura società di capitali; anno del valore e definizione addetti obbligatori; revenue società != revenue prodotto |
| Bilancio camerale originale | Openapi `POST /bilancio-ottico` con P.IVA, callback o polling | D/C | Da €2,95 IVA esclusa con piano, singola €4,50 nel listino consultato; no credenziali/test yet |
| Organic Visibility SEO | SERP su paniere keyword non-brand versionato; Labs `ranked_keywords/live` come complemento | T SERP; D Labs | Modello Python deterministico, niente brand query nel paniere |
| Scoring sei dimensioni CCI | Dati normalizzati + Python funzioni v1.1 (non ML) | I | Se dati Social/Ads/Scale mancanti segnare Partial/Unavailable; CCI non validato empiricamente |

**Provider automatici prioritari per il modulo:** DataForSEO (SERP, SEO, reviews), crawler Python, **un solo** provider terzo iniziale per librerie Ads (proporrei SearchAPI perché riunisce Meta/Google/LinkedIn; Apify come alternativa), Openapi Company per dati societari. Non acquistare contemporaneamente SearchAPI, Apify e SerpApi senza test comparativo.

## Modulo 03 — UVP & ICP Intelligence
| Dato | Raccolta e verifica | Stato | Limiti |
|---|---|---|---|
| UVP, prodotto, pains/gains, proof aziendali | Solo Project Brief e form/chat utente; URL e materiale cliente | USER | Nessuna API esterna può certificare differenziazione interna non dichiarata |
| Evidenze bisogni espressi | Mod.01 (PAA, Autocomplete, query) + Mod.02 recensioni, pagine forum accessibili, ricerche pubbliche | T/D/C | Search demand != customer purchase evidence; recensioni competitor non coprono tutto il mercato |
| Ricerche e studi primari | **OpenAlex Works API** per discovery di studi; link originali + crawler PDF/HTML o documenti accessibili; Eurostat/Istat SDMX per statistiche | D | OpenAlex individua pubblicazioni, non garantisce testo completo né studi pertinenti |
| Segmenti firmografici e aziende nel territorio | Openapi `IT-search` supporta ATECO, area, addetti, fatturato (se caso B2B italiano) | D/C | È una distribuzione di imprese, NON prova di interesse/acquisto. Mod.03 non produce liste prospect |
| Codici ATECO2025 (max 3 esempi/ICP) | Scaricare tabella ufficiale ISTAT XLSX, indicizzare localmente e lookup Python | D/STATIC | Versionare tavola 2025 e raccordi aggiornati 2026; non generare codici a memoria |
| Buyer B2B job titles | Deducere dal buying context + classificazione **ESCO API** per descrizioni ufficiali delle professioni; siti/case study come evidenze | D/I | ESCO non prova chi decide in una determinata impresa; i buyer roles restano motivati/ipotetici |
| B2C unità di acquisto / household | Istat/Eurostat statistiche familiari aggregate + studi primari | D/I | Tipologie relazionali non possono essere inferite come comportamento individuale certo |
| Validazione solution willingness-to-pay | Survey/interviste reali **fornite o commissionate dall'utente**; price/recensioni competitor come segnali secondari | USER / X se manca | Non fingere che SERP o Google Trends misurino acquisto effettivo o WTP |

## Modulo 04 — Value Proposition & Positioning
| Dato | Metodo | Stato | Limiti |
|---|---|---|---|
| Alternative/offerte e capacità verificabili | Riutilizzo Mod.02 website/review intelligence, input utente, case study pubblici | D/T ered. | Non riscrapare tutto |
| Differenziatori e prove | Matrice Python/LLM, documenti e testimonianze effettive | I/USER | Zero differenziatori è valido; non promuovere ipotesi a prove |
| Tone of Voice storico | Contenuti brand pubblici via crawler + esempi utente | C/USER | Se nuovi brand niente TOV storico; è una proposta da approvare |
| Message architecture | Agente + KB approvata, no provider esterno obbligatorio | I | Nessun claim per prodotto in sviluppo; QA editoriale e verifiche fonte |

## Modulo 05 — Channel & GTM Strategy
| Dato | Percorso | Stato | Limiti |
|---|---|---|---|
| Raggiungibilità ICP e domanda Search | Mod.01 search; Mod.03 buyer; pubblica documentazione piattaforme | T/D | Non sostituire targetability reale a evidenza di conversione |
| Competitor uso canali | Mod.02 website/ads/social | D/C | Competitor attivo != canale efficace o conveniente |
| Caratteristiche targeting Ads | Google/Meta/LinkedIn documentazione e, se account cliente collegato, relative API Ads (OAuth/approval) | D/C | Mai supporre audience o funzionalità sempre uguali |
| Segnali di mercato osservabili | DataForSEO Google News LIVE, siti aziende, news/press releases, sitemap/RSS, Openapi eventi società quando disponibili | D/C | Segnale ≠ necessità o propensione acquisto; osservabilità dipende dalla fonte |
| Benchmarks indipendenti | OpenAlex + studi pubblici/KB con metodo, mercato, periodo e limiti | D/I | Provider guide sono documentazione tecnica, non prova imparziale dell'efficacia |
| Raccomandazione 1 primario + <=2 complementari | Agente + playbook GitHub/Markdown pertinenti | I | Decisione strategica verificabile, non scoring universale |

## Modulo 06 — GTM Execution Planning
| Dato | Come ottenere | Stato | Limiti |
|---|---|---|---|
| Budget Paid mensile | Campo utente, **solo media/inserzioni** | USER | Non inglobare freelance, software o ads creatività in media budget |
| Numero persone, ore TOTALI, competenze | Tre input utente (SEO & Content Strategy categoria unica); niente ruoli/team chart | USER | La strategia non si adegua alle skill; queste determinano il gap |
| CPC e domanda in Search | DataForSEO LIVE Mod.01; opzionale `/ad_traffic_by_keywords/live` per scenari | T/D | CPC in USD secondo specifica provider; valuta e unità esplicite. Forecast non garantito |
| Meta/LinkedIn CPC CPM competitor/mercato | Proprietari Ads API **solo account autorizzati**, ricerche pubblicate (campione/metodologia) | C/I | Nessun accesso pubblico universale ai CPC effettivi di terzi; se manca budget minimo preciso, scenario condizionale |
| Prezzo tool e API | Catalogo/prezzario pubblico HTTP + KB versionata, ove accessibile | D/CRAWL | Variabile per piano, quantità, territorio e data |
| Ore richieste attività | Work packages stimati con regole/KB e taratura sui piloti | I | Stima dichiarata, non misura osservata; nessuna valorizzazione monetaria ore interne automatica |
| Ore esterne e costi freelancer/agenzia | Gap del team + preventivo/quotazione esterna o benchmark chiaramente identificato | I/USER | Il preventivo esatto non è recuperabile automaticamente senza partner/preventivo; trattare `indicativo` |
| KPI tracciati | GA4/GSC/Google Ads/Meta Insights **solo se gli account sono dell'utente e OAuth è concesso**; altrimenti definizione eventi | C/USER | Senza account collegato GTM Engine può progettare KPI, non osservare i risultati |
| Sequenze, trigger, timeline | Agente/KB + Python deterministic planner | I | Progetta, non pubblica/invia campagne nell'MVP |

## Modulo 07 — GTM Strategy Deck
| Dato | Metodo | Stato | Limiti |
|---|---|---|---|
| Analisi approvate Mod.01–06 | Supabase Postgres con raw + normalizzato + evidence IDs | Decisione stack | Nessuna nuova ricerca esterna/inferenze numeriche nel deck |
| Main cover / section cover quando utili / 2 content template | Template PPTX e componenti nativi `python-pptx` | Libreria documentata, implementazione da fare | I template devono contenere elementi editabili; font e branding forniti dall'utente |
| Tabelle/grafici/testi editabili | python-pptx; grafici nativi, tabelle nativi, immagini solo asset | D | Preview server-side con LibreOffice/headless o render apposito da collaudare visivamente |
| PDF opzionale | Conversione headless file PPTX | C | Il PPTX rimane l'originale master modificabile |

## Dati che NON vanno inventati nemmeno utilizzando provider terzi
1. Spesa mensile effettiva advertising di concorrenti generici.
2. Reach/impression organici privati degli account social di concorrenti.
3. Numero di clienti, performance commerciale, conversion rate e ROI dei concorrenti privati.
4. WTP effettiva del buyer senza ricerche primarie o transazioni osservate.
5. Quota di mercato, TAM e fatturato di un singolo prodotto dedotti dal fatturato della società.
6. Budget Paid «minimo per ottenere vendite» garantite; sono ammissibili soltanto soglie per **test osservabile** e scenari condizionati.
7. Accessi e credenziali disponibili: una pagina di pricing/documentazione non attiva un contratto.


</details>
