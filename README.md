# notion-sdk-harn

Typed [Notion REST API](https://developers.notion.com/reference) SDK in pure
Harn. The source is generated from
[Notion's OpenAPI 3.1 spec](https://developers.notion.com/openapi.json) via
[harn-openapi](https://github.com/burin-labs/harn-openapi).

> **Status: pre-alpha** — actively developed in tandem with
> [burin-labs/harn](https://github.com/burin-labs/harn). See the
> [Pure-Harn Connectors Pivot epic #350](https://github.com/burin-labs/harn/issues/350).

This SDK covers **outbound** API calls only. For inbound webhook handling,
see [harn-notion-connector](https://github.com/burin-labs/harn-notion-connector),
which imports this SDK for its outbound surface.

## Install

```sh
harn add github.com/burin-labs/notion-sdk-harn@main
```

That publishable path resolves this package and its generator/runtime helper
dependencies from `harn.toml`; it does not require sibling checkouts.

For local multi-repo development, a path dependency is still useful:

```toml
[dependencies]
notion-sdk-harn = { path = "../notion-sdk-harn" }
```

Keep path dependencies local-only. Before publishing or opening package
readiness changes, switch back to the git-backed manifest dependency path and
run `harn install --locked`.

## Usage

```harn
import notion from "notion-sdk-harn/default"

let client = notion.Client({
  token: env("NOTION_TOKEN"),
  notion_version: "2022-06-28",
})

// Retrieve a page
let page = client.pages.retrieve({ page_id: "abc123..." })
println(page.properties.Title.title[0].plain_text)

// Query a database with auto-pagination
for row in client.databases.query_all({
  database_id: "def456...",
  filter: { property: "Status", select: { equals: "Done" } },
}) {
  println(row.id)
}

// Create a comment
client.comments.create({
  parent: { page_id: "abc123..." },
  rich_text: [{ text: { content: "Hello from Harn!" } }],
})
```

Errors come back as a structured `NotionError` shape:

```harn
let res = try client.pages.retrieve({ page_id: "missing" })
if res.is_err() {
  let e = res.err()
  // e == { status: 404, code: "object_not_found", message: "...", request_id: "..." }
}
```

## Regenerating from the OpenAPI spec

```sh
harn install --locked
harn run scripts/regen.harn -- --apply
harn run scripts/regen.harn
```

This reads the pinned `tests/fixtures/notion.openapi.json` and rewrites
`src/lib.harn` via [harn-openapi](https://github.com/burin-labs/harn-openapi).
The current generator ref is the `harn-openapi` revision pinned in
`harn.toml` and `harn.lock`. The second command is the drift check used by CI:
it exits non-zero when the committed SDK output is missing or stale.

To refresh the upstream Notion OpenAPI fixture:

```sh
curl -fsSL https://developers.notion.com/openapi.json \
  > tests/fixtures/notion.openapi.json
harn run scripts/regen.harn -- --apply
harn check src scripts
harn lint src scripts
harn fmt --check src scripts
harn run scripts/regen.harn
```

## Development

This repo is being built out by Claude Code sessions following a structured
prompt. **Read [SESSION_PROMPT.md](./SESSION_PROMPT.md) before making changes.**

Install the pinned Harn CLI from crates.io and resolve package dependencies:

```sh
version="$(tr -d '[:space:]' < .harn-version)"
cargo install harn-cli --version "$version" --locked
harn install --locked
harn check src scripts
harn lint src scripts
harn fmt --check src scripts
harn run scripts/regen.harn
```

CI uses the same `.harn-version` pin, installing `harn-cli` from crates.io
instead of relying on an ambient sibling checkout.

## License

Dual-licensed under MIT and Apache-2.0.

- [LICENSE-MIT](./LICENSE-MIT)
- [LICENSE-APACHE](./LICENSE-APACHE)
