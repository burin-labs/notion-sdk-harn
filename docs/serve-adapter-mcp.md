# Serve Notion over MCP

[Configure the adapter](configure-adapter.md) in this checkout first.
Configure your MCP client to start:

```sh
harn serve mcp /absolute/path/to/notion-sdk-harn/src/main.harn
```

Replace the path with your checkout path and pass the credential variables
through the client's secret injection settings. The process uses MCP stdio,
so reserve its standard input and output for the client.

The server publishes the same 46 operation identities as the CLI and SDK.
Use `tools/list` to discover them, then `tools/call` to invoke a named operation
such as `retrieve_a_page` with a `page_id` argument. Both surfaces use the same
generated input schemas, credential checks and HTTP policy.
