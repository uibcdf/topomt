# Straight tube

Can a probe travel through a tube even after its straight axis becomes blocked?
This many-cell atomic system tests continuous passage, two physical end openings
and the interpretation of graph-derived channels and paths.

**Read [the system](system.ipynb) first**, then [DFND observations](dfnd.ipynb).
Both notebooks run independently in fresh kernels from this directory. They
replay independent references and run actual public receiving without original
providers, server submissions or changes to retained evidence.
On the web, expand a code block when you want its implementation; the default
reading route keeps the explanations, tables and figures together.

```{figure} artifacts/cylinder_tube_v1/system_study.png
:alt: Atomic tube centers and a verified bent path, with separately labeled lateral displacement along z.
:width: 100%

The finite atomic input and an independently checked bent route. Marker sizes
show atomic centers, rather than the physical ball radii; all axes are Å.
```

```{toctree}
:maxdepth: 1

system
dfnd
Evidence and replay <artifacts/cylinder_tube_v1/README>
```

## The three controls

The input contains 81 argon balls (radius 1.88 Å) on nine perturbed rings.
Full-precision coordinates and explicit units define the atomic model; the
rounded PDB supplies topology only. The finite carrier is the atomic-center
convex hull, with isolated, nonperiodic exterior conditions.

| Probe | Independent reference | Initial native/public observation at `b07a20e` | Disposition |
| --- | --- | --- | --- |
| 1.2 Å | Clear axis, independently verified end-to-end path and exactly two free hull patches. | Two wet components; OpenConcavity/Mouth and Channel/two Mouth children; three native links. | Selected skeleton segments are clear; physical patch receiving remains unresolved, [#180](https://github.com/uibcdf/topomt/issues/180). |
| 1.4 Å | Axis blocked, but a bent route remains clear; exactly two free hull patches. | Same public families; physical arrangement budget exhausted. | Selected skeleton collides despite the valid independent route; general physical paths [#76](https://github.com/uibcdf/topomt/issues/76). |
| 2.5 Å | No strict-free probe center anywhere in the finite hull. | Three wet graph components; OpenConcavity/Mouth and Groove/Mouth. | Local candidate/all-atom interpretation needs diagnosis and a public qualification decision, [#181](https://github.com/uibcdf/topomt/issues/181). |

Native links, public Mouth children and physical hull patches count different
objects. The extra local finding does not establish a side-wall opening.
An unresolved physical count is unknown, rather than zero. The large-probe
discrepancy is not yet a diagnosed capacity-solver error: current local operators
use three/four obstacle atoms and do not certify the all-atom free set.

## What the references establish

The independently checked bent polyline has minimum all-atom clearance
**1.440735021 Å**, including every complete segment and both outward infinite
tails. Its 1.4 Å margin is **0.040735021 Å**. This establishes one route, without
claiming a globally optimal bottleneck. Separate complete hull certificates
prove that the lateral wall is covered and that the two strict-free patches
are at opposite ends for both smaller probes.

At 2.5 Å, a conservative nominal-grid perturbation bound covers every point
of the finite hull: the actual-atom distance bound is **4.083579632 Å**, below
the expanded radius **4.38 Å**. The unbounded exterior still exists. This is
not an ideal-cylinder volume approximation or a negative conclusion from a
failed path search.

The catalog input was already known during development. These are retrospective,
case-guided references, not a held-out evaluation panel. Original reference
attempts and their explicitly refined protocols are retained alongside the
accepted certificates.

## Current development boundary

This is a useful diagnostic unit, **not a completed tube qualification**. Stay
with its physical boundary and all-atom/public questions under #180/#181 before
adding another geometry. The [finding register](https://github.com/uibcdf/topomt/discussions/154)
maintains version-scoped conclusions; the case's original observations remain
historical evidence when later fixes arrive.

No original third-party comparison has been executed here. A subsequent
comparison needs matching atom/radius models, starting conditions, finite-carrier
versus exterior definitions and an original-execution protocol. Existing
CAVER/MOLE four-atom investigations remain #155/#156. No superiority, general
biological accuracy, optimal path, aperture area or volume-precision claim
follows from this stage.

## Download and reproduce

Download the {download}`complete source-bound tube study <../../../../_static/benchlab/cylinder_tube_v1.zip>`,
extract it and read `README_STUDY.md`. It includes both notebooks, full input,
independent reference helpers, reviewed outputs, attribution, environment inputs
and a SHA-256 manifest. The tested route uses Python 3.14 and TopoMT source
`b07a20ed0ee1533cc16a0b6e30ace73c2ab09ac4`. This is source receiving, not an
installed-release or platform-matrix claim. Source acquisition can need network
access; notebook Run All does not submit scientific inputs remotely.

The [evidence guide](artifacts/cylinder_tube_v1/README.md) explains the order of
protocol commits, retained failed attempts and resource bounds. The previously
published three-case downloads and scientific inputs remain unchanged.
