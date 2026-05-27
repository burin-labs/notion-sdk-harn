# notion-sdk-harn

Typed [Notion REST API](https://developers.notion.com/reference) SDK in pure
Harn. The source is generated from
[Notion's OpenAPI 3.1 spec](https://developers.notion.com/openapi.json) via
[harn-openapi](https://github.com/burin-labs/harn-openapi).

> **Status: pre-1.0.** The SDK tracks the current Harn 0.8 package workflow
> and the pinned Notion OpenAPI snapshot in this repo.

This SDK covers **outbound** API calls only. For inbound webhook handling,
see [harn-notion-connector](https://github.com/burin-labs/harn-notion-connector),
which imports this SDK for its outbound surface.

## Install

```sh
harn add github.com/burin-labs/notion-sdk-harn
```

That publishable path resolves this package and its generator/runtime helper
dependencies from `harn.toml`; it does not require sibling checkouts. Pin a tag
when you need reproducible installs:

```sh
harn add github.com/burin-labs/notion-sdk-harn@v0.1.0
```

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
import {
  get_users,
  new_client,
  patch_page,
  post_database_query,
  post_page,
  retrieve_a_page,
} from "notion-sdk-harn/default"
import { collect_all, decode_thrown, paginate } from "notion-sdk-harn/helpers"

let client = new_client(
  "https://api.notion.com",
  env("NOTION_TOKEN"),
  nil,
  "",
  "",
  nil,
  {"Notion-Version": "2022-06-28"},
)

// Retrieve a page
let page = retrieve_a_page(client, "abc123...")
println(page.properties.Name.title[0].plain_text)

// Query a data source with auto-pagination (lazy stream)
for row in paginate(
  fn(args) {
    return post_database_query(
      client,
      "def456...",
      {filter: {property: "Status", select: {equals: "Done"}}, ...args},
    )
  },
) {
  println(row.id)
}

// Or collect every row eagerly
let all_rows = collect_all(
  fn(args) { return post_database_query(client, "def456...", args) },
)

// Create a comment using a typed variant constructor
import { create_a_comment, create_a_comment_variant1 } from "notion-sdk-harn/default"

create_a_comment(
  client,
  create_a_comment_variant1(
    {type: "page_id", page_id: "abc123..."},
    [{type: "text", text: {content: "Hello from Harn!"}}],
  ),
)
```

## Errors

Generated operations throw on any non-2xx response. Wrap calls in `try { ... }`
and pass the `Err` value through `decode_thrown` to recover a structured error:

```harn
import { decode_thrown } from "notion-sdk-harn/helpers"

let result = try { retrieve_a_page(client, "missing") }
if is_err(result) {
  let err = decode_thrown(unwrap_err(result))
  // err == {
  //   status: 404,
  //   code: "object_not_found",
  //   message: "Could not find page with ID: ...",
  //   request_id: "req_...",      // from x-request-id when present
  //   body: "{...raw body...}",
  //   operation: "retrieve_a_page",
  // }
}
```

`decode_thrown` defaults `code` to a canonical Notion error string when the
upstream payload omits it (e.g. `unauthorized` for 401, `rate_limited` for 429),
following the Notion
[status-codes reference](https://developers.notion.com/reference/status-codes).

## Supported endpoints

The package re-exports every operation in the pinned Notion OpenAPI document
(46 operations across the resource families below). Names are snake_case
versions of the Notion `operationId`s; argument lists follow the spec's
parameter order with optional parameters defaulted to `nil`.

| Resource | Operations |
| --- | --- |
| **pages** | `retrieve_a_page`, `post_page`, `patch_page`, `move_page`, `retrieve_a_page_property`, `retrieve_page_markdown`, `update_page_markdown` (+ `update_page_markdown_*` variant constructors) |
| **databases** | `create_database`, `create_a_database`, `retrieve_database`, `update_database` |
| **data\_sources** | `retrieve_a_data_source`, `update_a_data_source`, `post_database_query`, `list_data_source_templates` |
| **blocks** | `retrieve_a_block`, `update_a_block` (+ variants), `delete_a_block`, `get_block_children`, `patch_block_children` |
| **comments** | `create_a_comment` (+ variants), `list_comments`, `retrieve_comment`, `update_a_comment`, `delete_a_comment` |
| **users** | `get_self`, `get_user`, `get_users` |
| **search** | `post_search` |
| **file uploads** | `create_file`, `list_file_uploads`, `retrieve_file_upload`, `upload_file`, `complete_file_upload` |
| **views** | `create_view`, `list_views`, `retrieve_a_view`, `update_a_view`, `delete_view`, `create_view_query`, `get_view_query_results`, `delete_view_query` |
| **emojis** | `list_custom_emojis` |
| **OAuth** | `create_a_token` (+ variants), `introspect_token`, `revoke_token` |

Every list-style endpoint that follows Notion's `next_cursor` / `has_more`
convention (databases query, comments, users, blocks children, custom emojis,
views, file uploads, view query results, data-source templates) is walkable
with the [`paginate`](src/helpers.harn) helper.

The full machine-readable inventory ships in `src/lib.harn`'s
`pagination_plans()` and `rate_limit_metadata()` exports.

## Unsupported endpoints

The following Notion surfaces are not in this package:

- **Inbound webhook delivery and verification.** Webhook subscription
  management lives in the Notion integration UI, not the public REST API.
  Webhook receivers, including payload verification, normalization, and dispatch,
  belong in [harn-notion-connector](https://github.com/burin-labs/harn-notion-connector).
- **Operations the upstream OpenAPI doesn't describe.** If Notion adds a new
  endpoint, refresh the fixture and regenerate as described below. Do not
  hand-write one-off wrappers here.
- **Streaming / long-poll endpoints.** None exist in the current Notion API.

If you hit a missing operation, refresh `tests/fixtures/notion.openapi.json`
from `https://developers.notion.com/openapi.json` and regenerate.

## API-version pin

`new_client` defaults `Notion-Version` to `2022-06-28`. You can pin a
different default through `extra_headers`:

```harn
let client = new_client(
  "https://api.notion.com",
  env("NOTION_TOKEN"),
  nil, "", "", nil,
  {"Notion-Version": "2022-06-28"},
)
```

Generated operations also accept an optional trailing `notion_version`
argument for one-off calls that need a newer dialect:

```harn
let page = retrieve_a_page(client, "abc123...", nil, "2026-03-11")
```

Notion guarantees backward compatibility within a major version per its
[versioning policy](https://developers.notion.com/reference/versioning).

The pinned upstream OpenAPI snapshot lives at
`tests/fixtures/notion.openapi.json`; bump it (and regenerate) any time
you intentionally adopt a new Notion API version.

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
The generated SDK opts into the shared Harn connector HTTP policy transport:
safe/idempotent operations use bounded retries, unsafe writes do not retry
unless the OpenAPI operation exposes an `Idempotency-Key` parameter, and
connector envelopes carry standardized retry, rate-limit, and JSON parse
errors for callers that catch thrown responses.

To refresh the upstream Notion OpenAPI fixture:

```sh
curl -fsSL https://developers.notion.com/openapi.json \
  > tests/fixtures/notion.openapi.json
harn run scripts/regen.harn -- --apply
harn package check
harn check src scripts tests
harn lint src scripts tests
harn fmt --check src scripts tests
harn run scripts/regen.harn
harn run tests/recorded/notion_sdk_smoke.harn
```

## Development

Install the pinned Harn CLI and resolve package dependencies. The matching
GitHub release binary is fastest; `cargo install` is a portable fallback:

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

CI uses the same `.harn-version` pin, downloading and checksum-verifying the
matching Linux release binary instead of relying on an ambient sibling checkout.
The `tests/recorded/` suite uses the stdlib `http_mock` runtime; CI makes no
live Notion HTTP calls. Live integration tests behind `NOTION_TOKEN` are
welcome but not required; keep them out of CI.

## Releases

Tagged releases are listed on the
[GitHub Releases page](https://github.com/burin-labs/notion-sdk-harn/releases)
and summarised in [CHANGELOG.md](./CHANGELOG.md). The package-index entry in
`burin-labs/harn-cloud` is updated by a PR on each release.

## License

Dual-licensed under MIT and Apache-2.0.

- [LICENSE-MIT](./LICENSE-MIT)
- [LICENSE-APACHE](./LICENSE-APACHE)
