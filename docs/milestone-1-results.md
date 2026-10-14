# Milestone 1 results

Run: `live-070d798484d1497495fa28fac99dcb2f`. Assigned review date: **August 26, 2026**. Actual capture times are October 11, 2026 UTC; these are not historical retrieval timestamps.

## Completed

- Canonical root `regulatory-change-impact-brief/` package with SKILL.md, source manifest, Python capture helper and operation guide. Repository discovery junction points to that package. The installed Codex app-server scanner returned it enabled, repository scope, no errors, using an isolated configuration. Existing IDE sessions may need reloading to refresh their Skill list; automatic selection was not tested.
- Ten exact interview-disclosed original routes plus seven authorized public alternatives: 17 fresh read-only GET attempts per run. No credential or cookie use, authentication bypass, company writes, or fictional evidence fallback.
- Response bytes, diagnostic bodies, extracts, original/alternate URLs, redirects, hashes, actual start/response/completion times, identity and observed versions retained. See deliverables/attempts.json and snapshot 02.
- Only snapshots 01-scope.json and 02-source-capture.json generated. Both validate against the unchanged schema, with predecessor and evidence hash checks. Scope keeps all SYSTEMS registry systems in collection scope; individual business normalization is deferred.

## Verification

Nine focused unittest tests passed after the parser correction. They cover fresh attempts, repeat-run preservation, fixed date, schema validity, evidence/predecessor tampering, table columns, identity/landing-page rejection, network failures, and unsafe locators. Fixture tests use synthetic responses only in temporary test folders. The live output is separately retrieved evidence.

Skill creator structure validation passed. Final --validate passed for both live snapshots and captured hashes. SHA-256 comparison confirms snapshot.schema.json and interviews/project-b-regulatory-compliance-20261011-2051.md unchanged.

## Live attempts

| Source / route | HTTP | Result | Actual response time (UTC) |
|---|---:|---|---|
| POLICY / original | 403 | unavailable | 2026-10-11T23:26:23.954847+00:00 |
| POLICY / policy-api | 401 | unavailable | 2026-10-11T23:26:24.178585+00:00 |
| SYSTEMS / original | 200 | retrieved | 2026-10-11T23:26:24.935165+00:00 |
| EVIDENCE / original | 200 | retrieved | 2026-10-11T23:26:25.827271+00:00 |
| CALENDAR / original | 200 | retrieved | 2026-10-11T23:26:26.595996+00:00 |
| LAW / original | 200 | retrieved | 2026-10-11T23:26:26.876751+00:00 |
| OJ / original | 202 | unavailable | 2026-10-11T23:26:27.094144+00:00 |
| OJ / cellar-metadata | 200 | retrieved | 2026-10-11T23:26:27.860313+00:00 |
| OJ / cellar-content | 200 | retrieved | 2026-10-11T23:26:29.080661+00:00 |
| AMEND / original | 202 | unavailable | 2026-10-11T23:26:29.571154+00:00 |
| AMEND / cellar-metadata | 200 | retrieved | 2026-10-11T23:26:30.391775+00:00 |
| AMEND / cellar-content | 200 | retrieved | 2026-10-11T23:26:31.533287+00:00 |
| CONSOLIDATED / original | 202 | unavailable | 2026-10-11T23:26:31.754820+00:00 |
| CONSOLIDATED / cellar-metadata | 200 | retrieved | 2026-10-11T23:26:32.493921+00:00 |
| CONSOLIDATED / cellar-content | 200 | retrieved | 2026-10-11T23:26:33.559559+00:00 |
| TIME / original | 200 | retrieved | 2026-10-11T23:26:33.946677+00:00 |
| FAQ / original | 200 | retrieved | 2026-10-11T23:26:34.119082+00:00 |

Nine distinct requested source documents were retrieved. POLICY remains unavailable: original 403, official unauthenticated Notion API 401. The three original EUR-Lex routes returned empty 202 responses; their official Cellar metadata and text alternatives succeeded. Failed response bytes remain diagnostics and have no successful-document content hash.

## Remaining limitations

POLICY requires authorized content or access assistance from the source owner/facilitator. Its identity, version and policy requirements cannot be verified. No policy-dependent compliance conclusion or approval is possible from this milestone. Snapshot 02 is deliberately partial.

Source version labels are observations, not historical-completeness guarantees. Official guidance may have changed since the review date; authority, dates, conflicts and applicability must be reconciled in stage 03. Cellar HTTP redirects are recorded and no cryptographic authenticity claim is made.

Stages 03–07, legal interpretations, review requests, approvals, final CSV/brief/calendar, full recovery and assignment end-to-end tests are not implemented. Minimal capture journaling and prior-run preservation exist. Entire session capture and formal assessment acceptance remain separately unverified. No commit or push was performed.

## Run again

Follow regulatory-change-impact-brief/references/milestone-1.md. In this workspace the existing local verification runtime can run:

```powershell
.\.runtime\python\python.exe regulatory-change-impact-brief/scripts/capture_sources.py
.\.runtime\python\python.exe regulatory-change-impact-brief/scripts/capture_sources.py --validate
```

Each capture command creates a new live run and retains the prior milestone-1 bundle under deliverables/history/. Validation alone makes no source requests.
