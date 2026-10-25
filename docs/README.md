# GTM Engine — Documentazione di progetto
**Stato al 24 ottobre 2026:** Scoping funzionale 01–07 completo; architettura e roadmap MVP definite per Codex. L'integrazione dei provider non è tutta verificata. Nessun software end-to-end sviluppato.

## Ordine di lettura per Codex
1. `00_PROJECT/PROJECT_SCOPE.md` — requisiti trasversali.
2. `00_PROJECT/PROVIDER_ACCESS_AND_VALIDATION_MATRIX.md` — **stato reale di ogni dato richiesto** e accreditamento della fonte.
3. `00_PROJECT/TECHNOLOGY_STACK_AND_ARCHITECTURE.md` — stack e contratti.
4. `00_PROJECT/DEVELOPMENT_ROADMAP_AND_OWNER_ACTIONS.md` — gate/compiti utente/criteri superamento.
5. `00_PROJECT/DATA_ACCESS_AUDIT_2026-10-24.md` — dettagli metodi, test e fonti.
6. `00_PROJECT/KNOWLEDGE_BASE.md` — playbook condivisi GitHub Markdown.
7. `01_.../SCOPE.md` … `07_.../SCOPE.md`; `02_.../SCORING_MODEL.md`.
8. `00_PROJECT/EVOLUTION_BACKLOG.md` — evolutive, non MVP.

## Naming
Ogni modulo ha `SCOPE.md`; il Modulo 02 include `SCORING_MODEL.md`. Il file istruzioni Codex si chiama **`AGENTS.md`** nella root del repository (ancora da redigere dopo questa fase). Non rinominare in `agents.md`.

## Scelte confermate
- React/TypeScript frontend creato da **Codex**, non Lovable; Vercel deploy.
- Python FastAPI backend+worker su Render, Supabase Postgres+Storage, OpenAI API agents.
- DataForSEO primary for keyword, search, local and Google ads competitor transparency.
- Meta official Ad Library API per annunci UE come prima strada; Instagram Business Discovery dove autorizzato; provider terzi solo fallback.
- Openapi per dati impresa Italia, previa verifica API key e costi.
- Markdown Knowledge Base, NO vector RAG; PowerPoint editable via python-pptx.

## Nota sulle percentuali
100% specifica architettura/roadmap = scelte e azioni definite, **non** connessioni o moduli installati. `T / T_LIMITED / D / G / U / X` nella matrice è l'unico stato ufficiale di accessibilità fino ai test Codex.
