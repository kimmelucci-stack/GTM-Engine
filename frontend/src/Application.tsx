import { useCallback, useEffect, useRef, useState, type FormEvent } from 'react';
import { api, ApiError, type Project, type Run } from './api';
import { Icon } from './Icon';
import { Workspace } from './Workspace';

const states: Record<string, string> = { queued: 'In attesa', running: 'In corso', completed: 'Completata',
  partial: 'Parziale', failed: 'Non riuscita', cancelled: 'Annullata' };
const date = (value: string) => new Date(value).toLocaleString('it-IT', { dateStyle: 'medium', timeStyle: 'short' });
const message = (error: unknown) => error instanceof ApiError ? error.message : 'Operazione non riuscita. Riprova.';

export function Application() {
  return window.location.pathname === '/demo' ? <Workspace /> : <PrivateWorkspace />;
}

function PrivateWorkspace() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);
  const [error, setError] = useState('');
  const [loginBusy, setLoginBusy] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<Project | null>(null);
  const [creating, setCreating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [runs, setRuns] = useState<Run[]>([]);
  const [current, setCurrent] = useState<Run | null>(null);
  const [starting, setStarting] = useState(false);
  const [activityError, setActivityError] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);
  const requests = useRef(new Map<string, string>());
  const epoch = useRef(0);
  const dialog = useRef<HTMLElement>(null);
  const activeProject = useRef<string | null>(null);
  activeProject.current = selected?.id ?? null;

  useEffect(() => {
    let mounted = true;
    api<{ authenticated: boolean }>('/auth/session').catch(async e => {
      if (!(e instanceof ApiError && e.status === 401)) throw e;
      await api('/auth/refresh', { method: 'POST' });
      return api<{ authenticated: boolean }>('/auth/session');
    }).then(() => { if (mounted) setAuthenticated(true); })
      .catch(e => { if (mounted) { setAuthenticated(false); if (!(e instanceof ApiError && e.status === 401)) setError(message(e)); } });
    const expired = () => { epoch.current++; setAuthenticated(false); setSelected(null); setProjects([]); setCurrent(null); setRuns([]); setError('Sessione scaduta. Accedi di nuovo.'); };
    window.addEventListener('gtm-session-expired', expired);
    return () => { mounted = false; window.removeEventListener('gtm-session-expired', expired); };
  }, []);

  const loadProjects = useCallback(async () => {
    const generation = epoch.current;
    setLoading(true); setError('');
    try { const value = await api<Project[]>('/projects'); if (generation === epoch.current) setProjects(value); }
    catch (e) { if (generation === epoch.current) setError(message(e)); }
    finally { if (generation === epoch.current) setLoading(false); }
  }, []);
  useEffect(() => { if (authenticated) void loadProjects(); }, [authenticated, loadProjects]);

  useEffect(() => {
    if (!creating) return;
    const previous = document.activeElement as HTMLElement | null;
    const handle = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !saving) setCreating(false);
      if (event.key !== 'Tab') return;
      const elements = [...(dialog.current?.querySelectorAll<HTMLElement>('input:not(:disabled),textarea,button:not(:disabled)') ?? [])];
      const first = elements[0], last = elements[elements.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    document.addEventListener('keydown', handle);
    return () => { document.removeEventListener('keydown', handle); previous?.focus(); };
  }, [creating, saving]);

  const loadRuns = useCallback(async (project: Project) => {
    try {
      const value = await api<{ runs: Run[] }>(`/projects/${project.id}/runs`);
      if (activeProject.current === project.id) { setRuns(value.runs); setCurrent(value.runs[0] ?? null); }
    } catch (e) { if (activeProject.current === project.id) setActivityError(message(e)); }
  }, []);
  useEffect(() => { setRuns([]); setCurrent(null); setExpanded(null); setActivityError(''); if (selected) void loadRuns(selected); }, [selected, loadRuns]);

  useEffect(() => {
    if (!current || !selected) return;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout>;
    const projectId = selected.id;
    const poll = async () => {
      try {
        const run = await api<Run>(`/runs/${current.id}`);
        if (stopped || activeProject.current !== projectId) return;
        setCurrent(run); setRuns(previous => previous.map(r => r.id === run.id ? run : r)); setActivityError('');
        if (['queued', 'running'].includes(run.status)) timer = setTimeout(poll, document.hidden ? 10000 : 2500);
      } catch (e) { if (!stopped) setActivityError(message(e)); }
    };
    void poll();
    return () => { stopped = true; clearTimeout(timer); };
  }, [current?.id, selected?.id]);

  async function login(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); epoch.current++; setLoginBusy(true); setError('');
    const form = event.currentTarget; const data = new FormData(form);
    try {
      await api('/auth/login', { method: 'POST', body: JSON.stringify({ email: data.get('email'), password: data.get('password') }) });
      form.reset(); setAuthenticated(true);
    } catch (e) { setError(e instanceof ApiError && e.status === 401 ? 'Accesso non riuscito. Verifica email e password.' : message(e)); }
    finally { setLoginBusy(false); }
  }
  async function logout() {
    try { await api('/auth/logout', { method: 'POST' }); epoch.current++; setAuthenticated(false); setProjects([]); setSelected(null); setCurrent(null); setRuns([]); requests.current.clear(); }
    catch (e) { setError(message(e)); }
  }
  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setSaving(true); setError('');
    const generation = epoch.current;
    const data = new FormData(event.currentTarget);
    try {
      const project = await api<Project>('/projects', { method: 'POST', body: JSON.stringify({
        title: data.get('title'), offer_brief: { offer: data.get('offer') }, geo: { area: data.get('area') },
        product_in_development: data.get('development') === 'on', locale: 'it-IT' }) });
      if (generation === epoch.current) { setCreating(false); setProjects(previous => [project, ...previous]); setSelected(project); }
    } catch (e) { setError(message(e)); } finally { setSaving(false); }
  }
  async function start() {
    if (!selected) return;
    const project = selected; setStarting(true); setActivityError('');
    const request = requests.current.get(project.id) ?? crypto.randomUUID(); requests.current.set(project.id, request);
    try {
      const run = await api<Run>(`/projects/${project.id}/runs`, { method: 'POST', body: JSON.stringify({ request_id: request, operation: 'catalog.archive', cap_usd: '10' }) });
      requests.current.delete(project.id);
      if (activeProject.current === project.id) { setCurrent(run); setRuns(previous => [run, ...previous.filter(r => r.id !== run.id)]); }
    } catch (e) { if (activeProject.current === project.id) setActivityError(message(e)); }
    finally { setStarting(false); }
  }
  async function download(identifier: string) {
    try {
      const blob = await api<Blob>(`/artifacts/${identifier}/content`);
      const url = URL.createObjectURL(blob); const link = document.createElement('a');
      link.href = url; link.download = 'evidenza.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    } catch (e) { setActivityError(message(e)); }
  }

  if (authenticated === null) return <div className="access-page"><span className="access-loading" role="status">Apertura dello spazio di lavoro…</span></div>;
  if (!authenticated) return <div className="access-page"><header className="access-brand"><span className="brand-symbol">g</span>GTM Engine</header>
    <main className="access-panel"><span className="section-label">IL TUO SPAZIO DI LAVORO</span><h1>Accedi a GTM Engine</h1>
      <p>Progetti, evidenze e attività in un unico spazio privato.</p>
      <form onSubmit={login}><label htmlFor="login-email">Email</label><input id="login-email" name="email" type="email" autoComplete="username" required maxLength={320} />
        <label htmlFor="login-password">Password</label><input id="login-password" name="password" type="password" autoComplete="current-password" required maxLength={1024} />
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="primary-button" disabled={loginBusy}>{loginBusy ? 'Accesso in corso…' : 'Accedi'}</button></form>
      <p className="access-note">Usa un account di GTM Engine. L’accesso al pannello Supabase è separato.</p>
      <a className="demo-link" href="/demo">Esplora la demo</a></main><footer className="access-footer">Il lavoro resta nel tuo account.</footer></div>;

  return <div className="app-shell"><aside inert={creating} className="sidebar" aria-label="Navigazione workspace">
    <a className="wordmark" href="/"><span className="brand-symbol">g</span><span>GTM Engine</span></a>
    <div className="workspace-switch"><span className="workspace-avatar">W</span><div>Il tuo workspace<small>Spazio privato</small></div></div>
    <p className="nav-heading">Workspace</p><button className="nav-item active" onClick={() => { setSelected(null); setCreating(false); void loadProjects(); }}><Icon name="grid" />Progetti</button>
    <div className="sidebar-bottom"><a className="nav-item" href="/demo">Demo competitor</a><button className="nav-item" onClick={() => void logout()}>Esci</button></div>
  </aside><div inert={creating} className="workspace-main"><header className="topbar"><div className="breadcrumb"><Icon name="grid" size={16} />{selected ? <button className="breadcrumb-button" onClick={() => setSelected(null)}>Elenco progetti</button> : <span>Workspace</span>}{selected && <><span className="slash">/</span><strong>{selected.title}</strong></>}</div><span className="design-badge">Spazio privato</span><button className="text-button mobile-signout" onClick={() => void logout()}>Esci</button></header>
    <main><div className="project-heading"><div><h1>{selected ? selected.title : 'Progetti'}</h1><p>{selected ? 'Brief, attività e risultati del progetto.' : 'Organizza il lavoro per prodotto, servizio e mercato.'}</p></div>
      <button className="secondary-button" onClick={() => { setCreating(true); setError(''); }}>Nuovo progetto</button></div>
      {error && <p className="form-error workspace-notice" role="alert">{error}</p>}
      {!selected ? <section className="project-list" aria-label="I tuoi progetti"><div className="project-list-header"><span>Nome progetto</span><span>Mercato</span><span>Creato il</span></div>
        {loading ? <p className="empty-state" role="status">Caricamento progetti…</p> : projects.length ? projects.map(project => <button className="project-row" key={project.id} onClick={() => setSelected(project)}>
          <span><span className="project-mark"><Icon name="file" size={16} /></span><strong>{project.title}</strong></span><span>{project.geo.area || 'Non indicato'}</span><span>{date(project.created_at)}</span></button>)
          : <div className="empty-state"><span className="empty-mark"><Icon name="file" size={24} /></span><h2>Il tuo primo progetto</h2><p>Aggiungi l’offerta e il mercato da cui partire.</p><button className="secondary-button" onClick={() => setCreating(true)}>Crea progetto</button></div>}
        {error && <button className="secondary-button list-retry" onClick={() => void loadProjects()}>Riprova caricamento</button>}
      </section> : <div className="project-detail"><section className="brief-panel"><h2>Il progetto</h2><dl><div><dt>Offerta</dt><dd>{selected.offer_brief.offer || 'Non indicata'}</dd></div><div><dt>Mercato</dt><dd>{selected.geo.area || 'Non indicato'}</dd></div><div><dt>Disponibilità</dt><dd>{selected.product_in_development ? 'In sviluppo' : 'Già disponibile'}</dd></div></dl></section>
        <section className="activity-panel"><div className="activity-heading"><div><h2>Attività</h2><p>Verifica il collegamento e conserva un’evidenza privata. Le analisi GTM non sono ancora avviabili.</p></div>
          <button className="secondary-button" disabled={starting || runs.some(r => ['queued', 'running'].includes(r.status))} onClick={() => void start()}>{starting ? 'Avvio in corso…' : requests.current.has(selected.id) ? 'Riprova avvio' : 'Verifica spazio di lavoro'}</button></div>
          {activityError && <div className="activity-notice"><p role="alert">{activityError}</p><button className="secondary-button" onClick={() => { setCurrent(null); void loadRuns(selected); }}>Aggiorna stato</button></div>}
          {runs.length ? <div className="run-list">{runs.map(run => <div className="run-row" key={run.id}><div><strong>Verifica spazio di lavoro</strong><small>{date(run.created_at)}</small></div><span className={`run-status status-${run.status}`}>{states[run.status] ?? 'Da verificare'}</span>
            <div className="run-evidence">{run.jobs?.some(j => j.lease_expired) && <span className="muted">Richiede un controllo</span>}<button className="text-button" aria-expanded={expanded === run.id} aria-controls={`run-${run.id}`} onClick={() => { setExpanded(expanded === run.id ? null : run.id); setCurrent(run); }}>{expanded === run.id ? 'Nascondi dettagli' : 'Dettagli'}</button>{run.artifact_ids?.map(id => <button key={id} className="text-button" onClick={() => void download(id)}>Scarica evidenza</button>)}</div>
            {expanded === run.id && <div className="run-details" id={`run-${run.id}`}>{run.jobs ? <><p>{run.started_at ? `Avviata il ${date(run.started_at)}` : 'In attesa di avvio.'}</p>{run.completed_at && <p>Conclusa il {date(run.completed_at)}</p>}{run.jobs.map((job, index) => <p key={index}>Tentativo {job.attempt} · {states[job.status] ?? 'Da verificare'}{job.lease_expired ? ' · È necessario verificare l’esecuzione.' : ''}</p>)}</> : <p role="status">Caricamento dettagli…</p>}</div>}</div>)}</div>
            : <div className="activity-empty"><p>Nessuna attività avviata.</p><small>Lo stato comparirà qui dopo l’avvio.</small></div>}
        </section></div>}
    </main></div>
    {creating && <div className="modal-backdrop"><section ref={dialog} className="project-dialog" role="dialog" aria-modal="true" aria-labelledby="new-project-title"><div className="dialog-title"><h2 id="new-project-title">Nuovo progetto</h2><button className="icon-button" aria-label="Chiudi nuovo progetto" disabled={saving} onClick={() => setCreating(false)}><Icon name="close" /></button></div>
      <form onSubmit={create}><label htmlFor="project-title">Nome progetto</label><input id="project-title" name="title" required maxLength={200} autoFocus placeholder="Es. Eventi aziendali" />
        <label htmlFor="project-offer">Prodotto o servizio</label><textarea id="project-offer" name="offer" required maxLength={10000} rows={3} placeholder="Descrivi in breve l’offerta da analizzare" />
        <label htmlFor="project-area">Mercato di riferimento</label><input id="project-area" name="area" required maxLength={200} placeholder="Es. Torino, Piemonte, Italia" />
        <label className="check-label"><input name="development" type="checkbox" />Il prodotto o servizio è ancora in sviluppo</label>
        {error && <p className="form-error" role="alert">{error}</p>}<div className="dialog-actions"><button type="button" className="secondary-button" disabled={saving} onClick={() => setCreating(false)}>Annulla</button><button className="primary-button" disabled={saving}>{saving ? 'Salvataggio…' : 'Crea progetto'}</button></div></form></section></div>}
  </div>;
}
