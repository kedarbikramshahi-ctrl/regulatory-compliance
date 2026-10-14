# Milestone 3 operation

Continue the verified captured run through stages 05 and 06. This is local preparation from stages 01–04, not a new live retrieval run. Retain the existing run ID, actual source retrieval times and assigned August 26, 2026 review date. No API, model subscription or new dependency is required.

Using Python 3.10+ and requirements.txt, from the project root:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/analyze_impacts.py
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/analyze_impacts.py --validate
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_analyze_impacts.py -v
```

The workspace's existing `.\.runtime\python\python.exe` may replace the virtual-environment executable. `--output` selects a captured bundle. The creation command refuses existing later-stage outputs; validation makes no source requests. Full fresh-run orchestration/recovery is still incomplete. Never delete prior evidence or silently reuse an old validation result. Unexpected CLI errors are recorded in milestone-3-failure.json with retained boundary outputs for inspection.

Stage 05 analyzes each captured system separately against Article 50(1), (2), (3), the two distinct (4) bases, (5), (6), (7), the Article 111(4) transition, and inaccessible POLICY. IDs are based on system/rule, not row positions. All reports remain provisional. State meanings:

- supported-impact: a supported notice-remediation review need in the registers, not a finding of breach, confirmed provider responsibility or approved change.
- supported-no-impact: a bounded screening observation from disclosed roles/output/publication scope, not proof of compliance or an exception. Legal must review these too.
- conflicting: opposing notice claims or a provenance concern remain separate; visible labels do not establish machine-readable marking.
- unresolved: actor/function/exception/timing/evidence facts or authority require confirmation. Missing POLICY is never replaced with assumptions.

Do not infer emotion recognition from classification, a deep fake from any synthetic output, public-interest publication from every generated text, an exemption from a human-review label, or a blanket transition from a future date. All supporting artifact references remain uncaptured register claims. Every system retains a POLICY unresolved item. No system is declared wholly unaffected or compliant.

Stage 06 creates undated evidence/review proposals for impacts requiring work. It separately preserves each existing calendar proposal with its exact action, owner and date, pending human approval. The ALL calendar action links all systems' remaining work. Invalid or missing source dates remain null, with the raw value and reason preserved. Source-proposed dates are not legal dates or approved deadlines.

Requests include request ID, system/impact/action subjects, run ID, captured source versions/hashes/times, evidence, question and required reviewer. Legal reviews paragraph-specific scope, including all bounded no-impact outcomes. Operations/Legal review the existing calendar proposals according to their disclosed required role. Requests are unsent, feedback is absent and approvals pending. Final draft path/hash binding is explicitly deferred to stage 07; no request has been sent and no actual reviewer response is simulated.

Outputs are snapshots/05-impact-analysis.json, snapshots/06-actions-and-approvals.json and milestone-3-validation.json. Validation checks schemas, exact predecessor hashes, record/evidence references and replays current impact/action/request state against the retained evidence chain. Both stages remain partial. No stage 07, final CSV/brief/calendar, approval or company-system write is performed.

See docs/milestone-3-results.md for actual results and human-review limitations.

After Stage 07 and final drafts have been generated, use scripts/publish_drafts.py --validate for the current seven-stage bundle. The milestone-3-only validator still refuses Stage 07 by default.
