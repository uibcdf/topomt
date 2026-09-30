---
summary: Complete contributor full-CI routes and skipped-push recovery.
issue: uibcdf/topomt#58
status: active
opened: 2026-09-30
closed:
severity: medium
verification: measured
area: [governance, ci]
guard: tests/test_ci_backlog.py
normative:
blocked_by: []
supersedes: []
---

# Full-CI contributor routes and skipped-push recovery

## What

Implement uibcdf/molsyssuite#39 in TopoMT while preserving component-owned
scientific tests and environments. Baseline main 19ab4bf is unprotected;
complete six-cell Linux/macOS Python 3.11–3.13 CI excludes documentation PRs.
Weekly and recent push matrices fail in the actual test step, as separately
tracked in uibcdf/topomt#16. Governance needs independent execution.

## How

Remove only PR path exclusions; keep the existing documentation push filter.
Preserve full scientific pytest selection, minor-specific Conda environments,
controlled suite revisions and the separately tested MolSysMT source pin.
Pin macOS to macos-15 and assert arm64 and each interpreter minor before tests.
Add an independent reporting/backlog/PR-route job using administrative targets
and --noconftest, which avoids importing the scientific fixture module only
for those governance tests. Full scientific jobs retain their original conftest.

Keep unconditional weekly Monday 09:00 UTC and manual complete execution;
add daily conditional recovery at 01:55 America/Mexico_City. Manual
probe_backlog=true runs governance and the detector, omitting heavy jobs.
Require explicit PRs and strict Ruff/governance/supported full checks, with
zero mandatory approvals and admin bypass for current maintainers dprada/LMMV.

A watermark requires a successful ancestral main push/schedule/manual CI run
with all three Linux minors and their actual successful Run tests steps.
Probe success, PRs, other branches, failures and skipped tests cannot clear
skipped-commit debt. Missing or uncertain evidence runs a complete matrix.
The debt survives calendar boundaries and ordinary commits until executed
complete coverage includes the skipped commits.

## Why

External contributors run the complete supported suite on every PR; internal
maintainers retain lightweight direct iteration and explicit skip-CI. Recovery
remains observable even while scientific CI is red, and those failures cannot
be reclassified as successful governance or as a cleared backlog.

## What is measured and what is assumed

On 2026-09-30, fresh API returned main unprotected and only dprada/LMMV,
both admins. GH Run Receptor 1.0.0 preserved failure for baseline CI
36700609235 at 507e347; native evidence confirms all six Run tests steps failed.
Linux 3.11 reported 88 failed, 716 passed, 69 skipped and five xfailed in
816.90 seconds; Linux 3.12 reported the same counts in 1847.47 seconds.
Missing fpocket is one of nine grouped causes, not a complete diagnosis.

The new PR-route regression failed against the old workflow because its
paths-ignore excluded documentation PRs. New governance execution and
protection evidence are pending verification.

## What was refuted

A successful governance probe is not successful scientific coverage. Adding
continue-on-error or removing scientific tests would hide existing failures.
A calendar-day-only detector loses earlier unpaid skipped commits. Full
scientific conftest imports are unnecessary for administrative report/debt
checks and would couple their independent gate to the scientific stack.

## Scope and exclusions

CI routing, administrative guards, architecture evidence, protection and
reporting only. No implementation, scientific assertion, source dependency
revision, release or support-range change. Existing matrix failure and optional
engine/provider adoption remain with uibcdf/topomt#16, uibcdf/topomt#56,
uibcdf/topomt#53 and uibcdf/molsyssuite#62. The user has deferred scientific
execution reviews for active MolSysMT/MolSysViewer.

## Acceptance criteria

- Verify strict complete supported checks, explicit PR rule and admin bypass.
- Run independent hosted governance and backlog probes; demonstrate that
  skipped pushes remain due after failed or unexecuted complete coverage.
- Dispatch the complete six-cell lane and preserve actual scientific results.
- Observe actual daily schedule and hosted external PR before final adoption.
- Review distribution-platform claims separately.
- Retain tests/test_ci_backlog.py and tests/test_ci_routes.py as durable guards.

This issue remains partial until the unobserved execution and platform gates
are satisfied; no scientific pass is required to establish configuration.

## Local implementation verification

Python 3.13.15: seven administrative tests passed with --noconftest and
pytest-receptor llm. Ruff lint and formatting passed (367 files), report indexes
are current and central component conformance passed. Scoped mypy 2.3.1 checked
only the new devtools/ci_backlog.py successfully in a temporary isolated tool
environment; the shared environment was preserved.

The updated protection API confirms strict eight checks, an explicit PR rule
with zero required approvals, administrator exemption, and no force/deletion.
Scientific tests, environments, controlled dependency revisions and the tested
MolSysMT source pin remain unchanged. The implementation direct push uses
[skip ci] under the user's exception; explicit dispatches verify governance,
Ruff/policy and the complete lane once, avoiding repeated scientific matrices
for each development step.

A concurrent component development advanced main to c5b6588 before publication.
The rejected first push changed no remote files; the unpublished governance
commit was rebased over those provider/provenance/AlphaSpace2 changes. Its delta
still contains only CI routing, administrative guards and this report; external
component implementation is preserved. Governance dispatch evidence must name
the rebased source, not the older head used by the rejected dispatch attempt.

## First hosted verification and bootstrap correction

At published 47683f5 (implementation 8bd0a83), GitHub confirmed bypass of the
explicit PR rule and all eight required checks. Ruff 36715830303 and suite
policy 36715837117 passed. Initial probe 36715825226 found no eligible executed
green full watermark and reported 39 skipped commits, including both new
internal skips and the earlier guide-distribution commit; heavy jobs were
omitted as requested. The probe's overall result was failure because the new
governance-only pip bootstrap requested pytest-receptor 0.6.0, a Conda pin not
available from PyPI. Native pip evidence listed published 1.0.0/1.1.0/1.2.0.

Correct the new independent pip job to exact published 1.0.0, already proven
by other suite consumers. Preserve the scientific Conda environments' existing
0.6.0 pins and complete scientific pytest selection. This is a local workflow
bootstrap error under #58, not a provider/scientific defect or a suite-wide
mandatory tool upgrade. Retain the initial failed run as evidence.
