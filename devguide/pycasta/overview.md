# pyCASTA provider overview

Reviewed: 2026-10-01 (repository and issue state). Scientific evidence dates are
stated below; this organizational update does not rerun or extend that evidence.
Role: integrated provider and comparison reference. Implementation work remains
paused under the [delivery checkpoint](../provider_pocket_output_checkpoint.md).

## Identity, installation and use

Upstream: <https://github.com/giorgioluciano/pycasta>. Follow upstream licensing and scientific citation
requirements; checked versions are evidence targets, not claims of latest release.

```bash
python -m pip install pycasta biopandas colorama
```

Published pyCASTA 1.0.8 omits the Biopandas and Colorama runtime requirements in its package metadata. The original adapter was checked on Linux/Python 3.13 and runs the installed scripts in an isolated subprocess. Optional upstream mesh/SASA validation has additional requirements; absence of `rtree` is not demonstrated to cause the native count regression.

Original routes: Original Python library/scripts. Returned class: `PyCASTAOutput`.

```python
import topomt as tmt

output = tmt.get_provider_output('protein.pdb', method='pycasta')
pockets = output.pockets
```

Requirements and additional options: [user installation guide](../../docs/content/user/third_party_engines.md).
The high-level original-output entry point rejects `backend='native'`; legacy
`get_topography` routes retain their defaults. No optional engine is installed
or silently substituted by this overview.

## Contract and evidence

Original library comparisons and run retention have bounded passing evidence. Native comparison on 2026-09-30 reproduced [#53](https://github.com/uibcdf/topomt/issues/53): `1a6w` yields three local pockets and four upstream pockets (tetrahedron counts 77, 74, 92, 8). Across the selected Pocketeer/AlphaSpace2/pyCASTA modules, 25 tests passed and this one failed in 169.95 seconds.

The [common output checkpoint](../provider_pocket_output_checkpoint.md) defines
shared pocket access, exact run evidence, units, source mapping and missing
geometry. The [viewer checkpoint](../provider_output_viewer_checkpoint.md)
records initial consumer adoption. Point/membership displays are not exact
closed pocket regions. Exhaustive original fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19), independently of native parity.

## Local implementation

`topomt.third_party.pycasta.native` implements the reproducible repository core, not all stronger claims in the paper. Its legacy Pocket adapter uses volume as score and bare center/volume values; descriptor identity and quantity boundaries need review before broader native acceptance. The original adapter score correction in #35 does not certify this local route.

DFND remains the native semantic reference for public Topography admission.
See the [deferred native-method plan](../native_methods_plan.md); this profile
does not resume implementation or promise an equivalence deadline.

## Roadmap and issue history

- Restore the demonstrated native count/membership/volume parity under [#53](https://github.com/uibcdf/topomt/issues/53), without weakening the oracle or assertion.
- Review independent ranking [#36](https://github.com/uibcdf/topomt/issues/36), depth [#37](https://github.com/uibcdf/topomt/issues/37), mouth area [#38](https://github.com/uibcdf/topomt/issues/38), mouth perimeter [#39](https://github.com/uibcdf/topomt/issues/39) and representative point [#40](https://github.com/uibcdf/topomt/issues/40).
- Complete original index-space, configuration and optional validation coverage under [#19](https://github.com/uibcdf/topomt/issues/19).
- Preserve [#35](https://github.com/uibcdf/topomt/issues/35) as resolved original-adapter score history.

Initial output delivery [#65](https://github.com/uibcdf/topomt/issues/65) and
viewer adoption [#66](https://github.com/uibcdf/topomt/issues/66) are closed
bounded outcomes, not full-provider certification.

## Detailed records and discussion

- [Original output inventory](external_output_inventory.md).
- [Native contract and repository/paper distinction](contract.md).
- [Native adapter](../../topomt/third_party/pycasta/native.py).
- [Native parity regression](../../tests/methods/pycasta/test_parity.py).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.

