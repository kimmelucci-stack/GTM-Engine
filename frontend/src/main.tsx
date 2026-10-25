import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

function App() {
  return (
    <main>
      <p className="eyebrow">GTM Engine</p>
      <h1>Dalle evidenze alla strategia.</h1>
      <section aria-labelledby="status-title">
        <h2 id="status-title">Preparazione del progetto</h2>
        <p>La piattaforma è in sviluppo. Nessuna analisi è stata avviata.</p>
        <details>
          <summary>Stato delle fonti</summary>
          <p>L’accesso ai provider deve essere verificato in questo ambiente prima di raccogliere dati.</p>
        </details>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>);
