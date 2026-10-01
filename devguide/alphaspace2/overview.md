# AlphaSpace2 provider overview

Reviewed: 2026-10-01 (repository and issue state). Scientific evidence dates are
stated below; this organizational update does not rerun or extend that evidence.
Role: integrated provider and comparison reference. Implementation work remains
paused under the [delivery checkpoint](../provider_pocket_output_checkpoint.md).

## Identity, installation and use

Upstream: <https://github.com/RedesignScience/AlphaSpace2>. Follow upstream licensing and scientific citation
requirements; checked versions are evidence targets, not claims of latest release.

```bash
python -m pip install alphaspace2
```

The upstream Python package requires MDTraj, SciPy, Cython and configargparser. Original AlphaSpace2 0.1.2 was checked on Linux/Python 3.13; the adapter has compatibility adjustments recorded in its run evidence.

Original routes: Original Python library, with optional upstream `binder` input. Returned class: `AlphaSpace2Output`.

```python
import topomt as tmt

output = tmt.get_provider_output('protein.pdb', method='alphaspace2')
pockets = output.pockets
```

Requirements and additional options: [user installation guide](../../docs/content/user/third_party_engines.md).
The high-level original-output entry point rejects `backend='native'`; legacy
`get_topography` routes retain their defaults. No optional engine is installed
or silently substituted by this overview.

## Contract and evidence

The original adapter has installed-engine receptor/contact/occupancy comparisons. The selected native tests passed on 2026-09-30, covering alpha/beta geometry and grouping, contacts and a typed CDK2 scoring case with explicit tolerances. Broad nonpolar, typing, scoring and input coverage remains unclosed.

The [common output checkpoint](../provider_pocket_output_checkpoint.md) defines
shared pocket access, exact run evidence, units, source mapping and missing
geometry. The [viewer checkpoint](../provider_output_viewer_checkpoint.md)
records initial consumer adoption. Point/membership displays are not exact
closed pocket regions. Exhaustive original fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19), independently of native parity.

## Local implementation

`topomt.third_party.alphaspace2.native` includes alpha/beta generation, lining-atom recovery, contact propagation and a Vina-aware score route. Native typed scoring and the original adapter are distinct: the original adapter currently submits an untyped receptor and does not expose advanced Vina typing.

DFND remains the native semantic reference for public Topography admission.
See the [deferred native-method plan](../native_methods_plan.md); this profile
does not resume implementation or promise an equivalence deadline.

## Roadmap and issue history

- Complete original atom ordering and typed-receptor scoring coverage under [#19](https://github.com/uibcdf/topomt/issues/19).
- Review occupied and nonpolar volumes and occupancy definitions under [#31](https://github.com/uibcdf/topomt/issues/31), [#32](https://github.com/uibcdf/topomt/issues/32), [#33](https://github.com/uibcdf/topomt/issues/33) and [#34](https://github.com/uibcdf/topomt/issues/34).
- Broaden native nonpolar/contact/typing evidence when its separate review resumes.

Initial output delivery [#65](https://github.com/uibcdf/topomt/issues/65) and
viewer adoption [#66](https://github.com/uibcdf/topomt/issues/66) are closed
bounded outcomes, not full-provider certification.

## Detailed records and discussion

- [Original output inventory](external_output_inventory.md).
- [Native checkpoint and numerical limits](native_checkpoint.md).
- [Contract](contract.md).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.

