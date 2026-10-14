# Milestone 1 operation

From the Project B repository root, using Python 3.10+ and requirements.txt:

~~~powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/capture_sources.py
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/capture_sources.py --validate
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_capture_sources.py -v
~~~

The manifest is references/sources.json. --manifest accepts another file with all ten disclosed source names and the fixed review_date. The --output option controls the local output parent; it does not alter remote sources. No keys are required or consumed by this milestone.

Each command run makes 17 GET attempts: ten original routes, one unauthenticated POLICY API request, and XML/XHTML Cellar requests for the three legal sources. It does not use cookies, credentials, cached local evidence, or challenge-solving. Requests have a 20-second timeout and 16-MiB response limit. Source failures are retained, not silently retried. Any timeout/size limitation is reported.

Output: deliverables/sources/ contains exact response bytes, including diagnostic error/shell/landing bodies, and successful-source extracts with locators. deliverables/snapshots/ contains 01-scope.json and 02-source-capture.json only. attempts.json journals each attempt; source-manifest.json preserves inputs; capture-validation.json records structural and hash checks.

A failed requested document has null content_hash/local_reference, while a captured diagnostic response can have its own separate path/hash. Each source attempt preserves original and alternate routes, redirect chain, actual request/response/capture-completion times, response status, content type, identity metadata and resolution need. The fixed as_of is 2026-08-26T00:00:00Z, a serialization convention for the assigned calendar date; it does not assert that source events happened at midnight.

Cells/rows are extracted from returned HTML rather than guessed from header positions. Field meanings, complete business validation, rule applicability, and historical completeness belong to later milestones. Date/version fields are preserved, not automatically approved. A known pre-review legal rendition remains subject to later authority/timing reconciliation. Public Cellar redirects to HTTP are recorded as a transport limitation; no authenticity signature is claimed.

An existing milestone-1 bundle is retained under deliverables/history/<old-run-id>/ before promotion of a validated new bundle. A later-stage bundle is not replaced by this command. Incomplete staging evidence is left available if an unexpected technical failure prevents promotion. This is minimal preservation for capture runs, not the full assignment recovery implementation.

The repository discovery path .agents/skills/regulatory-change-impact-brief is a junction to this canonical root folder, avoiding duplicate definitions. If copying/cloning elsewhere, recreate a supported discovery link/registration for that environment; Windows junctions are not portable Git content. The required root package remains the submission artifact.

Never report stages 03–07, impact-register.csv, compliance-brief.md, or action-calendar.ics as implemented. This milestone is source-access capture only; missing POLICY blocks policy-dependent later conclusions and gates.

After continuation through stages 03–04, use the milestone-2 validator described in milestone-2.md. The milestone-1-only validator and capture command intentionally refuse a later-stage bundle.
