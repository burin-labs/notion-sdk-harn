# Run a Notion command

[Configure the adapter](configure-adapter.md) in this checkout first.
Inspect the available resource groups and a command's arguments:

```sh
harn tool run src/main.harn --help
harn tool run src/main.harn pages retrieve_a_page --help
```

Retrieve a page your integration can access:

```sh
harn tool run src/main.harn pages retrieve_a_page \
  --page-id 11111111-1111-1111-1111-111111111111 --json
```

Replace the example page ID with your page's ID. The CLI invokes the generated
SDK through its operation registry. Invalid input fails before an HTTP request.
