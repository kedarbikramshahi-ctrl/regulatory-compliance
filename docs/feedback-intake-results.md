# Feedback intake and binding validation results

Implemented regulatory-change-impact-brief/scripts/validate_feedback.py as an explicitly invoked, network-free intake command. It validates the actual current bundle, matches request/run/subject/source-version/draft-path/hash bindings and preserves supplied response times, reported outcomes, reasons, conditions and verification evidence. Receipt records include exact observed Stage 06/07 and final-draft hashes and the expected detached binding.

Each invocation creates a unique receipt directory with the exact supplied response bytes, supplied attestation bytes when readable, and validation-report.json. Missing, malformed, stale, mismatched or unverified responses remain unresolved with explanations. Duplicate JSON keys/response IDs/source IDs/draft paths are not silently collapsed. Readable malformed input bytes are preserved. Missing input bytes are reported honestly. Existing receipts cannot be overwritten; output inside the protected bundle/interview/Git/Skill directories is refused.

Names and verified flags do not authenticate anyone. A separate facilitator attestation requires a SHA-256 pin confirmed separately by a human. The pin, attestation byte hash, exact response-file hash, canonical response hash, identity/role/channel and verification-time evidence must match. The script records human-pinned-attestation-matched, not independent authentication. A matching genuine response can only be validated-for-human-review. An explicitly synthetic response remains test-only. No decision is applied.

## Commands and documentation

See regulatory-change-impact-brief/references/feedback-intake.md for the response and attestation contracts, the operator trust boundary, commands, report locations and exit codes. SKILL.md links this mode; end-to-end.md now describes separate intake instead of saying it is unimplemented.

~~~powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/validate_feedback.py --responses path\to\responses.json --bundle deliverables
~~~

Without trusted facilitator evidence this correctly produces an unresolved receipt and exits 2. Exit 0 means validated for human review only; exit 1 reports technical failure. Supplying a name or calculating a hash of an untrusted attachment does not establish facilitator verification.

## Observed checks

- Feedback regression: 13 passed after the final code change. Synthetic fixtures cover binding fields, versions/hashes, reviewer identity/role, channel/proof/time, malformed/missing inputs, duplicates, tampered bundles, record reorder, append-only preservation and CLI exit behavior.
- Publication regression: 6 passed.
- Impact regression: 7 passed, including the earlier unknown-output and unknown-reviewer fixes.
- Total relevant tests in these three separate final invocations: 26 passed, zero failures. The entire repository suite was not rerun for this additive mode.
- Skill structure: Skill is valid!
- Current bundle live-c873be1df1c843eea1d9813d7b23ea84 passed read-only seven-stage schema/run/predecessor/evidence/artifact/request-binding/Stage 06 agreement/calendar validation.
- Preservation: all 280 baseline evidence, deliverable/history, interview and schema files retained identical SHA-256 hashes.
- The first CLI test exposed missing helper import-path setup in the isolated Python runtime. That was corrected; the CLI test and final feedback suite passed.

Raw final test logs: docs/feedback-intake-tests.txt. All test feedback/attestations were explicitly synthetic and generated in temporary test directories, never treated as live feedback or written into the assessed bundle. No actual response file was supplied, so no real feedback receipt or human decision is claimed.

## Remaining limits

The facilitator must confirm the accepted verification process and genuine reviewer identity/channel provenance. The tool cannot independently authenticate a login, signature or facilitator channel; a trusted pin is an explicit human trust input, not a substitute for its provenance. Applying reviewed decisions into future snapshots/drafts remains a separate human-controlled task. A response file does not prove an unsent request was delivered.

POLICY remains unresolved, interpretation/approvals pending, requests unsent and publication blocked. Current snapshots, sources, drafts and history were not regenerated or edited. Source access, missing artifacts, capture verification, clean-checkout reproduction and submission readiness remain separate work. No company writes, external messages, calendar writes, approvals, commit or push occurred.
