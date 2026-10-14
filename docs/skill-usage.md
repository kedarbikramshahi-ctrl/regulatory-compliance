# Use the Project B Agent Skill

The current canonical package is `regulatory-change-impact-brief/`. Codex discovers it through `.agents/skills/regulatory-change-impact-brief`, a local junction to the root package. The old regulatory-change-review discovery entry has been retired; its local backup is in .runtime.

Invoke it in a newly refreshed Codex session:

> $regulatory-change-impact-brief Capture all ten disclosed Project B sources fresh and generate snapshots 01 and 02 only. Keep August 26, 2026 as the review date and POLICY unresolved without authorized evidence.

Read [operation instructions](../regulatory-change-impact-brief/references/milestone-1.md) for setup, manual execution, validation and tests. See [milestone results](milestone-1-results.md) for verified discovery and live capture results. Automatic selection in your current IDE session still needs testing.

The fictional prototype remains available through review.py and docs/mvp-setup.md. It does not satisfy live-source requirements. Stages 03 and 04 are now available through scripts/reconcile_evidence.py; see [Milestone 2 instructions](../regulatory-change-impact-brief/references/milestone-2.md) and [results](milestone-2-results.md). Stages 05 and 06 are now available through scripts/analyze_impacts.py; see [Milestone 3 instructions](../regulatory-change-impact-brief/references/milestone-3.md) and [results](milestone-3-results.md). Stage 07 and the three review-only drafts are now available through scripts/publish_drafts.py. See [Stage 07 instructions](../regulatory-change-impact-brief/references/stage-7.md) and [results](stage-7-results.md). Fresh orchestration/history/recovery now use scripts/run_review.py; see [end-to-end instructions](../regulatory-change-impact-brief/references/end-to-end.md). Human review and facilitator verification remain unfinished. The original historical discovery report describes the previous Skill, not this package.
