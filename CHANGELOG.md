# Changelog — viaggigoated-sdk

## [Unreleased]
### Added
- Snapshot iniziale `contracts/openapi.yaml` (23 router, Pydantic strict)
- Python package `viaggigoated-sdk 1.0.0` (httpx, Pydantic v2, `ViaggigoatedClient` + `ApiError` con `code/user_message/retryable`)
- TS package `@viaggigoated/sdk 1.0.0` (zod, fetch, `createClient` + SSE helpers `streamRoundtrip`/`streamAnywhere`)
- `scripts/codegen.sh` (openapi-generator + orval)

## [1.0.0] — 2026-08-25
- Prima release versionata, pin `^1.x` per frontend/cli/ai
