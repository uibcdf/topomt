# Regular tetrahedron

Can a probe fit inside a gap while being too large to pass through its faces?
This unit studies four equal atomic balls at the vertices of a regular
tetrahedron, with edge **5.3 Å** and atomic radius **1.7 Å**. Only the probe radius
changes across the three principal experiments.

| Stage | What it explains | Current status |
| --- | --- | --- |
| [System and independent expectations](system.ipynb) | Input geometry, visualization, analytic clearance references and three predictions fixed before inspecting DFND. | Executed in a fresh kernel; independent checks pass. |
| [DFND experiments and analysis](dfnd.ipynb) | Primitive errors, the three probes, raw versus reported results, exterior grouping, a probe sweep and volume limits. | Executed in another fresh kernel; declared checks pass. |
| [Original-method comparisons](comparisons.ipynb) | Atomic-model audit, original results, diagnostics and spatial interpretation. | Executed independently from retained evidence; earlier observations remain historical. |

```{toctree}
:maxdepth: 1

system
dfnd
comparisons
Comparison evidence <artifacts/comparisons_v1/README>
Historical combined record <historical>
```

## The three experiments

| Probe radius | Geometry predicts | Current DFND observation |
| --- | --- | --- |
| 1.2 Å | Room inside and through all four faces. | One fully open (`percolating`) component; four permeable faces grouped into one exterior link. |
| 1.4 Å | Room inside, with all faces sealed to this probe. | One `void` component without an exterior link. |
| 1.7 Å | No room for this probe inside the finite cell. | No resident wet component; the tetrahedron itself still exists. |

The independent face and residence clearances are approximately **1.359956 Å**
and **1.545574 Å**. Their different values explain the intermediate sealed regime.
The complete notebook reports retain full precision, units, tolerances and input
checksums.

This control supports the declared symmetric clearances and nonmarginal query
regimes. It does not certify solvent-volume precision, general continuous probe
navigation or biological pocket accuracy. An exterior-link cluster is distinct
from a collection of independently identified physical mouths. Report filtering
also changes what is displayed without changing the raw geometry.

## Inputs, results and reproducibility

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
