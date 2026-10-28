# PromptGod-Go (GGO)

**God Prompt: source-grounded prompt engineering for Agent Skills and Python.**

**Author:** Gabriel Godoi de Oliveira

**License:** MIT for the original package files; external sources retain their own licenses.

God Prompt is an installable Agent Skill and a portable Python command-line tool for planning, composing, expanding, and auditing specialized prompts. It includes 16 instruction modules, 25 original prompt strategies, 38 public skill references, a deterministic planner for 300 candidate architectures, source tracking, and resumable TXT exports. English is the default natural language; APL-formatted UTF-8 `.txt` is the default output syntax.

The Python tool requires **Python 3.10+** and only the standard library. Planning, local source import, seed creation, host-written page import, export, and audit work offline. Web research, cloud access, and model generation require tools, permissions, or credentials actually available in the host environment. Installing the skill does not connect accounts or create a background generator.


[![Checks](https://github.com/gabrielgodoioliveira123-commits/GGO/actions/workflows/ci.yml/badge.svg)](https://github.com/gabrielgodoioliveira123-commits/GGO/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/downloads/)

## Download

- **[Download the latest ZIP](https://github.com/gabrielgodoioliveira123-commits/GGO/releases/latest/download/PromptGod-Go.zip)** — extract with Windows, macOS, or Linux ZIP tools.
- **[Download the Agent Skill](https://github.com/gabrielgodoioliveira123-commits/GGO/releases/latest/download/god-prompt.skill)** — for compatible skill importers.
- **[Release notes and SHA-256 checksums](https://github.com/gabrielgodoioliveira123-commits/GGO/releases/latest)** — verify your download.

No GitHub account, API key, or payment is required to download the project or run its offline commands. Optional model API expansion uses your own provider account and may incur charges.

## What can I use it for?

- Turn a concrete task into a structured, source-grounded master prompt.
- Compare 300 deterministic candidate designs and inspect the selected structure.
- Preserve authorized text sources and user requirements with traceable provenance.
- Import substantive pages, resume a longer project, and export verified TXT volumes.
- Load the same instructions as the `god-prompt` skill in a compatible host.

The planner creates designs and instruction artifacts; it is not a standalone AI model, and its 16 declarative modules do not imply live cloud connections.

## Quick start

Download or clone the **complete repository**, including its subdirectories. The repository is named `GGO`; the installable skill keeps the compatible name `god-prompt`. The installer and release archives place it in that folder automatically.

```bash
git clone https://github.com/gabrielgodoioliveira123-commits/GGO.git
cd GGO
python scripts/god_prompt.py estimate --pages 10000 --words-per-page 500 --pages-per-txt 100
python scripts/god_prompt.py doctor
python scripts/god_prompt.py init --request examples/request_quickstart.json --out output/my-project
python scripts/god_prompt.py ingest --project output/my-project examples/EXAMPLE_NOTE.txt
python scripts/god_prompt.py build --project output/my-project
python scripts/god_prompt.py add-page --project output/my-project --file examples/page_001.txt
python scripts/god_prompt.py export --project output/my-project --assemble
python scripts/god_prompt.py audit --project output/my-project
```

Use `py` on Windows or `python3` on macOS/Linux if that is your Python command. This offline example imports a real bundled sample page; it does not call a model or claim that the sample was generated for a new task. Its one-page target reaches `COMPLETE` after a clean audit. `build` alone creates the full packaged workflow and contract seed, 300 ranked candidate records, a logical graph, and a separate source corpus, with status `SEED_READY` and zero additional substantive pages. Choose a new empty output directory for each project; existing files are preserved.

## Install as a skill

```bash
python scripts/install_skill.py --user
python scripts/install_skill.py --repo /path/to/your-project
```

Choose one installation scope. The user installation goes to `~/.agents/skills/god-prompt/`; the repository installation goes to `<project>/.agents/skills/god-prompt/`. The installer verifies the complete source inventory before writing. `--replace` preserves the previous installation in a sibling backup and rolls back an ordinary final-copy failure. Compatible hosts can also load the folder directly. Hosts without Agent Skills support can use `SKILL.md` and the APL files as explicitly supplied instructions. Application support varies.

Both [PromptGod-Go.zip](PromptGod-Go.zip) and [god-prompt.skill](god-prompt.skill) contain the same complete `god-prompt/` source folder in ZIP format. Extract it with a ZIP reader if the host does not import `.skill` files. Use `SHA256_RELEASE.txt` to check the archive and `SHA256SUMS` to check extracted source files. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for installation and publication details.

## Configure your request

```json
{
  "goal": "Create a God Prompt for designing and auditing my application",
  "format": "APL",
  "content_language": "English",
  "target_pages": 10000,
  "words_per_page": 500,
  "pages_per_txt": 100,
  "density": "dense",
  "cloud_urls": [],
  "github_repos": [],
  "constraints": ["Preserve every substantive user requirement"]
}
```

`format` selects the prompt's syntax; `content_language` selects its natural language. Generated prompts remain UTF-8 TXT files regardless of syntax. Request JSON and the Python runner configure execution; they are not embedded JavaScript in the generated prompt. User constraints are carried into the seed and expansion request. Imported source documents are preserved separately to avoid silently injecting external code into APL output.

The default target is **10,000 Word-equivalent pages**, at **500 substantive words per page**, grouped into **100 pages per TXT**. That means approximately **5 million words** and **100 planned TXT volumes**, available only after the content has actually been written and checked.

| Equivalent page target | Estimated words at 500/page | Planned TXT volumes at 100 pages/TXT |
| ---: | ---: | ---: |
| 10 | 5,000 | 1 |
| 100 | 50,000 | 1 |
| 1,000 | 500,000 | 10 |
| 5,000 | 2,500,000 | 50 |
| 10,000 | 5,000,000 | 100 |
| 10,100 | 5,050,000 | 101 |

Any positive page target is accepted for planning, including larger future targets. Actual feasibility depends on context, tokens, rate limits, processing, storage, and budget. One TXT per page, groups of 25, 50, 200, or a single combined TXT are also possible. Word equivalence is a configurable word-count estimate, not Microsoft Word visual pagination. Plain TXT can be larger than compressed DOCX. Compact APL syntax does not itself guarantee preserved meaning or a larger model context. See [references/page-equivalence.md](references/page-equivalence.md).

## Import sources and build

```bash
python scripts/god_prompt.py ingest --project output/my-project /path/to/authorized-texts
python scripts/god_prompt.py harvest --project output/my-project --online --max-files 30
python scripts/god_prompt.py build --project output/my-project
```

Local import accepts supported UTF-8 text formats up to 8 MB per file. Convert PDF, DOCX, and media through an appropriate authorized reader first. `harvest --online` checks public GitHub skill headers and metadata; it does not install or execute third-party skills. The Python runner does not automatically access private Google Drive or OneDrive accounts. Use an available authorized host connector, then import a permitted local export. Cloud URLs in a request remain unfetched links until a real connector retrieves them.

## Add substantive pages and export

Import a page written by an authorized host agent or by you, without a model API call:

```bash
python scripts/god_prompt.py add-page --project output/my-project --file my_apl_page.txt
python scripts/god_prompt.py export --project output/my-project --assemble
python scripts/god_prompt.py audit --project output/my-project
```

The page must meet the configured substantive-word threshold. The tool checks source/page hashes, page order, word counts, exact normalized duplicates across completed pages, and similarity to the preceding page. Automated checks do not replace factual and editorial review. `export` writes only existing verified pages and records requested versus delivered counts in `volumes/INDEX.json`. `--assemble` also writes one combined TXT; consider the practical size before choosing this for a very large work. Failed source-integrity checks preserve previously exported volumes.

Optional API expansion may incur charges. Supply your own authorized `OPENAI_API_KEY` through the environment and select a model actually enabled for your API account:

```bash
python scripts/god_prompt.py expand --project output/my-project --provider openai --model YOUR_MODEL --pages 3
```

`--pages` limits accepted pages in that invocation, with at most three content-validation attempts per page. Network or provider failures stop the command. An explicit `--max-output-tokens` cap can override the default per-response token budget; actual limits and charges depend on your account and model. This uses the OpenAI Responses API; it is not required for offline commands or `add-page`. No API credentials are included. `--mock` demonstrates control flow and credits zero pages; it is not a completed generation.

Change a future target or volume grouping and resume:

```bash
python scripts/god_prompt.py set-target --project output/my-project --pages 20000 --pages-per-txt 50
python scripts/god_prompt.py export --project output/my-project --pages-per-txt 50
```

## Repository contents

```text
SKILL.md                      Agent Skills entrypoint
agents/openai.yaml            Skill interface metadata
engine/                       APL core and specialization contracts
references/                   Architecture, connectors, audit rules, catalog
scripts/god_prompt.py         Portable command-line runner
scripts/install_skill.py      Optional local skill installer
scripts/validate_skill.py     Structure and syntax checks
scripts/verify_package.py     Source checksum verification
scripts/build_release.py      Reproducible English .skill packaging
scripts/make_catalog.py       Catalog generator
scripts/build_apl_instructions.py  Specialization contract generator
examples/                     Requests and a seed example
tests/                        Offline behavior tests
.github/workflows/ci.yml      Automated validation
```

## Validation and rebuilding

```bash
python -m unittest discover -s tests -v
python scripts/validate_skill.py
python scripts/verify_package.py
python scripts/build_release.py --check
```

After intentional source changes, run `python scripts/build_release.py`, repeat validation, and commit the updated manifest, checksums, and archive together. CI covers Linux with Python 3.10 and 3.12, Windows with Python 3.12, and macOS with Python 3.12. Tests include real offline CLI subprocesses and operating-system locks, rollback failure fixtures, installer backups, malformed packages, and simulated provider responses. They make no paid model calls. Source files use LF line endings to keep release hashes portable across operating systems.

## Research, attribution, and limits

The 25 strategies are original formulations. The 38 catalog entries are external references; the supplied v1.1.0 kit records 26 skill headers checked on October 27, 2026. This is historical metadata, not a claim that every link was checked again in this release. Review current complete sources and their licenses before reuse. No third-party implementation is bundled through the catalog.

The 300 variants are deterministic heuristic designs, not 300 independent model experiments or a universal best-prompt benchmark. Sixteen declarative modules describe behavior; they do not prove a live connection exists. Prompt quality depends on the model, task, sources, and review. The skill asks no more than three initial questions, skips already answered questions, preserves substantive requirements, and distinguishes `PLAN_ONLY`, `SEED_READY`, `PARTIAL`, audited `COMPLETE`, and `INVALID` states.

Credits stay in repository metadata rather than being added as advertising to every generated prompt. Do not publish private imported documents, personal output folders, or credentials. See [SECURITY.md](SECURITY.md), [CONTRIBUTING.md](CONTRIBUTING.md), [references/quality.md](references/quality.md), and [troubleshooting](references/troubleshooting.md).

## Community

Questions, reproducible bug reports, and concrete feature proposals are welcome in [GitHub Issues](https://github.com/gabrielgodoioliveira123-commits/GGO/issues). Read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request and [SECURITY.md](SECURITY.md) before reporting a vulnerability. Be respectful, keep discussions relevant, and share only information you have permission to publish.

If this project is useful to you, a star helps other developers discover it. Stars, downloads, search rankings, and model quality are not guaranteed by this project.

## Publication privacy

Public distribution files contain the author's name for attribution. Personal contact details, private documents, local machine paths, account credentials, logs, and generated customer output do not belong in the release. GGO starts with a clean Git history and uses a GitHub `noreply` commit identity. GitHub still displays the public repository owner's account identity as part of hosting the project.
