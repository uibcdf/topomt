# CASTp / CASTpFold provider overview

Reviewed: 2026-10-01 (repository and issue state). Scientific evidence dates are
stated below; this organizational update does not rerun or extend that evidence.
Role: integrated provider and comparison reference. The user resumed a bounded
local CASTp3 reconstruction under [#79](https://github.com/uibcdf/topomt/issues/79).
Broader provider work remains paused under the
[delivery checkpoint](../provider_pocket_output_checkpoint.md).

## Identity, installation and use

Upstream: <https://cfold.bme.uic.edu/castpfold/>. Follow upstream licensing and scientific citation
requirements; checked versions are evidence targets, not claims of latest release.

No original CASTp Python package is required. Server execution needs network access and a functioning service; importing persisted output needs neither an installed engine nor network. CASTp 3.0 and CASTpFold are separate server/artifact references.

The [2026-10-01 server-input audit](server_input_contract_2026_10_01.md) records
current form requirements, client discrepancies, synthetic-PDB alignment and
the two accepted CASTpFold jobs whose completion has not yet been observed.

Original routes: CASTp 3.0/CASTpFold servers and persisted archives/files. Returned class: `CASTpOutput`.

```python
import topomt as tmt

output = tmt.get_provider_output('protein.pdb', method='castp')
pockets = output.pockets
```

Requirements and additional options: [user installation guide](../../docs/content/user/third_party_engines.md).
The high-level original-output entry point rejects `backend='native'`; legacy
`get_topography` routes retain their defaults. No optional engine is installed
or silently substituted by this overview.

## Contract and evidence

Deterministic archives and mocked transports have passing parser/retention evidence;
they do not establish current live-service availability. CASTp1 has a historical
eleven-system closure with limited multi-mouth stress coverage; its generic
feature area/volume remain polyhedral. CASTp3-like native code is experimental
and has documented server discrepancies. The
[modern closed-void checkpoint](checkpoint_2026_10_01_modern_void_measurements.md)
records the first exact 2PK4 lining-atom and sixteen-measure SA/MS comparison,
rerun CAST regressions and the bounded new unit-bearing output.
The [expanded radius-profile checkpoint](checkpoint_2026_10_01_castp3_radius_profile.md)
identifies an explicit `castp3_protor` policy and extends agreement to thirteen
voids and fifty-two measures. Standard ProtOr differs in two of those voids.

The [common output checkpoint](../provider_pocket_output_checkpoint.md) defines
shared pocket access, exact run evidence, units, source mapping and missing
geometry. The [viewer checkpoint](../provider_output_viewer_checkpoint.md)
records initial consumer adoption. Point/membership displays are not exact
closed pocket regions. Exhaustive original fidelity remains under
[#19](https://github.com/uibcdf/topomt/issues/19), independently of native parity.

## Local implementation

`topomt.third_party.castp.native` implements the classical workflow.
`topomt.third_party.castp3.native` is a separate experimental CASTp3-like route.
The 2026-05-19 audit records unresolved modern-server differences. The current
target uses historical code and papers as algorithmic descriptions and pinned
modern outputs as the result oracle. It does not guarantee general equivalence.

DFND remains the native semantic reference for public Topography admission.
See the [native-method plan](../native_methods_plan.md) for the selected CASTp
exception to the deferred broader review. No equivalence deadline is promised.

## Roadmap and issue history

- Complete original archive layouts, optional atom contributions and bulb fields under [#19](https://github.com/uibcdf/topomt/issues/19).
- Validate live server availability separately and record the last successful submission/date.
- Review independent SA/MS metrics and mouth/surface definitions under [#41–#52](https://github.com/uibcdf/topomt/issues?q=is%3Aissue+is%3Aopen+CASTp).
- Retain CASTp1 historical evidence and experimental CASTp3 identity when native review resumes.

Initial output delivery [#65](https://github.com/uibcdf/topomt/issues/65) and
viewer adoption [#66](https://github.com/uibcdf/topomt/issues/66) are closed
bounded outcomes, not full-provider certification.

## Detailed records and discussion

- [Permanent CASTp / CASTpFold discussion #73](https://github.com/uibcdf/topomt/discussions/73) in External Tools.
- [Original output inventory](external_output_inventory.md).
- [Modern closed-void measurements checkpoint](checkpoint_2026_10_01_modern_void_measurements.md).
- [Modern radius profile and expanded panel](checkpoint_2026_10_01_castp3_radius_profile.md).
- [Classical functional closure](checkpoint_2026_04_23_castp1_functional_parity_closure.md).
- [CASTp3/CASTpFold reproducibility boundary](checkpoint_2026_05_19_castp3_reproducibility_boundary.md).
- [Historical fidelity contract](contract.md).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.
