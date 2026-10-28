# Installation, validation, and recovery

The folder is one complete skill: `SKILL.md` is its entrypoint and the engine, references, examples, metadata, and scripts are its supporting resources. Keep the full extracted folder together. Python is optional when a compatible host reads the instruction files directly; Python 3.10+ is required for the CLI.

## First-use checks

1. Extract `PromptGod-Go.zip`, then open the extracted `god-prompt` folder. A source checkout named `GGO` works too.
2. Run `python --version` (or `python3 --version` on systems using that name). Install Python 3.10+ from the official Python website if it is missing.
3. Run `python scripts/verify_package.py`, `python scripts/validate_skill.py`, and `python scripts/god_prompt.py doctor`.
4. Follow the README's offline example. It uses no network, API key, or paid model.

The installer copies only the complete verified source inventory. It refuses corrupt packages and linked destination paths. `--replace` retains the old installation in a sibling backup directory and restores it if final installation fails. Keep that backup until the replacement is confirmed working.

## Common messages

| Message | Action |
| --- | --- |
| Package hash mismatch or missing inventory | Download the complete release again. For intentional development changes, rebuild the release and run all checks. |
| Output directory is not empty | Resume its existing project, or choose a new empty directory. Existing files are preserved. |
| Build seed first | Run `build` after initialization or after importing new sources. |
| Another command is using this project | Wait for that invocation to finish. Operating-system locks release when the process exits; the `.ggo.lock` file alone is not a stale lock. |
| Unrecorded page already exists | Preserve it separately and inspect the manifest before retrying. The CLI does not overwrite an unrecorded result. |
| Duplicate or too-similar page | Supply new substantive content. Changing only a page number does not make it a new page. |
| Integrity mismatch / INVALID | Restore the affected source or page from your trusted copy, then run `audit`. Do not edit hashes to disguise missing or shortened content. |
| Exported or assembled file was edited | Preserve your edits under another filename before regenerating the owned export. |
| Exports are stale | Run `export` again; add `--assemble` to refresh the combined TXT. |
| Recovery files retained | Keep the named staging folder. Restore the saved files before retrying; do not delete possible recovery data. |

## Scope of automated checks

Only existing verified substantive pages count. Empty exports create an index with zero volumes. Failures do not credit fake pages. Export staging preserves unrelated user files and rolls back its owned files on ordinary write errors. Interrupted model generation can resume from recorded completed pages; inspect any unrecorded page rather than overwriting it.

Word thresholds, hashes, ordering, normalized exact duplicates, and adjacent shingle similarity are mechanical checks. They do not prove factual quality, legal permission, original reasoning, or suitability for every task. Review content before relying on it.

Optional API expansion requires your own authorized credentials, accessible model, network, and budget. A missing credential, incomplete response, service outage, or quota limit is not evidence of completed generation. Host cloud connectors are separately installed and authorized. None of these services is required for the offline example.
