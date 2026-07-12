# AGENTS.md

This repo is the pure-Harn outbound Notion REST SDK. When docs disagree, prefer
`README.md`, `harn.toml`, and `.github/workflows/ci.yml`.

## Repo facts

- `src/lib.harn` is generated from `tests/fixtures/notion.openapi.json` through
  `harn-openapi`.
- Fix generated behavior in `harn-openapi` or the pinned OpenAPI fixture, then
  run `scripts/regen.harn`. Do not hand-edit `src/lib.harn`.
- Hand-maintained code lives in `src/helpers.harn`, `scripts/regen.harn`, and
  `tests/`.
- Inbound webhook handling belongs in `harn-notion-connector`, not this SDK.

## Naming and layout

- Harn filenames use `snake_case` and the `.harn` extension.
- Repo directories use `kebab-case`.
- Recorded HTTP fixtures live under `tests/fixtures/recorded/` and replay with
  `http_mock`.
- The pinned upstream Notion OpenAPI snapshot is
  `tests/fixtures/notion.openapi.json`.

## Local gate

Install the pinned Harn CLI, then run the same checks CI runs. Prefer the
matching GitHub release binary for speed; `cargo install` is a portable
fallback:

```sh
version="$(tr -d '[:space:]' < .harn-version)"
cargo install harn-cli --version "$version" --locked
harn install --locked
harn package check
harn check src scripts tests
harn lint src scripts tests
harn fmt --check src scripts tests
harn run scripts/regen.harn
harn run tests/recorded/notion_sdk_smoke.harn
```

Recorded tests do not make live HTTP calls. Live integration work needs a
`NOTION_TOKEN` for a sandbox workspace and should stay out of CI.

## Multi-repo work

`harn-openapi` is pinned as a git dependency in `harn.toml` and `harn.lock`.
For local generator work, you may temporarily switch it to a sibling path
checkout such as `../harn-openapi`; restore the git pin before committing or
opening a package PR.

For general Harn conventions, use the canonical
[Harn contributor guidance](https://github.com/burin-labs/harn/blob/main/AGENTS.md).

## Avoid

- Committing live Notion tokens, request IDs, workspace data, or unredacted
  fixtures.
- Editing `LICENSE-*` or `.gitignore` unless the task explicitly requires it.
