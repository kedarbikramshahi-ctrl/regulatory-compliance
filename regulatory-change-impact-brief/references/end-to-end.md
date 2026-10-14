# Fresh end-to-end operation, history and recovery

## Setup

From a checkout containing the implementation and captured evidence, use standard Python 3.10+ with venv/pip on Windows. See [README reproduction prerequisites](../../README.md#reproduce-from-a-checkout) and [Codex discovery setup](../../README.md#codex-skill-discovery-after-checkout). If py is unavailable, use the full path to a standard Python installation; the isolated embedded audit runtime does not prove standard venv setup. From the repository root:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

No application environment variables or secret configuration are required. Outbound HTTPS access and writable local output are required for fresh runs; a sandbox network failure is not proof of source unavailability. Tests require the checked-in captured source bundle and label synthetic feedback explicitly. Runtime dependencies are jsonschema >=4.23,<5 and rfc3339-validator >=0.1.4,<1. Other execution code uses Python's standard library. No AI API, credentials, browser cookies or authenticated company connector is used. Virtual-environment activation is unnecessary; these commands avoid PowerShell activation-script restrictions. The ignored `.runtime/python/python.exe` used during local verification is machine-specific, not a portable submission dependency.

Keep Windows checkout/output paths short; staging and history add nested components. The deeply nested quality-test output failed at a 260+ character path; use a short checkout/output rather than changing OS permissions or long-path policy.

## One command

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py
```

Optional input/output/reason flags:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py --manifest regulatory-change-impact-brief/references/sources.json --output deliverables --reason "Fresh review after input changes"
```

The manifest must contain exactly the ten disclosed names and the fixed review_date 2026-08-26. Authorized public routes are validated; credential URLs, unapproved redirect hosts, robot-solving and authentication bypass are forbidden. Normal runs always attempt ten original routes plus the existing seven public alternatives, 17 GET attempts. POLICY failures remain unresolved, including the actual API 401 when returned; an API response is never invented when no response arrives. Failed reads remain source-specific diagnostics, not substituted local evidence.

All seven stages run in order. Each new run has a unique ID, new snapshot IDs, correct predecessor hashes, actual retrieval times and Stage 01 supersession/reason. The full run recomputes from the earliest changed basis by fetching and rebuilding everything; it does not infer that unchanged business labels permit reuse of a previous success. The assigned date is never replaced with today's date.

## Expected output

```text
deliverables/
  sources/                              exact responses/extracts/diagnostics
  snapshots/01-scope.json ... 07-publication-validation.json
  impact-register.csv
  compliance-brief.md
  action-calendar.ics                    local tentative proposals only
  workflow-result.json                   current execution result
  history/<old-run-id>/                   preserved prior bundle and inspection
  workflow-attempts/<new-run-id>/          durable journal/candidate/displaced state
```

Milestone-specific validation JSON files and source-manifest.json/attempts.json remain part of the bundle. A successful command exits 0 for a technically valid review-only package even when its publication gate is blocked. `workflow_status: finished` means automation finished; `assessment_complete: false` and the separate publication/approval states preserve business limitations. Technical failures exit 1 with an explicit JSON failure record; they never use an old successful result as current proof.

## Current validation and tests

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py --validate
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Validation makes no source requests. It inspects the actual seven snapshots, schema/run/hash/evidence bindings, three files, and all exact review-request bindings against Stage 06. The runner's prior-bundle inspection also lists missing outputs, malformed snapshots, broken predecessor/source/artifact hashes and available file inventories. No credential-bearing fields are fetched to solve access problems.

Integration tests inject a test-only transport using copies of actual captured bytes; the production CLI has no offline-fixture option. Tests demonstrate fresh transport calls each run/retry, unique IDs, supersession, unchanged archive hashes, preservation of damaged bytes and pre-existing gaps, stage failures, promotion interruption, stale/active/unknown locks and unavailable-source blocked drafts. Test responses are not live evidence or simulated reviewer feedback.

## Archive and promotion

1. Take a workflow lock and inspect the current bundle, including changed/missing/damaged files. Unknown or active lock ownership is not guessed or overridden.
2. Copy all available current payload entries into history/<old-run-id>/ and verify exact file inventories/hashes before any canonical replacement. Existing history is never merged over different evidence; collisions use a preserved-<attempt-id>/ occurrence inside the old run's history.
3. If no trustworthy single old run ID can be read, use an explicitly labelled unidentified-<attempt-id>/ archive locator and record that the original identity is unknown. Do not invent a historical run or fill missing files.
4. Build a new candidate under workflow-attempts/<new-run-id>/bundle. Persist a phase journal and every source-attempt boundary. Keep the old canonical bundle until the candidate validates.
5. Retain displaced canonical files, promote the candidate, and validate the actual canonical bundle before reporting success. Archive originals and any failure evidence remain available.

Old bundles can have valid historical hashes yet fail the current renderer's semantic check after a code/format change. Record that observed compatibility error and retain the original bytes; do not mislabel it as newly damaged source evidence. Old archived validation reports describe their actual earlier executions, not the new run.

## Recovery behavior

- A failure before promotion leaves the current bundle intact, with the failed candidate/journal retained. Retry the same command; the new run gets a new ID and new retrieval attempts.
- A failed or interrupted promotion retains the observed mixed/current files in recovery-observed-*/ before restoring the verified archived prior payload. A later invocation audits unfinished journals and performs the same recovery before starting fresh retrieval.
- Damaged/missing current evidence or drafts are archived as actually found, with their gaps and issues recorded. The next successful fresh run repairs the canonical bundle from new source responses, not an undisclosed old source copy.
- Missing/damaged recovery archives, uncertain lock ownership, unsafe links/paths or filesystem failures stop with an explicit failure and retained state. Inspect the reported paths/owner before retrying; do not delete a lock blindly, modify permissions or invent lost evidence.
- Restoration uses only verified bytes actually retained. Recovery cannot solve POLICY access, legal applicability, missing supporting artifacts or approval questions.

The lock and journals are local to one output directory. Moving an in-progress bundle to another machine requires manual review of journal paths. Promotion is a journalled multi-file operation, not an operating-system-wide transaction; manual simultaneous edits, machine/disk loss or corruption of all backups may require human assistance. No automated disk cleanup is performed, so history uses additional space.

## Human boundary and remaining limits

POLICY stays unresolved until authorized content is available. All approvals remain pending, requests unsent, feedback absent and production systems untouched. Required authority limitations keep publication blocked while bounded drafts may be technically valid. Existing source dates remain proposals; no new deadlines are invented.

Explicit response intake and exact binding validation are available through [feedback-intake.md](feedback-intake.md). Receipts remain separate from the workflow; applying actual decisions and independently authenticating the facilitator channel are not automated. Source/field meaning, legal authenticity/completeness and historical applicability require human review. The facilitator must separately verify interview completeness, actual coding-session capture, source permissions, assessment acceptance and submission destination/access. No commit/push or external publication is part of this command.
