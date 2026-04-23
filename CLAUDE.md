# CLAUDE.md — notion-sdk-harn

**Read [SESSION_PROMPT.md](./SESSION_PROMPT.md) first.** It contains the
pivot context, dependency on `harn-openapi`, what's blocked on package
management, and the v0 milestones.

## Quick repo conventions

- File extension: `.harn`. Use `snake_case` for filenames.
- Repo directories use `kebab-case`.
- Entry point: `src/lib.harn` (codegen output — usually edit the generator,
  not the generated file).
- Codegen entry: `scripts/regen.harn`.
- Tests live under `tests/`. Recorded HTTP fixtures live under
  `tests/fixtures/recorded/` (use `http_mock` to replay).
- Pinned upstream OpenAPI snapshot: `tests/fixtures/notion.openapi.json`.

## How to test

Install the pinned Harn CLI from crates.io and run the local gate:

```sh
cargo install harn-cli --version "$(cat .harn-version)" --locked
harn install
harn check src scripts
harn lint src scripts
harn fmt --check src scripts
harn run scripts/regen.harn
```

Live integration tests need a `NOTION_TOKEN` env var pointed at a sandbox
workspace. Recorded tests don't.

## Sibling repo

The codegen library is a git dependency on `harn-openapi`. For local
multi-repo development, temporarily switch that dependency to a path checkout
and switch it back before publishing a package PR.

## Upstream conventions

For general Harn coding conventions and project layout, defer to
[`/Users/ksinder/projects/harn/CLAUDE.md`](/Users/ksinder/projects/harn/CLAUDE.md).

## Don't

- Don't hand-edit `src/lib.harn` to fix a generated bug — fix the
  generator in `../harn-openapi` and re-run `scripts/regen.harn`.
- Don't add inbound webhook handling here. That belongs in
  `harn-notion-connector`.
- Don't hand-edit `LICENSE-*` or `.gitignore`.
