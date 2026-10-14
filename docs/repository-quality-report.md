# Repository quality and reproducibility report

Checked October 12, 2026. No commit/push, external messages, approvals, company writes or production calendar changes. Existing evidence/history, original interview and snapshot.schema.json were preserved.

**Result: local tests and workflow validation PASS; complete clean-checkout/submission readiness FAIL.** The assessed implementation is not in the current Git revision. Unverified external facts are identified separately rather than claimed as passes.

## PASS / FAIL checks

| Check | Result | Actual supporting evidence |
|---|---|---|
| Complete automated suite | PASS | One full unittest discover -s tests -v invocation: **61 tests, zero failures, 499.586 seconds**, exit 0. docs/repository-quality-tests.txt records every result, including feedback, workflow/recovery and status tests. |
| All seven snapshots against unchanged supplied schema | PASS | Fresh read-only publish_drafts.validate and run_review.inspect checks; docs/repository-quality-validation.json. Current run live-c873be1df1c843eea1d9813d7b23ea84. |
| Common run ID, predecessors, source hashes and evidence references | PASS | Actual snapshots/source bytes validated, not merely a cached success report. Current inspection valid, no reported issues. |
| CSV / brief / calendar / Stage 06 / request bindings | PASS | Actual bytes agree with expected Stage 06/evidence rendering; exact artifact hashes and detached request bindings match. Calendar validates. |
| workflow-result.json agrees with current bundle | PASS | All validation result fields, run ID, source attempt count, supersession and finished status checked against actual bundle/attempt records; no disagreements. |
| Current Skill structure and discovery | PASS | Codex 0.162.0-alpha.2 app-server skills/list, forceReload=true: regulatory-change-impact-brief, scope repo, enabled true, no discovery errors. docs/repository-quality-discovery.json. Existing local junction resolves to canonical root package. |
| Skill executable invocation | PASS | Loaded current SKILL.md and used its validation entry point; copied root package helper validates an isolated copy. Fresh isolated run also invoked the helper through a recreated discovery junction. This is not a separate model-selection experiment. |
| Fresh declared dependency install | PASS | Fresh isolated Python initially had no jsonschema. pip downloaded requirements and transitive dependencies without copying existing application packages. Validation passed outside sandbox. Resolved versions are in docs/repository-quality-validation.json. |
| Isolated working-tree reproduction | PASS with Windows path constraint | Copied implementation/evidence, fresh dependencies and recreated junction: one fresh run live-51ec509b6919424abf58bab679b999c2, 17 source attempts, all seven stages/draft checks passed, output .runtime/repro. This development check is not a replacement for submitted evidence. |
| Deep Windows output path | FAIL, documented workaround verified | Initial isolated run live-b596b97029ba43eb96f0c2dfc96c3f5b failed at a 263-character staging path. Its actual failed attempt remains under the isolated candidate directory recorded in validation JSON. A fresh short-output retry passed. Long-path resilience was not implemented or falsely claimed. |
| Clean checkout of current Git HEAD | FAIL — submission blocker | HEAD ee337e3d963d088cda3257bd806ac611d4118944 tracks only README.md and snapshot.schema.json. The Skill, Python implementation, dependencies, tests, interview and captured deliverables are not in that revision. The isolated candidate is a copy of uncommitted working files, not a clone of HEAD. |
| Preserved original/evidence/history files | PASS | Before/after SHA-256 comparison of **280 protected files**, no changes. Existing bundle was neither regenerated nor overwritten. |

## Reproduction prerequisites and corrections

Updated README.md and regulatory-change-impact-brief/references/end-to-end.md:

- Corrected the obsolete claim that no workflow implementation exists.
- Listed standard Python 3.10+ with venv/pip, HTTPS access for dependency installation/fresh sources, writable output and the required checkout contents.
- Included dependency installation, pip check, full tests, existing-bundle validation and isolated fresh-run commands.
- Explained that tests need the captured sources/snapshots in the revision; fictional fixtures and synthetic feedback are test-only.
- Documented recreation of the Windows discovery junction, without duplicating Skill packages or blindly overwriting an existing link, using official https://learn.chatgpt.com/docs/build-skills guidance.
- Clarified that the Python workflow needs no application environment variables, API key, .env file, authenticated company connector, database or browser automation configuration. Codex/account setup is separate from Python execution. Feedback provenance requires separately human-confirmed facilitator evidence; no verification secret is invented.
- Documented short Windows checkout/output paths and the distinction between successful technical execution and blocked publication/incomplete assessment.

requirements.txt already declares all direct runtime dependencies. Fresh installation resolved jsonschema 4.26.0 and rfc3339-validator 0.1.4 plus their declared transitive packages; no missing direct dependency was found. PyYAML used by an optional external Skill structure tool is not imported by the project or full suite and is not a workflow requirement.

The standard py/python launcher is not available on this agent session PATH. Consequently the exact standard py -m venv setup was **not verified** here. The isolated test used a copied Python 3.12.10 embedded runtime with a fresh application dependency directory and bootstrapped pip; it does not prove that a standard Python installation or Windows venv creation exists on a new user's machine. Install/provide standard Python first, or use its full executable path as documented. Do not rely on the ignored machine-specific .runtime runtime in a submission.

The sandbox initially blocked PyPI sockets. An approved outside-sandbox dependency install succeeded. The sandbox could not read some directories created by that installer and produced a misleading namespace/import failure; outside-sandbox validation passed. These are observed test-environment restrictions, not missing package versions. No ACL or OS permission changes were made.

The isolated Codex home deliberately did not trust the project: Codex reported project hooks/config disabled there while Skill discovery still succeeded. This says nothing about the trust state in the user's normal Codex home and is not proof of Entire capture. No authentication configuration was copied into the scanner environment.

## Remaining blockers and unverified items

1. **Include the work in an authorized submitted revision.** Current HEAD cannot reproduce it. Curate the canonical Skill, requirements, code/tests, original export, required sources/snapshots/drafts/history and matching capture evidence. Avoid committing .runtime, virtual environments, temporary test outputs, duplicated junction contents or accidental local cache files. No commit/push is performed here.
2. **Verify a true clean clone with standard Python once the revision exists.** Candidate working-copy reproduction passed, but it is not a substitute for the Git packaging check or the untested standard venv setup. Keep Windows paths short.
3. **Facilitator verification remains required.** Actual coding-session coverage, interview completeness/identity, permitted source access, repository destination/access and accepted reviewer verification channel cannot be established by this test suite. Missing past recordings cannot be recreated.
4. **UI/model invocation remains unverified.** Fresh scanner discovery and helper execution passed; a new normal CLI/IDE session's selector and automatic selection from an unnamed request were not tested. Do not claim automatic selection from a scanner result.

POLICY availability, missing supporting artifacts, historical completeness and human legal interpretation remain documented evidence limitations. Approvals stay pending, requests unsent, and publication blocked; these are expected safeguards, not failed automated tests. No actual reviewer response or legal conclusion was invented. The feedback validator has synthetic tests only and does not independently authenticate a remote facilitator channel or apply decisions.

## Files changed and evidence

Documentation: README.md and regulatory-change-impact-brief/references/end-to-end.md. New report/evidence: docs/repository-quality-report.md, docs/repository-quality-tests.txt, docs/repository-quality-discovery.json, docs/repository-quality-validation.json. Implementation and tests were not changed by this quality check. Isolated environments, copied evidence, failed long-path attempt and fresh reproduction outputs are retained under ignored .runtime/ for inspection; they are not assessed-source replacements.
