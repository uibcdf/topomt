# Regular tetrahedron

Can a probe fit inside a gap but fail to pass through its faces? Four equal
atomic balls separate residence from access as we change only the probe radius.

**Start here:** [current public study v2](public_topography_v2.ipynb), then use
[the system](system.ipynb) and [original DFND study](dfnd.ipynb) for their
frozen predictions and dated observations. The [complete v2 download](../index.md#download-and-run-the-current-reader-stage)
includes the parent, independent checkers and declared source environment.

```{figure} artifacts/native_study_v1/system_geometry.png
:alt: Atomic-ball geometry of the unchanged regular tetrahedron input.
:width: 75%

The frozen atomic-ball input; full-precision quantities, source mapping and
probe-specific reference statements are retained in the system stage.
```

## Current observations

| Question / probe | Independent expectation | Native / public observation | Current conclusion / owner |
| --- | --- | --- | --- |
| Access, 1.2 Å | Four disconnected hull patches, all reached from the centroid. | One face cluster; `Percolating`, zero `Mouth` children. | Separate physical view resolves four; native/Mouth compatibility retained; [#151](https://github.com/uibcdf/topomt/issues/151). |
| Enclosure, 1.4 Å | Free centroid, completely covered hull. | One `Void`, no exterior link or `Mouth`. | Enclosure qualified; general paths [#76](https://github.com/uibcdf/topomt/issues/76). |
| Exclusion, 1.7 Å | No free center in the finite hull. | No resident wet component or public feature. | Genuine empty resident result; [conditional volume receiving](../volume_measurements.md) uses the smaller-probe finite supports. |

The [public support and robustness continuation](../public_support_and_robustness.md)
recovers resident/connector supports, dry banks, coast relations, depth context
and source identities on this same input. Its availability table separates native
proxies, physical certificates and broader public/interface work.

Can a probe fit inside a gap while being too large to pass through its faces?
This unit studies four equal atomic balls at the vertices of a regular
tetrahedron, with edge **5.3 Å** and atomic radius **1.7 Å**. Only the probe radius
changes across the three principal experiments.

The method section supplies a
[complete input-to-Topography reading](../../../dfnd/worked_tetrahedron.md)
of this same frozen system, with definitions and source-support inspection.

The [earlier reader v1](public_topography.ipynb) is retained with its original
source/date. The current v2 stage independently reruns public, physical,
support and conditional-volume receiving without overwriting original evidence.

Download the complete study bundle from the [synthetic collection](../index.md#download-and-run-the-current-reader-stage),
including inputs, the parent shell, reference helpers and environment guidance.

**Volume continuation — 2026-11-10:** [matched independent and public measurements](../volume_measurements.md)
now distinguish carrier, bare empty and probe-center volumes, with conditional
intervals, convergence/error states and recoverable support. The #75 source
correction is `b7b5a60`; it does not make the fast local stencil an exact integral
or qualify every installed release. Earlier frozen notebook values keep their
original date/source. Wider model/support qualification remains #76.

| Stage | What it explains | Current status |
| --- | --- | --- |
| [System and independent expectations](system.ipynb) | Input geometry, visualization, analytic clearance references and three predictions fixed before inspecting DFND. | Executed in a fresh kernel; independent checks pass. |
| [DFND experiments and analysis](dfnd.ipynb) | Primitive errors, the three probes, raw versus reported results, exterior grouping, a probe sweep and volume limits. | Executed in another fresh kernel; declared checks pass. |
| [Original-method comparisons](comparisons.ipynb) | Atomic-model audit, original results, diagnostics and spatial interpretation. | Executed independently from retained evidence; earlier observations remain historical. |

```{toctree}
:maxdepth: 1

Current public study v2 <public_topography_v2>
Reader v1 (historical) <public_topography>
system
dfnd
comparisons
Public Topography receiving <topography>
Four boundary openings <boundary_connectivity>
Effective atomic models <atomic_models>
Comparison evidence <artifacts/comparisons_v1/README>
Historical combined record <historical>
```

## The three experiments

| Probe radius | Geometry predicts | Current DFND observation |
| --- | --- | --- |
| 1.2 Å | Room inside and through all four faces. | One native `percolating` component; four admitted faces grouped into one exterior link. |
| 1.4 Å | Room inside, with all faces sealed to this probe. | One `void` component without an exterior link. |
| 1.7 Å | No room for this probe inside the finite cell. | No resident wet component; the tetrahedron itself still exists. |

The independent face and residence clearances are approximately **1.359956 Å**
and **1.545574 Å**. Their different values explain the intermediate sealed regime.
The complete notebook reports retain full precision, units, tolerances and input
checksums.

This control supports the declared symmetric clearances and nonmarginal query
regimes. It does not certify solvent-volume precision, general continuous probe
navigation or biological pocket accuracy. An exterior-link cluster is distinct
from a collection of independently identified physical mouths. The new
[boundary-connectivity certificate](boundary_connectivity.md) establishes four
separate hull patches at 1.2 Å, while the current native result has one face
cluster and the public `Percolating` has no `Mouth` children. This identifies
physical-refinement work; it does not change the historical results. Report filtering
also changes what is displayed without changing the raw geometry.

## Inputs, results and reproducibility

The [public receiving audit](topography.md) now follows these same controls
through `get_topography(method='dfnd')`, checking the actual registry, Python
types, classification and source correspondence rather than raw output alone.

Both notebooks read the same
{download}`frozen quantity-aware input <artifacts/regular_tetrahedron_v1/input.json>`.
DFND reads the committed
{download}`independent reference <artifacts/native_study_v1/system_reference.json>`;
it does not require executing `system.ipynb` first or sharing kernel state.
The reviewed
{download}`DFND observations <artifacts/native_study_v1/dfnd_observations.json>`
record the actual software and source identities. Reruns display new observations
in memory without replacing frozen artifacts. The separate comparison notebook
also runs independently, verifies the retained original evidence and reconstructs
accepted results without an original executable or server request.

Standalone figures: {download}`system geometry <artifacts/native_study_v1/system_geometry.png>`,
{download}`independent regimes <artifacts/native_study_v1/system_thresholds.png>`,
{download}`three DFND probes <artifacts/native_study_v1/dfnd_probes.png>` and
{download}`DFND sweep <artifacts/native_study_v1/dfnd_sweep.png>`.

The [historical combined notebook](historical.ipynb), its old report and original
provider evidence retain their original bytes and dates. It includes optional
provider execution code and is retained for reading earlier observations; it is
not the execution route for the new system/native studies. Its comparisons have
not been rerun or requalified by this split.

The [comparison stage](comparisons.ipynb) adds a separately frozen protocol and
new pyKVFinder/GHECOM/CAVER/MOLE observations. Atomic radii differ from the native
reference; successful output, invalid files and original failures remain distinct.
An explicitly declared positive-cutoff diagnostic follows pyKVFinder's failed
zero-cutoff controls. Raw inputs, bundles, receipts, two figures and a
{download}`quantity-aware report <artifacts/comparisons_v1/comparison_report.json>`
are retained under `artifacts/comparisons_v1/`. The
[artifact guide](artifacts/comparisons_v1/README.md) explains original execution
and evidence history. This is characterization, without an accuracy ranking.

The [effective-radius follow-up](atomic_models.md) resolves the assignments that
were still unknown at the comparison checkpoint: GHECOM uses 1.87 Å and CAVER
uses 1.70 Å for these four carbon rows. A separate atom-name-alignment control
leaves both assignments unchanged. This changes the independent probe regimes
for GHECOM's atomic-ball model, without revising earlier observed outputs.

See the [current comparator disposition](../comparison_disposition.md) for retained
original results, unmatched observables and issue-owned eligibility work.

## Physical implementation and retained receiving

**Physical source increment — 2026-11-10:** the bounded DFND record now
computes separate hull patches and path-supported contacts. The independent
five-row panel gives tetrahedron 4/0/0 at 1.2/1.4/1.7 Å, closed shell zero at
0.2 Å and opened shell one at 1.4 Å. Native links, public classes and Mouth
promotion are preserved. The [method chapter](../../../dfnd/exterior_and_boundaries.md)
explains recovery and unresolved availability; wider path/geometry qualification
remains [#76](https://github.com/uibcdf/topomt/issues/76). Earlier versioned
reader outputs retain their source/date; they do not establish a present absence
of this capability. The fixing source is `4fc2353`.

Formal source receiving: {download}`protocol <artifacts/physical_refinement_v1/protocol.json>`
and {download}`complete physical observations <artifacts/physical_refinement_v1/observations.json>`.
These records are fixed-unit nm evidence with explicit schema, source context,
clipped support and attribution; they are not a saved Topography interchange API.

The [finite three-case acceptance](../three_case_disposition.md) records what
these controls establish and the explicit boundaries for the next study.
