# Source-bound recovery of original Pocketeer output

Date: 2026-11-06. Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
This follows the [reference-state boundary](chemical_context_checkpoint.md) and
the [long-term handoff plan](../provider_handoff_plan.md). Existing fidelity,
native and component-qualification owners retain their separate scope.

## Delivered source boundary

`get_provider_output(source, method='pocketeer', backend='files',
bundle_file='original.zip')` reconstructs PocketeerOutput from ProviderRun's
captured original JSON and the explicit mask supplement. It calls the existing
`ProviderRun.load` integrity/path/run-ID verifier and retains that original
library run, its bytes, order, IDs and measurement provenance. It never recaptures
the run as a new files execution. ArgDigest admits the bundle path; each route
has a closed leaf signature. Saved frame, selection and chemical context cannot
be replaced by recovery options. Legacy topography/native defaults are preserved.
The public recovery orchestration is traced through the existing SMonitor
integration, while argument diagnostics retain their owning ArgDigest catalog.

Run metadata's `output_protocol` links the original artifact to explicit field
units: centroid/sphere center/radius in angstroms, mean SASA in angstroms squared,
volume in angstroms cubed and score in unit 1. Recovery rejects absent or
conflicting unit protocols instead of inferring units from numbers or session
settings. This also keeps original JSON bytes intact.

Original execution adds `output/topomt_source_context.json`, schema 1. It records
the full source atom count; atom IDs/names/types, group IDs/names and chain IDs;
and the full selected source frame with an explicit nm unit. Unknown public
attributes stay unknown. Full-source agreement includes atoms omitted from the
submitted selection. Chemical reference admission/digest keeps its existing
contract. TopoMT only queries MolSysMT's public operations; this is adapter
provenance, not atom correspondence, alignment, chemistry or preparation.

The shared `pdb_context` tools serve the external boundary. The submitted-row
validator is extracted unchanged from fpocket, whose private entry point now
delegates. It verifies unique selection coverage, unique PDB serials and frame
coordinates at 0.00051 angstrom tolerance. Full-source coordinates compare at
absolute 1e-12 nm, with exact atom-attribute agreement. Source supplement bytes
can differ between new runs by unit-conversion roundoff; original engine outputs
still compare exactly, and every saved artifact remains byte-preserved.

The parser validates original pocket/sphere/residue fields, counts and IDs;
literal boolean masks with ordered matching IDs; unique/in-range atom maps;
finite coordinates/measurements and positive sphere radii. Ambiguous duplicate
JSON keys and nonfinite constants are rejected. Available empty output or residue
membership stays empty. Shared record conversion serves live original objects
and decoded records without recomputing provider measurements or detection.
The shared converter delegates angstrom-to-nanometer conversions to
PyUnitWizard, including the explicit cubic-length volume conversion.

## Tests and remaining qualification

`tests/methods/pocketeer/test_saved_output.py` executes the real public original
provider for its baseline, recovers under nm/ps/radian and pm/fs/radian policies,
checks every record field and demonstrates recovery with imports of Pocketeer
and Biotite blocked in a separate process. It exercises source changes,
incompatible schema/units, maps, masks, nonfinite data, caller overrides,
bundle tampering and independence from source mutation and removed input files.
Synthetic modified bundles test reader admission; they are not fresh detection
evidence. Existing direct-original, state, dispatch and fpocket guards are reused.

Executed on Linux/Python 3.14.7 in the retained independent scientific prefix:

- Test-first: all 30 initial reader cases failed because the files route was
  absent. Two later unit-protocol cases independently reproduced acceptance
  without a matching explicit protocol before that guard was implemented.
- The wider source selection passed 325 cases, with five skips, in 131.13 s.
  Skips: three unavailable local Pocketeer mirror cases, one absent AlphaSpace2
  and one absent pyCASTA. Real public Pocketeer controls executed. This selection
  includes fpocket input/map/state/argument, original-output and prepared consumer
  regressions; unchanged native-parity algorithms reuse their prior evidence.
- After the final unit protocol and PyUnitWizard conversion changes, all 127
  Pocketeer argument/original/recovery cases passed in 24.47 s. After adding the
  public SMonitor orchestration trace, all 48 saved-reader cases passed in 16 s.
- Distribution-contract checks passed 18 pytest cases plus five unittest
  subtests. The inventory includes all three new runtime modules.
- Ruff lint and formatting passed repository-wide (439 files). Scoped mypy
  passed 13 affected runtime modules, with the final two changed modules checked
  again. Report indexes are current.
- Sphinx's fresh HTML build succeeded with 12 existing diagnostics in other
  pages; the final incremental build had eight. The generated third-party guide
  source byte-matches the current file. PlantUML remains unavailable.

Intermediate test-harness corrections retain their failed reports: quantity-like
strings needed structural comparison, native H5MSM uses `file:h5msm`, and physical
geometry/source-supplement comparisons require their explicit 1e-12 nm tolerance
under alternate unit policies. Original engine output bytes, masks, IDs and
reported values still compare exactly. No original artifacts are rewritten to
make comparisons pass.

The bounded suite-state refresh preserved the upstream-less TopoMT branch and
the clean MolSysMT/ArgDigest checkouts behind their remotes (123/seven commits);
PharmacophoreMT was current and clean. These sibling worktrees were not changed.
The immutable installed dependency profile from the prior checkpoint was reused;
this is source evidence, not receiving against those sibling main branches.

### Final published-reporter verification

Closeout identified the inherited reporting tool as development version
`1.2.2+2.gb9676f8`. Its earlier reports above remain retained with their actual
identity. The final producer was then rechecked using the repository CI's
published **Pytest Receptor 1.2.0**, downloaded from PyPI and verified against
the registry SHA-256 `4e339abd53d85406c3acc0c643b895154b133c0a6f9d5f7a2350703f514a9971`.
A task-owned reporting overlay replaced no scientific distribution. All reporter
Python files matched the public wheel before and after execution.

The final current-source selection passed **333 cases, five skips, 123.88 s**
(338 collected), including all 48 saved-reader controls. The five skips retain
the reasons above. Distribution checks passed **18 cases and five subtests**
with the same public reporter. These results provide the published-tool evidence
for this producer; they do not retroactively qualify earlier installed wheels.

Producer: `35e43f23408c04a47b314fa66bc706b049b24db0`. The initial
[archive](evidence/pocketeer_saved_output_20261106.zip) and
[receipt](evidence/pocketeer_saved_output_20261106.json) retain test-first and
intermediate reports, original control files and the producer patch: 271,963
bytes, 43 members, SHA-256
`e4fd9a04fcf47e7f3ad1bb6945c50215f1ae3e5b3ea0c2bd5905b29ba5411673`.

The separate [public-reporter archive](evidence/pocketeer_saved_output_public_receptor_20261106.zip)
and [receipt](evidence/pocketeer_saved_output_public_receptor_20261106.json)
retain the public wheel, registry/origin checks, final reports and public
structural-control source/bundle pair: 182,226 bytes, 13 members, SHA-256
`a795eb8778f861ddff39e1cfc86284b87c6c819b1b53b788ffb33865a413f1cb`.
All archive member digests were verified. The task-owned raw directory and
reporting overlay at `/dev/shm/topomt-pocketeer-recovery-101` remain available for
the next source consumer control; use its public-reporter overlay when testing
with the retained scientific prefix. Existing experimental artifacts remain
unchanged rather than being relabelled as published-tool evidence.

Historical bundles lacking the source supplement remain readable as ProviderRun
artifacts, with no invented source-qualified reconstruction. The new source
reader does not itself qualify a new installed wheel, receptor chemistry or
PharmacophoreMT recognition. Those remain the next steps, using the established
prepared-receptor profile and public consumer operations.

Subsequent source work on 2026-11-06 completes that prepared receiving control;
see its [checkpoint](pharmacophore_handoff_checkpoint.md). The original source and
artifact identities above remain historical evidence. A new installed candidate
is the next Pocketeer requirement in the long-term plan.
