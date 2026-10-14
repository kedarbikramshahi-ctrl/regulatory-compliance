# Codex Skill discovery verification

## Result

The Skill is structurally valid, the installed Codex scanner discovers it, and its fictional demonstration works. Automatic selection from a natural-language request in the user's normal Codex session is still untested.

## Fixes

Moved the package from skills/regulatory-change-review/ to .agents/skills/regulatory-change-review/, Codex's documented repository discovery location. There is one package, not two competing copies. Updated usage commands and fixed the helper to find its repository by checking ancestor folders instead of assuming a fixed folder depth. An explicit --project path still works when the package is installed elsewhere.

The package has SKILL.md with name and description YAML frontmatter, scripts/run_demo.py, and two referenced Markdown documents. agents/openai.yaml is optional; it is not needed for discovery, and no policy disables implicit invocation.

Sources: [Official OpenAI Build skills documentation](https://learn.chatgpt.com/docs/build-skills), [Codex app-server documentation](https://learn.chatgpt.com/docs/app-server).

## Actual discovery check

Used the installed Codex CLI 0.162.0-alpha.2 app-server over stdio. Sent initialize, initialized, and skills/list with this repository as cwd and forceReload=true. No extra skill root was supplied. Codex returned regulatory-change-review at its .agents/skills/.../SKILL.md path, scope repo, enabled true, and no discovery errors. The evidence is saved in docs/skill-discovery-results.json.

The check used an isolated CODEX_HOME under the ignored .runtime/ directory to avoid writing to personal configuration and did not copy authentication or user settings. It did not verify personal settings, the live desktop/IDE selector, or a separate model turn. No account login, API call, Git commit, or push was performed.

## Demonstration and checks

Read the Skill and its fictional-demo instructions and invoked the relocated helper without --project, exercising the repaired repository detection. It created outputs/discovery-tests/demo-53b8eaf40096/.

The review retained two evidence gaps and conflicting notice_enabled claims (true and false). The agent prepared a separate agent-draft-review.md with evidence-linked reasoning and recommended evidence collection. No legal conclusion was made. Approvals remained pending, approved dates remained null, and final publication remained blocked.

- Official skill-creator quick_validate.py: passed.
- Seven snapshots: schema, timestamp, stage order, references, predecessor hashes, artifact hashes, and review controls passed.
- Existing Python regression tests: all eight passed.
- SHA-256 comparisons: snapshot.schema.json and the original interview export are unchanged.

## Remaining normal-session test

In Codex CLI or the IDE extension opened on this repository:

1. Run /skills or type $ and check that regulatory-change-review appears. If it does not, restart Codex and try again.
2. Send: "$regulatory-change-review Review our fictional sample-data/review.json, run the demonstration, and explain the evidence gaps and proposed actions. Keep human approvals pending."
3. Confirm the agent reads this package and generates a fresh seven-stage run with valid outputs.
4. In a fresh conversation, omit the skill name and ask for a regulatory-change evidence review. Observe whether Codex selects the Skill automatically. A relevant description enables selection but does not guarantee selection on every prompt.

Steps 1–4 in the user's normal UI/model session remain untested here. Direct instruction loading, the executable demonstration, and actual repository scanning were tested. The formal fellowship assignment's additional packaging and acceptance rules remain unverified.
