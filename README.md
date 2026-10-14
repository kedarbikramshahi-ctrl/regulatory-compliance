# Regulatory Change Impact & Compliance Actions

Build a reusable Skill that connects regulatory changes to company impacts and draft compliance actions.

## Start

1. Read the [formal assignment](https://private-pecorino-70e.notion.site/Project-B-Regulatory-Change-Impact-Compliance-Actions-Learner-assignment-3da0b700541e8152b6d1c638fd1c34fa?source=copy_link) for the work and acceptance requirements.
2. Create your own repository from [this starter](https://github.com/GitRollTraining/regulatory-compliance) using **Fork**, then clone your copy and work there.

## Supplied files

| File | Purpose |
|---|---|
| `README.md` | Starting instructions and links. |
| `snapshot.schema.json` | Public snapshot contract; keep it unchanged. |

This working tree contains the implemented live-source Skill, seven-stage Python workflow, draft deliverables, history/recovery, and separate feedback intake. The starter originally supplied only the two files above. A clone can reproduce this work only after the implementation, tests, required captured evidence and documentation are included in its submitted revision.

## Before you work

**Interview rule.** You conduct the stakeholder interview yourself, and the questions are yours. Do not connect a coding agent or any other AI to the interview to run, script, or automate it. The interview transcript is assessed together with the code; a project whose interview was run by an agent is not scored.

- Export your interview as the original Work Sim Markdown, save one final complete file per session under `interviews/`, and commit and push it with your code. Do not rewrite the export. If the export is unavailable, contact the facilitator.

- Use an Agent Skills-capable coding environment. Choose and document your implementation runtime and dependencies; no runtime or install command is supplied here.
- Follow the [shared course guide for session capture](https://classroom.google.com/c/ODcyMjA4NTkwNDk2/m/ODc0NzI2NzQzMzQ2/details) and verify capture is active before implementation. Keep credentials out of the repository.
- Meet the [stakeholder](https://work-sim.catalyte.ai/s/project-b-regulatory-compliance) to understand the work and relevant business sources. Read those online sources through their intended access route; an unavailable source is not permission to substitute repository data.

## Run the implemented review workflow

Follow the [end-to-end setup and recovery guide](regulatory-change-impact-brief/references/end-to-end.md), then run from this repository:

```powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py
```

This retrieves all ten disclosed sources fresh, runs seven stages, preserves prior bundles in history, and creates three local review-only drafts. The review date stays August 26, 2026. Missing POLICY and legal questions remain unresolved; approvals stay pending and requests unsent. See [Milestone 5 verification](docs/milestone-5-results.md) for actual results and remaining assignment requirements.

## Reproduce from a checkout

Prerequisites: standard Python 3.10+ with venv and pip (Python 3.12 was exercised here), outbound HTTPS access to PyPI for installation and disclosed sources for a fresh run, and a writable checkout/output directory. Git is needed to obtain the repository. Codex is needed only for Agent Skill discovery/invocation, not the Python workflow. Verify required coding-session capture separately using the course guide before assessed development.

Confirm that the checkout contains regulatory-change-impact-brief/, requirements.txt, tests/, sample-data/, interviews/, and the required deliverables/sources/ and snapshots/. The regression tests use the submitted captured evidence; a checkout containing only README and the schema is insufficient. See the [repository quality report](docs/repository-quality-report.md) for the actual checked revision status.

On Windows, from the checkout root:

~~~powershell
py --version
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py --validate
~~~

If py is unavailable, use the full path to a standard Python installation for the first two commands. The machine-specific ignored .runtime/python/ runtime is not a submission dependency. Virtual-environment activation is unnecessary. No application environment variables, OpenAI API key, company credentials, .env file, database, or browser automation setup are required. requirements.txt declares jsonschema and rfc3339-validator; pip installs their transitive dependencies. Network sandbox restrictions are separate from an upstream source failure; do not disable access controls to make retrieval succeed.

To perform a new live review, use the command in the section above. It attempts all ten disclosed sources, generates a new run ID, and archives prior available outputs. For an isolated reproduction that leaves submitted deliverables untouched:

~~~powershell
.\.venv\Scripts\python.exe regulatory-change-impact-brief/scripts/run_review.py --output reproduction-output --reason "Isolated reproduction check"
~~~

On Windows, keep the checkout and output paths short: nested workflow staging/history adds path components, and an overly deep test path failed during reproduction. Use a short checkout such as C:\work\project-b and a short output name. No Windows permission or long-path policy change is required by these instructions.

Compare schemas, references and behavior rather than expecting byte-identical run IDs, timestamps or current online responses. Missing sources can produce a technically valid blocked draft. Exit 0 is not legal approval; check publication_status and assessment_complete. Feedback intake is a separate command with explicit supplied files; see [feedback instructions](regulatory-change-impact-brief/references/feedback-intake.md). No authentic reviewer feedback is bundled as a test fixture.

## Codex Skill discovery after checkout

The canonical submission package is regulatory-change-impact-brief/. Codex discovers repository skills in .agents/skills/ and supports linked folders, as described in the [official Skill documentation](https://learn.chatgpt.com/docs/build-skills). Recreate a local discovery link instead of committing duplicate Skill contents or a machine-specific absolute junction.

On Windows, only if the link is absent:

~~~powershell
New-Item -ItemType Directory -Force -Path .agents\skills
if (-not (Test-Path -LiteralPath .agents\skills\regulatory-change-impact-brief)) {
    New-Item -ItemType Junction -Path .agents\skills\regulatory-change-impact-brief -Target (Join-Path (Get-Location).Path 'regulatory-change-impact-brief')
}
Get-Item .agents\skills\regulatory-change-impact-brief | Select-Object LinkType, Target
~~~

If an existing link points elsewhere, stop and inspect it; do not overwrite it blindly. Keep the local junction out of the submitted file selection and include the canonical root package. Restart Codex if the Skill does not appear, then use $regulatory-change-impact-brief to invoke it. A safe verification prompt is: "$regulatory-change-impact-brief Validate the existing seven-stage bundle and explain its unresolved evidence. Do not retrieve new sources or modify existing outputs." Automatic selection from an unnamed prompt is a separate UI/model test, not guaranteed by discovery.
