# Word-equivalent pages, dense APL, and TXT volumes

`target_pages` is a **content target** expressed in Word-equivalent pages, not a Microsoft Word layout result. Each page must meet a configurable substantive-word threshold (`words_per_page`, default 500), checked against the text actually written.

The planned TXT count is `ceil(target_pages / pages_per_txt)`. The delivered count includes only volumes containing existing verified pages. Plain TXT has no fixed visual pages; this measure estimates content size.

## Example targets

| Equivalent pages | Estimated words at 500/page | Pages/TXT | Planned TXT volumes |
| ---: | ---: | ---: | ---: |
| 10 | 5,000 | 100 | 1 |
| 100 | 50,000 | 100 | 1 |
| 1,000 | 500,000 | 100 | 10 |
| 5,000 | 2,500,000 | 100 | 50 |
| 10,000 | 5,000,000 | 100 | 100 |
| 10,100 | 5,050,000 | 100 | 101 |
| 10,000 | 5,000,000 | 50 | 200 |
| 10,000 | 5,000,000 | 1 | 10,000 |
| 10,000 | 5,000,000 | 10,000 | 1 |
| 20,000 | 10,000,000 | 100 | 200 |

## Measurement and limits

1. **Word layout is separate.** Margins, font, spacing, tables, and graphics determine physical pages. Adjust `words_per_page` to approximate your intended layout.
2. **Dense APL is not guaranteed lossless semantic compression.** Reuse definitions and reduce repetition while auditing all unique information. Do not discard useful details to reach a smaller byte count.
3. **The default artifact contains no JavaScript.** Use UTF-8 APL structure and comments. The optional Python runner is a separate execution tool; another output syntax is allowed when requested.
4. **TXT is not always smaller than DOCX.** DOCX is compressed. Disk bytes, information, words, and model tokens are different measures.
5. **Model context is bounded.** Generate in parts, revisit authorized source notes and manifests, and verify each volume progressively. Millions of words do not fit in one request merely because they are in a TXT file.
6. **Larger targets are plans.** Positive targets such as 10,100 or 20,000 are accepted without claiming that every model, budget, or runtime can complete them.
7. **Only real output counts.** `volumes/INDEX.json` records actual completed pages and exported TXT files alongside the plan.
8. **Novel substance requires review.** Each page should add useful requirements, distinctions, checks, examples, or risks. Hash, word, and adjacent-similarity checks can reject some bad output; they do not prove global originality or factual quality.

## Configuration

- `target_pages`: any positive integer; default 10,000.
- `words_per_page`: 100–3,000 substantive words; default 500.
- `pages_per_txt`: 1–100,000 pages per TXT; default 100.
- `density`: `dense` (default) or `readable`, with the same preservation requirements.
- `format`: `APL` by default, or another explicitly requested output syntax.
- `content_language`: `English` by default, independently of syntax.

`estimate` generates no content. `build` creates a plan and seed. `expand` or `add-page` adds real page text. `export` exports existing verified pages. `audit` checks hashes and word counts for recorded pages. Mock demonstrations never count as completed pages.
