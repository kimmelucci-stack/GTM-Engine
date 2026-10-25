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
    analysisId: `design-preview-${offer}`, revision: 'design-v2',
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
      <a className="wordmark" href="/" aria-label="GTM Engine, inizio"><span className="brand-symbol">g<span>↗</span></span>
        <span>gtm<span className="brand-light">engine</span><small>STRATEGY WORKSPACE</small></span></a>
      <div className="workspace-switch"><span className="workspace-avatar">W</span>
        <div>Il tuo workspace<small>Proposta di interfaccia</small></div></div>
      <p className="nav-heading">WORKSPACE</p>
      <button className="nav-item" disabled title="Disponibile con la gestione progetti"><Icon name="grid" />Progetti</button>
      <div className="sidebar-project"><span className="project-dot" />Progetto dimostrativo</div>
      <p className="nav-heading phases-label">PERCORSO GTM</p>
      <nav>{stages.map(([icon, label], i) => <button key={label}
        className={`nav-item ${i === 1 ? 'active' : ''}`} disabled={i !== 1}
        aria-current={i === 1 ? 'page' : undefined} title={i === 1 ? 'Vista corrente' : 'Fase non ancora disponibile'}>
        <Icon name={icon} /><span>{label}</span><span className="stage-number">0{i + 1}</span></button>)}</nav>
      <div className="sidebar-bottom">
        <button className={`nav-item ${references ? 'active' : ''}`} onClick={() => setReferences(!references)}>
          <Icon name="book" />Direzione di design<Icon name="external" size={13} /></button>
        <div className="preview-label"><span className="status-dot" /><span>Anteprima interattiva<small>Nessun dato di progetto reale</small></span></div>
      </div>
    </aside>
    <div className="workspace-main">
      <header className="topbar"><div className="breadcrumb"><Icon name="grid" size={16} />
        <span>Progetto dimostrativo</span><span className="slash">/</span><strong>Scenario competitivo</strong></div>
        <span className="design-badge">Design preview <span>v02</span></span></header>
      <main>
        <div className="page-heading"><div><p className="eyebrow">MARKET INTELLIGENCE</p>
          <h1>Il tuo scenario competitivo<span>.</span></h1>
          <p>Individua le alternative. Confronta le evidenze. Scegli chi approfondire.</p></div>
          <div className="step-marker"><span>02</span><div>Scenario competitivo<small>Selezione dei competitor</small></div></div></div>
        <div className="workflow-strip" aria-label="Fasi dello scenario competitivo">
          <span><span className="step-circle">1</span>Individuazione</span><span className="workflow-line" />
          <span className="current"><span className="step-circle">2</span>Selezione</span><span className="workflow-line" />
          <span><span className="step-circle">3</span>Analisi</span><span className="workflow-line" />
          <span><span className="step-circle">4</span>Confronto</span>
          <span className="workflow-note">Navigazione proposta · esempio sintetico</span>
        </div>
        {references && <section className="design-direction" aria-label="Direzione di design">
          <div><p className="eyebrow">DIREZIONE A · WORKSPACE ANALITICO</p><h2>Chiarezza prima della decorazione.</h2>
            <p>Struttura di progetto, confronto a tabella e dettagli laterali. Una decisione principale per schermata.</p></div>
          <div className="reference-links"><a href="https://linear.app/docs/projects" target="_blank" rel="noreferrer">Linear <Icon name="external" size={13} /></a>
            <a href="https://attio.com/" target="_blank" rel="noreferrer">Attio <Icon name="external" size={13} /></a>
            <a href="https://www.clay.com/" target="_blank" rel="noreferrer">Clay <Icon name="external" size={13} /></a></div>
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
