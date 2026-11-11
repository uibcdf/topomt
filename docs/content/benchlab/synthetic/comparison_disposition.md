# Which comparisons are justified here?

The three systems now have independent geometric and numerical references.
Agreement with a detector is useful characterization, but it cannot replace
those references. This checkpoint reuses retained **original executions** and
keeps a failed run, a completed empty output and an ineligible observable distinct.
No new local detector execution is selected for this checkpoint.

## What the existing evidence says

| Tool / question | Regular tetrahedron | Closed shell | Opened shell | Disposition |
| --- | --- | --- | --- | --- |
| Pocketeer pocket detection | Retained completed empty result | Retained one pocket | Not executed | Describe its detector/voxel semantics; no assertion about physical patch counts. |
| AlphaSpace2 alpha-space pockets | Retained execution failure | Retained one pocket | Not executed | Alpha-space volume is distinct from the frozen carrier integrals. |
| fpocket / pyCASTA | Retained failures | Retained failures | Not executed | No accepted pocket counts; molecular smoke evidence has a separate scope. |
| pyKVFinder dual-probe grid cavities | Completed standard and separately declared positive-cutoff diagnostic; invalid zero-cutoff exports retained | No matched execution selected | No matched execution selected | Eligibility and grid/operator audit remain [#158](https://github.com/uibcdf/topomt/issues/158). |
| GHECOM morphological grid pockets | Retained original outputs and effective-radius audit | No matched execution selected | No matched execution selected | Its 1.87 Å atomic radius changes the equal-ball reference; no same-label accuracy ranking. |
| CAVER origin-to-surface tunnels | Retained four-atom execution failure | No matched execution selected | No matched execution selected | Tiny-input/origin/shell applicability remains [#155](https://github.com/uibcdf/topomt/issues/155). |
| MOLE channels/cavities | Retained four-atom complex failure | No matched execution selected | No matched execution selected | Tiny-input cause/scope remains [#156](https://github.com/uibcdf/topomt/issues/156). |
| CASTpFold remote results | Existing receipt; current result retrieval unavailable | Existing receipt; current result retrieval unavailable | No job submitted | Retained-job disposition remains [#168](https://github.com/uibcdf/topomt/issues/168); no replacement upload. |
| POVME / MoloVol / PyVOL volume candidates | Not selected as this study's reference | Not selected | Not selected | Acquisition/licence and observable review remains [#159](https://github.com/uibcdf/topomt/issues/159). |

The original tetrahedron [comparison notebook](regular_tetrahedron/comparisons.ipynb),
[artifact guide](regular_tetrahedron/artifacts/comparisons_v1/README.md) and
[effective atomic models](regular_tetrahedron/atomic_models.md) retain inputs,
versions, output states and definitions. The closed shell's
{download}`historical report <closed_shell/artifacts/closed_shell_v1/report.json>`
and [historical notebook](closed_shell/historical.ipynb) retain its original
Pocketeer/AlphaSpace2 observations and failed runs. These have not been rerun
or requalified by the current DFND changes.

## Why the pending work is kept separate

Reading CAVER's retained bundle reveals an original warning that its starting
point is outside the configured search region, followed by absent tunnel output.
Its settings include a 0.9 Å probe, shell radius 3 Å and shell depth 4 Å. This
is a concrete configuration/applicability lead, **not a zero-tunnel verdict**
or a diagnosis that four atoms are always unsupported. Its original atom reader
assigns 1.70 Å to these rows; reader success does not establish detector success.

MOLE reads four atoms/four residues and fails during complex construction with
an object-reference error. The recorded defaults include surface probe radius
3 Å, interior threshold 1.25 Å and bottleneck radius 1.25 Å. None can silently
be treated as DFND's query. The maintained original source reference is clean
at `sb-ncbr/webchemistry@fe0e84582a6bd42bc69224fd3a3022bf5c51cec3`;
its successful molecular controls do not establish tiny-input applicability.
The legacy MOLE tree remains a separate reference.

Both finding cards remain **`needs_review`** under their open issues. A new
bounded execution would first need a supported input/operator/origin question
and frozen protocol. No inference of DFND superiority follows from these failures.

Grid comparisons need matched input selection, effective radii, PDB coordinate
rounding, inner/outer probes, morphological operators, finite domain, spacing,
orientation and cutoff/export settings. Current pyKVFinder consultation trees
were inspected without updating them: upstream `20add3537319ffd11e5e660a9181dd986651e928`
and compatibility fork `e0f0fa6d32109ebd02d951ef4d7f84f3e1a88fb9`, both clean.
This inspection does not qualify a new version or execute a detector.
The broader LIGSITE and volume-candidate reviews remain open; a wrapper licence
alone does not qualify every backend's no-payment acquisition route.

For the present volume question we instead use explicit tetrahedron supports,
an analytic control, independent Cartesian integration and a paired common-hull
cap-deletion reference. These satisfy the [declared volume study](volume_measurements.md)
without importing a third party's differently defined region as truth.
No unreviewed candidate is presented as a supported free engine.

## Existing server receipts

A bounded recovery on **2026-11-11 UTC** requested each original result URL
once, with a 15-second timeout and an 8 MiB response ceiling. Both returned
HTTP 200 with the same **713-byte `text/html` response, not a ZIP**. The dated
receipt is retained under #168. Pocket counts remain unavailable; this does not
establish permanent expiry, successful calculation or an empty result.
No coordinates were submitted and no new jobs were created. Another recovery
is useful if the service recovers or an original archive becomes available;
repeated polling is not part of Run All.

## What this permits next

The current checkpoint admits independent native-method development on the next
synthetic question without waiting for unrelated provider investigations.
It does **not** admit an accuracy/performance ranking, a demonstrated advantage,
a general third-party limitation or a paper claim from the pending comparisons.
The [comparative-findings hub](https://github.com/uibcdf/topomt/discussions/154)
keeps current state and dated history separate. Every remaining concrete review
above has an open issue; a later selected execution needs its own fixed protocol
and real completion/attribution evidence.
