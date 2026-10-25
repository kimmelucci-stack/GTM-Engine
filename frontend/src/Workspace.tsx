import { useState, type KeyboardEvent } from 'react';
import { CompetitorReview, type ReviewProposal } from './CompetitorReview';
import { Icon } from './Icon';

const stages = [
  ['search', 'Domanda di mercato'], ['market', 'Scenario competitivo'],
  ['users', 'Clienti ideali'], ['target', 'Posizionamento'],
  ['route', 'Strategia canali'], ['file', 'Piano operativo'], ['deck', 'Presentazione'],
];
const names = ['Atlas Club', 'Forma Studio', 'Verde Social Club', 'Nove Outdoor',
  'Riva Experience', 'Campo Collective', 'Spazio Uno'];
const reasons = ['Stessa occasione d’acquisto e offerta sportiva comparabile.',
  'Un’esperienza di gruppo alternativa per lo stesso pubblico.',
  'Servizi sportivi e spazi dedicati alla socialità.',
  'Attività all’aperto come alternativa alla giornata al club.',
  'Unisce attività di gruppo e momenti di convivialità.',
  'Alternativa da confrontare sul servizio e sul territorio.',
  'Spazi per incontri ed esperienze condivise.'];

export function Workspace() {
  const [offer, setOffer] = useState('club');
  const [references, setReferences] = useState(false);
  function navigateOffer(event: KeyboardEvent<HTMLButtonElement>) {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const index = event.key === 'Home' ? 0 : event.key === 'End' ? 1 : offer === 'club' ? 1 : 0;
    setOffer(index === 0 ? 'club' : 'business');
    event.currentTarget.parentElement?.querySelectorAll<HTMLButtonElement>('[role=tab]')[index]?.focus();
  }
  const proposal: ReviewProposal = {
    analysisId: `design-preview-${offer}`, revision: 'design-v3',
    offer: offer === 'club' ? 'Sport e tempo libero' : 'Eventi aziendali',
    proposedIds: ['1', '2', '3', '4', '5'],
    candidates: names.map((name, i) => ({
      id: String(i + 1), name, website: `https://example${i}.test/`,
      relation: i % 2 === 0 ? 'direct' : 'substitute', rationale: reasons[i],
      eligible: true, organic: 'Da verificare', paid: 'Da verificare', sources: [],
    })),
  };
  return <div className="app-shell">
    <aside className="sidebar" aria-label="Navigazione progetto">
      <a className="wordmark" href="/" aria-label="GTM Engine, inizio"><span className="brand-symbol">g</span>
        <span>GTM Engine</span></a>
      <div className="workspace-switch"><span className="workspace-avatar">W</span>
        <div>Il tuo workspace<small>Proposta di interfaccia</small></div></div>
      <p className="nav-heading">Workspace</p>
      <button className="nav-item" disabled title="Disponibile con la gestione progetti"><Icon name="grid" />Progetti</button>
      <div className="sidebar-project"><span className="project-dot" />Progetto dimostrativo</div>
      <p className="nav-heading phases-label">Percorso GTM</p>
      <nav>{stages.map(([icon, label], i) => <button key={label}
        className={`nav-item ${i === 1 ? 'active' : ''}`} disabled={i !== 1}
        aria-current={i === 1 ? 'page' : undefined} title={i === 1 ? 'Vista corrente' : 'Fase non ancora disponibile'}>
        <Icon name={icon} /><span>{label}</span></button>)}</nav>
      <div className="sidebar-bottom">
        <button className={`nav-item ${references ? 'active' : ''}`} onClick={() => setReferences(!references)}>
          <Icon name="book" />Direzione di design</button>
        <div className="preview-label"><span className="status-dot" /><span>Anteprima interattiva<small>Nessun dato di progetto reale</small></span></div>
      </div>
    </aside>
    <div className="workspace-main">
      <header className="topbar"><div className="breadcrumb"><Icon name="grid" size={16} />
        <span>Progetto dimostrativo</span><span className="slash">/</span><strong>Scenario competitivo</strong></div>
        <span className="design-badge">Anteprima con dati sintetici</span></header>
      <main>
        <div className="page-heading"><Icon name="market" size={21} /><div>
          <h1>Competitor</h1><p>Confronta i candidati e conferma i profili da analizzare.</p></div></div>
        {references && <section className="design-direction" aria-label="Direzione di design">
          <div><h2>Riferimento: l’app Attio</h2>
            <p>Inter variabile, tabella continua, controlli compatti e dettagli su richiesta. CTA senza frecce.</p></div>
          <div className="reference-links"><a href="https://attio.com/help/reference/attio-101/introduction-to-navigating-attio" target="_blank" rel="noreferrer">Interfaccia Attio</a>
            <a href="https://rsms.me/inter/" target="_blank" rel="noreferrer">Font Inter</a></div>
          <button className="icon-button" aria-label="Chiudi direzione di design" onClick={() => setReferences(false)}><Icon name="close" /></button>
        </section>}
        <div className="offer-header"><div role="tablist" aria-label="Offerta da analizzare">
          <button role="tab" tabIndex={offer === 'club' ? 0 : -1} aria-selected={offer === 'club'} onKeyDown={navigateOffer} onClick={() => setOffer('club')}>Sport e tempo libero</button>
          <button role="tab" tabIndex={offer === 'business' ? 0 : -1} aria-selected={offer === 'business'} onKeyDown={navigateOffer} onClick={() => setOffer('business')}>Eventi aziendali</button></div>
          <span className="offer-note"><Icon name="globe" size={14} />Mercato dimostrativo</span></div>
        <CompetitorReview key={`${proposal.analysisId}:${proposal.revision}`} proposal={proposal}
          preview onConfirm={async () => { /* Preview only: no API, storage or job simulation. */ }} />
        <p className="canvas-footnote"><Icon name="info" size={14} />Nomi e classificazioni dimostrativi. Le conferme restano in questa sessione; nessuna analisi viene avviata.</p>
      </main>
    </div>
  </div>;
}
