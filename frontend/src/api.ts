export class ApiError extends Error {
  constructor(readonly status: number, message: string) { super(message); }
}
let renewing: Promise<boolean> | null = null;
export async function api<T>(path: string, options: RequestInit = {}, retry = true): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...options, credentials: 'same-origin', cache: 'no-store',
      headers: { 'Content-Type': 'application/json', ...options.headers } });
  } catch { throw new ApiError(0, 'Collegamento interrotto. Riprova per recuperare lo stato.'); }
  if (response.status === 401 && retry && !path.startsWith('/auth/')) {
    renewing ??= fetch('/api/auth/refresh', { method: 'POST', credentials: 'same-origin', cache: 'no-store' })
      .then(r => r.ok).catch(() => false).finally(() => { renewing = null; });
    if (await renewing) return api<T>(path, options, false);
    window.dispatchEvent(new Event('gtm-session-expired'));
  }
  if (!response.ok) {
    const message = response.status === 401 ? 'Sessione scaduta. Accedi di nuovo.'
      : response.status === 403 ? 'Operazione non consentita.'
      : response.status === 404 ? 'Contenuto non disponibile.'
      : response.status === 409 ? 'Questa richiesta è già stata utilizzata con dati diversi.'
      : response.status === 422 ? 'Controlla i campi e riprova.'
      : response.status === 429 ? 'Troppi tentativi. Attendi e riprova.'
      : 'Servizio temporaneamente non disponibile. Riprova tra poco.';
    throw new ApiError(response.status, message);
  }
  if (path.endsWith('/content')) return await response.blob() as T;
  return await response.json() as T;
}

export interface Project {
  id: string; title: string; offer_brief: { offer?: string }; geo: { area?: string };
  product_in_development: boolean; created_at: string;
}
export interface Run {
  id: string; mode: string; status: string; created_at: string;
  started_at?: string | null; completed_at?: string | null;
  jobs?: { status: string; attempt: number; lease_expired: boolean }[];
  artifact_ids?: string[];
}
