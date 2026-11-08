---
summary: Separate the closed-shell reference and native study with certified probe controls.
issue: uibcdf/topomt#144
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: medium
verification: measured
area: [dfnd, docs]
guard: tests/test_closed_shell_study.py::test_closed_shell_native_observations_match_the_certified_scope
normative:
blocked_by: []
supersedes: []
---

# Closed-shell system and native notebooks

## What

Continue BenchLab with the unchanged 72-ball shell. Preserve the old combined
notebook as history and introduce a short case index and independent system
and DFND notebooks. No provider/server execution belongs in these new stages.

## How

Freeze the protocol, original bytes and independently selected ray witness
before fresh native observation. Retain the existing 1.4 Å wall-coverage proof.
Use a 0.05 Å probe with a straight ray whose all-atom clearance exceeds 0.095 Å
as an independently certified access control. At 5 Å, a convex-combination
bound proves full coverage of the finite hull by probe-expanded atomic balls.
The old 0.2 Å triangle-coverage bound remains inconclusive, not a leak proof.

Execute system.ipynb in a fresh kernel, freeze its quantity-aware reference and
figures, then execute dfnd.ipynb in another kernel. Compare origin-containing
raw supports, exterior links and public reporting to justified claims; inspect
the original 49-point sweep and a reporting filter. Do not assert an exact
global cavity count or use an uncertified volume estimate as reference truth.

## Why

A sampled sphere and an algorithmic void label alone do not prove closure.
The original historical study provides useful evidence, but its combined live
provider code and shared kernel state are unsuitable for the new staged unit.

## What was refuted

The conservative wall certificate failing at 0.2 Å does not establish access.
The independent ray search found no certified 0.2 Å ray among its fixed
geometry-based candidates; that negative search is also inconclusive. The
successful 0.05 Å all-atom ray is a positive witness and supports only its
explicit probe/control, without proving general DFND path correctness.

## Scope and exclusions

One frozen synthetic case and reference/query extension. Historical artifacts,
tetrahedron studies, DFND kernels, external methods and environments remain
unchanged. #75/#76, full synthetic qualification, proteins and installed/matrix
gates remain owned work. This is no blanket case-closure or release claim.

## Acceptance criteria

Two independently executed notebooks, reviewed figures, dimensional reference
and observation reports, meaningful independent geometry/unit/rigid-motion and
history guards, correct navigation and a rendered documentation build. A native
contradiction with the new positive witness requires separate reproduction and
owning defect evidence; do not silently tune the reference or query to pass.

## Resolution

The historical notebook relocation is byte-for-byte (`3a784df`), and all nine
original input/report/provider/server files retain their hashes. A short
`index.md` preserves the documentation index route, with links to independent
`system.ipynb` and `dfnd.ipynb` plus the unchanged `historical.ipynb`. The
system stage has five code cells; the native stage has six. Neither new stage
runs an original provider or contacts a server, and ordinary reruns write no
artifact. Existing native/public APIs and scientific kernels are unchanged.

The declaration and frozen witness precede the new staged controls. The 1.4 Å
historical observations and existing receiving regression were already known;
this is characterization, not blind evaluation. Independent reference and
initial executed system notebook were committed at `3172ac9` before fresh native
observation. The small-probe ray clearance is 0.095285334 Å, certifying access
at 0.05 Å. The original 1.4 Å wall-coverage/free-origin certificate remains
valid, and the 5 Å enclosing-ball bound proves every finite-hull point blocked
by probe-expanded atomic balls. The 0.2 Å reference stays inconclusive.

DFND agrees at those scopes: the small-probe component reaches the exterior
(current `channel` family, 128 resident cells, ten contact clusters); the 1.4 Å
central void has 33 resident cells and zero exterior links; at 5 Å no wet
resident component remains. Contact-cluster count is not an independently
certified mouth count. The original 49-point sweep is retained, with nested
resident-cell availability checked rather than imposing monotone region counts.
At `min_size=34`, the reported void disappears while raw supports and the
physical result key stay unchanged. No native contradiction or kernel fix was
needed for these three controls.

Four standalone figures, quantity-aware reference/native records, source/software
fingerprints and an execution receipt accompany the notebooks. The final
sequential fresh-kernel replay adds folded report display and verifies exact
numerical records and all four PNG bytes against the previous executions.
The independent reference remains unchanged from its pre-native commit.

Verification: 44 selected reference, geometry, rigid-motion, unit-policy,
notebook, historical-provider and governance checks pass on shared Python
3.14.10. Ruff passes across the repository; focused mypy passes for two affected
test files. Full HTML documentation builds with the same twelve existing
warnings and no new warnings; the case overview, two new stages, historical
page, folded reports and all nine downloads are verified. Selected checks and
source execution do not qualify the full suite/matrix or an installed/public
artifact (#16/#19/#81 retain those gates). Incremental commits carry the
maintainer-requested `[skip ci]`.

The first system run took 5.35 seconds and the first native run 8.98 seconds;
the refined-layout native replay took 7.16 seconds. Each ran on one OS CPU with
6 GiB process address-space ceiling and bounded CPU/per-cell time. Maximum
observed process RSS was below 220 MiB. The final folded-display runs were
sequential and their timing/memory receipts retain units. These are technical
receipts, not a speed benchmark or resource reservation. The shared host and
Slurm were inspected; no memory pressure or active swapping was observed.

All required scientific evidence is versioned. Task-owned generators, logs and
the rendered preview remain in ignored `.cache/closed-shell-study/` for maintainer
review of this checkpoint and can be removed after that review. The redundant
copied documentation source can be removed after publication. Kernel processes
were scoped to their clients; shared environments, engine checkouts and unrelated
resources were not modified. The pre-existing version-file edit remains intact.

This resolves only the staged notebook/reference extension. The 0.2 Å
enclosure, exact global physical cavity count, solvent-volume precision #75,
full independent panel #76 and the full synthetic phase remain open at their
stated scopes. The next opening must derive from this same frozen wall, preserve
atom correspondence and obtain an independent access witness at the chosen probe.
