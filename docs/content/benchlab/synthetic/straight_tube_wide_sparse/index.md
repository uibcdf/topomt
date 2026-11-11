# Straight tube: wide, sparse sampling

Can a wall made from separate atomic balls enclose a clear passage without
leaking through its sides? This wider companion to the narrow tube lets us
separate a successful channel observation from incomplete physical-boundary
receiving and the limits of local candidates.

**Start with [the system](system.ipynb)**, then read [DFND observations](dfnd.ipynb).
The notebooks run independently in fresh kernels. The website keeps long code
inputs expandable, with explanations, tables and figures visible by default.

```{figure} artifacts/straight_tube_wide_sparse_v1/system_study.png
:alt: The 77 atomic centers around a verified axial route, and all-atom clearance along that axis compared with three probe radii.
:width: 100%

The fixed input and its independent passage reference. Markers denote atomic
centers; the continuous reference checks complete segments, not plotted samples.
```

```{toctree}
:maxdepth: 1

system
dfnd
Evidence and replay <artifacts/straight_tube_wide_sparse_v1/README>
```

## Three controls on one fixed input

The model has **77 argon balls**, each of radius 1.88 Å, on seven perturbed
rings. The nominal ring radius is 6 Å, the length is 20 Å and the nominal sampling
parameter is 3.5 Å. Full-precision coordinates define the geometry; the rounded
PDB supplies topology. The carrier is the atomic-center convex hull, with
isolated, nonperiodic exterior conditions.

| Probe | Independent reference | Actual native/public observation | Interpretation and owner |
| --- | --- | --- | --- |
| 1.4 Å | Clear axial route, covered lateral wall, exactly two free end patches. | Six wet components, seven native links, six other public objects and seven Mouth children. The global physical count is two; the Channel's two contacts resolve. | Selected native interior skeleton is clear. Ten associations for other local candidates remain unknown; wider paths #76 and support diagnosis #181. |
| 2.5 Å | Same clear route and exactly two end patches. | Nine wet components, ten links, eight other public objects and eight Mouth children. Physical count is unknown: critical-section ordering lies within the numerical margin. | Selected native interior skeleton is clear; boundary availability remains [#184](https://github.com/uibcdf/topomt/issues/184). |
| 5 Å | Every point in the finite hull is covered by expanded balls. | One wet component and an OpenConcavity/Mouth pair; physical arrangement budget exhausted. | Budget [#180](https://github.com/uibcdf/topomt/issues/180); local versus all-atom/public qualification [#181](https://github.com/uibcdf/topomt/issues/181), `needs_review`. |

These are the observed profiles, rather than a claim of complete qualification.
Original executions and the clean-source reader retain separate source/version
identities in the [evidence guide](artifacts/straight_tube_wide_sparse_v1/README.md).
Native links, Mouth children and physical hull patches count different objects.
An unknown count is never interpreted as zero. Additional local candidates do
not establish side-wall openings or additional physical three-dimensional regions.

## What is independently established

The entire axis has minimum all-atom clearance **3.906596981 Å**, including all
segments and both outward infinite tails. Complete hull certificates prove
68 lateral triangles covered and resolve the 18 end triangles: exactly two
strict-free end patches at both smaller probes. At 5 Å, a sufficient whole-hull
distance bound of **6.594243009 Å** is below the expanded radius **6.88 Å**.
The finite carrier is empty of strict-free centers; unbounded exterior persists.

The two selected native interior skeletons have minimum all-atom clearance
**3.607542780 Å**. Both are clear for their respective probes, while their
original native collision-validation flag remains false. Their segment checks
and the independently certified end-to-infinity axis have different scopes.
The 1.4 Å Channel also retains checked physical attachment paths and exterior
rays; the other local candidates do not acquire that qualification automatically.

## Compare the two tubes

| Property | Narrow, dense sampling | Wide, sparse sampling |
| --- | --- | --- |
| Frozen input | [81 balls](../straight_tube_narrow_dense/index.md), nominal radius 3.5 Å, nominal sampling 2.5 Å | 77 balls, nominal radius 6 Å, nominal sampling 3.5 Å |
| Shared 1.4 Å probe | Axis blocked; a bent path is certified. Native skeleton collides; physical count unknown. | Axis clear; native interior skeleton clear. Two global physical patches and Channel contacts resolved; other associations unknown. |
| Shared 2.5 Å probe | Whole finite hull covered; local/public candidates survive. | Clear axis and two independent end patches. Native skeleton clear, physical count numerically unresolved. |
| Larger exclusion control | 2.5 Å, cover margin 0.296420368 Å | 5 Å, cover margin 0.285756991 Å |

This pair exposes different physical regimes at the same probe sizes. **Both
radius and sampling change**, so it cannot isolate a sampling-density effect.
A nominally sparse wall can still be completely covered by expanded atomic
balls. Neither input is an ideal smooth cylinder, and neither study establishes
all free-volume component counts, exact volume, aperture area or an optimal path.

## Download and reproduce

Download the {download}`complete wide-tube study <../../../../_static/benchlab/straight_tube_wide_sparse_v1.zip>`,
extract it and follow `README_STUDY.md`. It includes both notebooks, full input,
independent reference helpers, original observations, attribution, environment
inputs and a per-file SHA-256 manifest. Run All uses the specified TopoMT source
revision, writes no retained evidence and makes no original-provider/server call.
Source/environment acquisition can need network access. This is source-bound
receiving, rather than installed-release or platform-matrix qualification.

The existing input was known during development. This is a retrospective,
case-guided study, not a blind benchmark. No original third-party comparison has
been executed for either tube; a later comparison needs eligible matched inputs
and explicit path, carrier, radius and exterior definitions. No general
superiority or biological-accuracy claim follows.

## Development follow-up

The [finding register](https://github.com/uibcdf/topomt/discussions/154) maintains
current version-scoped conclusions. The establishment of this unit is #183;
scientific questions remain with #180, #181, #184 and the wider path work #76.
The earlier narrow-tube findings remain open. Future corrections must add a
linked current interpretation while preserving these original observations.
