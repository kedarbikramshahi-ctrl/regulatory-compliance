# Stage 07 operation

Continue the existing verified captured run through local draft generation and publication validation. No source retrieval occurs in this continuation. Source bytes, snapshots 01–06, their run ID and actual retrieval timestamps remain unchanged. The assigned review date remains August 26, 2026.

Use Python 3.10+ and the existing requirements.txt environment. From the repository root:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/publish_drafts.py
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/publish_drafts.py --validate
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The workspace verification runtime `.\.runtime\python\python.exe` can replace the virtual-environment executable. `--output` chooses an existing captured bundle. Existing final drafts or snapshot 07 are never overwritten by the creation command. For the current seven-stage bundle, use this validator rather than earlier milestone-only validators.

## Draft contract

- impact-register.csv is UTF-8 with the ten required columns and extra run/date/action/limitation fields. It has one row per scoped impact and separate preserved unresolved/conflicting source issue. Empty owner/action/date fields include a reason/resolution need. Exact action/date pairs are retained separately; a shared or multiple-action proposal is not converted into a deadline for a new undated action. No formula or workbook feature is required by this CSV contract.
- compliance-brief.md includes the run/date/recipients/status, source quality, evidence-supported observations, conflicts/unresolved scope, proposed owners/actions/dates, and all human questions. It points to detached bindings and contains no self-hash.
- action-calendar.ics is a local RFC 5545 VCALENDAR, never a production-calendar write. Existing dated source proposals become STATUS:TENTATIVE all-day DATE events with stable action-linked UIDs. DTSTAMP uses the actual Stage 06 proposal-version creation timestamp; it is not a backdated claim about retrieval or completion. DESCRIPTION includes action/system/role/run/evidence/approval basis. No DTEND is necessary for one-day proposals; no fictitious end date is added. Undated actions are omitted and explained. An empty valid calendar is produced when no dated proposal is supportable.

Calendar lines use CRLF, escaped text and folding at 75 UTF-8 octets without splitting characters. The focused checks parse required calendar properties, dates, UIDs, wrappers and tentative status, as well as compare actual events to Stage 06. No application-specific calendar import was tested or performed.

## Exact request bindings

Write all three final files, compute SHA-256 from the actual bytes, and put artifact records plus state.review_request_bindings in snapshots/07-publication-validation.json. Each request binds to all three exact paths/hashes, its run, subjects, reviewer and captured source versions. Paths are relative to the directory containing sources/ and snapshots/, which is deliverables/ in this repository. Thus impact-register.csv means deliverables/impact-register.csv in the submitted tree, and similarly for the brief/calendar.

Every request remains unsent and every approval pending. The bindings do not simulate delivery, reviewer feedback or authenticated acceptance. Stage 06 remains immutable; its earlier deferred-binding marker is now resolved by detached Stage 07 records, without editing the original request.

## Validation and blockers

The validator checks all seven schemas and shared run ID, predecessor hashes, captured-source integrity, record/evidence references, artifact paths/hashes, every request binding, CSV inventory and values, brief actions/requests, and calendar agreement against Stage 06. It replays expected content against the current upstream evidence. Updating a hash after changing an action/date/approval cannot conceal disagreement with Stage 06.

Technical checks passing is distinct from the authority/publication gate. The current historical-authority blocker leaves Stage 07 and publication blocked; POLICY and supporting-evidence gaps remain unresolved. Dependent formal conclusions are withheld. Existing source proposals can support limited human scheduling discussion without activating policy or changing deadlines.

Unexpected CLI failures write uniquely named stage-7-failure-*.json files and retain partial outputs. A failed final check marks the newly created Stage 07 failed rather than leaving passing claims. The first in-session development draft was retained under deliverables/history/<captured-run-id>/stage-7-initial-development-draft/ before improving the date presentation. That is actual development history on the same capture, not a new fresh-source run. Full automatic run orchestration, archive/retry/recovery and verified feedback processing remain incomplete.

See docs/stage-7-results.md for the actual checks and unfinished assignment requirements.
