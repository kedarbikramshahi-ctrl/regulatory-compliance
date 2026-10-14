# Milestone 2 operation

Continue the completed, unchanged milestone-1 capture through authority/timing and evidence reconciliation. This command makes **no network requests** and preserves the existing run ID, review date, source bytes and stages 01–02. It is a stage continuation, not a fresh full review run. Actual retrieval times remain those recorded in stage 02.

Use Python 3.10+ with requirements.txt, following the milestone-1 environment setup. From the repository root:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/reconcile_evidence.py
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/reconcile_evidence.py --validate
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_reconcile_evidence.py -v
```

The existing workspace verification runtime can substitute `.\.runtime\python\python.exe`. `--output` selects another captured bundle. Validation reparses retained bytes, checks source identities, schema, references, hashes and the actual stage states. Each validation constructs a new in-memory verification cache; it never reuses a previous validation result.

Stage 03 retains exact claim-bearing quotes with section names and start/end offsets in newline-joined visible HTML text. Raw bytes and their hashes remain the primary capture. Paragraph comparisons ignore whitespace, source change markers, isolated NEW/AMENDED display labels and spacing before commas/semicolons; raw quotes remain unchanged. It compares paragraphs 1–6 and verifies paragraph 7 against the operative replacement. Entry dates use publication dates plus the stated intervals. Article 113 exceptions and the conditional Article 111(4) provider transition remain distinct. Guidance remains advisory and the consolidation remains a documentation aid. These comparisons do not establish system applicability, legal authenticity signatures or exhaustive historical coverage.

Stage 04 reparses company tables and requires disclosed fields without guessing renamed meanings. It preserves full row values, revisions, row locators, owners, statuses, dates and notes. It links exact system IDs and the CALENDAR ALL entry; duplicate identities, orphan rows, invalid dates, unknown actor roles and missing fields remain visible. Complete evidence/closed incidents do not imply compliance. Conflicting notes remain register claims; referenced screenshots, release records, SOPs and other items have not been independently retrieved. POLICY controls remain empty with a separate unresolved access record. Calendar rows remain source proposals with unverified approvals, never activated events.

Outputs: snapshots/03-authority-and-timing.json, snapshots/04-evidence-reconciliation.json and milestone-2-validation.json. All four stages share the captured run ID. New stage snapshot IDs are unique and predecessor hashes refer to the actual preceding files. Authority parsing or comparison failures block stage 03; ordinary unresolved historical scope leaves it partial. Stage 04 remains partial. No stage 05–07, final draft or approval is generated.

Existing stages 03/04 are not overwritten. Use --validate to inspect them. CLI failures persist milestone-2-failure.json and leave actual boundary evidence available. During development, the initial paragraph-layout failure and pre-context-check boundaries were preserved under deliverables/technical-failures/. These are local development attempts on the same source capture, not newly fetched full review runs or fabricated history. Full fresh-run orchestration and assignment recovery remain a later milestone; the capture command deliberately refuses to replace later-stage bundles. Obtain authorization for any future full run and retain the complete old bundle before replacing it.

See docs/milestone-2-results.md for expected versus observed results and outstanding human review.

After stages 05–06 have been generated, use scripts/analyze_impacts.py --validate for the current six-stage bundle. The milestone-2-only validator still refuses later-stage bundles by default.
