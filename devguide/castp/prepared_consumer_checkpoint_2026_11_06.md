# Prepared CASTpFold consumer — 2026-11-06 local / 2026-11-07 UTC

Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101). This checkpoint
extends the [original-file source binding](source_binding_checkpoint_2026_11_06.md)
and [live processed-PDB diagnostic](live_server_checkpoint_2026_11_06.md) to an
explicit prepared-receptor profile. Exact installed qualification, exhaustive
provider fidelity (#19) and component/full-matrix evidence (#16/#58) remain
separate gates. No native CASTp implementation substitutes for the original.

## Declared source and submission profile

The unchanged prepared seed has SHA-256
`a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`:
4047 atoms, 4088 bonds, one frame and one reference chemical state at index 0.
Public MolSysMT tools permute the complete source and add translated frame 1,
as in the preceding four-provider receiving controls. No chemistry is repaired
or regenerated. Full-source hydrogens remain available to PharmacophoreMT.

An all-protein PDB preflight fails strict row identity: 2028 hydrogen names have
five characters, whereas PDB atom names have four columns. This failed export
is retained. Before submitting or seeing another CASTpFold result, the pilot
explicitly selects **1975 protein heavy atoms**, excluding hydrogen atoms from
the submitted PDB while preserving all 4047 source atoms. This is a declared
subset for this control, not equivalence with an all-hydrogen calculation.
The heavy export preserves names, residues, chains, elements, unique serials
and coordinates; its nonconsecutive indices retain a known map to the full
source. The maximum coordinate difference is `1.42e-14` angstroms.

The submitted heavy PDB is 194392 bytes, SHA-256
`4394a721e92593ce6ecd2aba4a675234869b91704616d8559255d34ce844ff25`.
Its preflight predecessor has SHA-256
`d5c2a591dce388eaf882db8a570294a7d1208121f1cd4b37a16d192630217912`;
only the exporter timestamp in its REMARK differs. Submitted bytes are retained
unchanged; coordinates and atom rows are identical.
The persisted two-frame full source is 3584591 bytes, SHA-256
`c967e3f15cdb5a5401ab016588aa1cf886675083ab750ea8fbd0008eabff8580`.
The original service parameters are probe 1.4 angstroms and email `N/A`.

Public MolSysMT readiness diagnostics retain 167 absent numeric `bond_order`
values on explicitly aromatic covalent bonds. Its effective multiplicity is
present; no numeric values are filled locally. The 24 selected atom-ID warnings
are labels duplicated against excluded nonprotein atoms, not duplicate source
indices or export serials. These diagnostics do not certify general chemical
preparation. Public `pharmacophoremt.modeler.get_features` successfully recognizes
429 hydrophobic features on the complete source before any pocket selection.

The controlled source environment uses MolSysMT `00abb958fb93649131d5ce5fe5e12e90cf4900e9`
and PharmacophoreMT `b934471ac8ab8bdb1bd7646550ac23baeb07daa7`, with exact retained
dependency wheels identified in the [pyCASTA checkpoint](../pycasta/installed_receiving_checkpoint.md).
These pins do not establish a public-only dependency route or qualify the older
TopoMT wheel installed in that prefix. Current TopoMT source is loaded explicitly.
The working development environment is unchanged.

Both full-source frames retain the crystallographic box, in nm:
`[[10.55, 0, 0], [-5.275, 9.136568, 0], [0, 0, 13.608]]`.
The analytical projections use Cartesian coordinates without periodic imaging.
The consumer recorder's former description of a "nonperiodic frame" is corrected;
the original source box is preserved. Earlier receipts retain their original
wording and are not retroactively rewritten.

## Fixed consumer recipe and resumable submission

The recipe is recorded before POST: **`Pocket 1`**, hydrophobicity, +X projection
of **0.30 nm**, radius **0.15 nm**, essentiality `True`, weight `1`. Recognition,
projections and native JSON persistence belong to public PharmacophoreMT APIs.
An empty or unsupported chosen pocket remains a negative outcome: no alternate
pocket, feature family, membership expansion or chemistry repair is attempted.
The recipe is an analytical composition control, with no binding relevance claim.

`CastpFoldClient.submit(..., submission_file=...)` reserves a receipt exclusively
before POST, retains the exact HTTP response before parsing it and atomically
updates the record. Existing receipts block another POST even after failures or
interruptions. An explicitly successful acknowledgement with a safe job ID is
required; exceptions preserve the original transport/parser error. Acceptance,
pending retrieval and a received archive remain distinct. A failed local receipt
does not prove the server created no job. Existing retry-count and HTML/not-ready
diagnostic limitations remain outside this change.

## Actual original execution and public consumption

After explicit authorization for this exact PDB and endpoint, one POST at
**2026-11-07 01:47:06 UTC** was accepted as **`j_6aee831b083dc`**. The retained
HTTP acknowledgement confirms `success=true`, filename `input.pdb`, probe `1.4`
and email `N/A`. Raw acknowledgement bytes, SHA-256 and parsed fields agree.
No resubmission occurred. At **01:47:53 UTC**, the existing client returned a
**108382-byte ZIP**, all eight members CRC-clean, SHA-256
`9fde6df53fc44ad1efb29164940ba8084548baa16f3e1898ec1c56e6f7f38270`.
These observations bound availability, not exact server computation time.

The original export reports **42 pockets** and **22 mouth aggregates** with
**23 reported openings**. All 1975 submitted atoms return exactly once. Their
preserved serials supply the known source map; the source-bound reader validates
identities, elements and coordinates. This does not identify every atom's role
inside upstream preprocessing or establish general provider fidelity.
The bound `castp/files`, server `castpfold`, run ID is
`e121c3d691e29a1474355735cf6c5ad30b9a87fa92aa3a689c246e83d065d877`.
Portable recovery preserves the run and original records.

The declared **`Pocket 1`** recipe produces **16 hydrophobic interaction sites**
from full-source indices **364, 387, 388, 671, 672, 702, 711, 712, 730, 842, 844,
845, 971, 1005, 1796 and 1806**. Membership has role `provider_lining_atoms`.
Two fresh processes select `nm/ps/radians` and `pm/fs/radians` before importing
PharmacophoreMT. Both recover the saved original and build native query JSON
with network submission/retrieval blocked. Site identities, physical centers,
radii, essentiality, weights and source/run/state/frame context agree. Native
query roundtrips pass and source coordinates, chemical context and file bytes
remain unchanged. Initial receipts with the former frame wording are retained
separately from the corrected receipts.

## Reproduction and remaining gates

The developer recorder separates the three explicit phases:

```bash
python -m devtools.qualify_castpfold_handoff prepare handoff --input-file prepared.h5msm
python -m devtools.qualify_castpfold_handoff submit handoff
python -m devtools.qualify_castpfold_handoff collect handoff
```

Only `submit` uploads. Repeated collection uses the accepted job; retained ZIPs
and matching bundles can complete interrupted local recording without a GET or
POST. A completed final receipt is protected from overwrite. Source, PDB and map
hashes, raw acknowledgement and fixed parameters are checked before recovery.
Use the retained source/results for offline repetition; another live submission
is unnecessary for the saved consumer regression.

This completes one bounded prepared **source** consumer. Exact qualification of
a newly built TopoMT wheel remains next under #101. It does not qualify the older
installed TopoMT bytes, public-only dependency acquisition, current sibling mains,
other servers, platforms/interpreters or the complete source suite. CASTp3's
separate upload failure remains unresolved; it is never replaced silently by Fold.
The user-requested `[skip ci]` commits retain those remote/full-matrix deferrals
under #16/#58 and the version/build transition under #78.

## Executed checks and retained evidence

Source producer: **`00f6a9a04d6f511303dc82da326754322d0523f4`**, following
the client receipt commit `e0e6508`. The human `_version.py` edit remains
byte-identical, SHA-256
`f1bd65409d11db2a86406d5e323b7c6599c3446573f7df1e196634b1e44200a7`.
Its historical version string is not used as this source producer's identity.

| Check | Executed result |
| --- | --- |
| Final client/lifecycle/consumer selection | **97 passed, zero skips**, including both real prepared unit-policy cases, 17.63 seconds |
| Adapter and source-bound recovery selection | **200 passed, three skips** requiring separate pyCASTA prepared inputs; 56.61 seconds |
| Distribution/reporting contracts | **20 passed**, 4.57 seconds |
| Offline interrupted-recording recovery | Existing matching bundle accepted, independent H5 source readback, nine checks true; network blocked and original directory unchanged |
| Ruff | Whole-repository check passed; **484 files** already formatted |
| Local mypy | Three changed executable modules passed with imports skipped and absent optional imports ignored |
| Documentation | HTML built; 12 existing warnings, including unavailable PlantUML; no new diagram was added |
| Report indexes | Current; no issue lifecycle was closed |

The selections overlap and are not additive coverage. Unit/lifecycle runs use
explicit Pytest Receptor loading and `--noconftest`; they do not claim execution
of the global warmup or unrelated fixtures. The designated real consumer uses
the controlled source pins, with the opt-in artifact present and no skips.

Client and consumer-admission failing-first logs are retained. The lifecycle
failing-first runs survive only in the agent terminal transcript, not as
standalone archived logs. One early lifecycle negative test reached DNS
resolution because its transport mock was missing; it failed before connection
or HTTP. The unconditional transport blocker was added before its final 32
cases, all included in the 97-case passing selection. There was no additional
service submission. This correction is recorded without inventing missing logs.

The [evidence receipt](evidence/castpfold_prepared_source_20261107.json) identifies
the [2335267-byte archive](evidence/castpfold_prepared_source_20261107.zip), with
**75 hashed payloads**, plus its manifest. All payload hashes and ZIP CRCs were
verified. Archive SHA-256:
`6c1a4289a55d06a7ef3c59863812f3da44db2bee974b511d92ec9f69c492609b`.
It retains the seed, exact submitted PDB, complete source/map, original ZIP,
submission/collection receipts, portable bundle, both public query flows,
preflight diagnostics, code identities and validation output. Recovered-copy
evidence retains its new receipt and references the identical original artifacts.

Task cache and the existing controlled engine-free prefix remain active for
the next installed-candidate gate under #101. Review them by **2026-11-13**;
remove task-only resources after installed receiving and durable retention of
required candidate bytes. Shared and human resources remain protected.
