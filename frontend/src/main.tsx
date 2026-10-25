import { StrictMode, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { CompetitorReview, type ReviewProposal } from './CompetitorReview';
import './style.css';

function App() {
  const [preview, setPreview] = useState(false);
  const proposal: ReviewProposal = {
    analysisId: 'synthetic-preview', revision: 'preview-v1',
    offer: 'Esempio sintetico · attività di gruppo',
    proposedIds: ['1', '2', '3', '4', '5'],
    candidates: Array.from({ length: 7 }, (_, i) => ({
      id: String(i + 1), name: `Operatore di esempio ${i + 1}`, website: `https://example${i}.test/`,
      relation: i % 2 === 0 ? 'direct' : 'substitute',
      rationale: i < 5 ? 'Candidato sintetico proposto per mostrare la revisione.'
        : 'Alternativa sintetica disponibile per una sostituzione.',
      eligible: true, organic: 'Non verificata · esempio sintetico',
      paid: 'Non verificati · esempio sintetico', sources: [],
    })),
  };
  return (
    <main>
      <p className="eyebrow">GTM Engine</p>
      <h1>Dalle evidenze alla strategia.</h1>
      <section aria-labelledby="status-title">
        <h2 id="status-title">Preparazione del progetto</h2>
        <p>La piattaforma è in sviluppo. Nessuna analisi è stata avviata.</p>
        <details>
          <summary>Stato delle fonti</summary>
          <p>Alcuni accessi sono stati collaudati su campioni. Il flusso applicativo e il salvataggio delle approvazioni non sono ancora collegati.</p>
        </details>
      </section>
      <section>
        <h2>Approvazione dei competitor</h2>
        <p>Nessuna proposta di progetto disponibile.</p>
        <button onClick={() => setPreview(!preview)}>{preview ? 'Chiudi esempio' : 'Apri esempio interattivo'}</button>
      </section>
      {preview && <>
        <p className="notice">Anteprima con nomi inventati. La conferma resta solo in memoria,
          non viene salvata e non avvia analisi. Chiudendo l’esempio la selezione viene azzerata.</p>
        <CompetitorReview key={`${proposal.analysisId}:${proposal.revision}`} proposal={proposal}
          preview onConfirm={async () => { /* Deliberate preview: no simulated API or job. */ }} />
      </>}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
