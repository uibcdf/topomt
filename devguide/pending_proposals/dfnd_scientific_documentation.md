---
summary: Present DFND theory and method in a dedicated public documentation section.
issue: uibcdf/topomt#170
status: open
opened: 2026-11-09
closed:
severity: low
verification: inspected
area: [docs, dfnd]
guard:
normative:
blocked_by: []
supersedes: []
---

# Dedicated DFND scientific documentation

## What

The maintainer requests a carefully studied proposal for a complete presentation
of DFND and its theoretical basis. The proposed public destination is
`docs/content/dfnd/`, titled **DFND: Theory and Method**, as a first-class section
beside the User guide and BenchLab.

The [section plan](../DFND/documentation_section_plan.md) supplies thirteen
chapter briefs, appendices/references, reading routes, a source/evidence map,
figures/examples and authoring/publication gates. It is a proposal, not a
delivered public section or a scientific-kernel change.

## How

Review the current implementation and accepted developer contracts alongside
the original design, later audits, tests and canonical BenchLab evidence. Curate
one progressive explanation for intuitive and formal readers. Keep model,
algorithm, catalog interpretation and evidence distinct, with scope and
implementation maturity at each relevant inference.

## Why

Current public material explains geometry/query operation and individual case
results but does not teach the complete method. Developer material spans
different design stages, including the original alpha/discrete-flow proposal,
later local-capacity graphs and unresolved physical interpretation. Copying it
unchanged would teach conflicting definitions and stale implementation status.

## What was refuted

The existing geometry guide and BenchLab are not substitutes for a scientific
method narrative. Historical filenames and implementation/test presence do not
establish an adopted specification or independent physical correctness. The
section must cover dry structure, boundaries, relief and interfaces, while
keeping future detectors and qualified physical paths distinct from current
descriptors and graph connectivity.

## Scope and exclusions

#170 owns documentary proposal, reconciliation, authoring and section integration.
#76/#151/#75 retain their scientific questions; #60/#61 retain support/interface
adoption; #16 installed/matrix evidence and #18 site identity/deployment remain
separate. No new native protein work, geometry, engine execution, remote
submission, package installation or algorithm change is part of this proposal.
The existing three-case scientific continuation keeps its priority.

## Acceptance criteria

The proposal must map the complete narrative to current code, accepted contracts
and evidence, with explicit page tree, reading routes, figures, worked examples,
authoring order and qualification limits. Later completion requires reviewed
public pages/navigation, consistent notation and units, verified citations and
meaningful examples, plus bounded documentation checks. Keep this issue open
after the proposal: an outline alone does not deliver the public section.

## Proposal checkpoint — 2026-11-09

Reviewed source `dc525ce63c6d30531f4924c9469511384394d9b3`, the current
theoretical/design contracts, code and relevant tests, public navigation and
existing BenchLab evidence. The implementation/evidence map records inspected
material; no new scientific calculation or literature priority claim follows.

Executed checks: **16 reporting/comparative tests passed**; regenerated report
indexes and their check pass, as does offline comparative consistency and the
diff whitespace check. The three authored/edited contributor documents parse
with MyST without warnings, treating Markdown links as URIs in the standalone
parser and checking **129 local link targets** separately. The generated queue
index is covered by the reporting checks.

Tests ran sequentially on one CPU with one-thread numerical libraries, 6 GiB
address-space and 60 s CPU limits: 2.34 s elapsed, peak RSS 153 MiB. Preflight
found about 56.5 GiB available of 60.5 GiB physical memory, zero memory PSI and
no swapping in the sampled live interval. Slurm discovery could not open its
socket and was stopped after three seconds; no allocation was claimed. Raw
local logs are in `.cache/dfnd-documentation-proposal/` for this open issue.

This delivery changes developer proposal/navigation records only. Public section
authoring/integration and its Sphinx/example checks remain under #170; the full
scientific suite, public-site deployment, installed artifacts and support matrix
were not run or qualified by these checks. The pre-existing human version-file
change is preserved outside this delivery.
