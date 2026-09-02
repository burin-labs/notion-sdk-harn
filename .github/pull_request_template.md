<!--
Title this pull request `[Area] Sentence case description`.
Areas: SDK, Codegen, Docs, CI, Tests, Release.
Example: [Codegen] Regenerate against the 2026-08 Notion snapshot
-->

## Description

<!--
Three to five sentences in plain language: what changed, why, the one risk,
and how you verified it. Say whether the change is generated or hand-written,
because a hand-edit to a generated file is erased at the next regeneration.

Worked example:

  The pinned Notion OpenAPI snapshot moved to the 2026-08 revision, which adds
  the data-source query operations and renames two response fields. This
  regenerates `src/default.harn` against it and updates the helper re-exports.
  The risk is that a consumer pinned to the old field names breaks on upgrade,
  so this ships as a minor version with the renames listed in CHANGELOG.md.
  Verified with the package gate and by resolving the new package into a clean
  consumer checkout.
-->

## Test plan

<!--
What you actually ran and what happened. Name the check that would have failed
if this change were wrong, and say what remains unverified.
-->
