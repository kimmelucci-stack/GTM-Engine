# GTM Engine — Matrice definitiva delle fonti, dei test e degli accessi
**Decisioni del 24 ottobre 2026; prove e legenda aggiornate il 25 ottobre.** Perimetro: dati degli scope 00–07. Gate 1A DataForSEO riprodotto; crawler HTTP collaudato nel solo screening leggero sotto descritto, altri accessi API non collaudati. La tabella storica sottostante conserva le evidenze precedenti; il registro corrente qui sotto prevale per il solo campione effettivamente riprodotto.

## Accessibilità corrente — repository, 25 ottobre 2026

Gate 1A **PASS_WITH_LIMITATIONS**, spesa 0,31847 USD contro cap 5 USD. Autenticazione/tariffe via endpoint gratuito verificati. Fonti DataForSEO `tested` per catalogo IT, volumi città/regione/nazione, ideas, intent, autocomplete, SERP organica/PAA, Maps, reviews POST/GET, Trends e Google Ads Advertisers/Search. Dati disponibili per i campioni; Trends `partial` (2/54 valori non null), SERP iniziale senza PAA ma PAA verificato su query supplementare. Nessun dato economico inferito. Dettagli, campioni, query, costi e riferimenti privati nell'[audit](DATA_ACCESS_AUDIT_2026-10-24.md).

Crawler HTTP: nove domini campione, una pagina di offerta per sito, otto con contenuto/evidenze e uno `failed` per HTTP 403 su robots.txt. Accesso `tested` alle otto pagine; dataset complessivo `partial`, prezzi osservati su due pagine con estrattore `web-extract-v2`, case study non osservati nel campione. Nessuna prova di ranking o volume di domanda; sostituibilità commerciale ancora da qualificare, nessuna shortlist approvata. Il rendering dinamico resta testato su fixture sintetiche, non su questi siti. Questo screening storico non superava il gate. Successivo crawl tecnico autorizzato: Gate 1B PASS_WITH_LIMITATIONS su cinque siti, 15 GET, otto pagine disponibili e una risorsa non HTML; 95 estratti, prezzi su sei pagine, otto hash verificati. Nessuna esecuzione browser necessaria, nessuna validazione di ranking o shortlist commerciale. Dettagli e report privati nell'audit.

Stati e limiti valgono per il pilota, non per ogni paese/query/competitor. Credenziali e raw privati esclusi dal portfolio. Nessun gate successivo o accesso API ulteriore promosso a tested.

## Livelli da non confondere
- **T / TESTED_DATA:** richiesta autenticata con dati nell'ambiente specificato. La tabella storica si riferisce al precedente ambiente; il registro corrente indica le prove del repository. Ogni T richiede ambiente, data e fixture.
- **T_LIMITED:** endpoint interrogato ma copertura insufficiente, qualità da verificare o campione ridotto.
- **D / DOCUMENTED:** servizio e metodo verificati nella documentazione attuale, nessun test autenticato nel runtime applicativo.
- **G / GATED:** account/token/permessi/piano da procurare; test necessario prima di dichiarare la fonte operativa.
- **U / USER:** dato che conosce e immette l'utente o approvazione richiesta.
- **X / UNOBSERVABLE:** il dato non è lecitamente e affidabilmente disponibile tramite le fonti identificate; segnare unavailable, non compilare a fantasia.

### Tre assi distinti
1. **Accessibilità della fonte:** `documented`, `gated`, `tested`, `failed`, sempre con ambiente/data/limiti. T storico non equivale a tested nel repository; G non prova che l'account non esista, solo che l'accesso non è verificato.
2. **Disponibilità del dato:** `available`, `partial`, `unavailable`, `not_checked`; preservare null, zero verificato ed errore come casi diversi. T_LIMITED riassume accesso storico riuscito con dati parziali; un HTTP 200 non garantisce disponibilità.
3. **Natura epistemica:** `Observed`, `Derived` (metodo/versione) o `Inferred` (interpretazione/ipotesi); supporto del claim separato (`Supported/Mixed/Unverified` secondo Modulo 03). L'AI non determina l'accessibilità della fonte. `I` significa inferenza, non stato API; `U` indica input/approvazione utente, non test provider.

Le sigle della tabella sono riepiloghi di progettazione/storici. Le forme `U/D`, `D/I` e `D/T ereditato` combinano provenienza o natura, non nuovi stati di accesso. I tre assi saranno persistiti separatamente al Gate 2. Stato locale: DataForSEO tested e crawler HTTP tested solo nel campione di screening sopra; altri accessi API not_checked/gated. `GATE_0_VALIDATION.md` riguarda soltanto la foundation, l'audit contiene le successive prove provider.

## Copertura e fallback: nessun obbligo di ricerca manuale su dati esterni pubblici
| Dato/campo | Primaria (metodo) | Riserva / condizione | Stato storico/progettazione | Azione dell'utente | Prova di chiusura |
|---|---|---|---|---|---|
| Brief offerta, obiettivi, stato prodotto | Modulo 00 form | sito pubblico in supporto | U | Descrivere offerta; selezionare sviluppo sì/no | campi validati; nessuna inferenza promossa a fatto |
| URL sito, competitor aggiunti e asset | input + crawler | URL aggiuntivi opzionali | U/D | Fornire se disponibili | URL apribile o assenza esplicita |
| Geografia città | DataForSEO Ads geo code | catalogo geografia | T | Nulla | Torino verificata; altri mercati per campione |
| Geografia regione | parent code DataForSEO Ads | mapping geografie versionato | T_LIMITED | Nulla | Piemonte 9053436 interrogato; altri codici campione |
| Geografia paese | DataForSEO code 2380 Italia | geo endpoint | D | Nulla | richiesta nazione reale |
| Keyword discovery espansione | DataForSEO Labs keyword ideas | suggestions; LLM marcato come ipotesi | T | Nulla | 5 risultati pilota; cluster pertinenti |
| Volumi, CPC, concorrenza e storico | DataForSEO Google Ads Search Volume LIVE | `null` dove dati assenti | T | Credenziale API in Codex | Torino e Piemonte provati |
| Intent | DataForSEO Labs Search Intent | classificazione LLM solo se dichiarata | T | Nulla | intent con probabilità |
| Autocomplete | DataForSEO Google Autocomplete LIVE | SERP related | T | Nulla | 15 suggerimenti |
| PAA/related / SERP | DataForSEO Organic Advanced LIVE | feature potrebbe mancare | T_LIMITED | Nulla | SERP organica provata; PAA da testare su query presente |
| Trend/stagionalità | DataForSEO Google Trends LIVE | monthly Google Ads (segnale diverso); non interpolare | T_LIMITED | Nulla | **3/53 valori non-null**: QA boccia trend settimanale pilota |
| Competitor candidate da SERP e Maps | DataForSEO Organic + Maps LIVE | classifier offerta; sito | T | approvare eventuali casi ambigui | candidati con overlap commerciale, non soli editori |
| Crawler offerte/prezzi/case study | Python httpx + BS4/trafilatura + schema.org/sitemap | Playwright su JS; assenza se non pubblico | D | fornire eventuali script preesistenti | 5 siti reali con evidence URL e timestamp |
| Social Instagram 50 post | Instagram Graph Business Discovery | Apify Instagram actor, se autorizzato | G | token/app Meta + script se esiste; in alternativa Apify token | 2 account business e 50 post ove disponibili, contare copertura |
| Meta ads commerciali in Italia | **Meta Ad Library API ufficiale UE** `GET /ads_archive` | SearchAPI Meta, poi Apify | G | Meta developer/account/token; in caso di fallimento SearchAPI trial | paginazione 2 pagine, 2 advertiser IT, testo/date/creatività |
| Google Ads Transparency concorrenti | **DataForSEO Ads Advertisers + Ads Search LIVE** | SearchAPI/SerpApi solo per gap | T | stessa API DataForSEO | 18 advertisers + 19 creatività per target campione |
| LinkedIn Ads Library concorrenti | SearchAPI LinkedIn Ad Library | visualizzazione pubblica; non essenziale in tutti i settori | G | SearchAPI key solo se canale pertinente | 2 advertiser Italia, fields, limiti e paginazione |
| Spesa Ads effettiva concorrenti | nessuna fonte universale credibile | solo dati particolari dichiarati | X | nessuno | `unavailable`, nessun euro inventato |
| Instagram reach/impression privati | non osservabile per terzi genericamente | eventuali insights propri con autorizzazione | X | nessuno | `unavailable` |
| Google rating e count | DataForSEO Maps LIVE | Maps/Places API | T | nulla | rating, place_id e numero recensioni ottenuti |
| Recensioni Google estese | DataForSEO Reviews POST→GET | provider reviews alternate | T | stessa key DataForSEO | 10 recensioni con rating/date/testo se esistente |
| Trustpilot/Tripadvisor | DataForSEO Trustpilot TASK o provider verticali | solo se competitor usa piattaforma | D/G | nessun token salvo fornitore aggiuntivo | campione specifico verticale, non prerequisito universale |
| Dati società, P.IVA, ATECO e fatturato | Openapi Company /IT-search + advanced | note legali pubbliche + fonti istituzionali | G | Openapi key, autorizzare interrogazioni piccole | match 3 società con periodo; 1 bilancio ufficiale |
| Dipendenti con anno | Openapi Company | altre banche dati commerciali verificabili | G | Openapi key | addetti/anno, null se mancano |
| ATECO 2025 official descriptions | ISTAT classificazione scaricabile | riferimento statico versionato | D | nessuno | download e lookup tre codici con descrizione |
| Studi e dati per ICP/B2B/B2C | OpenAlex, ISTAT/Eurostat SDMX, ESCO | documenti primari pubblici; KB | D | fonti proprietarie se esistono | 1 query/download per fonte, pubblicazione e pertinenza |
| Buyer title / family role | ESCO + framework + fonti ICP | user feedback per specifici buyer | D/I | validare ICP | nessuno stereotipo; ruoli da contesto |
| UVP reale / proof / claims | brief utente e fonti possedute | sito e casi pubblici, verifica | U/D | approvare materiali reali | no claim in development |
| Relevance canali + segnali | dati 01–04, SERP, news/RSS aziende, KB | DataForSEO news LIVE se necessario | D/T ereditato | nulla salvo obiettivi e budget | canale/segno/tattica distinti; fonti e fattibilità |
| Paid budget | input utente solo media/inserzioni | nessuna inferenza | U | euro mensili paid | non confondere tool/freelance con media budget |
| Risorse internal team | numero persone, ore settimanali complessive, skill | nessun organigramma | U | compilare 3 campi | strategie non degradate per skill |
| Costi software e outsourcing | price pages pubbliche + richieste vendor; stime esplicite | preventivo effettivo solo con utente | D/I | accettare preventivo per prezzo certo | categorie costi separate, gap motivato |
| Performance reali delle campagne | GA4/Ads propri collegati via OAuth | progettare KPI se account assente | G/U | autorizzare solo se vuole dati reali | mai inferire performance da benchmark |
| Deck/pptx | DB outputs approvati → `python-pptx` | LibreOffice headless preview | D (libreria)/build pending | branding e approvazione | Native text/table/chart edit, QA visivo |

## Requisiti generali di validazione dati
- Provider API success **non** equivale a dato utilizzabile: qualificare quantità, tempo, copertura territoriale, aderenza ICP e campione.
- Per ogni `field` salvare `source_url/endpoint`, `observed_at`, `geo_requested`, `geo_effective`, `period`, `raw_ref`, `state`, `limitations`. Se stimato: `derived=true` e metodo.
- Retry e fallback automatizzati soltanto dove c'è connettore realmente testato. Se primaria non produce dati e fallback non è collaudato, stato `partial/unavailable`, senza ricerca manuale obbligatoria.
- Per ogni fonte GATED definire credenziale richiesta, max spesa e sample esatto, e segnare il gate bloccato fino a successo.
- Non propagare il token ChatGPT Plus alla nuova utenza Pro: rigenerare/configurare token provider separatamente.

## Riferimenti primari
- https://docs.dataforseo.com/v3/serp/google/ads_search/live/advanced/
- https://docs.dataforseo.com/v3/serp/google/ads_advertisers/live/advanced/
- https://docs.dataforseo.com/v3/keywords_data/google_ads/search_volume/live/
- https://docs.dataforseo.com/v3/business_data/google/reviews/task_post/
- https://www.facebook.com/ads/library/api/
- https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-facebook-login/business-discovery
- https://www.searchapi.io/docs/linkedin-ad-library-api
- https://www.searchapi.io/docs/meta-ad-library-api
- https://console.openapi.com/apis/company/documentation
- https://www.istat.it/classificazione/ateco-2025/
- https://ec.europa.eu/eurostat/en/web/user-guides/data-browser/api-data-access/api-introduction
- https://esco.ec.europa.eu/en/use-esco/use-esco-services-api
- https://help.openalex.org/api/
