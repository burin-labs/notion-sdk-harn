# Repository settings proposal

This page proposes settings changes for `burin-labs/notion-sdk-harn`. Nothing
here has been applied. Repository and organization settings are the founder's
to change, so this file is a request, not a record.

Status: **proposed, not applied** (2026-09-01).

## Proposals

### 1. Keep issues enabled, keep discussions off

This package is published to the Harn package index as `@burin/notion-sdk` and
`harn-notion-connector` depends on it, so a consumer needs somewhere to report
a broken generated operation. Keep issues on. Discussions have never been
enabled and there is no audience for them, so leave them off.

Verification before acting: none needed, this proposal changes nothing.

### 2. Restrict who can open a pull request from a fork

The source under `src/` is generated, so an outside pull request against it is
work that cannot land. Requiring organization membership to open a pull request
against `main` makes that boundary visible before someone spends the effort,
and `CONTRIBUTING.md` routes them to `harn-openapi` instead.

Verification before acting: confirm no non-member has an open pull request
here, so nothing in flight is cut off.

### 3. Point the repository homepage at the package index entry

A visitor who found this through `harn add @burin/notion-sdk` should reach the
index entry and its version history.

Verification before acting: confirm
<https://packages.harnlang.com/harn-package-index.toml> still lists
`@burin/notion-sdk`.

## Not proposed

- Archiving. The package is released and has a live consumer.
- Disabling issues. See proposal 1.
- Any branch-protection change. Those are set org-wide and are out of scope for
  a hygiene sweep.
