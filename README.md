# viaggigoated-sdk — contratti centrali + SDK Python/TS

Single source of truth per `viaggigoated`. Backend genera `contracts/openapi.yaml`, questo repo pubblica `viaggigoated-sdk` (Python, pip) e `@viaggigoated/sdk` (TS, npm) versionati con semver. Frontend, CLI e `viaggigoated-ai` pin nano versione `^1.x`, nessun path import.

## Struttura
```
contracts/openapi.yaml  # snapshot committato da backend (source of truth)
python/                 # package viaggigoated-sdk (Pydantic v2, httpx)
typescript/             # package @viaggigoated/sdk (zod, fetch, SSE helpers)
scripts/codegen.sh      # rigenera client da openapi.yaml
```

## Uso

Python:
```py
from viaggigoated_sdk import ViaggigoatedClient
sdk = ViaggigoatedClient(base_url="http://localhost:8000", token="...")
sdk.trails.search(lat=46.07, lon=11.12, radius_m=10000)
```

TypeScript:
```ts
import { createClient } from "@viaggigoated/sdk"
const sdk = createClient({ baseUrl: import.meta.env.VITE_API_BASE_URL, getToken: () => localStorage.token })
await sdk.weather.forecast({ lat: 44.5, lon: 11.3, start_date: "2026-08-24", end_date: "2026-08-26" })
```

## Generazione
```bash
./scripts/codegen.sh  # richiede openapi.yaml aggiornato
```

## Versioning
- MAJOR su campo rimosso/rename, MINOR su aggiunta opzionale, PATCH su fix. Consumer pin `^1.x`.
- CI blocca drift `openapi.yaml == backend /openapi.json`.
- Contract test `schemathesis run <url>/openapi.json` in CI.

## Link fonte
Ogni metodo SDK mantiene `url`/`gpx_url` e `providers_used/failed` come da backend, così UI/CLI/AI mostrano link alla fonte originale.
