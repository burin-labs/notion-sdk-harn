# Recorded HTTP fixtures

These JSON files are recorded responses from sandbox Notion workspaces.
Identifiers (page ids, user ids, request ids) have been redacted to opaque
synthetic values. They are replayed via the stdlib `http_mock` runtime —
no live HTTP traffic in CI.

Files here are loaded by smoke tests under `tests/recorded/*.harn`.
