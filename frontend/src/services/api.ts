import type { AnalysisResponse, BackendHealth, UserProfile } from '../types';

export class ApiError extends Error {
  statusCode: number;
  detail: string;

  constructor(statusCode: number, detail: string) {
    super(detail);
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

// In-memory / sessionStorage fallback token
let inMemoryToken: string | null = null;
try {
  inMemoryToken = sessionStorage.getItem('rigcheck_token');
} catch {
  // SessionStorage might be unavailable in some sandboxes
}

export function setSessionToken(token: string | null) {
  inMemoryToken = token;
  try {
    if (token) {
      sessionStorage.setItem('rigcheck_token', token);
    } else {
      sessionStorage.removeItem('rigcheck_token');
    }
  } catch {
    // Ignore storage errors
  }
}

export function getSessionToken(): string | null {
  return inMemoryToken;
}

/**
 * Resolves the active API base URL.
 * Priority:
 * 1. User runtime setting in localStorage ('rigcheck_api_base_url')
 * 2. Build-time Vite env var (import.meta.env.VITE_API_BASE_URL)
 * 3. Default empty string '' (falls back to same-origin /api)
 */
export function getApiBaseUrl(): string {
  try {
    const custom = localStorage.getItem('rigcheck_api_base_url');
    if (custom && custom.trim()) {
      return custom.trim().replace(/\/+$/, '');
    }
  } catch {
    // SessionStorage/localStorage may be unavailable in some sandboxes
  }
  const envUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) || '';
  return envUrl.trim().replace(/\/+$/, '');
}

export function setApiBaseUrl(url: string | null): void {
  try {
    if (url && url.trim()) {
      localStorage.setItem('rigcheck_api_base_url', url.trim().replace(/\/+$/, ''));
    } else {
      localStorage.removeItem('rigcheck_api_base_url');
    }
  } catch {
    // Ignore storage errors
  }
}

export function resolveUrl(path: string): string {
  const base = getApiBaseUrl();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return base ? `${base}${normalizedPath}` : normalizedPath;
}

function getAuthHeaders(): HeadersInit {
  const headers: Record<string, string> = {};
  if (inMemoryToken) {
    headers['Authorization'] = `Bearer ${inMemoryToken}`;
    headers['X-RigCheck-Token'] = inMemoryToken;
  }
  return headers;
}

async function parseErrorMessage(res: Response, fallback: string): Promise<string> {
  try {
    const text = await res.text();
    if (!text || !text.trim()) {
      if (res.status === 404 || res.status === 405) {
        return 'Backend endpoint not found (HTTP 404/405). If running from Render, please configure your active Cloudflare Tunnel URL below.';
      }
      return `${fallback} (HTTP ${res.status})`;
    }
    try {
      const data = JSON.parse(text);
      return data.detail || data.message || fallback;
    } catch {
      if (text.includes('<!DOCTYPE') || text.includes('<html')) {
        return res.status === 404 || res.status === 405
          ? 'Backend endpoint not reachable on static host. Please configure your active Cloudflare Tunnel URL below.'
          : `${fallback} (HTTP ${res.status})`;
      }
      return text.length < 300 ? text : fallback;
    }
  } catch {
    return `${fallback} (HTTP ${res.status})`;
  }
}

export async function checkAuthStatus(): Promise<boolean> {
  try {
    const res = await fetch(resolveUrl('/api/auth/status'), {
      credentials: 'include',
      headers: getAuthHeaders(),
    });
    if (!res.ok) return false;
    const data = await res.json();
    return Boolean(data.authenticated);
  } catch {
    return false;
  }
}

export async function loginWithSecret(secret: string): Promise<string> {
  let res: Response;
  try {
    res = await fetch(resolveUrl('/api/auth/login'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ secret }),
    });
  } catch (netErr: any) {
    throw new ApiError(
      0,
      `Cannot connect to backend: ${netErr.message || 'Network error'}. Check if your Cloudflare Tunnel is running and accessible.`
    );
  }

  if (!res.ok) {
    const detail = await parseErrorMessage(res, 'Authentication failed');
    throw new ApiError(res.status, detail);
  }

  const data = await res.json();
  const token = data.session_token;
  setSessionToken(token);
  return token;
}

export async function logout(): Promise<void> {
  try {
    await fetch(resolveUrl('/api/auth/logout'), {
      method: 'POST',
      credentials: 'include',
      headers: getAuthHeaders(),
    });
  } finally {
    setSessionToken(null);
  }
}

export async function fetchHealth(): Promise<BackendHealth> {
  const res = await fetch(resolveUrl('/api/health'), {
    credentials: 'include',
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errorText = await parseErrorMessage(res, 'Failed to reach health endpoint');
    throw new ApiError(res.status, errorText);
  }
  return res.json();
}

export async function fetchProfile(): Promise<UserProfile> {
  const res = await fetch(resolveUrl('/api/profile'), {
    credentials: 'include',
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    const errDetail = await parseErrorMessage(res, 'Failed to load profile');
    throw new ApiError(res.status, errDetail);
  }
  return res.json();
}

export async function saveProfile(profile: UserProfile): Promise<UserProfile> {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
  };

  const res = await fetch(resolveUrl('/api/profile'), {
    method: 'PUT',
    headers,
    credentials: 'include',
    body: JSON.stringify(profile),
  });
  if (!res.ok) {
    const errDetail = await parseErrorMessage(res, 'Failed to update profile');
    throw new ApiError(res.status, errDetail);
  }
  return res.json();
}

export async function analyzeComponent(
  file: File,
  priceIdr?: number | null,
  enableSearch: boolean = true
): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (priceIdr !== undefined && priceIdr !== null) {
    formData.append('price_idr', priceIdr.toString());
  }
  formData.append('enable_search', enableSearch.toString());

  const res = await fetch(resolveUrl('/api/analyze'), {
    method: 'POST',
    credentials: 'include',
    headers: getAuthHeaders(),
    body: formData,
  });

  if (!res.ok) {
    const errorDetail = await parseErrorMessage(res, 'Analysis request failed');
    throw new ApiError(res.status, errorDetail);
  }

  return res.json();
}
