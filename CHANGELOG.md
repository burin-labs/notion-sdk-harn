# Changelog

All notable changes to `notion-sdk-harn` will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/burin-labs/notion-sdk-harn/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/burin-labs/notion-sdk-harn/releases/tag/v0.1.0
