# Configure the Notion adapter

Use Harn 0.10.200 or later and run `harn install --locked` in this checkout.
Have your host's secret manager inject these variables into the process that
starts Harn:

| Variable | Value |
| --- | --- |
| `NOTION_BEARERAUTH_TOKEN` | Notion integration or OAuth access token for REST operations |
| `NOTION_BASICAUTH_USERNAME` | OAuth client ID |
| `NOTION_BASICAUTH_PASSWORD` | OAuth client secret |

The executable publishes OAuth operations alongside REST operations, so both
security schemes must be configured before startup. SDK calls require only
the credentials used by the called operation. Credentials are keyed by the
OpenAPI names `bearerAuth` and `basicAuth`; they are not interchangeable.

The default base URL is `https://api.notion.com`. Set `NOTION_BASE_URL` when
using a test server. The generated client sends `Notion-Version: 2022-06-28`
unless the operation receives an explicit version override.

Check the complete registry without making an API request:

```sh
harn tool schema src/main.harn --pretty
```

Missing required credentials stop publication of the registry. Keep secret
values outside source files, command arguments and generation receipts.
