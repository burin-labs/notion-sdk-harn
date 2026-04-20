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

Until `harn add` ships
([harn#345](https://github.com/burin-labs/harn/issues/345)):

```sh
cd /Users/ksinder/projects/harn
cargo run --quiet --bin harn -- run /Users/ksinder/projects/notion-sdk-harn/tests/smoke.harn
cargo run --quiet --bin harn -- check /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
cargo run --quiet --bin harn -- lint  /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
cargo run --quiet --bin harn -- fmt --check /Users/ksinder/projects/notion-sdk-harn/src/lib.harn
```

Live integration tests need a `NOTION_TOKEN` env var pointed at a sandbox
workspace. Recorded tests don't.

## Sibling repo

Local relative path to the codegen library:
`/Users/ksinder/projects/harn-openapi`. Develop the two together; many bugs
in this repo will trace back to a missing case in the codegen.

## Upstream conventions

For general Harn coding conventions and project layout, defer to
[`/Users/ksinder/projects/harn/CLAUDE.md`](/Users/ksinder/projects/harn/CLAUDE.md).

## Don't

- Don't hand-edit `src/lib.harn` to fix a generated bug — fix the
  generator in `../harn-openapi` and re-run `scripts/regen.harn`.
- Don't add inbound webhook handling here. That belongs in
  `harn-notion-connector`.
- Don't hand-edit `LICENSE-*` or `.gitignore`.
