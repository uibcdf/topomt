---
summary: Separate independent tetrahedron expectations and native DFND experiments into executable notebooks.
issue: uibcdf/topomt#134
status: resolved
opened: 2026-11-07
closed: 2026-11-07
severity: low
verification: inspected
area: [documentation, dfnd]
guard: tests/test_dfnd_tetrahedron_study.py::test_system_study_freezes_independent_expectations_for_the_same_input
normative: devguide/DFND/study_zone.md
blocked_by: []
supersedes: []
---

# Independent tetrahedron system and native-study notebooks

## What

The maintainer approved a short case overview and separate system/reference,
native DFND and original-comparison stages, requesting the first two now.

## How

Create `system.ipynb` and `dfnd.ipynb` in the existing case unit, sharing the
unchanged frozen JSON input. Execute them in separate clean kernels. The system
stage derives reference clearances, finite hull volume and three probe regimes
without importing TopoMT. DFND reads the committed reference, checks primitives
and raw/reported results, and explains the observations and their limits.

Use `index.md` for navigation/synthesis. Retain the old combined notebook as
`historical.ipynb` with identical bytes; preserve all original artifacts. New
reference/native reports and standalone figures use `artifacts/native_study_v1/`.
Neither notebook overwrites frozen files on a rerun.

## Why

The stages have different questions and dependencies. Independent expected
answers must precede native interpretation, and optional provider execution must
not become a dependency of geometric/native checks. Separating stages also
keeps the teaching narrative readable and supports future original comparisons.

## What was refuted

Rerunning a monolithic provider notebook is unnecessary to establish the native
observations. A presentation filter hiding a one-node component does not alter
its raw geometry. A cell's finite hull and solvent estimate do not measure the
same object. Four permeable faces are not four independently detected mouths.

## Scope and exclusions

One symmetric input and the declared nonmarginal regimes only. No kernel fix,
original-provider/server execution, new protein work, comparative superiority,
exact solvent-volume precision or general continuous-path qualification.
Keep earlier scientific receipts and their dates; #75/#76 retain broader gates.

## Acceptance criteria

- Both notebooks execute from fresh kernels using the same input and no shared
  live state. Five system and ten native code cells run with no cell errors.
- The system notebook imports no TopoMT/DFND and derives independent answers.
- Three native anchors, primitive comparisons, the 81-point sweep and a
  `min_size=2` raw-versus-reported control pass their declared assertions.
- Four reviewed PNG figures have standalone downloads matching notebook bytes;
  the structured quantity-aware reports match the displayed records.
- The historical notebook and original artifacts retain exact baseline bytes.
- Navigation, rich tables, images and downloads render; applicable tests,
  static checks and reporting lifecycle pass under their actual scope.

## Execution and reference observations

The test-first run failed four new checks because the new notebooks/records did
not exist. Execution uses the shared Python 3.14 interpreter through temporary,
explicit kernel specs; no kernel is installed into a user's profile. The sandbox
initially blocked local Jupyter sockets, so the authorized execution used the
local-socket permission route. Each notebook starts and shuts down its own kernel.

The reference and DFND residence clearance are approximately 1.545573909 Å; the
face reference is approximately 1.359956427 Å. Native maximum residence error is zero and
maximum face error is approximately 1.11e-15 Å, within the fixed 1e-6 Å
absolute tolerance. Finite hull volume agrees with 17.5453227104516 Å³ under
the fixed 1e-12 relative tolerance. The solver's solvent-volume value is still
an uncertified estimate and its precision is not adopted by these checks.

At 1.2/1.4/1.7 Å the observations are respectively percolating, void and no
resident component. Raw and reported components agree for `min_size=0`; the
explicit filter control preserves one raw void while reporting none at size 2.
The 81-point sweep adds away-from-threshold checks, not an equality-policy test.

MyST-NB's default CommonMark output renderer displayed rich Markdown table
outputs as pipe-delimited paragraphs. The new notebooks select its supported
file-level MyST output format; rendered checks require three system and six
native tables. This is presentation metadata, with no scientific code/output
change. The historical notebook retains its original metadata.

No notebook cell writes study artifacts. The authoring/execution harness captures
new reports/figures once, then preserves the committed reference for independent
reruns. The full documentation configuration keeps notebook execution off.

## Verification and delivery scope

Twenty selected independent-reference, new study-record/notebook, historical
evidence, closed-shell and reporting-protocol checks pass in the shared Python
3.14 workspace. The new checks also bind standalone PNG bytes to notebook image
outputs and reject native/provider imports from the system notebook. Ruff passes
on both changed test modules and the extracted notebook code; test formatting
and mypy pass within that selected scope.

Fresh complete `make html` builds with `-j 1 -E -a` pass on the unmodified
baseline and candidate. Both have the same twelve pre-existing warnings.
Rendered checks cover twelve pages and 333 local link/image/download targets,
including all new study pages and earlier compatibility addresses. The new
tables render as three system tables and six native tables. All four standalone
figures were visually reviewed. The historical notebook and eight original
artifacts match both the committed baseline and the recorded SHA-256 values.

Local HTML preview and compact execution/build receipts are retained by TopoMT
maintainers until the next tetrahedron study review. Disposable baseline/source
copies and inactive task-owned kernel/runtime files can be removed after source
readback. Publication identities and final checks are recorded in #134.

No kernel, dependency recipe or original-provider state changed. These notebook
receipts do not qualify the full synthetic collection, protein behavior,
installed/support matrices or a release. Full scientific/remote-CI obligations
remain with #16/#58/#81; this increment follows the authorized `[skip ci]` route.
