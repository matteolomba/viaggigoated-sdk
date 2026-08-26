# AGENTS.md - Linee Guida Globali per il Progetto (v2)

> Aggiornato: 2026-08-12. La documentazione viva sta in `docs/` (repo
> `matteolomba/viaggigoated-docs`): `docs/index.md` è l'indice — leggilo per
> primo. Questo file dà le regole operative; i documenti fondativi dicono
> cosa costruire e com'è fatto il progetto.

## Principi di Qualità
- **Type Safety**: niente `any`/`unknown` senza narrowing esplicito
- **Strict Validation**: tutti gli input devono essere validati al confine
  (Zod nel frontend, Pydantic v2 strict nel backend)
- **Structured Logging**: JSON logs con campi obbligatori: `timestamp`, `level`, `service`, `trace_id`, `message`
- **TDD**: test first; backend coverage > 80%, frontend con vitest + Testing Library
- **Error Handling**: errori strutturati con codici; backend `AppError` con
  `code`/`user_message`/`retryable` (RNF-12), frontend `ApiError` che mostra
  `user_message` — mai stack trace all'utente

## Fonti di verità
- **`docs/`** (repo `viaggigoated-docs`) = fonte di verità attuale. Indice in
  `docs/index.md`: MODELLO, REQUISITI, FLOWS, ARCHITETTURA, CACHING,
  PROVIDERS, DESIGN_SYSTEM, COMPONENTI, TIMELINE, STILE, ROADMAP. La demo di
  design sta in `docs/design-demo/`, i prompt pronti in `docs/prompts/`.
- **`docs/openspec/`** = spec e change OpenSpec **della v1**: ragionamento
  storico (ADR, analisi), NON più fonte di verità. Una nuova change formale
  (solo per lavoro complesso) si crea in `docs/openspec/changes/` e cita i
  documenti v2.
- **`context/`** = tracking operativo, **gitignored, mai committato**:
  `TODO.md`, `PROGRESS.md`, `DECISIONS.md` (ADR), `ISSUES.md`, `QUESTIONS.md`,
  `NOTES.md`, `MIGLIORAMENTI.md`, `PULIZIA.md`.

## Struttura multi-repo
```
viaggigoated/          ← cartella di lavoro, NON un repo
├── backend/   → matteolomba/viaggigoated-backend   (git, FastAPI)
├── frontend/  → matteolomba/viaggigoated-frontend  (git, React)
├── docs/      → matteolomba/viaggigoated-docs      (git)
├── cli/       → matteolomba/viaggigoated-cli       (git, Typer) — thin su SDK
├── viaggigoated-sdk/ → matteolomba/viaggigoated-sdk (git, contracts + Python/TS SDK, public)
├── context/   ← tracking (gitignored)
└── data/har/  ← catture reverse engineering (mai committate)
viaggigoated-ai/ → matteolomba/viaggigoated-ai (git, sibling, Python optimizer) — usa viaggigoated-sdk via file:../viaggigoated/viaggigoated-sdk/python
```
Ogni parte ha il suo repo e il suo pre-commit. Un cambiamento che tocca due parti = **un commit per repo**. Operare dalla cartella del repo specifico. I contratti (OpenAPI, tipi) si condividono via **artifact versionato** `viaggigoated-sdk` (`contracts/openapi.yaml` + `python/` `viaggigoated-sdk` + `typescript/` `@viaggigoated/sdk` pin `^1.x`), mai via `file:../` manuale tra repo (solo `file:` locale per dev, publish su npm/pip per prod). `viaggigoated-ai` resta repo separato sibling per riuso optimizer, ma consuma lo stesso SDK — eventuale spostamento in `viaggigoated/ai/` è solo path, non fusione git.
## Tech Stack (implementato)
 - **Backend**: Python + **FastAPI**, **Pydantic v2 strict**, SQLAlchemy 2.0
  async + Alembic, **PostgreSQL in Docker** (`postgres:17.10-alpine`, mai
  `latest`), httpx (un solo punto di uscita con timeout/retry/breaker/rate
  limiter), structlog JSON, **uv**, **defusedxml** per XML provider (IRIS/Outdooractive)
 - **Frontend**: **React + Vite + TypeScript**, **Tailwind v4**, design system
  **Netto** (palette ambra·petrolio, 3 temi; token SOLO in
  `frontend/src/styles/tokens.css`), zod, Radix (mai dialoghi nativi del
  browser)
 - **Contracts**: **viaggigoated-sdk** — `contracts/openapi.yaml` snapshot (23 router) + `python/viaggigoated_sdk` (httpx, Pydantic) + `typescript/@viaggigoated/sdk` (zod, fetch, SSE helpers), semver `1.x`, pin `^1.x` in consumer
 - **Test**: pytest + httpx (doppi, mai rete) / vitest + Testing Library
  `start.sh` → `start.py` con `--help` e `--yes`

## OpenSpec Workflow
- Spec-first richiesto **solo per lavoro complesso/importante** (nuova
  feature, refactor multi-file, migrazione, integrazione, auth/security);
  bugfix e modifiche semplici vanno dritti all'implementazione
- Anche senza spec: registrare SEMPRE il cambiamento in `context/`
  (TODO/DECISIONS/PROGRESS)
- `docs/FLOWS.md` è la spec dei flussi: un comportamento cambiato aggiorna la
  voce di flusso nello stesso commit

## Logging Standard
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "service": "backend-search",
  "trace_id": "req-12345",
  "message": "Multimodal search completed",
  "duration_ms": 450,
  "providers_used": ["flights", "bus", "train"],
  "results_count": 12
}
```

## Commit Convention
- `feat:`: nuova funzionalità
- `fix:`: bug fix
- `docs:`: documentazione
- `refactor:`: refactoring senza cambio comportamento
- `test:`: aggiunta/modifica test
- `chore:`: manutenzione
- **Atomici**: un cambiamento logico per commit (codice + suo CHANGELOG).
  Identità obbligatoria: `Matteo Lombardi <matteo@lomba.dev>`. Mai
  `Co-authored-by`. Mai committare: secrets, build artifacts, `context/`,
  cache. Mai push/amend/force-push senza approvazione esplicita.

## Branch Strategy
- `main`: produzione stabile (default di tutti i repo)
- `develop`: integrazione feature (solo se serve)
- `feature/<nome>`: feature branch
- `hotfix/<nome>`: fix urgenti
- PR obbligatoria per i merge in main quando il team cresce; repo personali:
  commit atomici + CI verde bastano

## Code Review
- PR obbligatorio per ogni merge in develop/main
- Almeno 1 approvatore
- Checklist: test, docs, lint, security

---

# AGENTS — cosa fa l'AI con e senza viaggigoated

Tabella unica (sincronizzata in tutti i repo via `AGENTS.md`). Legenda: ✅ ok · ⚠️ limitato/lento/mock · ❌ no · · = non applicabile.

| Feature | AI solo (LetsFG+locale, no backend) | AI + viaggigoated (via `viaggigoated-sdk`) | `viaggigoated/cli` diretta | Frontend React | Note |
|---|---|---|---|---|---|
| `search` 1 rotta/1 data | ✅ `vg search` → LetsFG PFS (Bearer 90gg, `letsfg auth`) | ✅ stesso + fallback `GET /flights/aggregated` | ⚠️ `vg flights aggregated` solo Google Flights | ❌ | LetsFG ok; period search via matrix (§2) |
| Window ±N + `matrix-template` | ✅ `cheapest-date-matrix` espande ±N → N chiamate LetsFG | ✅ identico, ma può usare anche backend parallelo | ❌ no matrix (solo 1 data) | ⚠️ solo finestra fissa via `GET /flights/roundtrip?window` | Senza backend: Lento (legs×date chiamate, 60-90s/ea), cache 6h mitiga |
| `optimize` greedy/full + top-K (N gambe, cap 5000) | ✅ pura `optimizer.py`, testabile | ✅ identico | ❌ solo 2 gambe (`roundtrip`) | ⚠️ usa `trips/loop` backend (euristica >6 tappe) | Full ≤4 gambe esatto, >4 greedy |
| `run` end-to-end (matrix→fetch→optimize) | ✅ `ThreadPoolExecutor` 8 + jitter, degrada a `[]` | ✅ stesso + health check prima | ❌ | ❌ | Senza backend: 21 chiamate LetsFG per 3 gambe×7gg = 20-30min |
| `giro` breakdown completo | ✅ locale (`giro.py` + `local_hop` + `profile` + `scoring`) | ✅ stesso, ma `estimate-car`/`fuel-stations` reali se backend | ❌ | ✅ `trips/loop` + `trips/openjaw` con UI timeline | AI solo: stime parametriche, marchiate `estimated:true` |
| Cabin `M/W/C/F` + passeggeri | ✅ LetsFG `SearchParams` `m.max_stops` | ✅ idem | ✅ `flights roundtrip` `travelers` | ✅ | Wizz/Ryanair via LetsFG (include virtual interlining) |
| `profile` casa/raggio/viaggiatori | ✅ locale JSON | ✅ locale (inviato a backend come params) | · env/config | ✅ UI `Imp. profilo` | RNF-09: profilo resta client |
| `airports` entro N km | ✅ Haversine locale da `catalogo` | ✅ o `GET /airports/nearby` | ⚠️ solo `GET /airports/nearby` | ✅ | AI solo: catalogo statico 5-10 apt |
| `destinations` | ⚠️ mock locale ordinato | ✅ `GET /destinations` reale | ⚠️ `GET /destinations` | ✅ `GET /destinations` + filtri paese/prezzo | AI solo: lista mock, non prezzi reali |
| `collegamenti` apt↔città | ✅ tabella locale `BLQ/PRG/SOF` + fallback | ✅ `GET /airports/{iata}/access` o stima | ❌ | ✅ chip apt popup | RNF-46: fallback stimato |
| `gite` | ✅ `estimate_gita` (andata+ritorno, no notti) | ✅ idem | ❌ | ✅ via `trips/loop` gite |  |
| `local-hop` stima | ✅ `estimate_hop` distance×tariffa (tabella modificabile) | ✅ o `GET /local-hop` | ✅ `GET /local-hop` | ✅ | RF-19/21 |
| `fuel` / `estimate-car` | ⚠️ `vg fuel` locale (GPL 13km/L 0.85€/L) calcolabile | ✅ `POST /estimate/car` OSRM + pedaggi + `per_person` | ✅ `POST /estimate/car` | ✅ toggle auto in giro | AI solo: no OSRM/pedaggi reali |
| `fuel-stations` MIMIT | ❌ | ✅ `GET /fuel/stations` | ✅ `GET /fuel/stations` | ⚠️ via backend | Richiede backend |
| `score` preset 0-100 | ✅ locale `scoring.py` 4 preset | ✅ idem | ❌ | ✅ via backend scoring |  |
| `hotels` RF-A1..A8 | ⚠️ `search_hotels` PriceWin/Patchright (Agoda+Booking, timeout 280s, dump) o stima | ✅ o `GET /hotels`? (fallback stima) | ❌ | ⚠️ via backend | AI solo: browser headless, parziale ok |
| `things` RF-T1..T8 | ⚠️ OSM Overpass + Wikidata (2 fonti) | ✅ `GET /itinerary/places` (6 fonti: OSM/Wikidata/Atlas/OTM/FQ/Eventbrite) | ⚠️ `GET /itinerary/places` | ✅ mappa + filtri tag | AI solo: no Atlas/OTM/FQ/Eventbrite |
| `trails` + `trails-gpx` RF-TR | ❌ | ✅ `GET /trails/search` (4 provider paralleli) + `GET /trails/{p}/{id}/gpx` | ✅ idem | ✅ mappa + altimetria | Richiede backend |
| `weather` | ❌ | ✅ `GET /weather/forecast` (Open-Meteo+MetNorway, 7gg) | ✅ idem | ✅ card meteo tappa |  |
| `iris` ritardi | ❌ | ✅ `GET /iris/departures` (IRIS+db-rest) | ✅ idem | ⚠️ via backend |  |
| `itinerary` smart RF-IT | ❌ (solo `things` 2 fonti) | ✅ `POST /itinerary/plan` (pesi 0..100, wake/sleep, pace, urbex separato) | ✅ idem | ✅ wizard 3 step + DayPlan | AI solo manca pesi/orari veri |
| `flights-aggregated`/`roundtrip` | ⚠️ via LetsFG (non Google) | ✅ `GET /flights/aggregated|/roundtrip` (Google Flights via fast-flights) | ✅ idem | ✅ | Backend copre Wizz dove indicizzato |
| `anywhere`/`omio`/`bus`/`trains`/`hafas` | ❌ | ✅ `GET /anywhere|/omio|/bus|/trains|/hafas/*` | ✅ idem | ✅ via `anywhere` UI | Multi-modale |
| `health`/`diagnostics` | ❌ (no backend) | ✅ `GET /health` + `GET /diagnostics/metrics` | ✅ idem | ✅ health badge |  |
| `auth` / `saved_trips` / `prompt` | ⚠️ `save`/`reopen` locale file | ✅ `POST /auth/token` (`--save`), `POST /trips`, `GET /trips/{id}/prompt` | ✅ idem | ✅ login + salvataggio DB | AI solo: no DB, file locale |
| `itabus` | ❌ | ✅ `GET /itabus/stations` | ✅ idem | ⚠️ via backend |  |
| `trips-openjaw`/`trips-loop` | ⚠️ `giro` locale (euristica) | ✅ `GET /trips/openjaw` + `POST /trips/loop` (backend ottimizzato) | ✅ idem (via `trips`) | ✅ |  |
| `price-alert` / `watch` | ✅ cache 6h + `vg watch --threshold` | ✅ + `POST /alerts` backend | ⚠️ solo `POST /alerts` | ✅ alerts UI | AI solo: polling locale |
| LetsFG `letsfg auth` gratis | ✅ `npx letsfg auth` carta zero-amount → Bearer 90gg | ✅ idem | · | · | Unica via PFS `POST /api/search`+`GET /api/results`, no `register`/`setup-payment` |

Risposta a “tutto possibile senza viaggigoated?”: **giro N-gambe sì**, ma via LetsFG è **lento e seriale** (matrix = leggi×date chiamate), con **stime locali** per tratte/notti e **2 fonti** per things. Con backend: **parallelo, cache, 6 fonti, OSRM, MIMIT, trails/GPX, meteo, IRIS, itinerary pesato, health**. Frontend e `viaggigoated/cli` sono thin sul backend via **`viaggigoated-sdk`** (contratti centrali, semver 1.x — vedi `docs/ARCHITETTURA.md` §Contratti centrali): no optimizer N-gambe, no cache LetsFG.
