# Prepared Pocketeer source and public PharmacophoreMT receiving

Date: 2026-11-06. Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
This follows the [saved original-output reader](saved_output_checkpoint.md) and
advances the [long-term handoff plan](../provider_handoff_plan.md). It closes no
general scientific, public-release, platform/matrix or native-equivalence gate.

## Question and ownership

Can a prepared molecular source retain its atom namespace, frame, reference
state and units through original Pocketeer detection, source-bound recovery,
public PharmacophoreMT recognition/projections and native model persistence?

The integration recorder adds only orchestration. MolSysMT performs conversion,
selection, atom permutation, translation and coordinate-frame append through
its public tools. TopoMT executes/recovers the original detector and exposes
attributed membership/geometry. PharmacophoreMT performs chemical recognition,
complementation, projection construction and native model serialization.
Its essential/weight-one defaults remain consumer choices. No chemical
preparation, recognition rules, pharmacophore kernel or detector was copied.

`devtools/provider_handoff.py` extracts the existing fpocket source profile and
consumer-field comparisons into reusable TopoMT developer tools. The source
profile now calls public `molsysmt.structure.translate`; a caller-owned source
stays unchanged. Absent and present-empty state inventories remain distinct.
Legacy fpocket helper names delegate to those shared operations and its source
and consumer regressions still execute. The comparison contract covers ordered
consumer fields, original attributed measurements and 1e-12 nm geometry
tolerance; exhaustive provider-field fidelity retains #19.

## Declared receptor and recipe

The already prepared ERalpha/EST fragment is the same historical seed used in
the [fpocket consumer control](../fpocket4/pharmacophore_handoff_checkpoint.md).
It was loaded without regenerating preparation:

- Source archive: PharmacophoreMT `869cf967cba0a066e5c10e9c725b52c5272500fc`,
  `devguide/evidence/eralpha_interface_prepared_py314.h5msm.gz`.
- Compressed SHA-256:
  `ab67b64df320e1d2a12ee23f312344d207af528db69fdb6ee9bb10a10dee9b6c`.
- Verified decompressed seed SHA-256:
  `a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`.
- Historical preparation is a closed fragment 304–550 with chosen HIE/terminal
  states, inspected ARG atom naming and generated local H geometry. Its original
  [manifest](https://github.com/uibcdf/pharmacophoremt/blob/869cf967cba0a066e5c10e9c725b52c5272500fc/tests/data/eralpha_interface/manifest.json)
  retains those limits. This is not admission of a complete biological receptor.
- Seed: 4,047 atoms, 4,088 bonds, one frame and one reference state (0). Public
  MolSysMT operations interleave the atom axis and select 4,003 nonconsecutive
  protein/peptide atoms. Frame 1 is translated by `(0.3,-0.2,0.1) nm`; only
  Structures are appended, without asserting new historical interactions.

Original Pocketeer 0.4.0 runs with its original defaults; omitted options remain
owned by the detector. Its module label is `0.3.0`; metadata retains the distinct
distribution version `0.4.0`, API file digest and explicit output-unit protocol.
The qualified original source tag/commit remains
`v0.4.0` / `f59cd12fbe175ebf4c34d70405c4c41476d4cc03`.

The caller explicitly selects `pocketeer:0`, requests
`get_features(..., features=['hydrophobicity'], structure_index=1,
chemical_state=0)`, and sends that native inventory to
`from_receptor_projections`. Each source feature receives a declared +x query
displacement of **0.30 nm** and **0.15 nm** matching radius. Rank retains its
provider meaning; directions and query parameters are declared analytical
choices. Residue masks and alpha spheres are available representations rather
than exact closed regions or biological binding-site evidence.

## Measured results and executed guards

Both independent complete flows, one starting with **pm/fs/radians** before
PharmacophoreMT's first import and one with **nm/ps/radians**, passed:

- Original detection: **11 pockets**, in reported order
  `7,4,6,0,3,8,2,5,9,10,1`. The selected ID is fourth in that order.
- Selected residue membership: **408 source atoms**, role
  `pocket_residue_atoms`.
- Public consumer: **46 hydrophobic query sites**, each bound to its source atom
  at frame 1 and chemical state 0. Centers agree with the declared source
  coordinate plus `[0.30,0,0] nm`; radius is 0.15 nm, essential is true and weight
  is one, through native JSON roundtrip.
- Original JSON and masks are byte-identical across those two executions.
  Source frames and query geometry physically agree at absolute 1e-12 nm and
  zero relative tolerance. Distinct real run/source/query bytes retain their own
  hashes and provenance; no artifacts are rewritten to force equal run IDs.
- Recovery preserves the complete original Pocketeer run. Source coordinates,
  source-file bytes and recorded chemical context remain unchanged after
  consumer recognition/modeling. The active application unit policy is preserved,
  including the lazy first PharmacophoreMT import under pm/fs.

`devtools/qualify_pocketeer_handoff.py` writes `source.h5msm`, `original.zip` and
a checked `original-pocketeer-source-handoff-1` receipt. The existing
`qualify_pharmacophore_handoff` recorder admits that profile and the existing
fpocket profile. It verifies source checksum, original provider/backend/run,
frame and reference state before recognition. Pocketeer recovery uses the new
bundle reader and checks that its original run identity is unchanged.

Tests reject missing/ambiguous/boolean state context, conflicting/boolean frame,
unsupported or malformed receipts/checks, changed source bytes, conflicting run
or provider identity, unavailable/empty membership and absent pocket IDs. The
consumer also executes in a fresh process blocking imports of Pocketeer and
Biotite. Synthetic membership/receipt cases test admission; they are not fresh
detection evidence. The existing raw-3PTB chemistry guard still propagates
MolSysMT's incomplete-connectivity failure through public PharmacophoreMT tools.

Test-first: initial receiving tests reported five missing-recorder setup errors
and seven passing front-context guards. A separate malformed-receipt regression
reproduced an AttributeError before the root mapping guard was added. The
corrected shared/control selection passed **34 tests**, then the final affected
source selection passed **364 tests, five skips, 165.57 s** (369 collected).
The five skips are the existing three missing local Pocketeer mirror fixtures
and absent optional AlphaSpace2/pyCASTA packages; real original Pocketeer and
both prepared consumers executed. Thirteen standalone shared-tool cases cover
source independence, state/selection admission and changed scientific fields.
Published, CI-pinned Pytest Receptor **1.2.0** reported these runs.

Ruff lint/format passes repository-wide (443 files), scoped mypy passes four
developer modules, and distribution checks pass 18 cases plus five subtests.
The HTML documentation build succeeds with the same 12 diagnostics in other
pages, including the unavailable PlantUML executable; none concerns the edited
third-party guide. Report indexes are current.
No new runtime dependency or production module was introduced by this stage.
The human's `_version.py` edit remains unchanged.

## Actual environment and reproducible entry points

Linux/Python 3.14.7 uses the retained independent installed dependency profile,
with TopoMT imported from the source checkout. MolSysMT source remains
`00abb958fb93649131d5ce5fe5e12e90cf4900e9`; PharmacophoreMT remains
`b934471ac8ab8bdb1bd7646550ac23baeb07daa7`. Actual metadata labels include
MolSysMT `0.23.0+368.g00abb958f`, PharmacophoreMT `0.4.0+98.gb934471`,
PyUnitWizard `0.29.0+4.g9d74f0e`, ArgDigest `0.17.0`,
DepDigest `0.15.1+8.g0884f0c`, SMonitor `0.22.0+16.gccdcace` and Biotite `2.0.0`.
These are inspected source/artifact profiles, not claims of current public
provider delivery. Primary import paths and hashes are retained separately from
metadata labels; source-overlay TopoMT metadata and its preserved generated
version file do not identify the producer commit or a new installed wheel.

The bounded suite-state refresh preserved the upstream-less TopoMT branch,
clean MolSysMT/ArgDigest clones behind their remotes by 123/seven commits, and
the current clean PharmacophoreMT clone. No sibling worktree was changed.

From this source checkout in the recorded compatible environment, with the
verified historical seed and new output paths:

```bash
python -m devtools.qualify_pocketeer_handoff \
  "$TOPOMT_PREPARED_RECEPTOR" /tmp/pocketeer-handoff
python -m devtools.qualify_pharmacophore_handoff \
  /tmp/pocketeer-handoff /tmp/pocketeer-consumer \
  --pocket-id pocketeer:0 --direction 1 0 0 --distance '0.30 nm' --radius '0.15 nm'
python -m pytest --receptor=llm \
  tests/methods/pocketeer/test_pharmacophore_handoff.py \
  tests/test_provider_handoff_tools.py
```

The source/data environment variable is an explicit opt-in. When supplied, the
new real integration fixture fails for missing/shadowed original Pocketeer or a
different source hash instead of crediting a skip. The two expected ERROR lines
in the standalone log are the deliberate incompatible-source probes; both
complete positive flows return success.

Producer: `ba786b17717b94bc57b39d848068065c34991e33`, following the shared-tool
refactor `fdb5923`. All six source/test file hashes in the runtime identity
record were checked against the final producer's committed blobs. The
[archive](evidence/pocketeer_pharmacophore_20261106.zip) and
[receipt](evidence/pocketeer_pharmacophore_20261106.json) retain tests, exact
runtime origins, producer patches, the independent control script and both
complete source/bundle/query/receipt sets. Archive identity: 2,001,872 bytes,
42 members, SHA-256
`016a74b5ee1b832029d8ed86d0a6eb25b41ea3a740c3a3b801c7d787b0c5b82e`.
Every member digest was verified. Source labels, source hashes and both original
run IDs remain attached to their own execution rather than being normalized
across the two unit policies.

Task-owned raw controls remain at `/dev/shm/topomt-pocketeer-consumer-101` for
the next installed-candidate phase. The compatible scientific prefix and public
reporter overlay are retained from the preceding checkpoint; this source work
does not mutate their scientific distributions or qualify a new wheel.

## Remaining scope

An updated exact TopoMT wheel and clean installed receiving are next. The
current source control does not qualify a new installed candidate, component
support/matrix/full-suite gates, chemical preparation, binding relevance or
affinity. AlphaSpace2, pyCASTA and CASTp/CASTpFold retain the next provider work
in the long-term plan. Native equivalence and exhaustive descriptor fidelity
retain their independent owners.
