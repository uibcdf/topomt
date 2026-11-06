# AlphaSpace2 provider overview

Reviewed: 2026-11-06 for the original source-context handoff. Scientific evidence dates
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
detector implementation. At that producer, explicit chemical-state arguments
were rejected. The subsequent source-context stage below adds their reference
contract rather than silently ignoring them.

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

The following source-context stage advances this handoff. Saved reconstruction,
the prepared public PharmacophoreMT consumer and the changed exact installed
candidate retain their separate next steps.
This source checkpoint does not extend previous installed-wheel receipts,
general fidelity, native parity, full-suite, matrix or public-delivery claims.

## Independent receptor/binder source context, 2026-11-06

Producer `4bb881d1d6f0f4e542dd28e0e5947f9bf066127c` accepts
`chemical_state` and `binder_chemical_state` through ArgDigest. Each selector
names its source's existing, unambiguous reference or that reference's integer
index. A binder index requires a binder. Absent/empty/ambiguous inventories and
nonreference requests fail before either export. No reference, charge or bond
is assigned or changed. The shared MolSysMT-facing context tool records each
full-source reference fingerprint; all representation, selection, persistence
and coordinate manipulation remain public MolSysMT operations.

Both submitted PDBs must uniquely cover their selected source indices, retain
unique serials and agree with the requested coordinate frame at 0.00051
angstroms absolute tolerance. The loaded MDTraj rows must agree in declared nm
units, at 0.000051 nm absolute plus four float32 epsilons relative tolerance.
These are checks of an existing ordinal map, without inferred matching or
alignment. They precede the original AlphaSpace2 import/execution. Existing
DepDigest availability checks retain their own earlier responsibility.

Each run retains `output/topomt_source_context.json` and, when bound,
`output/topomt_binder_context.json`: full source atom identities, count and
selected-frame coordinates with explicit nm units. Metadata binds their paths,
independent chemical contexts, serial maps, source index axes, frames and actual
original-distribution identity. `output_protocol` declares the snapshot's length,
volume, ratio, unspecified score and setting units. Existing original exports
and snapshot schema 1 remain intact. NumPy selection axes are encoded as JSON
lists without mutating caller arrays. Submitted row maps retain the validated
source order independently of the caller's selection order.

The first context test run fails all 19 cases. After implementation, 101 of 102
cases pass; one incorrect byte-equality assertion exposes about 1e-16 nm rounding
differences between unit policies. The corrected test reuses the established
1e-12 nm source-context comparison and retains actual captured bytes/run IDs.
No evidence is rewritten to force identical source contexts. The final context
and argument selection passes **103 tests**, including a direct comparison of
original snapshot bytes and physical pocket geometry across policies.

The affected source regression passes **429 cases, zero skips/failures,
138.00 s**, preserving fpocket/Pocketeer controls and the eight installed-original
AlphaSpace2 comparisons. Six original divide warnings in `Cluster.py` retain
undefined occupancy semantics; the focused source control reports two of them.
Invalid state selectors, unsupported references, corrupt maps, PDB coordinates,
duplicate serials, multiple models and reordered loaded rows fail before the
original execution. Valid nonzero references export existing positive/negative
PDB charges without changing source chemical inventories.

An independent recorder starts from bundled 2pk4 (PDB SHA-256
`491d6fc18883b7b3f82c8b9c85023129a7390c7120ba94eb16b199801f2ee1c1`).
Public MolSysMT operations permute/interleave its 745 source atoms and append a
second frame translated by `(0.3,-0.2,0.1) nm`. Receptor and binder each have two
explicitly duplicated analytical states: reference 1/frame 1 for the receptor,
reference 0/frame 0 for the binder. These state/coordinate controls assert no
chemical preparation or biological ligand pose. Selections contain 630 protein
atoms and nine ACA atoms, respectively, in their own source namespaces.

Under nm/ps and pm/fs policies, both complete full sources first persist to and
restore from H5MSM. Original detection then yields **61 ordered pockets** with
`min_vertices=1`. Both bundles roundtrip exactly; original snapshot JSON agrees
byte-for-byte and membership/geometries agree physically at 1e-12 nm. Application
unit policy and source chemical fingerprints are preserved. Changing the actual
caller sources after execution leaves the captured evidence unchanged. This
is source and state bookkeeping, not prepared PharmacophoreMT receiving.

Ruff passes 448 Python files, scoped mypy passes six source modules, and the 20
distribution/reporting cases pass against the unchanged 628-resource inventory.
The HTML build succeeds with the same 12 known diagnostics outside the edited
guide. Public Pytest Receptor 1.2.0 reports all pytest runs. The four original
engine-overlay distributions still pass their 479 RECORD hashes in a separate
identity probe; this is not before/after pytest instrumentation or a new
installed TopoMT claim. The retained source/dependency profile and earlier
compatibility adjustments remain those of the argument checkpoint.

The [source-context archive](evidence/alphaspace2_source_context_20261106.zip)
and [sidecar](evidence/alphaspace2_source_context_20261106.json) retain producer
files/patch, exact source identities, tests and initial failures, standalone
recorder, four full H5MSM sources and both original bundles. Archive: 823,284
bytes, 64 members, SHA-256
`cf4c3c1ba85d4d9e941d1a8716f187148789897bdf17ea25414495922a7f3933`.
All member digests are checked. Raw artifacts remain under
`/dev/shm/topomt-alphaspace2-context-101`. The human's version file and all
principal/sibling environments remain unchanged; no dependency was added.

Next: engine-free, source-bound snapshot reconstruction, then prepared public
PharmacophoreMT receiving and qualification of an exact updated installed wheel.
Native equivalence, exhaustive provider fidelity, general component gates and
public release remain outside this bounded result.

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
