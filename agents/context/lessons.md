# Lessons

## Working Norms
- Keep task scope single-purpose; avoid mixing feature work, docs-only work, and infra work in one task/PR.
- Prefer incremental TDD loops: add one test, implement minimal code, verify, then continue.
- Keep context files concise and operational; avoid long historical narrative in active planning files.

## Repository Hygiene
- Run `git status -sb` before staging and before opening a PR.
- Prefer focused commits with explicit intent and matching verification logs.
- Avoid committing generated artifacts (`__pycache__`, coverage outputs, built docs) unless explicitly required.

## API/Data Lessons
- For dictionary-like signal lookups, handle key normalization explicitly (case and string/int ambiguity).
- For file-I/O tests, mock concrete content payloads rather than raw `MagicMock` objects.
