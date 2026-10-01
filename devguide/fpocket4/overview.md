# fpocket provider overview

Reviewed: 2026-10-01 (repository and issue state). Scientific evidence dates are
stated below; this organizational update does not rerun or extend that evidence.
Role: integrated provider and comparison reference. Implementation work remains
paused under the [delivery checkpoint](../provider_pocket_output_checkpoint.md).

## Identity, installation and use

Upstream: <https://github.com/Discngine/fpocket>. Follow upstream licensing and scientific citation
requirements; checked versions are evidence targets, not claims of latest release.

```bash
conda install -c conda-forge fpocket
```

The executable must be on PATH, or supplied as `fpocket_cmd`. The installed original CLI comparison used fpocket 4.2.3 on Linux/Python 3.13.

Original routes: CLI and persisted output files. Returned class: `FpocketOutput`.

```python
import topomt as tmt

output = tmt.get_provider_output('protein.pdb', method='fpocket')
pockets = output.pockets
```

Requirements and additional options: [user installation guide](../../docs/content/user/third_party_engines.md).
The high-level original-output entry point rejects `backend='native'`; legacy
`get_topography` routes retain their defaults. No optional engine is installed
or silently substituted by this overview.

## Contract and evidence

Original CLI, file retention and the initial viewer consumer have bounded passing evidence in the delivery checkpoints below. The native checkpoint documents historical final-pocket parity on ten structures against a specific audited source build; it is not a certificate for every binary build. That native battery was not rerun on 2026-09-30.

The [common output checkpoint](../provider_pocket_output_checkpoint.md) defines
shared pocket access, exact run evidence, units, source mapping and missing
geometry. The [viewer checkpoint](../provider_output_viewer_checkpoint.md)
records initial consumer adoption. Point/membership displays are not exact
closed pocket regions. Exhaustive original fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19), independently of native parity.

## Local implementation

`topomt.third_party.fpocket.native` reproduces an audited source workflow. `topomt.third_party.fpocket.topomt` is an intentional variant with identity `fpocket-topomt`. Keep source, binary and variant identities separate; raw tessellation differences and build-dependent final pockets remain documented.

DFND remains the native semantic reference for public Topography admission.
See the [deferred native-method plan](../native_methods_plan.md); this profile
does not resume implementation or promise an equivalence deadline.

## Roadmap and issue history

- Complete original-field, atom/sphere identity and route coverage under [#19](https://github.com/uibcdf/topomt/issues/19).
- Review independent descriptor definitions in [#20–#29](https://github.com/uibcdf/topomt/issues?q=is%3Aissue+is%3Aopen+fpocket).
- Recertify native stage/descriptor parity against pinned source/build inputs when the deferred native review resumes.

Initial output delivery [#65](https://github.com/uibcdf/topomt/issues/65) and
viewer adoption [#66](https://github.com/uibcdf/topomt/issues/66) are closed
bounded outcomes, not full-provider certification.

## Detailed records and discussion

- [Permanent fpocket discussion #69](https://github.com/uibcdf/topomt/discussions/69) in External Tools.
- [Original output inventory](external_output_inventory.md).
- [Native evidence and caveats](native_checkpoint.md).
- [Source/binary parity matrix](../native_methods_plan.md).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.
