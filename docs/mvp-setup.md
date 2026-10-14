# Run the fictional Project B MVP

## What it does

This is an offline Python demonstration, using only fictional training data. It does not contact an AI service, retrieve real law, decide compliance, approve deadlines, or activate systems. The reusable Agent Skill is now available in .agents/skills/regulatory-change-review/; see docs/skill-usage.md. The real-source Python workflow is still future work.

The sample proposes a fictional customer-facing AI notice review for DEMO-001. It deliberately contains two evidence gaps and conflicting notice_enabled values. Legal applicability remains unresolved. All human approvals remain pending even if the evidence fields are filled in.

## Setup on Windows

Install Python 3.10 or later from python.org. In PowerShell, open this project folder and run:

~~~powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe review.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
~~~

If your machine uses python instead of py, use python for the first command. Using the full virtual-environment path avoids PowerShell activation-policy issues. No API keys are needed.

For this session, a local verification runtime was downloaded under .runtime/. It is excluded from Git and is not required for your submission. Normal setup should use the virtual environment above.

## Find your output

Each execution prints a new outputs/demo-... folder. It contains:

- input.json: the exact fictional input used for that run.
- Seven numbered JSON snapshots, one for each schema stage.
- review-report.md: a draft brief, impact register, and action calendar in one document.
- validation-results.json: results from the schema and additional checks.

A new folder is created each time; earlier runs are preserved. Final publication stays blocked because Legal and Operations decisions remain pending. A complete source-capture stage means that fictional input was captured, not that compliance is established.

Validate a saved run again, replacing the example folder name with yours:

~~~powershell
.\.venv\Scripts\python.exe review.py --validate outputs/demo-YOUR-RUN-ID
~~~

Use an edited fictional input without changing the original sample:

~~~powershell
.\.venv\Scripts\python.exe review.py --input sample-data/my-example.json
~~~

Keep fictional set to true. This MVP rejects real-data inputs. Use one system ID, unique record IDs, Boolean notice_enabled values, and the sample's structure. Required evidence counts as present only when its status is available and it has nonempty content. These structured checks are not an assessment of whether evidence is legally sufficient.

## Checks and tests

The program uses JSON Schema Draft 2020-12 and date-time format checking against the unchanged snapshot.schema.json. It also checks stage order, run identity, predecessor IDs and hashes, input/output record references, evidence references, artifact hashes, pending approvals, and blocked final publication.

Tests cover missing and conflicting evidence, a complete consistent example, seven valid snapshots, preserved runs, invalid timestamps and missing fields, altered predecessor/report files, unresolved references, blocked publication, and rejection of real data or duplicate IDs.

A failed validation or malformed input causes the command to exit with an error. Do not treat files in an interrupted run as validated. validation-results.json is written only after a successful full-run check.

## What remains for the fellowship

- Read the full formal assignment and verify its exact deliverables, rubric, output templates, and Skill packaging requirements. It was inaccessible in the earlier review; this demo does not establish acceptance.
- Verify the shared course session-capture instructions and active capture. Current capture status is not verified by this program.
- Verify the new reusable Agent Skill against the formal assignment and test its discovery in your chosen environment. Add any required real-source AI drafting integration with human review.
- Retrieve the actual regulatory and business sources through their intended access routes. Fictional data here is an explicitly requested mechanics demonstration, not a substitute for those sources.
- Add authority/version/timing analysis, richer system/policy/incident comparisons, actual human decision entry, dependencies, separate output templates if required, and cross-run change comparison.
- Check the original Work Sim export is complete and unchanged, and commit and push it under interviews/ with the final code. The export is already in that folder; submission via Git is not done by this MVP.
- Confirm your fork, required submission method, and any additional assessment scenarios.

The existing README, interview notes, project plan, original export, and snapshot schema are preserved.
