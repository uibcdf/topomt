# Pocketeer provider overview

Reviewed: 2026-10-01 (repository and issue state). Scientific evidence dates are
stated below; this organizational update does not rerun or extend that evidence.
Role: integrated provider and comparison reference. Implementation work remains
paused under the [delivery checkpoint](../provider_pocket_output_checkpoint.md).

## Identity, installation and use

Upstream: <https://github.com/cch1999/pocketeer>. Follow upstream licensing and scientific citation
requirements; checked versions are evidence targets, not claims of latest release.

```bash
python -m pip install pocketeer
```

The original package brings its upstream requirements, including Biotite and atomview. Original Pocketeer 0.4.0 was checked on Linux/Python 3.13. The local reproduction requires Biotite for SASA but does not require Pocketeer itself.

Original routes: Original Python library. Returned class: `PocketeerOutput`.

```python
import topomt as tmt

output = tmt.get_provider_output('protein.pdb', method='pocketeer')
pockets = output.pockets
```

Requirements and additional options: [user installation guide](../../docs/content/user/third_party_engines.md).
The high-level original-output entry point rejects `backend='native'`; legacy
`get_topography` routes retain their defaults. No optional engine is installed
or silently substituted by this overview.

## Contract and evidence

Original adapter evidence includes the 6qrd/2xjx source references and installed-engine checks linked below. On 2026-09-30 the selected native test passed, but its assertions allow extra local pockets, relative volume differences below 0.6 and score differences below 2.5; centroid equality is not asserted. This is approximate evidence, not full native equivalence.

The [common output checkpoint](../provider_pocket_output_checkpoint.md) defines
shared pocket access, exact run evidence, units, source mapping and missing
geometry. The [viewer checkpoint](../provider_output_viewer_checkpoint.md)
records initial consumer adoption. Point/membership displays are not exact
closed pocket regions. Exhaustive original fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19), independently of native parity.

## Local implementation

`topomt.third_party.pocketeer.native` implements alpha spheres, SASA burial, graph grouping, a grid volume estimate and local scoring. A passing permissive comparison does not establish identical sphere membership, ordering or descriptors.

DFND remains the native semantic reference for public Topography admission.
See the [deferred native-method plan](../native_methods_plan.md); this profile
does not resume implementation or promise an equivalence deadline.

## Roadmap and issue history

- Complete original membership, selection, ordering and failure-case coverage under [#19](https://github.com/uibcdf/topomt/issues/19).
- Implement and validate per-sphere mean SASA under [#30](https://github.com/uibcdf/topomt/issues/30).
- Define a stage/field matching contract and stronger native comparisons when that review resumes.

Initial output delivery [#65](https://github.com/uibcdf/topomt/issues/65) and
viewer adoption [#66](https://github.com/uibcdf/topomt/issues/66) are closed
bounded outcomes, not full-provider certification.

## Detailed records and discussion

- [Original output inventory](external_output_inventory.md).
- [Existing native contract](../pocketeer_contract.md).
- [Native comparison assertions](../../tests/methods/pocketeer/test_parity.py).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.

