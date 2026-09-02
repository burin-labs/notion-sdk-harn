# Contributing

## Most of this repository is generated, so do not hand-edit it

`notion-sdk-harn` is a typed Notion REST API SDK written in pure Harn. The
source under `src/` is generated from Notion's OpenAPI 3.1 description by
[harn-openapi](https://github.com/burin-labs/harn-openapi). A hand-edit to a
generated file is erased the next time the generator runs.

That makes a patch against this repository almost always the wrong place to
send a fix. Three cases cover nearly everything:

- **The generated code is wrong or missing an operation.** The bug is in the
  generator. File it at
  <https://github.com/burin-labs/harn-openapi/issues/new>.
- **Notion changed its API.** The pinned OpenAPI snapshot in this repository
  needs refreshing, which is internal maintenance work. File it here as an
  issue rather than a pull request.
- **You want a different helper surface.** `src/helpers.harn` is the small
  hand-written layer. Open an issue describing the call you want to write
  before you write code.

## This repository does not take external contributions

It is a first-party Burin Labs package published to the Harn package index as
`@burin/notion-sdk`, and `harn-notion-connector` depends on it for its outbound
surface. Its surface moves with the Notion spec and the Harn runtime, on an
internal cadence. Pull requests from outside Burin Labs are closed unread.

If you want Notion coverage that this SDK does not have, say so at
<https://github.com/burin-labs/harn/issues/new> with the label
`area/connectors`, and name the workflow you are trying to build.

## If you work at Burin Labs

Install the Harn CLI pinned by `.harn-version`, then run `harn fmt --check src
tests`, `harn check .`, `harn test tests --parallel`, and `harn package verify
.` before you open a pull request.

Regenerate rather than edit. `scripts/` owns the generation entry point, and
the OpenAPI snapshot is pinned in this repository on purpose so a Notion-side
change cannot move a release out from under a consumer.

Do not edit anything between the `<!-- BEGIN HARN SHARED AGENT CONTRACT -->`
markers in `AGENTS.md`, or `.github/workflows/ci.yml` and
`.github/dependabot.yml`. Those are projections owned by `harn-bump-fleet` and
a local edit is overwritten at the next fleet sync.

### Pull request titles

Title every pull request `[Area] Sentence case description`, for example
`[Codegen] Regenerate against the 2026-08 Notion snapshot`. Use one of `SDK`,
`Codegen`, `Docs`, `CI`, `Tests`, or `Release`. Keep the description to three
to five sentences: what changed, why, the one risk, and how you verified it.

### Labels

`.github/labels.yml` records the label vocabulary. Priority, status, and effort
come from the org taxonomy in
[burin-labs/.github](https://github.com/burin-labs/.github); `area/*` is local
to this repository. Reuse `bug`, `enhancement`, and `documentation` for type
rather than adding a `type/*` prefix.
