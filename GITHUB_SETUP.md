# GitHub publication and skill installation

## Get the complete project

```bash
git clone https://github.com/gabrielgodoioliveira123-commits/GGO.git
cd GGO
```

Alternatively, download the repository ZIP and extract its contents into a source folder named `GGO`. Release archives extract the installable skill into `god-prompt/`, matching its manifest name. Keep `SKILL.md` at its root and include `engine`, `references`, `agents`, `scripts`, `tests`, `examples`, and `.github`. A root-only web upload omits essential runtime files. Check `.github/workflows/ci.yml` and `.gitignore`, which some file pickers hide.

## Validate and publish changes

```bash
python scripts/build_release.py
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/verify_package.py
python scripts/build_release.py --check
git add .
git commit -m "Update God Prompt source and verified release package"
git push origin main
```

Use your normal authenticated GitHub workflow and the branch appropriate to your repository. Review the diff before committing. No password or token belongs in this repository or in a chat. Open the **Actions** tab after pushing to inspect automated checks. Repository content and release notes use English.

`PromptGod-Go.zip` and `god-prompt.skill` are byte-identical reproducible ZIP-format archives containing the complete `god-prompt/` source folder. `SHA256_RELEASE.txt` checks the archive bytes; the archive includes `SHA256SUMS` for source integrity. A source archive is not evidence that API generation or external connectors have been exercised.

## Install locally

Choose one scope:

```bash
python scripts/install_skill.py --user
python scripts/install_skill.py --repo /path/to/your-project
```

The first copies to `~/.agents/skills/god-prompt/`; the second to `<project>/.agents/skills/god-prompt/`. Existing targets require an explicit `--replace`. Compatible Codex hosts may also install from the GitHub URL through their skill installer. Other hosts have their own import support; the folder remains usable as explicitly supplied instruction material when automatic discovery is unavailable.

## Keep private work local

`output/`, environment files, caches, logs, and common credential files are ignored by Git. Review staged files anyway. Do not publish private prompts, Drive exports, or commercial output without the owner's authorization. Connected tools belong to the host: cloning does not authenticate GitHub, Google Drive, OneDrive, or any other service. Use an authorized connector or a permitted local text export with `ingest`.

See `README.md`, `SECURITY.md`, and `references/connectors.md` for runtime behavior and limits.
