# GTM Engine — Documentazione di progetto
**Stato al 25 ottobre 2026:** scope 01–07 consolidati; Gate 0 verificato; Gate 1A DataForSEO PASS_WITH_LIMITATIONS con prove live. Gate 1B PASS_WITH_LIMITATIONS: crawl tecnico su cinque siti, otto pagine disponibili; delega del proprietario per il solo campione di test, non approvazione commerciale. Nessun modulo end-to-end; Meta in attesa, Openapi non collaudato e fonti pubbliche Gate 1E parzialmente verificate. Prove storiche, DataForSEO e screening web distinti nell'audit.

## Ordine di lettura per Codex
1. `00_PROJECT/PROJECT_SCOPE.md` — requisiti trasversali.
2. `00_PROJECT/PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md` — **stato reale di ogni dato richiesto** e accreditamento della fonte.
3. `00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md` — stack e contratti.
4. `00_PROJECT/DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md` — gate/compiti utente/criteri superamento.
5. `00_PROJECT/DATA_ACCESS_AUDIT_2026-10-24.md` — dettagli metodi, test e fonti.
6. `00_PROJECT/KNOWLEDGE_BASE.md` — playbook condivisi GitHub Markdown.
7. [Demand](01_DEMAND_INTELLIGENCE/SCOPE.md), [Market](02_MARKET_INTELLIGENCE/SCOPE.md), [UVP/ICP](03_UVP_ICP_INTELLIGENCE/SCOPE.md), [Positioning](04_VALUE_PROPOSITION_POSITIONING/SCOPE.md), [Channels](05_CHANNEL_GTM_STRATEGY/SCOPE.md), [Execution](06_GTM_EXECUTION_PLANNING/SCOPE.md), [Deck](07_GTM_STRATEGY_DECK/SCOPE.md); [Scoring v1.1](02_MARKET_INTELLIGENCE/SCORING_MODEL.md).
8. `00_PROJECT/EVOLUTION_BACKLOG.md` — evolutive e KB-001 assegnato al Gate 2 con accettazione prima della release al Gate 8.

Stato e consegne: [handoff](00_PROJECT/HANDOFF_TO_CODEX.md) e [verifiche Gate 0](00_PROJECT/GATE_0_VALIDATION.md).

## Naming
Ogni modulo ha un solo `SCOPE.md` canonico; il Modulo 02 include `02_MARKET_INTELLIGENCE/SCORING_MODEL.md` v1.1, invariato. I vecchi nomi dei Moduli 06–07 sono solo rimandi compatibili. Il backlog canonico è esclusivamente `00_PROJECT/EVOLUTION_BACKLOG.md`. [AGENTS.md](../AGENTS.md) nella root contiene le istruzioni permanenti per Codex.

## Scelte confermate
- React/TypeScript frontend creato da **Codex**, non Lovable; Vercel deploy.
- Python FastAPI backend+worker su Render, Supabase Postgres+Storage, OpenAI API agents.
- DataForSEO primary for keyword, search, local and Google ads competitor transparency.
- Meta official Ad Library API per annunci UE come prima strada; Instagram Business Discovery dove autorizzato; provider terzi solo fallback.
- Openapi per dati impresa Italia, previa verifica API key e costi.
- Markdown Knowledge Base, NO vector RAG; PowerPoint editable via python-pptx.

## Nota sulle percentuali
Completezza della specifica non significa integrazioni operative. La matrice distingue accessibilità, disponibilità e natura epistemica; T/T_LIMITED richiedono ambiente/data/fixture. Il registro corrente del Gate 1A è distinto dalla tabella storica; l'archivio dell'audit conserva scelte superate senza renderle normative.

Repository pubblica per portfolio su richiesta del proprietario; credenziali, utenze provider, token, dati cliente e raw privati esclusi dai contenuti e dalla cronologia pubblicabili. Codice pubblico non equivale a deploy dell'applicazione.

Directory di riferimento per il buyer mapping B2B: [funzioni operative per reparto](03_UVP_ICP_INTELLIGENCE/BUSINESS_FUNCTION_DIRECTORY.md), con dati canonici nel backend; non è un organigramma né un catalogo di professioni.
