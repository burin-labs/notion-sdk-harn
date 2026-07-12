# Changelog

All notable changes to `notion-sdk-harn` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-11

### Changed

- Migrated the package and generated SDK to Harn 0.10, with the repository and
  CI pinned to Harn 0.10.10.
- Regenerated the Notion API surface with the pinned `harn-openapi` revision.

### Security

- **F7 (LOW, 2026-05-23 sweep) — redacted error envelopes.** Generated SDK
  operations now `throw redact_response(resp)` instead of the raw response
  envelope, stripping the request `Authorization` header (and other
  secret-bearing headers like `Cookie` / `X-API-Key` / `Notion-Token`) and
  truncating the response body to 1024 characters before the value crosses a
  thrown boundary. Existing `decode_thrown` consumers keep working — the
  redacted envelope preserves `status`, `ok`, `request_id`, and the parsed
  fields they look at.
- **Known limitation (F13 — deferred).** Hand-coded `retry: {max_attempts: N}`
  is still embedded per generated operation; threading an optional
  caller-supplied retry policy through `client` is tracked separately and not
  in this PR's scope (it touches every op signature and is best handled in the
  upstream `harn-openapi` codegen template).

## [0.1.0] - 2026-05-22

Initial tagged release of the pure-Harn Notion REST SDK. Cuts a stable
`v0.1.0` git tag so consumers (notably `harn-notion-connector`) can pin to
a reproducible version instead of tracking `branch = "main"`.

### Added

- Typed wrappers around the full Notion REST surface generated from the
  pinned Notion OpenAPI 3.1 snapshot via `harn-openapi`
  (`src/lib.harn`, `scripts/regen.harn`).
- `paginate(...)` helper, structured `NotionError`, and a recorded smoke
  suite covering pagination, page CRUD, database queries, and the latest
  API surface (`tests/recorded/notion_sdk_smoke.harn`).
- `helpers` export with shared transport plumbing reused by the connector
  contract.
- Provider/runtime pinning: `harn = ">=0.8,<0.9"`,
  `harn-openapi = { rev = "v0.1.1-rc.1" }`.

### Notes

- `harn-openapi` is pinned at `v0.1.1-rc.1` for reproducible codegen
  refreshes; bumping it requires a CHANGELOG entry here.
- This SDK covers outbound Notion API calls only. Inbound webhook
  handling lives in
  [`harn-notion-connector`](https://github.com/burin-labs/harn-notion-connector).

[Unreleased]: https://github.com/burin-labs/notion-sdk-harn/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/burin-labs/notion-sdk-harn/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/burin-labs/notion-sdk-harn/releases/tag/v0.1.0
