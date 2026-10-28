# Changelog

## v1.2.1 · 2026-10-28

- Carry the complete packaged skill workflow and specialization contracts into the generated seed and optional expansion context.
- Validate sources, pages, word counts, ordering, duplicates, and seed integrity before accepting or exporting work; report invalid and stale results accurately.
- Stage project writes, restore owned outputs after ordinary write failures, preserve unrelated or edited files, and prevent simultaneous CLI mutations with operating-system locks.
- Verify the full package inventory before installation, copy only verified files, retain the previous installation as a backup, and restore it after a failed final rename.
- Handle malformed metadata and incomplete provider responses, rotate bounded source excerpts, and support explicit model output-token budgets.
- Add a complete offline quickstart, package diagnostics, recovery guidance, regression fixtures, and CI across Windows, macOS, Linux, and Python 3.10/3.12.

Provider responses are tested with offline fixtures. Live model access, model quality, cloud connectors, and execution of the APL reference in an interpreter are not certified by these tests.

## v1.2.0 · 2026-10-28

- Publish PromptGod-Go (GGO), the public God Prompt distribution, with English documentation and a clean GitHub noreply history.
- Retain only the author's name in project attribution; omit personal contact information, organization, and external promotional site metadata.
- Add direct ZIP and Agent Skill downloads, descriptive repository topics, usage guidance, and community issue templates.
- Exclude ignored credentials, private environment files, logs, caches, and symbolic-link traversal from source release packaging.
- Preserve the tested Python CLI, APL instruction contracts, prompt strategy catalog, local source import, resumable page tracking, and TXT export from the earlier God Prompt implementation.

The distribution does not contain pre-generated 10,000-page output. Paid API calls and live cloud integrations require separate authorized configuration.
