import { useState } from 'react';

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

  return <section aria-labelledby="review-title">
    <p className="eyebrow">Concorrenti · Selezione</p>
    <h2 id="review-title">Chi vuoi includere nell’analisi?</h2>
    <p>{proposal.offer}</p>
    <p>Scegli cinque concorrenti. Puoi sostituire quelli proposti con le alternative disponibili.</p>
    {eligible < 5 && <p className="notice">Sono verificati soltanto {eligible} candidati.
      Puoi confermare il campione disponibile; la copertura resterà parziale.</p>}
    <fieldset disabled={busy}>
      <legend>Competitor proposti e alternative</legend>
      {proposal.candidates.map(candidate => <article className="candidate" key={candidate.id}>
        <label className="candidate-label">
          <input type="checkbox" checked={selected.has(candidate.id)}
            disabled={!candidate.eligible} onChange={() => toggle(candidate.id)} />
          <span><strong>{candidate.name}</strong><span className="badge">
            {candidate.relation === 'direct' ? 'Diretto' : candidate.relation === 'substitute'
              ? 'Indiretto · alternativa allo stesso bisogno' : 'Da verificare'}</span></span>
        </label>
        <p className="candidate-reason">{candidate.rationale}</p>
        {!candidate.eligible && <p className="candidate-reason">Da verificare prima della selezione.</p>}
        <details><summary>Presenza online e fonti</summary>
          <p>Ricerche: {candidate.organic}<br />Annunci: {candidate.paid}</p>
          {publicWebsite(candidate.website) && <a href={candidate.website} target="_blank"
            rel="noopener noreferrer">Visita il sito</a>}
          <ul>{candidate.sources.filter(s => publicWebsite(s.url)).map((source, index) =>
            <li key={index}><a href={source.url} target="_blank"
              rel="noopener noreferrer">{source.label}</a></li>)}</ul>
        </details>
      </article>)}
    </fieldset>
    <details className="manual"><summary>Aggiungi un competitor tramite sito web</summary>
      <p>Fino a tre aggiunte. I nuovi siti devono essere verificati prima della conferma:
        l’inserimento non avvia raccolte o chiamate a pagamento.</p>
      <label htmlFor="competitor-url">Sito del competitor</label>
      <div className="url-row"><input id="competitor-url" type="url" value={url}
        placeholder="https://…" disabled={busy} onChange={e => setUrl(e.target.value)} />
      <button type="button" disabled={busy || manualCount >= 3}
        onClick={addUrl}>Aggiungi</button></div>
      <ul>{manualUrls.map(value => <li key={value}>{value} — In attesa di verifica{' '}
        <button type="button" disabled={busy} onClick={() => {
          setManualUrls(manualUrls.filter(u => u !== value)); setConfirmed(false);
        }}>Rimuovi</button></li>)}</ul>
      {manualUrls.length > 0 && <p role="status">Verifica dei nuovi siti non ancora collegata.
        Puoi rimuoverli per confermare il campione già verificato.</p>}
    </details>
    <div className="review-footer">
      <p aria-live="polite">{baseCount} selezionati su {required}
        {extraCount > 0 && ` · ${extraCount} aggiunti`}
        {baseCount > required && ' · Deseleziona un candidato prima di confermare.'}</p>
      <button type="button" disabled={!valid || busy || confirmed} onClick={confirm}>
        {busy ? 'Conferma in corso…' : preview ? 'Conferma selezione di prova' : 'Conferma competitor'}
      </button>
    </div>
    {error && <p role="alert">{error}</p>}
    {confirmed && <p role="status">{preview
      ? 'Selezione di prova confermata in questa sessione. Nessuna analisi avviata.'
      : 'Selezione confermata.'}</p>}
  </section>;
}
