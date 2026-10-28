# GOD PROMPT | Architecture and specification

## Objective

Create a portable Agent Skill that accepts one end-user goal and optional cloud files, discovers suitable prompt strategies and expert skills, evaluates 300 distinct architectures and produces a substantial APL-script-shaped *textual instruction artifact*. The tool does not claim that APL itself can call Google Drive, GitHub, or language models unless an authorized adapter exists. `SKILL.md` is a launch manifest demanded by Agent Skills; `engine/god_prompt.apl` is the native APL core and generated output defaults to APL syntax with `⍝` comments.

## Pipeline / modules

`GOAL → AUTHORIZATION → SOURCE DISCOVERY → INGESTION → PROVENANCE → LICENSE SCAN → TOPICAL SELECTION → MULTI-EXPERT GRAPH → CONFLICT DETECTION → 300 CANDIDATE DESIGNS → EVALUATION → APL SEED → LONG-FORM EXPANSION → AUDIT → TXT EXPORT`

Sixteen core modules connect logically to 25 prompt patterns and 38 skill leads. Build exports `interaction_graph.json`, a complete directed adjacency (except reflexive edges). Communication is an information-routing *capability*; do not send every large document to every other module or imply 6,162 concurrent external operations. Transport is provided by the host or script runner. A retrieved module does not become a higher-priority instruction source.

## Skill/prompt selection

`catalog.json` is a candidate set, not a list of globally agreed "top 25" prompts. Prompt effectiveness depends on task and model, and the internet has no authoritative universal top-25 leaderboard. The selection stage must inspect at least 25 archetypes and at least 25 eligible skill references if available, with task-specific applicability, license, security, recent maintenance and user-data relevance. The supplied v1.1.0 kit records a 26-item header-level verification snapshot dated 2026-10-27; this release preserves that historical metadata without claiming fresh verification. Other entries are repository-directory candidates. For fully integrating each third-party skill, fetch and review the *complete* SKILL.md and linked references under their licenses. This package includes links and original short rule descriptors, not transcribed third-party code.

## Requirement preservation / conflict matrix

Keep `user_requirement` and `external_claim` records independent. Source identity is required. When two sources disagree, record both and report the contradiction with relevance and provenance. Higher-priority safety, law, privacy, and host tool authorization take precedence. ADD_ONLY means preserve all nonredundant requirements and semantic detail, not blindly append incorrect content. No edits that intentionally disguise evidence or create fake source citations. If a requirement is technically impossible, include it in the original request and mark its implementation limitations rather than erasing it.

## 300 variants and scored selection

The deterministic fallback constructs 300 different design records from curated archetype IDs, external skill anchors, and four weighted quality axes. Files contain rubric fields and `not_an_empirical_benchmark=true`. The best heuristic candidate is one chosen *within this experiment*, not the world's best prompt. For an actual evidence-based quality winner, run candidate prompts against the same test suite through real models and compare accuracy, hallucination rate, task completion, cost, latency, safety and user constraints. Keep evaluation inputs and outcomes.

## Scaling to volumes and 10,000 equivalent pages

The default goal is 10,000 Word-equivalent pages at 500 substantive words/page, approximately **5,000,000 words**. Users may choose any positive page count; larger future targets require realistic model, budget, rate-limit and storage checks. Page equivalence is a configurable word-based estimate, not literal Microsoft Word pagination (font, spacing, margins and images vary). Generation is incremental. No 5 million words are loaded into a single chat turn, context window, or APL variable. Pages are stored as `pages/page_000001.txt` etc. The exporter builds `volumes/VOLUME_00001.txt` etc grouping a user-selected number of pages, default 100 pages per TXT, and optionally assembles an entire UTF-8 text file for Notepad. For 10,000 requested pages, there are 100 *planned* volumes at the default grouping, but zero *produced* volumes until page content actually exists. Completion is decided by real-page count plus hash and word audits; headings, empty placeholders and repeated content do not count. Plain TXT/APL may be syntactically compact but is not guaranteed smaller than compressed DOCX or automatically semantically equivalent to a Word document.

## Source connectivity

- GitHub: native connected GitHub tool if present, or optional read-only public GitHub API via `harvest --online` with `GITHUB_TOKEN` in environment when necessary. `harvest` reviews skill frontmatter for metadata and sha, and does not execute or copy source code.
- Websites: host web-search and page-reading tools. Do not assume script Internet availability from inside a constrained sandbox.
- Clouds: authorized Google Drive/OneDrive/Dropbox connectors if provided by host, with user-granted scopes; otherwise user-supplied downloaded `.txt`/`.md`/`.json` files imported with `ingest`. A link is not an authentication grant. See `connectors.md`.
- Models: optional OpenAI Responses API used by the included Python expander, with explicit key/model; host agent can replace this by its built-in model. The bundled Python is an orchestration aid, not a secret unapproved background daemon.

## Limits and verifiable statuses

`PLAN_ONLY`: input manifest recorded. `SEED_READY`: corpus index, 300 candidate configs, winning heuristic and APL seed built. `PARTIAL`: at least one completed model-generated page exists but below target. `COMPLETE`: target substantive page count met and audit clean. A local `--mock` test never advances status. Network inaccessible / no access / costs / API quotas / insufficient copyright permission are explicit blockers. Never suppress them.

## Portability

Codex, ChatGPT agents with skill support, and compatible Agent Skills runtimes: install directory containing `SKILL.md`. Claude supports compatible skill packaging in supported contexts. Gemini or a custom assistant without skills loading: use SKILL.md + APL file as explicitly supplied instructions, or implement an adapter. Raw APL execution requires an APL interpreter (e.g., Dyalog); API calls must still be managed by a host or Python bridge.
