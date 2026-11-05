# Original fpocket source handoff pilot

Date: 2026-11-05. Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
This bounded work was resumed with the user's approval. It does not resume
native parity or complete PharmacophoreMT adoption, DFND admission, or #101.
Provider compatibility remains linked to
[#100](https://github.com/uibcdf/topomt/issues/100) and
[#97](https://github.com/uibcdf/topomt/issues/97).

## Delivered boundary

The original CLI uses the shared input exporter, rejects empty selections and
multiple submitted frames, and selects one frame from multi-model PDBs. The
exporter returns atom indices in exported source order. CLI runs retain that
map as `submitted_atom_indices`; the files route can use it independently of
source atom-ID labels or renumbered PDB serials. Explicit maps must uniquely
cover the selection and match the source frame within 0.00051 Å. Legacy files
calls without a map retain their serial-to-atom-ID behavior.

`python -m devtools.qualify_fpocket_handoff` executes the original binary and
retains `original.zip`, `source.h5msm`, and `receipt.json`. It constructs a
nonconsecutive protein selection using the provider-owned `permute_atoms`,
appends a translated copy as frame 1, and records one reference chemical state.
The source is persisted and restored through MolSysMT's H5MSM route. Temporary
engine directories have disappeared before bundle recovery.

Checks cover exact ordered pocket identities, source memberships, original
measurement values/units/definitions/provenance, and geometry; source labels,
frames and state cardinality/reference survive persistence. Alternate-policy
geometry comparisons allow only 1e-12 nm absolute conversion roundoff, with no
relative tolerance. Definitions and original measurements still compare exactly.
The detached output survives later source-coordinate mutation, and replay
against that changed pose is rejected. This is evidence transfer for a future
consumer; no PharmacophoreMT operation is invoked.

## Exact source and runtime profile

- TopoMT base: `0f82d5adfae73ae24846f713ab5bf62782a4f1ad`, with this local
  handoff change. The pre-existing generated-version edit was preserved.
- MolSysMT source: `00abb958fb93649131d5ce5fe5e12e90cf4900e9`, imported from
  an isolated sparse source checkout. The principal sibling checkout stayed
  at `71fbe4f46d3c70e4e973c8025f01752a8c9b1084`.
- The two MolSysMT revisions have the same Rust tree,
  `32cfb07b9c26ae9ad3ed379c1b76fab85669cf67`. The source probe reused the host
  extension, SHA256
  `9a485965d06f4966d9a78a420b8622765159e80e3dafb8b475e7a5ed6e01275e`.
  It did not build or qualify a new installed MolSysMT distribution.
- Python 3.14.7, NumPy 2.4.6; PyUnitWizard source
  `9d74f0e1e911d78c1906948e74ce8da93935557d`.
- Original executable: conda-forge Linux package
  `fpocket-4.2.3-h5fd1fdb_2.conda`, archive SHA256
  `0d77bf44c6342d32a78cd9bbde6e478539d02673877cb6c1d65fcb552cca0445`;
  binary SHA256
  `18a3a5e78481e572018703fd7e463969dd1cc598464efde18acf30284f5941eb`.
  Its help banner says `fpocket 4.0`; retain the package and binary identities
  rather than inferring the installed build from that banner. The executable
  was extracted into task-local storage and resolved its host shared libraries.
- Seed PDB: `topomt/data/CASTp_3.0_server/3ptb.pdb`, SHA256
  `c079cac40dc56c2e6d62497ae5db47e2510ea9c91aaa539ee68bf0c93aa41dbb`.
  The generated source has 1,701 atoms and two frames; the selection has 1,629
  protein/peptide atoms, beginning `[0, 2, 4, 6, 8, 10, ...]`. Frame 1 is
  translated by `[0.3, -0.2, 0.1]` nm; the sole chemical-state reference is 0.

The retained standalone execution reported **9 pockets** and passed all ten
receipt checks. Its run ID is
`1b29c31d8180e7ef8bf1124962d39eeb24545bf32cb231e7a4370376aa094480`;
its saved H5MSM SHA256 is
`39d96dce60310b08f92bfe28004db2720e3d77b0d969c91e66c3fae72722e213`.
These identify that execution, not a universal pocket count or a bitwise
reproduction requirement for future executions.

## Validation and reproduction

The new guards were written before the corresponding fixes. Initial failures
exposed NumPy-selection ambiguity, empty/multiframe acceptance (including an
empty frame-index list), copied PDB
trajectories, the missing explicit map, and NumPy context JSON serialization.
The alternate-unit check initially differed only by approximately 1.8e-15 nm;
the bounded geometry tolerance above records that numerical boundary.

The selected source-context, registry, provider-output, fpocket-file, new
handoff/input/map, shared dependency-boundary and governance battery passed
**136 tests** with five unrelated installed-engine/subprocess cases deselected. The original
fpocket executable was available, and the handoff integration test executed.
Fifteen new tests protect the added input/map and handoff cases. The 14 input/map
tests also passed against the unchanged host MolSysMT checkout, without the
pinned-source override. Ruff lint/format and bounded mypy 2.3.1 passed for the
four changed executable modules. Mypy ran from
task-local Python sources after its compiled installation exceeded temporary
storage quota; the shared environment was not changed.

`make -C docs html` completed with 12 diagnostics outside the edited user guide.
The missing `sphinxcontrib.plantuml` extension was supplied in task-local storage;
the PlantUML executable itself remains absent, so an existing diagram was not
rendered. The other documentation diagnostics remain outside this change and
with the existing [documentation owner #64](https://github.com/uibcdf/topomt/issues/64).
The changed user page has no Sphinx diagnostic.

Set `PILOT_MOLSYSMT` to the pinned source root and `PILOT_FPOCKET` to the original
binary. The output directory must not already exist:

```bash
PYTHONPATH="$PILOT_MOLSYSMT" python -m devtools.qualify_fpocket_handoff \
  topomt/data/CASTp_3.0_server/3ptb.pdb /tmp/topomt-fpocket-handoff \
  --fpocket-cmd "$PILOT_FPOCKET"
TOPOMT_FPOCKET_CMD="$PILOT_FPOCKET" PYTHONPATH="$PILOT_MOLSYSMT" \
  python -m pytest --noconftest --receptor=llm \
  tests/methods/fpocket4/test_handoff_pilot.py \
  tests/methods/fpocket4/test_input_preparation.py \
  tests/methods/fpocket4/test_submission_mapping.py
```

The integration test is explicitly opt-in through `TOPOMT_FPOCKET_CMD` because
its source-fixture preparation uses provider APIs not qualified in a published
MolSysMT package here. Once selected, a missing binary or failed check fails the
pilot; the command does not substitute a native engine or silently skip work.

## Remaining evidence

This does not qualify alternative/missing chemical-state contexts, chemical
matching, other engines, a clean installed provider route, or scientific pocket
stability across new executions/transforms. Those remain with #101, #100 and
the existing [uncertainty owner #75](https://github.com/uibcdf/topomt/issues/75).
It introduces no inferred minimum MolSysMT package version or public support
claim. This initial spatial control did not exercise PharmacophoreMT. The
subsequent [prepared-source consumer control](pharmacophore_handoff_checkpoint.md)
records that bounded follow-up and preserves the incomplete-chemistry rejection
of this 3PTB source.

The host `pip check` already reported seven conflicts involving Amber-related
tools, pdb2pqr, NumPy and Biopython; they were not repaired by this pilot. The
full test suite, required hosted CI and installed/package qualification remain
outside this local selector. This checkpoint neither clears their backlog nor
closes the owning issues. No publication or release is performed.
