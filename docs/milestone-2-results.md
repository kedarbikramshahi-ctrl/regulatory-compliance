# Milestone 2 results

## Completed scope

Implemented stages 03 (Authority and Timing) and 04 (Evidence Reconciliation) in `regulatory-change-impact-brief/scripts/reconcile_evidence.py`. The Skill and operation guide now explain both milestones. No stages 05–07, final drafts, compliance approval or company-system writes were implemented.

This continues captured run `live-070d798484d1497495fa28fac99dcb2f`, retaining the assigned review date **August 26, 2026**. No new source retrieval occurred in this continuation. The original capture's actual October 11, 2026 retrieval times remain in snapshot 02. This is not a claim of having fetched the sources on the assigned date or a fresh full review run.

## Authority and timing observations

The helper reparses the preserved source bytes and verifies them against the captured document identity/version metadata. Each retained legal passage has its source ID/hash, section name, exact quote and offsets in newline-joined visible HTML text. These are source observations for Legal, not final legal advice.

| Captured basis | Observed result | Limitation |
|---|---|---|
| Original Regulation 2024/1689, published July 12, 2024 | Article 113's twenty-day entry interval calculates to August 1, 2024. | Calculation from captured text; no authenticity signature verification. |
| Amendment 2026/1744, published July 24, 2026 | Article 4's three-day entry interval calculates to July 27, 2026. | Legal must confirm authoritative completeness and applicability. |
| July 27, 2026 consolidation, revision 001.001 | Header names amendment 2026/1744 and explicitly states that the consolidation has no legal effect. | Used as a comparison aid; original operative acts remain the basis. |
| Article 50 paragraphs 1–6 | Normalized text matches between original and consolidation. | This does not establish that any particular company system meets a duty or exception. |
| Article 50(7) | Revised paragraph matches the replacement in amendment Article 1(20). | Code-of-practice text is separate from company compliance evidence. |
| General Article 113 application date | August 2, 2026 retained in both renditions. Other amended exception dates are recorded separately. | High-risk Chapter III timing is not treated as a blanket delay to Chapter IV transparency. |
| Article 111(4), added by amendment Article 1(39) | Conditional December 2, 2026 transition for Article 50(2), limited by provider and pre-August-2 placing-on-market conditions. | Company eligibility remains unresolved; required date/actor facts are not established. |
| LAW, TIME and FAQ | LAW's paragraph text matches the consolidation; TIME/FAQ contain the tested general/transition dates. Declared LAW basis is July 27, 2026; FAQ's stated update is July 24, 2026. | Guidance is advisory; date-phrase agreement is not complete semantic verification of guidance or historical completeness. TIME's historical revision is unverified. |

Captured operative dates precede the assigned review date, but later retrieval does not prove that the legal set is exhaustive for that date. This limitation remains an explicit authority blocker for human review. Stage 03 is **partial**, and dependent formal conclusions remain withheld.

## Company reconciliation

Stage 04 preserves and links **8 SYSTEMS rows, 10 EVIDENCE rows and 8 CALENDAR rows** by exact system IDs. It retains actual row values, locators, revisions, dates, owners and notes. The CALENDAR `ALL` row remains a shared register action. Calendar dates remain source proposals with unverified approval, separate from legal dates.

The snapshot retains **3 conflict records and 21 evidence-gap records**. These are issue records, not a count of legal violations; several refer to the same system or different aspects of a single evidence item.

- AI-007: SYSTEMS reports conflicting evidence; REC-008 preserves the owner's banner claim and the opposing capture statement.
- AI-003 / REC-003: visible labelling and possible loss of exported metadata remain distinct observations. One does not prove the other.
- Missing, partial and stale states remain visible, including the AI-005 provider-role uncertainty and stale release evidence.
- REC-004 remains an incident with complete evidence that reports no first-interaction AI notice. Complete evidence is not treated as compliance or incident closure.
- REC-010 remains a draft exception request, with its reported missing Legal approval/expiry preserved. No exception is applied.
- All ten `evidence_ref` items remain register references, not independently inspected supporting documents. A register statement does not verify the contents of a screenshot, release record or SOP.
- POLICY remains unresolved, based on the retained original 403 and API 401. `policy_controls` is empty. No assumed policy requirement or authenticated retry is added.

Stage 04 is **partial**. Legal retains interpretations, exceptions and transition eligibility. System owners must supply missing facts/supporting material. Operations retains activation and approved deadlines.

## Expected versus observed checks

| Check | Observed result |
|---|---|
| New focused tests | **8 passed**; exact paragraphs/dates, missing authority/fields, duplicate/orphan IDs, row ordering/extra fields, invalid values, unresolved POLICY/support/exception, tampering and refusal to overwrite. |
| Milestone 1 regression tests | **9 passed** after the upstream validator change. Milestone-1-only validation still refuses later-stage bundles by default. |
| Schema and chain | Stages 01–04 valid; common run ID, correct predecessor hashes, resolvable consumed/evidence IDs and produced records. |
| Source integrity and semantic replay | Passed: retained captures/extract hashes validate, identity metadata is reparsed, and current stage states agree with recomputation from captured evidence. |
| Skill structure | Official local skill-creator validator: `Skill is valid!` |
| Stage boundary | No snapshots 05–07 or final draft package generated. |

The first development run failed paragraph extraction because the original and consolidated renditions put paragraph numbers on different lines. It returned a blocked authority result rather than inventing rules. The corrected parser supports both layouts. A subsequent focused test caught display-label and hyperlink punctuation spacing in the advisory LAW comparison; normalization was corrected without changing raw quotes. Final tests have **no failures**. Earlier local boundary outputs are retained under `deliverables/technical-failures/`, with distinct replacement snapshot IDs, as actual development evidence on the same capture. They are not new live runs or replacement coding-session capture.

The original interview export and `snapshot.schema.json` were not edited. Git's read-only diff reported no changes for those paths; current SHA-256 values are recorded in `docs/milestone-2-protected-file-hashes.json`. Stages 01–02 and source bytes were retained and their hash chain validated. No commit or push was performed.

## Run and validate

See `regulatory-change-impact-brief/references/milestone-2.md` for setup and commands. Current output validation:

```powershell
.\.runtime\python\python.exe regulatory-change-impact-brief/scripts/reconcile_evidence.py --validate
```

The creation command refuses to overwrite existing stages 03/04. Full fresh-run orchestration, archive-before-replacement and assignment recovery are still later work; this milestone deliberately does not claim that contract is complete. For the current four-stage bundle use this validator rather than the milestone-1-only validator.

## Still requiring human review

1. Obtain authorized POLICY content/version through the source owner or facilitator.
2. Verify referenced supporting artifacts, actor roles, placing-on-market dates, exception decisions and unresolved opposing claims.
3. Have Legal confirm the complete authority set and its historical applicability, including conditional transitions and paragraph-specific exceptions. No system/rule impact determination has been made yet.
4. Have Operations verify any approved deadlines and business dependencies; register dates have not been activated or changed.
5. Separately verify coding-session capture and formal assessment acceptance with the facilitator. This report is not a substitute for actual session capture.

Stages 05–07 and final CSV/brief/calendar remain incomplete and require a later authorized milestone.
