# Pocketeer reference-state provenance

Date: 2026-11-06. Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
This source boundary follows the [argument and structural checkpoint](argument_handoff_checkpoint.md).
It does not extend that checkpoint's exact installed-wheel evidence to changed source.

## Scientific ownership

MolSysMT owns the source molecular representation, chemical states and PDB
conversion. TopoMT selects and records the existing reference state for its
original-provider boundary. It neither calculates a protonation state nor
changes charges, bonds or the reference. PharmacophoreMT owns downstream
chemical feature recognition and pharmacophore modeling.

The reviewed original Pocketeer source is tag v0.4.0, commit
`f59cd12fbe175ebf4c34d70405c4c41476d4cc03`; its 14 Python files previously matched
the public 0.4.0 wheel. In `src/pocketeer/api.py`, `find_pockets` filters hydrogen,
solvent and hetero atoms according to its original flags, computes alpha spheres,
labels burial through SASA, clusters and scores pockets. Hydrogen filtering is
enabled by default. `src/pocketeer/core/tessellation.py` uses Biotite radius tables
and SASA; it does not perform protonation or assign formal charges. The adapter
continues to call the original library for pocket detection. TopoMT performs
no chemical preparation.

## Boundary and guards

The original library route now admits `chemical_state='reference'` or the
reference's nonnegative integer index. ArgDigest rejects malformed selectors.
Source-dependent admission rejects absent/empty states, ambiguous references
and selection of a nonreference state before export and original execution.
Nonzero reference indices are supported without changing the source.

`topomt.third_party.pdb_context.reference_chemical_context` is the reusable
TopoMT tool for this PDB boundary. Both fpocket and Pocketeer call it. It uses
MolSysMT's public operations and retains the existing fpocket schema: index,
reference index, state count, state ID and `pdb_chemistry_sha256`. The digest covers
full-source formal charges in elementary-charge units, the bond table and
connectivity completeness. Unknown connectivity and a known empty graph remain
distinct. The digest establishes neither chemical readiness nor authentication;
it does not imply that Pocketeer interprets every recorded field.

The executable guards are `tests/methods/pocketeer/test_chemical_context.py`,
`test_argument_contracts.py` and `test_original_handoff.py`, alongside fpocket's
existing chemical-state tests. Tests cover rejected contexts before execution,
actual MolSysMT charge export, unchanged source states, original Pocketeer runs
with a nonzero reference, detached run metadata and saved ProviderRun retention.

## Executed source checks

Linux/Python 3.14.7 used the same isolated scientific prefix and inspected
provider/dependency profile as the preceding argument checkpoint; TopoMT was
imported from the changed source. No sibling worktree or installed distribution
was changed for this boundary.

- The initial test-first chemical-context module failed all eight cases because
  the selector/shared tool were absent. The focused original/argument/state
  controls subsequently passed 98 cases. A corrected NumPy snapshot assertion
  and stronger pre-export guards were verified in the final 11-case run.
- The selected fpocket/Pocketeer, provider-output/dispatch and reporting suite
  passed 294 cases with four skips in 290.17 seconds. Three skips lack BCIF
  fixtures; the fourth is the existing 2HGR deep-validation exclusion. Its 36
  warnings concern LO1/LO2 atom names and an existing native divide operation.
- Distribution-contract checks passed all 18 cases, including the updated
  inventory for the shared runtime module. Its five passing unittest subtests
  account for JUnit's declared count of 23; the receptor reports 18 pytest cases.
- Repository-wide Ruff lint and formatting passed (435 files); the final two
  strengthened test modules passed again. Scoped mypy passed six changed runtime
  modules. Report indexes are current.
- `make -C docs html` succeeded with 12 existing warnings outside the edited
  third-party guide, including the unavailable PlantUML executable. The generated
  guide source byte-matches the current file.

These are source checks, not a replacement for the previous exact installed
wheel, a new installed candidate, complete-suite qualification or the supported
Python/platform matrix. The human's pre-existing `_version.py` edit is preserved.

Producer commit: `c16dd3d609a5192c0c7c4cba269ff6ae999b497b`. The
[evidence archive](evidence/pocketeer_chemical_context_20261106.zip) retains the
test-first failure, intermediate/final reports, event streams and producer patch.
Its [receipt](evidence/pocketeer_chemical_context_20261106.json) records counts,
scope and archive identity: 80,569 bytes, 17 members, SHA-256
`9806d6a47e621d5ab6c94aa73de7b5a6e67b4865c6864c700bfec3445dd5f0bb`.
Every retained member digest was verified. The earlier intermediate snapshot
comparison failure remains visible alongside the corrected final run.

## Remaining scope

Subsequent work on 2026-11-06 delivers the
[saved-output reader](saved_output_checkpoint.md), using the source-owned
reference state and public atom/frame queries. The pending statements below
describe this checkpoint's original boundary; prepared PharmacophoreMT receiving
and qualification of the updated installed candidate remain open.

Reporting-tool identity addendum: the inherited event streams for the earlier
source checks record development Pytest Receptor `1.2.2+2.gb9676f8`. The subsequent
saved-output checkpoint retains those facts and supplies a new current-source
verification with published CI-pinned Receptor 1.2.0, including the state and
fpocket guards. Earlier producer/artifact evidence retains its original scope.

Recovering ProviderRun artifact bytes is already supported; reconstructing a
PocketeerOutput from those saved bytes with source agreement checks remains
pending. The prepared-receptor PharmacophoreMT receiving control is also pending.
Neither this provenance boundary nor structural detection certifies receptor
chemistry, feature perception, a full pharmacophore or binding affinity.
Broader fidelity (#19), native equivalence and source/full-matrix backlog retain
their existing owners and evidence limits.
