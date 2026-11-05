Bounded local source checkpoint — 2026-11-05

The original-fpocket handoff and actual PharmacophoreMT consumer control are
implemented and locally committed. Candidate:
`2209e38f9b2c5f23b129519e85d2a5cbd96788b6` on `work/fpocket-handoff-101`.
The five local commits (`cc4f976`, `d406caf`, `4bd7450`, `6f54622`, `2209e38`)
have **not been pushed**. The pre-existing generated-version edit is excluded.

Provider: MolSysMT `00abb958fb93649131d5ce5fe5e12e90cf4900e9`, Python 3.14.7,
with the recorded unchanged native artifact. Original executable: conda-forge
Linux `fpocket-4.2.3-h5fd1fdb_2`, binary SHA256
`18a3a5e78481e572018703fd7e463969dd1cc598464efde18acf30284f5941eb`.
Its help banner says 4.0. No sibling checkout or shared environment was changed.

Measured outcomes:

- Real original execution and files recovery preserve ordered pockets, source
  atom maps, available geometry, attributed measurements and units, including
  nonconsecutive selections and explicit frames.
- The retained prepared ERalpha/EST run has 14 pockets. `fpocket:1` supplies 48
  mapped atoms to public PHMT `get_features` / `from_receptor_projections`, yielding
  15 hydrophobic query sites. The +x 0.30-nm displacement and 0.15-nm radius are
  explicit analytical controls. Native JSON round-trip passes under nm/ps and pm/fs.
- Raw 3PTB remains unsuitable for native chemical recognition because its
  declared connectivity is incomplete; this expected provider failure is retained.
- The qualified PDB converter exports its unambiguous reference. TopoMT accepts
  that selector or its integer index, including index 1. Nonreference,
  ambiguous/absent/zero-state inputs and unsupported selectors reject before
  original execution; no private provider context or reference mutation is used.
- New metadata binds reference identity/count and provider chemistry digest.
  Recovery rejects changed chemistry at unchanged coordinates. Unknown and
  complete zero-bond graphs remain distinct. A real two-state/reference-1 run
  reports 10 pockets and recovers from H5MSM plus original artifacts. Historical
  files imports remain readable without retroactive state qualification.

Validation: **153 selected tests passed, five deselected, zero executed skips**
in 121.64 s; original fpocket and PHMT cases execute. Eleven new state controls
and 14 legacy input/map cases on the unchanged host provider pass. Complete Ruff
lint/format passes across 417 files; scoped mypy 2.3.1 passes five executable
modules. HTML builds with the same 12 diagnostics outside the edited page.
This is not a full-suite/hosted/clean-installed qualification (#58/#16).

Durable local reports: `devguide/fpocket4/handoff_checkpoint.md`,
`pharmacophore_handoff_checkpoint.md`, `chemical_context_checkpoint.md`.
Original inputs/results and member digests are retained in:

- `devguide/fpocket4/evidence/original_handoff_20261105.zip`, SHA256
  `22f5bf4b3e5ddb23cec1e02a3dd9dbcec813158ac1ec883d77868cb67eb39d1c`;
- `devguide/fpocket4/evidence/reference_context_20261105.zip`, SHA256
  `be6475e50274c0083e315f96956c6efd19dd5c64d8f14eb5eb498eb7715e1635`.

These paths become remotely reviewable when the branch is published. This
supplies a bounded reference-state source profile for owner review. Independent
nonreference export needs an owning MolSysMT operation (#100 / molsysmt#255).
#97, wider #100 receiving, #19/#75 fidelity/stability and installed/public
delivery keep their separate scope. No biological validation, package, release,
new dependency minimum or issue closure is claimed.
