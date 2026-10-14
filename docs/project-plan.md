# Project B — Regulatory Change Impact implementation plan

## Basis and limits

This plan uses docs/interview-notes.md (interview dated October 11, 2026), README.md, and snapshot.schema.json. Interview requirements, project requirements, and recommended design choices are distinguished below.

The formal assignment linked in the README was inaccessible during the earlier review. Its full acceptance requirements still need to be checked before implementation. The notes do not identify the specific regulation, systems, source URLs, document formats, or exact output templates. Do not invent those details.

## Main business problem

The Compliance and Operations Manager spends too much time reviewing inconsistent AI system records and preparing compliance review packages. Information is spread across registers; evidence may be missing, incomplete, or contradictory. The manager must connect legal requirements to company facts, update an impact register, assign responsibilities, track deadlines in an action calendar, and prepare a package for Legal and Operations.

The tool should reduce repeated checking and document preparation while keeping every finding, correction, and decision traceable. It should help reviewers see what changed, what evidence is missing, what conflicts, who needs to act, and what still needs approval.

## Required features from the interview

| Need | Required tool behavior |
|---|---|
| Missing or incomplete evidence | List the gap, affected system or finding, source references, and who should supply the information. Never treat missing evidence as proof of compliance. |
| Conflicting records | Show the competing values and their sources. Keep the conflict open until a reviewer records a supported resolution. |
| Consistent documents | Generate the impact register, action calendar, and review summary from the same reviewed records. Check that shared IDs, owners, dates, and statuses agree. |
| Change tracking | Compare a review with its previous version. Show additions, corrections, removals, and changes to owners, dates, findings, and approvals. |
| Unresolved issues | Keep a visible list of legal questions, evidence gaps, conflicts, responsible roles, and blockers. |
| Review packages | Prepare clear summaries for Legal and Operations, with evidence links, impacts, actions, deadlines, and pending decisions. |
| Previous versions | Save each review separately. Keep old versions and record what changed, why, who changed it, and when. |

### Decision rules from the interview

- Legal makes final legal interpretations. AI may draft questions and analysis but cannot record its own interpretation as Legal approval.
- Operations controls activation and approved deadlines. Proposed dates must be clearly separated from approved dates. Generating a report must not activate a system or change an approved deadline.
- Unresolved legal questions must not be bypassed. The affected final decision or activation stays blocked until Legal resolves the question.
- Incomplete evidence must not automatically be marked compliant. A supported no-impact finding also requires evidence; it is not a compliance certification.
- Corrections must remain traceable. A new finding or source version must not silently replace its history. Recheck affected decisions when supporting evidence changes.

These are workflow requirements in addition to the JSON format checks below.

## Project requirements from README and schema

Build a reusable Agent Skill that connects regulatory changes to company impacts and draft compliance actions. Use an Agent Skills-capable environment, document the runtime and dependencies, and keep credentials out of the repository.

Keep snapshot.schema.json unchanged. A snapshot is a saved record of one review stage. The schema defines seven stages in this order:

| Stage | Required stage data | Plain-English purpose |
|---|---|---|
| 1. scope | as_of, review_type, systems_in_scope, audiences, approval_gates | Decide what is being reviewed, for whom, and which approvals are required. |
| 2. source-capture | sources | Record the sources and whether they were successfully retrieved. |
| 3. authority-and-timing | binding_rules, timing_rules, guidance_context, authority_blockers | Separate binding rules from guidance and identify applicable dates and legal questions. |
| 4. evidence-reconciliation | system_facts, policy_controls, incident_evidence, conflicts, evidence_gaps | Compare company records and identify missing or contradictory evidence. |
| 5. impact-analysis | impacts, unaffected_items, conflicts, unresolved_items | Explain supported impacts, supported no-impact findings, conflicts, and uncertainty. |
| 6. actions-and-approvals | proposed_actions, approval_requirements, escalations | Draft work, identify owners, and track the actual review decisions. |
| 7. publication-validation | artifacts, validation_checks, publication_status | Check the output package and record whether publication is validated, blocked, or failed. |

Every snapshot must include schema_version (regulatory-compliance-stage-snapshot/2), snapshot_id, run_id, stage, sequence, created_at, status, predecessor, consumed_record_ids, produced_record_ids, state, unresolved, and decisions. Stage status is complete, partial, blocked, or failed.

Stage 1 has a null predecessor and no consumed record IDs. Stages 2–7 require at least one consumed record ID and a predecessor containing the previous snapshot's ID, path, and SHA-256 hash. A hash is a fingerprint that detects file changes.

Source records need an ID, summary, evidence IDs, source role, authority, location, retrieval time and status, content type, version metadata, content hash, and local reference. Use the permitted null values where appropriate. Distinguish binding regulation, official guidance, internal policy, operational records, and other sources. Show unavailable, invalid, unverified, or stale sources honestly.

Impact records use supported-impact, supported-no-impact, conflicting, or unresolved. Approval records use pending, approved, rejected, or not-required. Decisions need a reason and at least one tradeoff. Output artifact records require an ID, path, hash, and validation status.

The schema allows additional fields. Use those fields for deadline approval details, change history, and reviewer information without changing the schema. Schema validation alone does not confirm legal correctness, real approval, document consistency, or valid evidence links; implement separate workflow checks.

The README also requires the original complete Work Sim Markdown export under interviews/, without rewriting it, committed and pushed with the eventual code. The interview notes are useful planning material but do not establish that this separate export requirement has been met. If the original export is unavailable, contact the facilitator. Verify course session capture is active before implementation. Read stakeholder business sources through their intended access route; do not replace unavailable sources with repository data.

## Recommended beginner MVP

Build a single-user, command-line workflow for one regulatory change and one AI system. Use Python, JSON review records, a JSON Schema validator such as jsonschema, and Markdown output tables. These are recommended implementation choices, subject to the formal assignment.

Use a small, fixed set of real sources retrieved through their intended access route: the relevant regulatory material, AI system records, policies or operational evidence, and the existing impact register and action calendar. Exact inputs and formats must be confirmed first. Keep retrieved copies only where permitted.

The reusable Skill guides the seven stages. AI drafts summaries, possible conflicts, impacts, and actions using the supplied evidence. Python performs exact field comparisons, validates structure and references, preserves versions, and generates consistent outputs. The user records actual Legal and Operations decisions manually for the MVP.

### MVP outputs

Recommended outputs, with final formats to be checked against the assignment:

1. Impact register: stable finding ID, system ID, rule reference, impact state, explanation, evidence references, unresolved questions, and linked action IDs.
2. Action calendar: stable action ID, linked finding IDs, task, responsible role, proposed date, Operations-approved date, approval status, and blocking issues. Unknown values stay unknown.
3. Review package: a common evidence summary plus a Legal section for interpretation questions and an Operations section for owners, activation blockers, and approved deadlines.
4. Change history: previous and current values, reason, reviewer or author, timestamp, and source references. Unreviewed AI suggestions stay labelled as drafts.
5. Seven schema-valid stage snapshots for each completed review run, with preserved predecessor links.

Generate all three business documents from one reviewed set of JSON records. Do not independently ask AI to rewrite each document, because that could introduce inconsistent facts. In the MVP, outputs are proposed updated versions for review; writing back to live registers is a later feature.

Keep the first version small: manual source selection, manual decisions, file-based storage, and comparison with one previous run. A dashboard, automatic regulatory monitoring, live calendar connections, and multi-user editing can wait unless the assignment requires them.

## Step-by-step implementation plan

### 1. Confirm assignment and source access

Read the full assignment and course capture guide. Locate the unchanged original interview export. Identify the actual system records, impact register, action calendar, regulatory sources, and required output templates through their intended access routes.

Done when: required deliverables and access routes are known, and missing inputs are recorded rather than replaced with guesses.

### 2. Define one small review case and its approval gates

Choose one regulatory change and one AI system. Record review date, review type, system, audiences (Legal and Operations), and required approval gates. Identify which questions Legal resolves and which activation and deadline decisions Operations controls. Agree on what may be published as a draft while decisions remain pending.

Done when: scope and blockers are clear enough to explain on one page.

### 3. Agree on shared records and identifiers

Define simple fields for sources, systems, findings, actions, deadlines, approvals, issues, and changes. Give records stable IDs so all outputs refer to the same facts. Keep proposed and approved dates separate. Store reviewer, decision time, evidence, and reason for approvals and corrections. Identify the previous review baseline, if one exists.

Done when: a sample finding can be traced from a source to an impact, action, and calendar entry without ambiguity.

### 4. Set up the runtime and reusable Skill

When implementation begins, document Python setup and dependencies. Create the reusable SKILL.md with inputs, the seven stages, evidence rules, and human decision points. Follow the assignment's packaging rules and keep credentials outside the repository.

Done when: another beginner can follow the setup and invoke the workflow.

### 5. Implement scope and source capture (stages 1–2)

Save the scope snapshot. Retrieve allowed sources, record their metadata and versions, and fingerprint retrieved content. Preserve the original source copies where permitted. Record missing, stale, and unavailable sources explicitly.

Done when: every captured fact can be tied to a named source and its retrieval status.

### 6. Implement authority and timing (stage 3)

Draft applicable requirements, timing rules, and guidance context with evidence references. Keep uncertain interpretations as questions for Legal. Track legal effective dates separately from proposed action dates and Operations-approved deadlines.

Done when: legal questions and timing uncertainty are visible, and AI has not invented approval or dates.

### 7. Implement evidence comparison (stage 4)

Compare shared fields across system records, policies, registers, and calendar entries. Use exact checks for mismatched IDs, owners, statuses, and dates. Use AI to suggest possible contradictions in descriptive text, with source passages for human checking. Record missing evidence and competing claims without silently choosing a winner.

Done when: gaps and conflicts have IDs, evidence references where available, affected records, and responsible roles.

### 8. Implement impact analysis (stage 5)

Ask AI to draft evidence-linked impacts and no-impact findings. Keep conflicting and unresolved findings in their correct states. Review the drafts against the sources. Do not convert a missing-evidence case into a compliant or supported no-impact result.

Done when: each finding has a clear reason and supporting evidence or an explicit unresolved issue.

### 9. Implement actions, calendar entries, and approvals (stage 6)

Draft actions for findings and evidence gaps. Assign proposed responsibilities to system owners, Legal, or Operations as supported by the workflow. Link actions to findings. Record proposed deadlines separately from actual Operations-approved deadlines. Keep approvals pending until a real decision is entered, with reviewer and reason. Escalate unresolved legal questions and retain activation blockers.

Done when: every calendar entry refers to a known action, and no draft is mistaken for an approved action, deadline, or activation.

### 10. Preserve versions and compare changes

Save each run in a separate directory. Keep completed snapshots and old business documents unchanged. Compare stable IDs with the previous run and show added, changed, and removed records; retain removed records in history. Record correction reasons and who made them. When evidence or a finding changes, flag affected actions and approvals for review instead of silently carrying approval forward.

Done when: a reviewer can inspect both versions and understand every change. Stage predecessor links explain progress within a run; the change log explains changes between runs.

### 11. Generate and validate the review package (stage 7)

Generate the impact register, action calendar, Legal summary, Operations summary, and change log from the same reviewed records. Validate snapshots against the unchanged schema with date-time format checking. Check record references, stage order, predecessor hashes, and output hashes separately.

Check that owners, dates, IDs, and statuses agree across documents. Verify approval evidence and blockers. Label an unfinished package as a draft and prevent final approved publication or activation when required gates remain open. Record artifacts, validation checks, and publication status in stage 7.

Done when: the package is consistent, evidence-linked, and accurately reports pending and blocked decisions. Passing file validation is not Legal approval or Operations authorization.

### 12. Test the important business rules

Use meaningful cases: a supported impact; a supported no-impact finding; missing evidence; contradictory records; an unresolved legal question; a proposed deadline without Operations approval; a correction that changes a previously reviewed finding; inconsistent register/calendar values; and a changed predecessor file.

Expected results: issues remain visible, unauthorized approval and activation do not occur, changed evidence triggers review, old versions remain available, and invalid or inconsistent outputs are flagged. Clearly labelled synthetic data may test mechanics, but it must not replace inaccessible business sources in the real review.

Done when: both the normal case and these failure cases behave as the interview requires.

### 13. Prepare the fellowship demonstration

Show one end-to-end review and a second run with a correction. Walk through evidence gaps, conflicts, impact and action links, Legal and Operations decisions, consistent outputs, and preserved history. Document setup and limitations. Check the full formal assignment, original export, and capture requirements before submission.

Done when: another person can repeat the review and see why a result is supported, unresolved, or blocked.

## MVP success criteria

- The manager gets an impact register, action calendar, and review package from one consistent set of reviewed records.
- Missing evidence and conflicts are detected and remain visible until properly resolved.
- Legal retains final interpretation authority; Operations retains activation and deadline authority.
- AI never supplies a human approval or silently labels incomplete evidence compliant.
- Previous versions, corrections, and the reasons for changes can be inspected.
- Every completed run has seven structurally valid snapshots and passes cross-file checks.
- Full assignment requirements are verified before the MVP is claimed complete.

## Immediate next steps, before coding

1. Open the formal assignment and confirm the exact required outputs and acceptance rules.
2. Locate the original interview export required under interviews/ without rewriting it.
3. Identify the real source locations and choose one regulatory change and one AI system.
4. Confirm source formats, shared record IDs, and how Legal and Operations decisions will be recorded.
5. Review this small MVP scope, then begin implementation when requested.

Only docs/project-plan.md is updated during this planning task. No application code is started.
