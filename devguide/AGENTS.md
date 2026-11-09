# topomt developer-guide instructions

Read `../AGENTS.md`, `reporting_protocol.md` and
[the common working-instruction policy](../MOLSYSSUITE_GUIDE.md#durable-working-instructions).
The common MolSysSuite layer required by the root `AGENTS.md` retains precedence;
this file refines only local rules within its directory.

For this repository's report lifecycle, use the actual paths and commands in
`reporting_protocol.md`. Regenerate local indexes with
`python devtools/devguide_index.py`, then verify them with `--check`.

For resource catalogues, literature reviews, study-area comparisons and GitHub
Discussions upkeep, read `discussions.md` and consult `discussion_resources.md`.
Update the affected navigation links when a resource conversation or maintained
record changes; resource registries stay outside the defect/proposal queues.
Apply the action-to-issue rule in `discussions.md` to every concrete future task,
including `needs_review` findings. Keep the issue link visible at its origin and
in affected navigation; use `discussion_actions.md` for the dated coverage audit.
An unresolved review needs an open owning/follow-up issue, not only a Discussion.

For comparative findings or a report closing a linked limitation, read
`comparative_findings.md` and use `templates/comparative_finding.md`. Maintain the
current state and dated history in Discussions, lifecycle/navigation metadata in
`comparative_findings.toml`, and reproducible evidence in BenchLab. Run
`python devtools/comparative_findings.py --check` and the report-index check;
read back remote issue/card/index state before declaring reconciliation complete.
Resolved history stays visible and excluded from the current view. Manuscript
reuse always needs the target-specific review defined in the operating guide.
