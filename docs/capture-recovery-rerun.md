# Capture recovery and fresh rerun

October 14, 2026 (America/New_York). Followed the facilitator/helper's recovery instructions using the preserved original recordings. Recovered sessions remain historical transcripts; attaching them does not establish that their original hook execution was successful or independently certify complete course capture.

## Recovery

- Original Git refs and current recording/session metadata were backed up under ignored `.runtime/capture-recovery-20261014/` before recovery.
- The user reviewed/trusted all seven Entire hooks in Codex. Corresponding enabled trust entries are present in the user's configuration. Entire 0.11.3 `doctor` continues to report missing approval records, so that diagnostic discrepancy is retained rather than represented as a clean doctor pass. Git and Codex hook installation checks pass. No stuck session was reported; no session was discarded and `doctor --force` was not used.
- The normal Git confirmation hook reproduced its Windows stall. An Entire maintainer recommends the local `commit_linking: always` workaround: https://github.com/entireio/cli/issues/2726. Applied only to ignored `.entire/settings.local.json`; no hooks were bypassed or trusted-hash entries fabricated. The already-stalled hook process was stopped so the new empty recovery commit could finish; recordings were then attached explicitly.
- `entire session attach ... --agent codex --force` recovered the four previously unlinked sessions below. The first automatic amend failed because the target commit was empty; the generated checkpoint trailer was added with Git's `--amend --allow-empty`. Only the new, unpublished recovery commit was amended; published implementation commits `32fc74a` and `c15daf6` remain unchanged.

| Original session | Original scope |
|---|---|
| `01a1305a-ab69-70f2-9496-166dd8ad192d` | October 12 capture-hook check |
| `01a1318a-7d45-7d20-b9ba-29ff6ff6726d` | October 12 session; full original transcript retained |
| `01a13191-6556-7541-9442-fca752e92c13` | October 12 session; full original transcript retained |
| `01a138bd-0d69-75c2-bbca-0135a2d2a8c9` | October 14 implementation/audit/fix/testing/recovery conversation |

Permanent recovery checkpoint: `01M4YNMJ0YXDMSK5EKCTRJP4C5`.

Linked recovery commit: `55920c17d59f85fe4182181069ce9e4eb4b72a5d`.

Verified on GitHub: `refs/entire/checkpoints/C5/01M4YNMJ0YXDMSK5EKCTRJP4C5` resolved to `cdf625c97c2a862c10da081573c117e9ed8d7a39`, matching the local ref after all four attachments. The recovery commit contains the `Entire-Checkpoint` trailer. The earlier October 12 sessions already linked to checkpoints were not duplicated.

## Fresh review

Executed the production `run_review.py` command with reason `Fresh end-to-end rerun after hook trust review and Entire checkpoint recovery`. No synthetic transport was used.

- Run: `live-cbf3e01bbbaa4176845f4a457fd08ed9`.
- Finished: `2026-10-15T02:27:16.078043+00:00` (October 14, 10:27 p.m. New York).
- Seventeen fresh source attempts covering all ten disclosed names.
- Seven stages, schemas, run IDs, predecessor/evidence/artifact hashes, exact request bindings, Stage 06 agreement and calendar checks passed.
- Prior run `live-3de35e38c0b44bc9bd964de5baf74737` was valid and preserved in history before replacement.
- Assigned review date remains August 26, 2026. POLICY and human legal/evidence questions remain unresolved, approvals pending, requests unsent and publication blocked. Technical success is not compliance approval.

The implementation was not changed for this rerun. The preceding 64-test result remains the implementation regression evidence; this exercise reruns the actual live workflow and validates its resulting bytes.

The following normal hooked commit is used to test automatic checkpoint creation. Its actual `Entire-Checkpoint` trailer, stored transcript content and remote ref are the evidence of success; neither this report nor the recovered checkpoint alone proves new automatic capture. See the final verification result for that commit rather than assuming it from settings or an old checkpoint.
