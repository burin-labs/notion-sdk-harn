# Pinned OpenAPI fixtures

This directory holds the snapshot of Notion's OpenAPI 3.1 spec that
`scripts/regen.harn` feeds into `harn-openapi` to produce `src/lib.harn`.
The fixture is pinned. Refresh it only when adopting a new upstream Notion API
shape, then regenerate the SDK and run the local gate from `AGENTS.md`.

## Refresh command

```sh
curl -fsSL https://developers.notion.com/openapi.json \
  > tests/fixtures/notion.openapi.json
```
