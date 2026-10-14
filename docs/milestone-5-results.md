# Milestone 5 results

Implemented `regulatory-change-impact-brief/scripts/run_review.py`: one fresh end-to-end command with all seven boundaries, three final draft files, prior-run preservation, current-output inspection, journalled promotion/recovery and explicit technical failure reporting.

## Actual live execution

```powershell
.\.runtime\python\python.exe regulatory-change-impact-brief/scripts/run_review.py --reason "Milestone 5: first fresh end-to-end run; retain prior Stage 07 bundle"
```

New run: **live-1ce68e8edd6e4c7ca56f039f06cdae60**. Supersedes: **live-070d798484d1497495fa28fac99dcb2f**. Assigned review date remains **August 26, 2026**. Actual new retrieval timestamps are October 12, 2026 UTC; they were not backdated to the review date.

The command made **17 fresh GET attempts**, covering all ten disclosed original routes and the seven existing public alternatives. The three drafts and all seven snapshots were generated automatically. `deliverables/workflow-result.json` reports that automation finished, all seven run IDs agree, schemas/predecessors/evidence references/hash bindings validate, final files agree with Stage 06, and the local calendar validates.

POLICY remains unavailable: original route **403** at `2026-10-12T04:03:42.596649+00:00`; official unauthenticated API **401** at `2026-10-12T04:03:42.849816+00:00`. Original EUR-Lex failures and successful Cellar alternatives remain visible in snapshot 02. No credentials, browser cookies or fictional demo evidence were used in the live execution.

`workflow_status: finished` means technical automation finished. Publication is **blocked**, `assessment_complete: false`, approvals pending, review requests unsent and feedback absent. No dependent formal legal conclusion is released.

## History and recovery

- The complete previous available bundle is preserved under `deliverables/history/live-070d798484d1497495fa28fac99dcb2f/`, alongside its existing development history. Original sources, seven snapshots, three drafts and prior validation records remain intact. Archive copies are verified against the original inspection inventory before canonical replacement.
- A candidate is built separately under `workflow-attempts/<new-run-id>/bundle`. The old canonical bundle remains until the new candidate passes all checks. The actual canonical files are validated after promotion; cached results cannot establish current success.
- Missing/malformed snapshots, damaged/missing source evidence or drafts, broken hashes and incompatible current render content are reported. Their available bytes and pre-existing gaps are archived as found; missing history is not manufactured.
- Stage failures preserve the current bundle and failed candidate. Interrupted promotion preserves observed mixed/new state and restores the verified archived prior payload. The next attempt uses a new run ID and fresh source attempts.
- Active locks are respected, safely identified stale locks retained, and unknown lock ownership left untouched for human inspection. Unsafe linked/escaping paths or an archive that changes during copying stop replacement.
- Every attempt has a durable phase/status journal and failure owner/resolution need. Technical CLI failures exit nonzero, with a retained failure record where writable; the console still reports failure if a filesystem error prevents recording it.

The initial check of the old Stage 07 brief failed against the updated formatter. The prior artifact's own hashes remain correct; this is recorded as an observed **format/semantic compatibility mismatch**, not newly corrupted source evidence. The initial check failure is retained under workflow-attempts. The fresh run regenerated compatible drafts rather than silently trusting the old report.

## Verification results

| Check | Result |
|---|---|
| New integration tests | 6 passed. Fresh calls/IDs, full seven-stage execution, archive hashes/supersession, missing drafts/snapshots, damaged evidence/calendar, stage failure/retry, interrupted promotion restoration, stale/active locks. |
| Complete regression invocation | **42 passed**, including the 36 prior tests and six new integration tests. |
| Additional final safety checks | **3 passed**: unknown lock preservation, malformed-snapshot fresh blocked recovery, and changed archive basis stopping replacement. |
| Distinct tests across final checks | **45 passed**. The 42-test suite and three targeted tests are separate recorded invocations; no combined 45-test invocation is claimed. |
| Final actual-bundle validation | All seven schemas/run IDs/predecessors/evidence references, final file hashes, review-request bindings, Stage 06 agreement and calendar checks passed. |
| Current damage inspection | `valid: true`, no issues and no missing required files. |
| Skill structure | Local skill-creator validator passed: `Skill is valid!`. |
| Protected original files | Original interview export and snapshot.schema.json SHA-256 values unchanged. |
| Prior evidence preservation | 34 previously protected original/source/stage files unchanged in their original or archived locations. Archived final draft hashes also match prior snapshot 07. |

Raw observed logs/results are `milestone-5-integration-tests.txt`, `milestone-5-regression-tests.txt`, `milestone-5-safety-tests.txt` and their corresponding result JSON files. Preservation checks are in `milestone-5-history-preservation-check.json` and `milestone-5-final-preservation-check.json`.

The integration transports are explicitly test-only fixtures using captured bytes; unavailable-source cases are synthetic test responses in temporary directories. They never replace required live evidence or simulate reviewer replies. The production CLI always uses fresh read-only retrieval.

**Final test failures: none.** Expected failure injections and the initial old-format mismatch remain recorded; they are not hidden or counted as successful assessment outcomes. Failed original source routes remain failed even when a legitimate alternate succeeds.

## Setup and daily use

Normal setup requires Python 3.10+, jsonschema >=4.23,<5 and rfc3339-validator >=0.1.4,<1. Create a virtual environment, install requirements.txt and run:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py
```

To inspect the actual current package without retrieving sources:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py --validate
```

See `regulatory-change-impact-brief/references/end-to-end.md` for setup, optional input/output/reason arguments, outputs, history, locks, failure handling and test commands. The verification-only `.runtime/python/python.exe` is machine-specific and is not the portable submission runtime.

## Still requiring human work or verification

1. Authorized POLICY content/version, supporting artifacts and resolution of actor/function facts, exception decisions, transition eligibility and historical authority completeness. Recovery does not create missing facts or approvals.
2. Actual Legal/Operations decisions. All proposed dates remain unapproved; all requests unsent. Verified-channel feedback ingestion/binding before applying real responses remains unimplemented because no actual feedback has been supplied.
3. Facilitator verification of original interview completeness, identity, actual coding-session capture, source permissions, assessment acceptance and submission repository/access. This report is not a replacement for actual session capture.
4. Operational limitations: journalled multi-file promotion is not a system-wide atomic transaction. Machine/disk loss, corruption of all backups, manual concurrent edits or relocated in-progress journals may require human assistance. Actual power-loss behavior and calendar-application import were not tested. History is retained without automated deletion.

The core one-command fresh-run/history/recovery workflow is implemented and tested. The formal assignment is not fully verified or approved. No authentication bypass, company edits, legal conclusions, messages, production-calendar writes, commit or push occurred.
