#!/usr/bin/env bash
set -euo pipefail
# Rigenera SDK Python/TS da contracts/openapi.yaml
# Richiede: openapi-generator-cli, orval, datamodel-codegen
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
YAML="$ROOT/contracts/openapi.yaml"
if [[ ! -f "$YAML" ]]; then
  echo "manca $YAML — genera prima da backend: python -m viaggigoated.scripts.export_openapi > $YAML" >&2
  exit 1
fi
echo "→ Python (openapi-generator) da $YAML ..."
# npx @openapitools/openapi-generator-cli generate -i "$YAML" -g python -o "$ROOT/python/generated" --additional-properties=packageName=viaggigoated_sdk
echo "TODO: python codegen — vedi README"
echo "→ TypeScript (orval) da $YAML ..."
# npx orval --input "$YAML" --output "$ROOT/typescript/src/client.ts"
echo "TODO: ts codegen — vedi README"
echo "fatto. Versiona con semver e pin consumer a ^1.x"
