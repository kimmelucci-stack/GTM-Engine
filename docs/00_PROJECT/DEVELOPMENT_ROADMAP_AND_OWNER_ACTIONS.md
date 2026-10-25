# GTM Engine — Roadmap pronta per Codex, dipendenze e attività dell'utente
**Decisioni del 24 ottobre 2026, consolidate il 25 ottobre.** Gate 0 verificato; Gate 1A DataForSEO PASS_WITH_LIMITATIONS (0,31847 USD, tredici campioni e approfondimento PAA). Gate 1B PASS_WITH_LIMITATIONS: cinque siti del campione tecnico delegato dal proprietario, 15 GET, otto pagine disponibili e una risorsa non HTML. Nessuna shortlist commerciale approvata; browser live non necessario, costo API zero. Gate 1C avviato: prova browser autenticata con permessi granted, Ads Library negata (codice 10), nessun IG ID restituito; NOT_PASSED, ora in attesa su istruzione del proprietario. Gate 1D non eseguito (chiave e cap mancanti); Gate 1E PARTIAL: import ATECO e query Eurostat/OpenAlex reali, ESCO non disponibile. Gate 2 avviato su istruzione del proprietario: KB-001 a richiesta e test offline implementati; integrazioni DB/worker/storage ancora da completare; anteprima UI e contratti parziali non equivalgono a Gate 2/4 completi. Repository pubblica per portfolio, con secret e dati privati esclusi; nessun deploy implicito.

## Sequenza vincolante, con ownership esplicita
| Gate | Responsabile Codex | Responsabile utente | Deliverable e condizione di uscita |
|---|---|---|---|
| **0 — Repository** | Audit, config React/FastAPI/worker, toolchain, `.env.example`, CI e protezione credenziali | Fornire repository e accesso; predisporre account per i rispettivi gate successivi | Repo collegato + healthcheck, build React e pytest; accessi provider non richiesti per i controlli locali |
| **1A — Proven DataForSEO** | Riprodurre 12 prove eseguite in audit; estrarre raw fixtures; controllare copertura; benchmark costo | Inserire DataForSEO API credentials nell'ambiente Codex, confermare limite richieste | Geo city/regione/nazione; keywords, SERP, trends nullable, Maps, reviews, Google Ads; log con evidence |
| **1B — Competitor web** | Crawl di 5 siti con HTTP e fallback Playwright, scraping prezzi/claims/cases | Dare script crawler già sviluppato se disponibile; confermare 5 competitor campione | Almeno 5 siti, output normalizzato e fonte per ogni claim, record unavailable |
| **1C — Meta Ads + IG** | Test ufficiale Meta `ads_archive` EU per 2 advertiser IT e Business Discovery per 2 account prof. Test provider fallback solo se l'ufficiale fallisce | Attivare Developer App/token/permessi e, se necessario, verifica identità; offrire script IG già usato. Se fallback, autorizzare SearchAPI/Apify | 2 advertiser e 2 pagine/50 media ove disponibili, copertura registrata, oppure gate bloccato con causa precisa |
| **1D — Openapi Company** | Test ricerca match società, P.IVA, ATECO, fatturato/anno e addetti/anno; confronto con bilancio | Creare/fornire Openapi token e limite spesa per 3 aziende + 1 bilancio | 3 company matches e record source/status; ambiguo non forzato |
| **1E — Fonti pubbliche** | Import test ISTAT ATECO2025 e query Eurostat/OpenAlex; ESCO opzionale, non prerequisito buyer mapping | Nessuna azione salvo input studi proprietari | Una richiesta/download reale per fonte obbligatoria, timestamp, versione e query salvati; prova ESCO storica conservata |
| **2 — Foundation** | Adapters, schema Postgres, evidenze, worker, cap, loader KB, fallback; implementare KB-001 controllo fonti ogni 45 giorni | Configurare Supabase/Render/Vercel e approvare registro fonti | REST+job+storage; retry/fail/timeout; test KB-001 su scadenze, HTTP condizionali, cambiamenti e errori |
| **3 — Demand** | Mod.01 workflow e minimal UI, metriche e quality status | Validare 20 keyword e 3 cluster pilota | Torino: keyword raw+cluster+fonti e QA |
| **4 — Competitive** | Mod.02: applicare `competitor-selection-v1` dello scope §4.4–4.7, discovery per offerta/bisogno, diretti/sostitutivi e canali distinti; 5+3 profili, score v1.1 invariato, spider + Social/Ads/Reviews/Company | Confermare proposta/alternative, associazioni brand→P.IVA/social e 3 scorecard | Cinque profili motivati per analisi/offerta oppure partial con lacune, fonti e copertura; classi pertinenti escluse motivate; revisione umana del metodo, no score inventati |
| **5 — UVP/ICP/Positioning** | Mod.03+04, buying committee B2B per job title e approccio motivato, ATECO, mode in development, TOV anti-slop | Fornire eventuale UVP/prove o spuntare in-development; approvare ICP e messaging | Test B2B+B2C, esistente/in sviluppo, no claim fake |
| **6 — Channels/Execution** | Mod.05+06, canali, orchestration, Paid budget min test, skill/resource gap esterno, KPI | Inserire Paid budget, persone, ore TOTALI settimanali, skills; approvare min budget, eventuali preventivi | Piano coerente, test budget insufficiente, costi media/tool/outsourcing distinti |
| **7 — Deck** | Mod.07, templates (main, optional section, two content), PPTX native, QA rendere | Fornire branding opzionale, approvare template, provare editabilità reale | Deck modificabile senza overflow e contenuti con source IDs |
| **8 — Release** | E2E, failure provider, storage/deploy, costi; verifica operativa KB-001 prima della release | Approvare spese, pilota e rilascio; rivedere report fonti | Smoke production + acceptance B2B/B2C + KB-001 collaudato + checklist owner firmata |

**Dipendenza critica:** i gate 1C e 1D richiedono accessi e prove reali; mock non sono tested. Gate 1A riprodotto nel repository il 25 ottobre: dati e copertura del campione registrati nell'audit, Trends limitato. Nessuna estensione automatica della validazione a tutti i mercati o alle altre fonti.

## Checklist proprietà — SOLO azioni davvero tue
| Quando | Azione tua | Credenziale / cosa fornire | Obbligatorietà | Risultato atteso |
|---|---|---|---|---|
| Gate 0 | Creare/collegare repo su account Pro; import docs | GitHub connessione o clone locale | Sì | Codex legge root `docs/`, quindi `AGENTS.md` |
| Prima dei test AI al Gate 2 | Attivare OpenAI Platform API, quota e key server-side | `OPENAI_API_KEY` env secret | Sì per agenti; non blocca Gate 0 locale | probe Structured Outputs testabile; ChatGPT Pro ≠ API billing |
| Gate 1A | Configurare accesso DataForSEO nel nuovo ambiente | Login/password API solo come secret server-side | Sì per Search; non blocca Gate 0 locale | stessi endpoint campione replicati |
| Gate 1C | Fornire/attivare Meta Developer e accesso Ad Library + Instagram Business Discovery | App ID/token con scopes effettivi, script IG preesistente | Per Social/Meta ufficiale | prova 2 advertiser, media competitor |
| Gate 1C | Autorizzare SearchAPI o Apify *solo se fallback necessario* | token, limite prova | Condizionale | nessun abbonamento duplicato |
| Gate 1D | Aprire Openapi Company e budget per 3 company/1 bilancio | API key server env | Sì per dati corporate automatici | fatturato/anno, addetti/anno, ATECO |
| Gate 1E | Fornire studi o casi interni se esistono | upload volontario | Facoltativo | supporto a UVP/buyer |
| Gate 2 | Aprire Supabase, Render (API+worker), Vercel | account e segreti deploy | Sì | end-to-end persistente |
| Gate 3/4 | Approvare dati campione e shortlist competitor | feedback umano sulle evidenze | Sì come quality gate | validazione business |
| Gate 5/6 | Inserire brief reale, UVP dove applicabile, budget Paid, persone, ore e skills | form MVP | Sì per piano | esecuzione coerente con risorse |
| Gate 7 | Fornire logo/colori/font licenziati se li vuoi | asset in repository | Facoltativo | deck brandizzato |
| Gate 8 | Accettare risultati reali e autorizzare pubblicazione | approvazione esplicita | Sì | deploy production autorizzato |

## Standard Gate QA
### KB-001 — accettazione prima della release
Implementazione al Gate 2 con Python e GitHub Actions/a richiesta: registro approvato, controllo giornaliero del solo calendario, richieste HTTP solo per fonti scadute dopo 45 giorni. Test con orologio controllato a 44/45/46 giorni; fonti senza precedente verifica; HTTP 304, ETag/Last-Modified, hash modificato/invariato, timeout/errore e rate limit; aggiornare `last_checked_at` solo per una verifica effettiva riuscita, mantenendo errori e tentativi separati. Report fonti cambiate/non raggiungibili, limiti e quote. Nessuna modifica a playbook o nuova fonte acquisita automaticamente. Gate 8: eseguire e osservare il percorso reale autorizzato e verificare report/schedulazione prima della release. Stato attuale: comando a richiesta e 27 test offline implementati; registro reale approvato, schedulazione e prova live restano da completare. Nessun monitor attivo.

Per considerare un gate `PASS`: `test_command`, `test_date`, `version`, `provider`, `endpoint`, `test_input`, `status_code`, `sample_count`, `coverage`, `cost`, `raw_fixture_ref`, `limitations`, `user_approval_if_needed`. Documentare prove nei file di log/fixtures. Se solo `documented` o `blocked`, il gate non è superato.

## Modalità di esecuzione Codex
Un gate alla volta, no sviluppo autonomo di gate successivi senza richiesta. Prima di scrivere codice leggere `docs/README.md`, `docs/00_PROJECT/PROJECT_SCOPE.md`, scope del modulo pertinente, matrice provider, stack e roadmap. Mai acquistare servizi o inventare credenziali. Dopo ogni gate: test, screenshot/interazioni UI se rilevanti, diff, aggiornamento checklist e passaggio di consegne.

## Milestone riassunte
1. **Infrastructure + Access:** repo e access proof.
2. **Data engine:** schema, worker, adapters.
3. **Analysis engine:** Moduli 01–02.
4. **Strategy engine:** Moduli 03–06.
5. **Deck + QA + Release:** Modulo 07, end-to-end, deploy.

**Durata:** da stimare solo dopo l'effettivo Gate 1 e i costi dei provider; non inserire promesse infondate di ore/uomo o date rilascio.

**Vincolo economico aggiornato dal proprietario (25 ottobre 2026):** pilota DataForSEO Gate 1A fino a 5 USD complessivi. Prodotto: obiettivo 10 USD e massimo 15 USD per l'intera esecuzione GTM, dati + AI + contenuto analitico/strategico + deck e costi attribuibili. Gate 1 misura i costi dei campioni; Gate 2 implementa il ledger trasversale e lo stop prima delle chiamate fuori budget; Gate 8 misura il totale reale e verifica la soglia su casi pilota senza ridurre i requisiti o inventare dati. Fattibilità economica non ancora dimostrata.
