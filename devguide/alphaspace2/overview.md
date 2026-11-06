# AlphaSpace2 provider overview

Reviewed: 2026-11-06 for the original argument handoff. Scientific evidence dates
are stated below; the historical native evidence retains its own scope.
Role: integrated provider and comparison reference. Original receiving work is
active under [#101](https://github.com/uibcdf/topomt/issues/101) and the
[provider handoff plan](../provider_handoff_plan.md); native work retains the
separate [delivery checkpoint](../provider_pocket_output_checkpoint.md).

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

## Original argument handoff, 2026-11-06

Producer `3e86d1b2adec16683b5b74bb4666781f276412f2` adds both ArgDigest axes
to the original library adapter and its public gateways. The original-output
domain follows the closed library signature; unknown option names are rejected
before delegation. Native options still belong to their own route, whose
default remains unchanged. Invalid original counts, selections, syntax names,
frame axes and source-import paths fail before optional dependency or molecular
work. Literal booleans are required for the internal bypass. NumPy integer
counts become Python integers, while caller-owned molecular objects and valid
index arrays retain their identity and contents.

Receptor and binder axes share the existing external-provider value admission,
with errors naming their respective argument. Source-dependent selection and
molecular-form conversion remain public MolSysMT operations. The source-import
root validator is extracted from Pocketeer's existing contract, preserving its
registry entry, instead of introducing another provider's path rules. This
stage introduces no molecular preparation, recognition, pharmacophore model or
detector implementation. Explicit chemical-state arguments remain unsupported
until the source-context stage; they are rejected rather than silently ignored.

The initial 70-case test run reports 67 failures and three passing native
delegation cases. One failure is the normalization probe's unavailable MDTraj;
the other failures expose absent argument admission or auditable plans. The
corrected contract passes all **70 cases** with original dependencies available.
A fresh process blocks both AlphaSpace2 and MDTraj to verify that invalid
arguments do not attempt either import. The final **78-case AlphaSpace2
selection** also passes its eight original-engine receptor, binder, occupancy,
empty-selection and displaced-frame comparisons. No local source mirror is
needed by that designated original-engine selection.

The wider affected source selection passes **396 cases, zero skips/failures,
123.03 s**. This includes the earlier fpocket and Pocketeer source/consumer
regressions after the common validator extraction. Both it and the final
78-case selection retain four RuntimeWarnings from original `Cluster.py:268`:
undefined nonpolar occupancy ratios keep their NaN semantics. These are not
replaced with zero. Original definitions retain their #33/#34 ownership.

The measured Linux/Python 3.14.7 profile uses original AlphaSpace2 **0.1.2**
built from its public source archive, MDTraj **1.11.1**, Cython **3.2.6** and
configargparser **0.0.2** in a separate temporary package overlay. All four
downloaded artifacts match PyPI's SHA-256 records, and all 12 original Python
files in the built AlphaSpace2 wheel match the source archive. The previously
documented NumPy, MDTraj SASA and unbound-contact compatibility adjustments
remain explicit parts of the adapter/reference profile. The four overlay
distributions pass 479 RECORD checks in a separate identity probe; this is not
before/after instrumentation of the pytest process. Other scientific dependencies
come from the retained independent receiving prefix. TopoMT itself runs from
this source checkout; metadata labels alone do not identify its producer.

Ruff passes across 447 Python files, scoped mypy passes seven source modules,
and the 20 administrative distribution/reporting cases pass with setuptools in
an isolated tool overlay. An initial administrative run lacked setuptools; its
failure and the corrected runner are retained without changing the scientific
prefix. The three new runtime modules are included in the 628-file resource
inventory. The fresh HTML documentation build succeeds with the same 12 known
diagnostics outside the edited guide, including unavailable PlantUML. Published
Pytest Receptor 1.2.0 reports every pytest run. The human's version edit remains
unchanged, and no dependency declaration or principal/sibling environment changes.

The [argument archive](evidence/alphaspace2_arguments_20261106.zip) and
[sidecar](evidence/alphaspace2_arguments_20261106.json) retain the producer,
source/test support, original inputs, public artifact hashes, identity probe,
two original bound-result bundles, commands/logs, initial failures and executed
outcomes. Archive: 542,302 bytes, 73 members, SHA-256
`9fbf9751f2f48bb165630c38d304caf1ecf7eab87b5817a9a5dd444a38b7dcf4`.
Every member digest is verified. Raw resources remain under
`/dev/shm/topomt-alphaspace2-101` for the next phase.

Next: bind receptor and binder reference-state/source evidence, reconstruct
saved results without the original engine, exercise the prepared public
PharmacophoreMT consumer and qualify the changed exact installed candidate.
This source checkpoint does not extend previous installed-wheel receipts,
general fidelity, native parity, full-suite, matrix or public-delivery claims.

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

- [Permanent AlphaSpace2 discussion #71](https://github.com/uibcdf/topomt/discussions/71) in External Tools.
- [Original output inventory](external_output_inventory.md).
- [Native checkpoint and numerical limits](native_checkpoint.md).
- [Contract](contract.md).
- [External-tool catalogue and stewardship](../external_tools_catalog.md).

Update this overview when installation, routes, evidence or issue state changes.
Keep detailed measurements in the linked inventories/checkpoints and public
work state in its owning issue; do not replace history with an unqualified green status.
