import { useEffect, useRef, useState } from 'react';
import { Icon } from './Icon';

export type ReviewCandidate = {
  id: string;
  name: string;
  website: string;
  relation: 'direct' | 'substitute' | 'unresolved';
  rationale: string;
  eligible: boolean;
  origin?: 'suggested' | 'manual';
  organic: string;
  paid: string;
  sources: { label: string; url: string }[];
};

export type ReviewProposal = {
  analysisId: string;
  revision: string;
  offer: string;
  candidates: ReviewCandidate[];
  proposedIds: string[];
  clientDomains?: string[];
};

export type ReviewDecision = {
  analysisId: string;
  revision: string;
  selectedIds: string[];
  manualUrls: string[];
};

function publicWebsite(value: string): string | null {
  try {
    const url = new URL(value);
    if (url.protocol !== 'https:' || url.username || url.password || url.search || url.hash
      || url.port || !url.hostname.includes('.') || url.hostname === 'localhost'
      || /^[\d.:]+$/.test(url.hostname) || url.hostname.endsWith('.local')) return null;
    return url.href;
  } catch { return null; }
}

function websiteLabel(value: string): string {
  try { return new URL(value).hostname; } catch { return 'Sito da verificare'; }
}

// Key the component by analysisId + revision: a new proposal must reset consent.
export function CompetitorReview({ proposal, onConfirm, preview = false }: {
  proposal: ReviewProposal;
  onConfirm: (decision: ReviewDecision) => Promise<void>;
  preview?: boolean;
}) {
  const [selected, setSelected] = useState(new Set(proposal.proposedIds.filter(id =>
    proposal.candidates.some(c => c.id === id && c.eligible))));
  const [manualUrls, setManualUrls] = useState<string[]>([]);
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');
  const [focused, setFocused] = useState(() => window.matchMedia('(min-width: 801px)').matches
    ? proposal.candidates[0]?.id ?? '' : '');
  const [showAdd, setShowAdd] = useState(false);
  const dialog = useRef<HTMLDialogElement>(null);
  const active = proposal.candidates.find(c => c.id === focused);
  const visible = proposal.candidates.filter(c =>
    c.name.toLocaleLowerCase('it').includes(search.toLocaleLowerCase('it'))
    && (filter === 'all' || (filter === 'selected' ? selected.has(c.id) : c.relation === filter)));
  useEffect(() => {
    if (showAdd) dialog.current?.showModal(); else dialog.current?.close();
  }, [showAdd]);
  const eligible = proposal.candidates.filter(c => c.eligible && c.origin !== 'manual').length;
  const required = Math.min(5, eligible);
  const baseCount = proposal.candidates.filter(c => selected.has(c.id) && c.origin !== 'manual').length;
  const extraCount = proposal.candidates.filter(c => selected.has(c.id) && c.origin === 'manual').length;
  const manualCount = proposal.candidates.filter(c => c.origin === 'manual').length + manualUrls.length;
  const valid = required > 0 && baseCount === required && extraCount <= 3 && manualUrls.length === 0;

  function toggle(id: string) {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelected(next); setConfirmed(false); setError('');
  }

  function addUrl() {
    const checked = publicWebsite(url.trim());
    if (!checked) { setError('Inserisci un sito HTTPS senza credenziali o parametri.'); return; }
    const host = new URL(checked).hostname.replace(/^www\./, '');
    if (proposal.clientDomains?.some(d => d.replace(/^www\./, '') === host)) {
      setError('Il sito del cliente non può essere aggiunto come competitor.'); return;
    }
    const known = [...proposal.candidates.map(c => c.website), ...manualUrls];
    if (known.some(value => {
      try { return new URL(value).hostname.replace(/^www\./, '') === host; }
      catch { return false; }
    })) { setError('Questo sito è già presente.'); return; }
    if (manualCount >= 3) { setError('Puoi aggiungere al massimo tre siti.'); return; }
    setManualUrls([...manualUrls, checked]); setUrl(''); setError(''); setConfirmed(false);
  }

  async function confirm() {
    if (!valid || busy) return;
    setBusy(true); setError('');
    try {
      await onConfirm({ analysisId: proposal.analysisId, revision: proposal.revision,
        selectedIds: [...selected], manualUrls });
      setConfirmed(true);
    } catch { setError('Conferma non riuscita. La selezione è conservata: puoi riprovare.'); }
    finally { setBusy(false); }
  }

  return <section className="review-workspace" aria-labelledby="review-title">
    <div className="review-heading"><div><h2 id="review-title">Seleziona i competitor <span className="count-badge">{proposal.candidates.length}</span></h2>
      <p>Conferma cinque profili da approfondire. Puoi confrontarli e sostituirli prima di procedere.</p></div>
      <button className="secondary-button" onClick={() => setShowAdd(true)} disabled={busy}>
        <Icon name="plus" size={16} />Aggiungi competitor</button></div>
    {eligible < 5 && <div className="inline-message">Campione parziale: {eligible} candidati verificati su cinque.</div>}
    <div className="review-layout">
      <div className="comparison-area">
        <div className="table-toolbar"><div className="filter-group" aria-label="Filtra competitor">
          {([['all', 'Tutti'], ['direct', 'Diretti'], ['substitute', 'Indiretti'], ['selected', 'Selezionati']] as const).map(([value, label]) =>
            <button key={value} className={filter === value ? 'selected-filter' : ''}
              aria-pressed={filter === value} onClick={() => setFilter(value)}>{label}
              {value === 'all' && <span>{proposal.candidates.length}</span>}</button>)}</div>
          <label className="search-input"><Icon name="search" size={16} />
            <input aria-label="Cerca competitor" placeholder="Cerca competitor…" value={search}
              onChange={event => setSearch(event.target.value)} /></label></div>
        <div className="table-scroll"><table className="competitor-table">
          <thead><tr><th className="check-cell"><span className="sr-only">Includi</span></th>
            <th>Competitor</th><th>Relazione</th><th>Ricerca organica</th><th>Annunci</th><th><span className="sr-only">Dettagli</span></th></tr></thead>
          <tbody>{visible.map((candidate, index) => <tr key={candidate.id}
            className={`${selected.has(candidate.id) ? 'included' : ''} ${focused === candidate.id ? 'focused-row' : ''}`}>
            <td className="check-cell"><input type="checkbox" checked={selected.has(candidate.id)}
              disabled={!candidate.eligible || busy} onChange={() => toggle(candidate.id)}
              aria-label={`Includi ${candidate.name}`} /></td>
            <td><button className="company-button" onClick={() => setFocused(candidate.id)}
              aria-label={`Dettagli ${candidate.name}`} aria-pressed={focused === candidate.id}>
              <span className={`company-avatar tone-${index % 5}`}>{candidate.name.split(' ').map(w => w[0]).slice(0, 2).join('')}</span>
              <span><strong>{candidate.name}</strong><small>{websiteLabel(candidate.website)}</small></span>
            </button></td>
            <td><span className={`relation-chip ${candidate.relation}`}><span />
              {candidate.relation === 'direct' ? 'Diretto' : candidate.relation === 'substitute' ? 'Indiretto' : 'Da verificare'}</span></td>
            <td><span className="unknown-value"><span className="unknown-dot" />{candidate.organic}</span></td>
            <td><span className="unknown-value"><span className="unknown-dot" />{candidate.paid}</span></td>
            <td><button className="icon-button row-detail" aria-label={`Apri scheda ${candidate.name}`}
              onClick={() => setFocused(candidate.id)}><Icon name="chevron" size={15} /></button></td>
          </tr>)}</tbody>
        </table>{visible.length === 0 && <div className="empty-results"><Icon name="search" size={24} />
          <h3>Nessun risultato</h3><p>Prova un altro nome o modifica il filtro.</p>
          <button className="text-button" onClick={() => { setSearch(''); setFilter('all'); }}>Mostra tutti</button></div>}</div>
        <div className="table-caption"><span>{visible.length} di {proposal.candidates.length} candidati</span>
          <span>La visibilità non equivale alla rilevanza commerciale.</span></div>
      </div>
      {active && <aside className="candidate-inspector" aria-label="Scheda competitor">
        <div className="inspector-top"><span>DETTAGLIO COMPETITOR</span><button className="icon-button" aria-label="Chiudi scheda" onClick={() => setFocused('')}><Icon name="close" size={15} /></button></div>
        <div className="inspector-identity"><span className="company-avatar large tone-0">{active.name.split(' ').map(w => w[0]).slice(0, 2).join('')}</span>
          <h3>{active.name}</h3><span className={`relation-chip ${active.relation}`}><span />{active.relation === 'direct' ? 'Concorrente diretto' : active.relation === 'substitute' ? 'Concorrente indiretto' : 'Da verificare'}</span></div>
        <div className="inspector-block"><h4>Perché è rilevante</h4><p>{active.rationale}</p>
          <span className="evaluation-label"><Icon name="info" size={13} />{preview ? 'Valutazione dimostrativa' : 'Valutazione da fonti'}</span></div>
        <div className="inspector-block"><h4>Presenza nei canali</h4><div className="channel-detail"><span>Ricerca organica</span><span>{active.organic}</span></div>
          <div className="channel-detail"><span>Annunci</span><span>{active.paid}</span></div>
          <p className="microcopy">Un dato non verificato non indica assenza dal mercato.</p></div>
        <div className="inspector-block"><h4>Fonti <span className="count-badge">{active.sources.length}</span></h4>
          {active.sources.length === 0 ? <div className="source-empty"><Icon name="file" size={18} /><span>{preview ? 'Nessuna fonte reale in questa anteprima.' : 'Nessuna fonte disponibile.'}</span></div>
            : active.sources.filter(s => publicWebsite(s.url)).map((source, i) => <a className="source-link" href={source.url} key={i} target="_blank" rel="noopener noreferrer">{source.label}<Icon name="external" size={13} /></a>)}
        </div>
        <button className={`inspector-select ${selected.has(active.id) ? 'is-included' : ''}`}
          disabled={busy || !active.eligible} onClick={() => toggle(active.id)}>
          <Icon name={selected.has(active.id) ? 'check' : 'plus'} size={16} />
          {selected.has(active.id) ? 'Incluso nella selezione' : 'Includi nella selezione'}</button>
      </aside>}
    </div>
    {manualUrls.length > 0 && <div className="pending-additions"><strong>Aggiunte da verificare</strong>
      {manualUrls.map(value => <div key={value}><span>{value}<small>In attesa di verifica</small></span>
        <button className="text-button" disabled={busy} onClick={() => { setManualUrls(manualUrls.filter(u => u !== value)); setConfirmed(false); }}>Rimuovi</button></div>)}
      <p role="status">Verifica dei nuovi siti non ancora collegata. Rimuovili per confermare il campione già verificato.</p></div>}
    <div className="review-footer"><div className="selection-summary"><span className={`selection-icon ${valid ? 'complete' : ''}`}><Icon name={valid ? 'check' : 'users'} size={19} /></span>
      <div><strong aria-live="polite">{baseCount} di {required} competitor selezionati{extraCount > 0 && ` + ${extraCount} aggiunti`}</strong>
        <small>{baseCount > required ? 'Deseleziona un candidato per continuare.' : manualUrls.length > 0 ? 'Completa la verifica dei siti aggiunti.' : 'La tua conferma precede l’analisi approfondita.'}</small></div></div>
      <button className="primary-button" type="button" disabled={!valid || busy || confirmed} onClick={confirm}>
        {busy ? 'Conferma in corso…' : confirmed ? 'Selezione confermata' : preview ? 'Conferma selezione di prova' : 'Conferma competitor'}<Icon name="arrow" size={17} /></button></div>
    {error && !showAdd && <p className="inline-message error-message" role="alert">{error}</p>}
    {confirmed && <p className="inline-message success-message" role="status">{preview ? 'Selezione di prova confermata in questa sessione. Nessuna analisi avviata.' : 'Selezione confermata.'}</p>}
    <dialog ref={dialog} className="add-dialog" onCancel={() => setShowAdd(false)} onClose={() => setShowAdd(false)} aria-labelledby="add-title">
      <div className="dialog-heading"><span className="dialog-icon"><Icon name="globe" size={22} /></span><button className="icon-button" aria-label="Chiudi aggiunta competitor" onClick={() => setShowAdd(false)}><Icon name="close" /></button></div>
      <h2 id="add-title">Aggiungi un competitor</h2><p>Inserisci il sito di un’azienda che vuoi includere nel confronto. Fino a tre aggiunte.</p>
      <label htmlFor="competitor-url">Sito web</label><input id="competitor-url" type="url" value={url} placeholder="https://azienda.it" disabled={busy} onChange={e => setUrl(e.target.value)} />
      {error && <p className="dialog-error" role="alert">{error}</p>}
      <div className="dialog-note"><Icon name="info" size={16} /><span>Prima dell’analisi verifichiamo identità e pertinenza. In questa anteprima la verifica non viene eseguita.</span></div>
      <div className="dialog-actions"><button className="secondary-button" onClick={() => setShowAdd(false)}>Chiudi</button><button className="primary-button" disabled={busy || manualCount >= 3} onClick={() => addUrl()}>Aggiungi</button></div>
      {manualUrls.length > 0 && <p className="dialog-added" role="status">{manualUrls.length} siti aggiunti, in attesa di verifica.</p>}
    </dialog>
  </section>;
}

