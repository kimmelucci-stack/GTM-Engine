# GTM Engine — Roadmap pronta per Codex, dipendenze e attività dell'utente
**24 ottobre 2026 · Roadmap di implementazione completa nella pianificazione, non eseguita.** Avvio codice e accessi esterni restano subordinati alle azioni del proprietario e a veri gate di accettazione. Il lavoro non è completato perché il piano è completo.

## Sequenza vincolante, con ownership esplicita
| Gate | Responsabile Codex | Responsabile utente | Deliverable e condizione di uscita |
|---|---|---|---|
| **0 — Repository** | Audit cartelle, config React/FastAPI/worker, versioni e toolchain, `.env.example`, basic CI | Aprire GitHub su ChatGPT Pro/Codex; caricare `docs/`; creare account OpenAI API/DataForSEO/Supabase/Vercel/Render e autorizzare limiti costo | Repo collegato + healthcheck, build React e pytest locali |
| **1A — Proven DataForSEO** | Riprodurre 12 prove eseguite in audit; estrarre raw fixtures; controllare copertura; benchmark costo | Inserire DataForSEO API credentials nell'ambiente Codex, confermare limite richieste | Geo city/regione/nazione; keywords, SERP, trends nullable, Maps, reviews, Google Ads; log con evidence |
| **1B — Competitor web** | Crawl di 5 siti con HTTP e fallback Playwright, scraping prezzi/claims/cases | Dare script crawler già sviluppato se disponibile; confermare 5 competitor campione | Almeno 5 siti, output normalizzato e fonte per ogni claim, record unavailable |
| **1C — Meta Ads + IG** | Test ufficiale Meta `ads_archive` EU per 2 advertiser IT e Business Discovery per 2 account prof. Test provider fallback solo se l'ufficiale fallisce | Attivare Developer App/token/permessi e, se necessario, verifica identità; offrire script IG già usato. Se fallback, autorizzare SearchAPI/Apify | 2 advertiser e 2 pagine/50 media ove disponibili, copertura registrata, oppure gate bloccato con causa precisa |
| **1D — Openapi Company** | Test ricerca match società, P.IVA, ATECO, fatturato/anno e addetti/anno; confronto con bilancio | Creare/fornire Openapi token e limite spesa per 3 aziende + 1 bilancio | 3 company matches e record source/status; ambiguo non forzato |
| **1E — Fonti pubbliche** | Import test ISTAT ATECO2025 e query Eurostat/ESCO/OpenAlex | Nessuna azione salvo input studi proprietari | Una richiesta/download reale per fonte, timestamp, versione e query salvati |
| **2 — Foundation** | Adapters, schema Postgres, source/evidence/observations, job worker, cost cap, loader KB, fallback contract | Creare Supabase con accessi ambiente; attivare Render API+worker e Vercel | REST+job+storage end-to-end; test retry, fail e timeout |
| **3 — Demand** | Mod.01 workflow e minimal UI, metriche e quality status | Validare 20 keyword e 3 cluster pilota | Torino: keyword raw+cluster+fonti e QA |
| **4 — Competitive** | Mod.02 5+3 competitor, score v1.1 invariato, spider + Social/Ads/Reviews/Company | Confermare associazioni brand→P.IVA/social e 3 scorecard | 5 società, dati misti/partial; no score inventati |
| **5 — UVP/ICP/Positioning** | Mod.03+04, buyer, ATECO, mode in development, TOV anti-slop | Fornire eventuale UVP/prove o spuntare in-development; approvare ICP e messaging | Test B2B+B2C, esistente/in sviluppo, no claim fake |
| **6 — Channels/Execution** | Mod.05+06, canali, orchestration, Paid budget min test, skill/resource gap esterno, KPI | Inserire Paid budget, persone, ore TOTALI settimanali, skills; approvare min budget, eventuali preventivi | Piano coerente, test budget insufficiente, costi media/tool/outsourcing distinti |
| **7 — Deck** | Mod.07, templates (main, optional section, two content), PPTX native, QA rendere | Fornire branding opzionale, approvare template, provare editabilità reale | Deck modificabile senza overflow e contenuti con source IDs |
| **8 — Release** | Test E2E, failure provider, storage/deploy, osservabilità/costi per run | Approvare spese cloud/run, risultato pilota e rilascio | Smoke production + acceptance B2B/B2C + checklist owner firmata |

**Dipendenza critica:** i gate 1C e 1D non possono essere segnati superati senza token e permessi; Codex può sviluppare mock e altre fasi indipendenti ma non mostrare fonti come `tested` quando non lo sono. Gate 1A DataForSEO ha alcune prove nella chat Plus, da ripetere nel runtime Pro con test automatici riproducibili.

## Checklist proprietà — SOLO azioni davvero tue
| Quando | Azione tua | Credenziale / cosa fornire | Obbligatorietà | Risultato atteso |
|---|---|---|---|---|
| Gate 0 | Creare/collegare repo su account Pro; import docs | GitHub connessione o clone locale | Sì | Codex legge root `docs/`, quindi `AGENTS.md` |
| Gate 0 | Attivare OpenAI Platform API, quota e key server-side | `OPENAI_API_KEY` env secret | Sì | probe Structured Outputs testabile; ChatGPT Pro ≠ API billing |
| Gate 0/1A | Trasferire accesso DataForSEO al nuovo ambiente | API login/password o token esposto come secret | Sì | stessi endpoint campione replicati |
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
