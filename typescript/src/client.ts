/* @viaggigoated/sdk — client TS tipato su openapi.yaml, generale + link fonte ovunque */

export class ApiError extends Error {
  status: number;
  body: unknown;
  code: string;
  retryable: boolean;
  userMessage: string;
  constructor(status: number, body: unknown, code = "UNKNOWN", retryable = false) {
    const rec = typeof body === "object" && body !== null ? (body as Record<string, unknown>) : null;
    const um = rec && typeof rec.user_message === "string" ? rec.user_message : typeof rec?.userMessage === "string" ? String(rec.userMessage) : String(body ?? "");
    const c = rec && typeof rec.code === "string" ? rec.code : code;
    const ret = rec && typeof rec.retryable === "boolean" ? rec.retryable : retryable;
    super(`HTTP ${status}: ${um || String(body)}`);
    this.status = status;
    this.body = body;
    this.code = c;
    this.retryable = ret;
    this.userMessage = um || this.message;
  }
}
export function createClient(opts: { baseUrl: string; getToken?: () => string | null; timeoutMs?: number }) {
  const baseUrl = opts.baseUrl.replace(/\/$/, "")
  const timeoutMs = opts.timeoutMs ?? 15000
  async function req(path: string, init: RequestInit & { params?: Record<string, string | number | boolean | null | undefined> } = {}): Promise<unknown> {
    const url = new URL(baseUrl + path)
    if (init.params) for (const [k, v] of Object.entries(init.params)) if (v != null) url.searchParams.set(k, String(v))
    const headers: Record<string, string> = { Accept: "application/json" }
    const token = opts.getToken?.()
    if (token) headers.Authorization = `Bearer ${token}`
    const ctl = new AbortController()
    const t = setTimeout(() => ctl.abort(), timeoutMs)
    try {
      const res = await fetch(url, { ...init, headers: { ...headers, ...(init.headers as Record<string, string> | undefined) }, signal: ctl.signal })
      const ct = res.headers.get("content-type") ?? ""
      if (ct.includes("gpx") || path.endsWith("/gpx")) {
        const text = await res.text()
        if (!res.ok) throw new ApiError(res.status, text)
        return text
      }
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new ApiError(res.status, data, (data as Record<string, unknown>)?.code as string | undefined)
      return data
    } finally {
      clearTimeout(t)
    }
  }
  return {
    health: () => req("/health"),
    trails: {
      search: (p: { lat: number; lon: number; radius_m?: number; limit?: number }) => req("/trails/search", { params: p as Record<string, string | number> }),
      gpx: (provider: string, id: string) => req(`/trails/${provider}/${id}/gpx`) as Promise<string>,
    },
    weather: { forecast: (p: { lat: number; lon: number; start_date: string; end_date: string }) => req("/weather/forecast", { params: p }) },
    iris: { departures: (station: string) => req("/iris/departures", { params: { station } }) },
    itinerary: { plan: (body: unknown) => req("/itinerary/plan", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }) },
    car: { estimate: (body: unknown) => req("/estimate/car", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }) },
    fuel: { stations: (p: { lat: number; lon: number; radius_km?: number; fuel?: string }) => req("/fuel/stations", { params: p as Record<string, string | number> }) },
    trips: {
      openjaw: (p: { from_home: string; area: string; window: string; nights: number; travelers?: number }) => req("/trips/openjaw", { params: p as Record<string, string | number> }),
      loop: (body: unknown) => req("/trips/loop", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
    },
    // helper SSE tipizzato
    stream: (path: string, handlers: Record<string, (data: unknown) => void>, onError?: (e: ApiError) => void) => {
      const token = opts.getToken?.()
      const url = new URL(baseUrl + path)
      if (token) url.searchParams.set("token", token)
      const es = new EventSource(url.toString())
      for (const [ev, cb] of Object.entries(handlers)) es.addEventListener(ev, (e) => cb(JSON.parse((e as MessageEvent).data)))
      es.addEventListener("error", () => onError?.(new ApiError(0, "SSE error")))
      return () => es.close()
    },
  }
}
