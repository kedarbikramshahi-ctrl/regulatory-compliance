# Feedback intake: separate receipts, no applied decisions

Use this only for explicitly supplied response files. It makes no network calls and leaves the seven snapshots, source evidence, drafts, approvals, requests and run history unchanged. Missing POLICY stays unresolved. Never infer request delivery from receiving a file.

## Command

From the repository root, after normal dependency setup:

~~~powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/validate_feedback.py --responses path\to\responses.json --bundle deliverables
~~~

This preserves the input and creates a new receipt under feedback-reports/feedback-<unique-id>/. Unverified feedback is unresolved, not discarded. Optional --report-root selects a separate receipt directory; bundle, interview, Git and Skill directories are forbidden output locations. Each invocation creates a new directory without overwriting any previous receipt.

Exit codes: 0 = validated for human review only; 2 = unresolved or synthetic test-only; 1 = technical failure to complete intake/reporting. Missing/invalid response files and invalid bundles are reported as unresolved when the report can be written. A filesystem failure may require human recovery; input files and existing evidence are never modified.

## Response JSON contract

The top-level object has format_version: 1 and a nonempty responses array. Optional synthetic: true marks test-only inputs; these never count as real reviewer evidence. Every response has:

- response_id: unique response identifier.
- request_id and run_id: exact Stage 06/07 identifiers.
- reviewer: identity_id, display_name and role. Role must match required_reviewer; unresolved required reviewers stay unresolved.
- subject: system_id, impact_ids and action_id. Use exact subject values, including null action_id for system-only requests.
- source_versions: all complete Stage 06 source-version records, including null values for unavailable sources. Do not substitute business labels for actual captured versions/hashes/times.
- drafts: all Stage 07 path/sha256 pairs. Use sha256:<64 lowercase hexadecimal digits>. Paths must match the detached binding exactly.
- response_time: RFC 3339 with timezone, at/after Stage 07 creation and not in the future.
- outcome: approve, reject, request-changes or comment. This is only the reported reviewer outcome; approve never changes an approval state.
- reasons: nonempty list of text; conditions: list of text, allowed to be empty.
- verification_channel_evidence: channel and locator of the actual facilitator verification record. No credential or token should be included.

Ordering of source_versions, drafts and subject impact_ids may change; their full values must match. Duplicate identifiers, missing records, changed subjects, stale runs/hashes, unsupported outcomes and malformed timestamps remain unresolved. Original input bytes and all reported reasons/conditions are retained in the receipt.

## Verification trust boundary

A name, verified:true, email address, channel label or attached file does not authenticate a reviewer. Without an explicitly supplied separate facilitator attestation and a hash confirmed independently by a human through the verified facilitator channel, responses remain unverified.

Optional attestation command:

~~~powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/validate_feedback.py --responses path\to\responses.json --bundle deliverables --verification path\to\facilitator-attestation.json --trusted-verification-sha256 sha256:<human-confirmed-hash>
~~~

The trusted pin is NOT a secret. Obtain/confirm it separately from the response and untrusted attachment; merely computing a hash of a supplied attachment does not establish provenance. Supplying this option asserts that the operator performed that separate confirmation. This local tool cannot establish that the confirmation actually happened, and it cannot authenticate a login, cryptographic signature, verifier identity or remote channel independently. Confirm the accepted verification process with the facilitator before using real feedback.

The attestation file has format_version: 1, response_file_sha256 (hash of exact supplied response-file bytes), and attestations (one unique record per response). Each attestation includes:

- response_id, request_id, run_id and reviewer: exact response values.
- response_sha256: hash of UTF-8 JSON serialized with sorted object keys, compact separators, unescaped Unicode, no NaN/Infinity (validate_feedback.response_digest implements this).
- channel: facilitator-verified.
- verified_by: identity_id and role: Facilitator.
- verified_at: RFC 3339 timestamp at/after response_time and not in the future.
- verification_evidence: nonempty array of objects with locator; it must include the response's verification locator. Retain any additional actual evidence fields. No endpoint is fetched or credential searched for.

Both exact input files are copied into the new receipt and hashed. A pinned, matching attestation yields human-pinned-attestation-matched, not independently authenticated. With all binding checks satisfied, real responses are validated-for-human-review; synthetic responses are test-only. Neither state authorizes a legal interpretation, applies an approval, resolves POLICY, publishes, sends a request or writes to an external system. Unmatched or ambiguous responses remain unresolved with explanations.

## Receipt contents and tests

Each new receipt contains response-input.json when bytes were available, verification-input.json when supplied/readable, and validation-report.json. The report preserves raw response values, attestation records, input hashes, bundle validation, field-specific failures, synthetic labeling and explicit no-change safeguards. Original snapshot.schema.json governs the existing snapshots; this separate receipt format does not alter that schema.

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_validate_feedback.py -v
~~~

Tests use explicitly labeled synthetic reviewer responses and synthetic attestations in temporary directories. They are not actual feedback or authentication evidence. Applying genuine decisions into a new reviewed workflow remains a separate human-controlled task.
