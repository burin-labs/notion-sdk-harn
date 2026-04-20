# SESSION_PROMPT.md — notion-sdk-harn v0

You are picking up the v0 build of `notion-sdk-harn`, a typed Notion REST
API SDK in pure Harn. The source is generated from Notion's OpenAPI 3.1
spec via `harn-openapi`. This file is your self-contained bootstrap.

## Pivot context (60 seconds)

Harn is moving per-provider connectors **out** of its Rust monorepo and
into external pure-Harn libraries under `burin-labs/`. This repo is the
**outbound** surface — every typed REST endpoint Notion exposes, accessible
from Harn scripts and from `harn-notion-connector` (which handles inbound
webhooks and depends on this SDK for its outbound dispatch).

Tracking ticket: [Pure-Harn Connectors Pivot epic
#350](https://github.com/burin-labs/harn/issues/350).

## What this repo specifically delivers

A pure-Harn module exposing:

- `Client({ token, notion_version? }) -> client_handle` — factory.
- Resource modules attached to the client: `pages`, `databases`,
  `data_sources`, `blocks`, `users`, `search`, `comments`. Each exports
  one function per OpenAPI operation, named with snake_case
  (`pages.retrieve`, `pages.create`, `databases.query`, `blocks.children.list`,
  etc.).
- Pagination helpers: every list-style endpoint exposes both the raw
  cursored form (`databases.query`) and an iterator form
  (`databases.query_all`) that auto-walks `next_cursor` / `has_more`.
- Error normalization: HTTP errors from Notion are decoded into a typed
  `NotionError` shape `{ status, code, message, request_id }` and returned
  via Harn's `Result` type.
- `scripts/regen.harn` — codegen entry point that re-renders `src/lib.harn`
  from `tests/fixtures/notion.openapi.json` via `harn-openapi`.

**Out of scope for this repo:** webhook receivers, inbound payload
verification, anything `provider_id()`-shaped. That's
`harn-notion-connector`.

## What's blocked

- **[harn#345 (Package management v0)](https://github.com/burin-labs/harn/issues/345)** —
  v0 release of *this* repo is gated on package management. The user has
  explicitly stated they want to ship a really really solid package
  manager before shipping dependent libraries; file-relative imports feel
  like a hack and aren't a long-term distribution path. Develop in
  parallel using `path = "../harn-openapi"` but **do not cut a v0.1.0
  release tag until #345 lands**.
- **[harn#346 (Connector interface contract)](https://github.com/burin-labs/harn/issues/346)** —
  not directly blocking this repo (no connector interface here), but
  worth tracking because `harn-notion-connector` will consume this SDK
  and call its outbound functions from inside its `call(method, args)`
  dispatch.

## What's unblocked

- `harn-openapi` parser + codegen (sibling repo at `../harn-openapi`).
  Develop both in lockstep; don't hand-edit generated source.
- Stdlib JSON, HTTP, file I/O, regex, dicts, lists, results, errors —
  everything you need.
- Notion's OpenAPI spec is public and stable enough to pin.

## v0 milestones (build in order)

### M1 — Pin the spec & smoke-test the codegen path

- Download `https://developers.notion.com/openapi.json` to
  `tests/fixtures/notion.openapi.json`. Document the fetch command in a
  comment in `tests/`. The file is ~995KB with ~150 schemas and heavy use
  of `oneOf` / `anyOf` discriminators (e.g. block types). Don't be
  surprised by it.
- Implement `scripts/regen.harn`: imports `harn-openapi`, reads the
  fixture, calls `parse` + `codegen_module`, writes to a temp path, then
  diffs against `src/lib.harn` (initially empty) and surfaces the diff.
- Acceptance: `harn run scripts/regen.harn --apply` writes a non-empty
  `src/lib.harn` and `harn check src/lib.harn` exits 0.

### M2 — Hand-shape the Client + first resource

While the generator catches up, hand-write the `Client` factory and one
resource (`pages`) in `src/client.harn` to lock down the ergonomic shape.
The codegen will eventually produce code matching this shape.

- `Client(opts) -> client` returning a dict with:
  - `_token: string`, `_notion_version: string`, `_base_url: string`,
    `_default_headers: dict`.
  - Bound resource modules (`pages`, `databases`, etc.) — each is a dict
    of methods that close over the client.
- `pages.retrieve({ page_id, filter_properties? }) -> result<page,
  NotionError>` — fully typed.
- `pages.create({ parent, properties, children?, icon?, cover? })`.
- `pages.update({ page_id, properties?, archived?, ... })`.
- Acceptance: `tests/pages_recorded.harn` uses `http_mock` to replay a
  recorded `pages.retrieve` round trip and asserts the parsed response.

### M3 — Codegen catches up to M2

- Generator in `harn-openapi` produces output matching the M2 shape for
  `pages`. Replace `src/client.harn` content with codegen output. Verify
  the recorded test still passes.
- Extend codegen to cover `databases`, `data_sources`, `blocks`, `users`,
  `search`, `comments`. Re-run `scripts/regen.harn`.
- Acceptance: every operation in the OpenAPI spec has a corresponding
  generated function in `src/lib.harn`. Total count should be roughly
  30–40 operations.

### M4 — Pagination, errors, polish

- Pagination helper: `paginate(fn, args) -> iterator<item>` walking
  `next_cursor` / `has_more`. Wire `_all` variants of every list-style
  operation through it (`databases.query_all`, `blocks.children.list_all`,
  `users.list_all`, `search.all`, `comments.list_all`).
- Error normalization: every method maps non-2xx HTTP responses to
  `Err(NotionError { status, code, message, request_id })`. Cover the
  documented Notion error codes
  (<https://developers.notion.com/reference/status-codes>).
- Acceptance: 3–5 recorded tests under `tests/recorded/` covering happy
  path + a 404 + a 429 + a paginated query.

## Recommended workflow

1. **Use a worktree per milestone:**
   ```sh
   cd /Users/ksinder/projects/notion-sdk-harn
   git worktree add ../notion-sdk-harn-wt-m1 -b m1-codegen-bootstrap
   ```
2. **Open `../harn-openapi` alongside.** Almost every M3+ change touches
   both repos.
3. **Hand-write before generating.** M2 exists deliberately so you have a
   target ergonomic shape; otherwise the codegen lands ugly and stays ugly.
4. **Record HTTP fixtures from a sandbox workspace**, never from a
   production workspace. Strip request IDs and tokens from recordings
   before committing.

## Reference materials

- Harn quickref: `/Users/ksinder/projects/harn/docs/llm/harn-quickref.md`.
- Harn language spec: `/Users/ksinder/projects/harn/spec/HARN_SPEC.md`.
- `harn-openapi` repo (sibling): `/Users/ksinder/projects/harn-openapi/`
  and its `SESSION_PROMPT.md`.
- Notion API reference: <https://developers.notion.com/reference>.
- Notion OpenAPI: <https://developers.notion.com/openapi.json>.
- Notion versioning: <https://developers.notion.com/reference/versioning>
  (default to `2022-06-28` for v0).
- Existing Rust impl as behavior spec: the **outbound** call paths in
  `/Users/ksinder/projects/harn/crates/harn-vm/src/connectors/notion/mod.rs`
  (1514 LOC, the canonical Rust connector). The inbound paths there
  belong to `harn-notion-connector`, not here.

## Testing expectations

- Every operation should have at least a `harn check` smoke pass via the
  generated module compiling cleanly.
- Use `http_mock` for recorded request/response tests; avoid live HTTP in
  CI.
- Live integration tests behind a `NOTION_TOKEN` env guard are welcome
  but not required for v0.
- Run before committing:
  ```sh
  cd /Users/ksinder/projects/harn
  cargo run --quiet --bin harn -- check /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
  cargo run --quiet --bin harn -- lint  /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
  cargo run --quiet --bin harn -- fmt --check /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
  for t in /Users/ksinder/projects/notion-sdk-harn/tests/*.harn; do
    cargo run --quiet --bin harn -- run "$t" || exit 1
  done
  ```

## Definition of done for v0

- [ ] `tests/fixtures/notion.openapi.json` pinned and used by all tests.
- [ ] `scripts/regen.harn` regenerates `src/lib.harn` from the fixture.
- [ ] All resource modules (`pages`, `databases`, `data_sources`,
      `blocks`, `users`, `search`, `comments`) covered by codegen.
- [ ] Pagination helper + `_all` variants on every list-style endpoint.
- [ ] `NotionError` normalization for all non-2xx responses.
- [ ] 3–5 recorded tests covering happy path, 404, 429, paginated query.
- [ ] README usage example matches the actual surface.
- [ ] **No v0.1.0 tag cut until [harn#345](https://github.com/burin-labs/harn/issues/345)
      lands and `harn add github.com/burin-labs/notion-sdk-harn` works
      end-to-end through the registry.**
