# Bounded PharmacophoreMT consumer control

Date: 2026-11-05. Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
This follows the [original-provider source pilot](handoff_checkpoint.md), with
the user's approval to test actual PharmacophoreMT consumption. It closes no
general provider, chemical-state, scientific-validation or publication gate.

## Question and declared control

Can original fpocket membership select a prepared receptor region for public
PharmacophoreMT operations, retaining source correspondence, frame, chemical
state and physical quantities through native JSON persistence?

The recipe selects the exact provider ID `fpocket:1`, requests only
`get_features(..., features=['hydrophobicity'])`, and passes that cached inventory
to `from_receptor_projections`. Every returned feature gets an explicitly
declared +x query displacement of **0.30 nm**, with **0.15 nm** matching radius.
These are analytical choices, not inferred molecular directions or optimized
binding parameters. PharmacophoreMT retains its essential/weight-one defaults;
fpocket score/ranking assigns no feature importance. No molecular recognition,
chemistry preparation, pocket parser or pharmacophore kernel was implemented
in the integration recorder.

## Input boundary and preserved negative result

The original 3PTB source is a valid spatial pocket input, but its declared
connectivity is incomplete. Native PharmacophoreMT hydrophobic extraction on
that source raises MolSysMT `StructuralInconsistencyError`: chemical graph
analysis requires connectivity declared complete. The new guard retains this
provider failure. No completeness flag, chemical assignment or fallback was
invented to obtain a positive result. Existing preparation ownership is
[MolSysMT #298](https://github.com/uibcdf/molsysmt/issues/298).

The positive control instead uses PharmacophoreMT's already archived prepared
ERalpha/EST fragment, loaded without regenerating preparation:

- Consumer source: `869cf967cba0a066e5c10e9c725b52c5272500fc`.
- [Original compressed H5MSM](https://github.com/uibcdf/pharmacophoremt/blob/869cf967cba0a066e5c10e9c725b52c5272500fc/devguide/evidence/eralpha_interface_prepared_py314.h5msm.gz),
  SHA256 `ab67b64df320e1d2a12ee23f312344d207af528db69fdb6ee9bb10a10dee9b6c`.
- Decompressed seed SHA256:
  `a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`.
- [Original manifest and preparation limits](https://github.com/uibcdf/pharmacophoremt/blob/869cf967cba0a066e5c10e9c725b52c5272500fc/tests/data/eralpha_interface/manifest.json):
  closed fragment 304–550, explicitly chosen HIE/terminal states, inspected ARG
  atom-name correspondence and generated local H geometry. This is historical
  declared preparation, not an admission of the full receptor or bound protomer.
- Seed: 4,047 atoms, 4,088 bonds, one frame and one reference chemical state (0).
  The source pilot preserves that chemistry while interleaving the atom axis,
  selecting 4,003 nonconsecutive protein/peptide atoms and using translated frame 1.

Appending the new frame uses public conversion to `molsysmt.Structures` and
`append_structures`: historical interaction analyses are not copied into a new
frame as if newly calculated. The original historical input remains unchanged.
TopoMT base, pinned MolSysMT `00abb958fb93649131d5ce5fe5e12e90cf4900e9`, reused
unchanged Rust artifact, Python 3.14.7, units provider and fpocket binary identities
remain those in the [source checkpoint](handoff_checkpoint.md#exact-source-and-runtime-profile).
The principal sibling checkouts were not updated or edited.

## Measured outcome and checks

The retained standalone execution reported **14 pockets**. `fpocket:1` had
**48 mapped source atoms** and produced **15 hydrophobic query sites**. This is
an observation of this saved execution, not a universal fpocket count.

Original run ID:
`55e92e4f7a58bfea89517093f4c829d127657a91af6faaaccb88aa677f63b6c8`.
Generated two-frame source SHA256:
`1b63f84a716f981d95c585758ce4908ee9ac396e6986f14db41f17e1ea40041e`.
Native query SHA256 under nm/ps:
`b801429b603274c092b04dce4959cec81c74e34045a2b617bbc3d53cbab98eff`;
under pm/fs:
`975c7cdaa7f35003d3c33780a37b845359195303d2a97e8d4a7311a062a3ebb1`.
Different serialization bytes retain physically equivalent geometry.

The [machine-readable evidence](pharmacophore_handoff_evidence.json) retains
source/worktree hashes, input/output identities, declared recipe and checks.
Original bundles, generated sources, native queries and receipts remain in the
local task workspace; they are not a published scientific archive.

Closeout: the original bytes are now preserved in
[the repository evidence archive](evidence/original_handoff_20261105.zip), with
[archive and member SHA256 identities](evidence/original_handoff_20261105.json).
This adds durable local retention without relabeling the original execution or
claiming public scientific publication. The earlier machine-readable record's
temporary-storage description is historical.

All ten original handoff checks and all five consumer checks passed. Native
JSON round-trip retains sites, their source indices, requiredness, weights and
context metadata; source coordinates and source-file bytes are unchanged.
The guard independently checks every site against its original atom coordinate
plus `[0.30, 0, 0]` nm, matching radius and feature kind. Both unit policies pass.
Physical comparisons use absolute 1e-12 nm tolerance with zero relative tolerance;
observed pm round-trip errors were at most 3.6e-15 nm in position and 5.6e-17 nm
in radius. Identity and query semantics remain exact. Receipt quantities carry
value and unit together; the native model uses PharmacophoreMT's own codec.

Missing state declaration, conflicting frame and changed source bytes are
rejected before consumer recognition. The source-profile receipt, original
bundle identity and submitted atom map are required; a checksum is integrity
evidence, not authentication of chemistry or physical relevance.

Test-first development retained the initial missing-recorder failure, the
historical-analysis append rejection, the corrected native-source test setup,
and the overly strict floating-point comparison before correction. A later
repeat failed when temporary storage was exhausted; no result was credited.
After removing only task-owned tooling and selecting task-local scratch space,
the final executed selector passed **10 tests**, with zero skips: the six
consumer cases, original-engine source regression and three governance guards.
Ruff lint/format passes across 415 files; mypy 2.3.1 passes both recorder modules.
`make -C docs html` completed with the same 12 diagnostics outside the changed
user page, including the unavailable PlantUML executable; no diagnostic concerns
the edited page. The extension is supplied from task-local tooling.
The earlier 136-test core/provider selection remains dated evidence for its
recorded scope, not a newly executed full suite or hosted/installed qualification.

## Reproduction and remaining scope

Use the compatible source environment recorded above. Verify both archive and
decompressed input hashes before use; supply the unchanged decompressed file
as `PILOT_PREPARED_RECEPTOR`. Choose new output directories:

```bash
PYTHONPATH="$PILOT_MOLSYSMT" python -m devtools.qualify_fpocket_handoff \
  "$PILOT_PREPARED_RECEPTOR" /tmp/eralpha-original-handoff \
  --fpocket-cmd "$PILOT_FPOCKET"
PYTHONPATH="$PILOT_MOLSYSMT" python -m devtools.qualify_pharmacophore_handoff \
  /tmp/eralpha-original-handoff /tmp/eralpha-consumer \
  --pocket-id fpocket:1 --direction 1 0 0 --distance '0.30 nm' --radius '0.15 nm'
TOPOMT_FPOCKET_CMD="$PILOT_FPOCKET" \
  TOPOMT_PREPARED_RECEPTOR="$PILOT_PREPARED_RECEPTOR" \
  PYTHONPATH="$PILOT_MOLSYSMT" python -m pytest --noconftest --receptor=llm \
  tests/methods/fpocket4/test_pharmacophore_handoff.py \
  tests/methods/fpocket4/test_handoff_pilot.py \
  tests/test_reporting_protocol.py tests/test_devguide_contract_terms.py
```

Consumer imports are lazy and optional; no TopoMT runtime dependency or
PharmacophoreMT production API was changed. The output is `query.json` plus a
receipt linking the original run and pocket. The engine is not needed to replay
that original bundle, but it is required for the explicitly opted-in fresh test.
Source and consumer artifacts remain local development evidence.

This is one hydrophobic analytical hypothesis on one declared prepared fragment,
not a complete receptor pharmacophore, fitted/search-evaluated model, affinity
prediction or biological validation. Alternative/missing source chemical states,
other feature families/engines, input preparation, clean installed/public
receiving and hosted qualification remain separate. Membership and alpha spheres
remain declared representations, not an exact volumetric pocket. #101 remains open.
