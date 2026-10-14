# Milestone 3 results

Implemented stages 05 (Impact Analysis) and 06 (Actions and Approvals). Both are **partial**, review-only outputs. No legal conclusion, approval, source-system change, external message or production-calendar write was made.

## Evidence and scope

The continuation uses the existing captured run `live-070d798484d1497495fa28fac99dcb2f`, with the assigned date **August 26, 2026**. It does not make new source requests or change recorded retrieval times. Stages 01–04, the source bytes, original interview export and supplied schema were preserved. Hash comparisons against the prior protected-file record confirm the schema, interview export and stages 01–02 unchanged; the preserved predecessor chain also validates.

All eight systems are screened separately against Article 50(1), (2), (3), the two (4) bases, (5), (6), (7), the conditional Article 111(4) transition, and unavailable POLICY. The resulting **80 scoped records** contain:

| State | Count | Meaning here |
|---|---:|---|
| supported-impact | 2 | Register-supported notice-remediation review needs for AI-004; not legal breaches or confirmed provider liability. |
| conflicting | 3 | AI-007 notice claims and AI-003 provenance concerns requiring investigation. |
| unresolved | 49 | Missing actor/function/exception/timing/supporting-evidence or POLICY facts. |
| supported-no-impact | 26 | Bounded actor/output/publication screening observations only; Legal still reviews them. |

These are not counts of violations. No system is declared compliant or wholly unaffected. Stage 04's missing/conflicting records and stage 03's authority limitations remain visible in the new chain.

## System-level observations

| System | Captured basis and unresolved review need | Recorded owner |
|---|---|---|
| AI-001 Learner Support Chat | Notice reported present; supporting notice/release artifacts uninspected. Provider responsibility and paragraph-specific notice scope still need confirmation. | Learner Operations |
| AI-002 Admissions Draft Assistant | Applicant email drafting is not reported public-interest publication. Notice practice remains unknown; do not infer a text exemption merely from advisor approval. | Admissions |
| AI-003 Campaign Image Studio | Visible label is reported, while exported metadata may be lost. Do not equate a visible label with machine-readable marking or every synthetic image with a deep fake. | Communications |
| AI-004 Pronunciation Coach | Register and incident describe no first-interaction notice. A supported remediation-review need exists, while provider duty and exception applicability remain for Legal. | Learning Experience |
| AI-005 Remote Proctor Signal | Provider role is unknown and release evidence stale. Classification and human adjudication do not establish emotion recognition or biometric categorisation. | Assessment Operations |
| AI-006 Staff Summary Assistant | Internal staff-note use supports only a bounded observation about the public-interest text-publication basis. It does not establish overall compliance or all duties/exception conditions. | People Operations |
| AI-007 Website Guide Avatar | Owner banner claim and opposing capture statement remain conflicting. No winner is selected and no incident is closed. | Marketing |
| AI-008 Video Localisation Tool | Visible label reported, provenance testing incomplete, and draft exception lacks verified Legal approval/expiry. Deep-fake facts and specific exceptions still need confirmation. | Communications |

Every system retains unresolved POLICY scope. The original 403 and API 401 remain in the source chain; no policy requirement or authorized content is invented. Conditional transition eligibility remains unresolved rather than granting a blanket delay.

## Proposed actions and human review

Stage 06 contains **62 proposed actions, 62 pending approval records and 70 unsent review requests**:

- 54 evidence/interpretation proposals for supported review needs, conflicts and unresolved impacts. They use the captured system owner as the proposed coordinator and have **no proposed date**.
- 8 existing CALENDAR proposals preserve their exact recorded actions, owners and dates. These dates are not approved deadlines or legal effective dates. The ALL action links remaining review work across all systems. Invalid/missing source dates would remain null with the raw value and explanation.
- Each proposed action has an unsent review request and pending approval. Eight additional Legal requests cover all paragraph-specific outcomes for each system, including bounded no-impact observations.

Requests identify the request/system/impact/action, current run, captured source versions/hashes/retrieval times, evidence, question and required reviewer. All remain `not-sent`, with no received feedback. Binding requests to exact final draft paths/hashes is explicitly deferred to stage 07. This is preparation for human review, not a claim that any reviewer was contacted.

POLICY access is a dependency for policy-dependent proposals; useful collection of other facts need not await fabricated policy requirements. Legal controls interpretation/exceptions, source owners verify facts, and Operations controls activation and approved dates.

## Verification

- Five new focused tests passed: eight-system coverage and distinct states, changed authority/actor facts, stable IDs under row ordering, dates/approval/request safeguards, full schema/reference/hash/replay checks and tamper rejection.
- Nine source-capture regression tests passed.
- Eight authority/reconciliation regression tests passed; the persisted result is in `milestone-3-reconciliation-check-result.json`.
- The local skill-creator structure check passed: `Skill is valid!`.
- The actual six-stage bundle passed schema, exact predecessor hash, evidence-reference and semantic-replay validation. Stage 07 is absent.

The tool runtime timed out during one combined regression invocation. That timeout is not counted as a passing test. A separate invocation writes its actual test output and result to files so it can be checked independently.

Initial stage 05/06 development boundaries were retained under `deliverables/development-attempts/` before refining requests and dependencies. They are actual local development attempts on the same capture, not newly retrieved runs or substitutes for coding-session capture. Full fresh-run orchestration and assignment recovery remain unfinished.

## Run and remaining work

Setup and commands are in `regulatory-change-impact-brief/references/milestone-3.md`. Validate the current six-stage bundle with:

```powershell
.\.runtime\python\python.exe regulatory-change-impact-brief/scripts/analyze_impacts.py --validate
```

The creation command refuses existing later-stage outputs. This continuation does not replace the assignment's eventual requirement for a fresh full run and recovery/history behavior.

Human review must resolve authorized POLICY access, supporting artifacts, actor/function facts, applicable exceptions, transition eligibility, authority completeness and approved operational dates. Stage 07, final CSV/brief/calendar, detached final-draft request bindings and full recovery remain unimplemented. Coding-session capture and facilitator acceptance still need separate verification. Nothing was committed or pushed.
