# Explicit pocket definitions and modern numerical geometry

Recorded: 2026-10-02. Owners: [#88](https://github.com/uibcdf/topomt/issues/88)
(region/reporting compatibility), [#89](https://github.com/uibcdf/topomt/issues/89)
(modern predicate grid). Python 3.11/3.12 CI work remains explicitly deferred.

## Contract and scientific interpretation

The user requested independent choices for the published pocket definition and
modern-server compatibility, as already provided for atomic radii. The local
experimental CASTp3 entry point accepts `pocket_definition='literature'` (default)
or `'castp3'`. Radius assignment remains independently selected by `radii_model`.
No result is presented as a newly defined DFND or Topography concept.

| Choice | Flow rule | Status of the evidence |
|---|---|---|
| `literature` | Maximum reachable depth; any reachable exterior excludes the tetrahedron. | Formal definition of non-wrapping pockets in the 1998 construction. |
| `castp3` | Lowest-rank reachable finite terminal; exterior only if no finite terminal is reachable. | Empirical reconstruction inferred from archived modern-server sphere regions. |

The primary source is Edelsbrunner, Facello and Liang,
[On the definition and the construction of pockets in macromolecules (1998)](https://doi.org/10.1016/S0166-218X(98)00067-5).
Its discrete flow is acyclic with increasing orthosphere radius; depth is the
maximum reachable tetrahedron index. The separate historical wrapping algorithm
helps motivate investigation of minimum-terminal behavior but does not prove
which code or definition CASTp3/CASTpFold uses. Modern export agreement is an
inference, not recovered server source and not a demonstrated server bug.

Both definitions report component vertices as lining atoms and actual mouth
triangle vertices as rim atoms, including attached triangles. The former
exterior-opposite substitutions compensated for different regions and are no
longer used. Experimental peripheral expansion remains explicit and separate.
Probe-limited depth is a literature-only diagnostic; requesting it with the
CASTp3 compatibility definition raises an error before geometry construction.
Unknown definitions are also rejected before preparation. Definitions and radius
profiles are never silently exchanged.

Each native feature record carries `properties['castp3_execution']`, including
the definition, radius model, probe, rank overrides and diagnostic switches.
The existing local Topography adapter preserves those properties. Original
server/archive output is untouched; the high-level provider-output native route
remains unimplemented.

## Forty-system geometric investigation before numeric correction

The complete diagnostic artifact is
[flow_audit_2026_10_02_vertex_panel40.json.gz](artifacts/flow_audit_2026_10_02_vertex_panel40.json.gz).
It records exact source hashes and all disagreements; gzip is deterministic.
The executed diagnostic source is retained alongside it as `.py.txt`, because
its old reporting variants must not be confused with the newly adopted contract.
Read the evidence with `json.loads(gzip.decompress(path.read_bytes()))`.

Before the independent numeric correction, minimum-terminal depth plus actual
vertices matched every exported feature/mouth atom-set multiset in 38/40 inputs.
Pocket sets improved from the dated 468/534 baseline to 533/534. Closed-void
sets were 388/388; channel sets 51/52; branched-channel sets 16/17; aggregate
mouth sets 600/603. These are completed *diagnostic* counts, not a fresh result
from the new production implementation.

Of 991 exported regions, 982 had uniquely validated empty four-contact sphere
supports. Of those, 980 regions matched exactly. The two validated region
mismatches were the 1CDO channel and branched channel joined by a false sink.
Nine regions had incomplete/ambiguous sphere witnesses and are not relabeled
as geometric failures or successes. Exact aggregate mouth atom sets do not
certify individual mouth triangulation or SA/MS quantities.

## Two residual diagnoses

1CDO contains a thin tetrahedron whose exact historical floor grid reverses its
power-radius order against its neighbors. This creates a false finite terminal.
Modern exact materialization now rounds to nearest integer coordinates/radii at
five decimal places, retaining the original decimal PDB grid. The separate
classical route remains historical. No fitted tolerance or archive membership
is used to alter the numerical calculation. Generic arbitrary-precision inputs
still have a finite-grid precision boundary.

1HIV's archived contribution list excludes all fourteen atoms of CSO A67/B67,
while MolSysMT correctly retains them in the general protein selection. They
are HETATM records. All 89 bundled contribution lists contain zero HETATM
atoms, evidence about this corpus rather than a universal server prohibition:
the server has a heterogen inclusion option. In a separately transformed
ATOM-only 1HIV input, the candidate diagnostic matches 13 pockets, three voids,
one channel and fourteen aggregate mouths. That transformed input is not the
original archived PDB. Native preparation currently retains the selected CSO
atoms; a general explicit heterogen-input contract remains pending. No
residue-name exclusion or radius fit is introduced to hide the difference.

## Validation and pause boundary

The independent numerical regression first failed on the historical grid and
passes after correction. Unit guards exercise finite/exterior bifurcation,
policy/radius independence, metadata, invalid definitions and attached mouth
vertices. Molecular guards cover 1STP and the separate 1CDO components.

Fresh production panel and closed-void verification results are recorded below
when completed. Open-pocket analytical SA/MS quantities, individual mouth
boundaries, unobserved terminal variants (#84) and general input parity remain
separate requirements. No full modern-server equivalence is asserted.

## Fresh production forty-system membership result

The [fresh membership artifact](artifacts/membership_audit_2026_10_02_definitions.json)
recomputes all forty exact archived PDBs with explicit `castp3` definition and
`castp3_protor`, full depth and zero diagnostic expansion/tolerance. It is
complete without calculation errors; 39/40 systems match every feature class.
Only 1HIV remains discrepant under the original archived input and general
protein/peptide selection.

| Class | Server | Native | Exact atom-set multiset matches |
|---|---:|---:|---:|
| Pocket | 534 | 534 | 533 |
| Closed void | 388 | 388 | 388 |
| Channel | 52 | 52 | 52 |
| Branched channel | 17 | 17 | 17 |
| Aggregated exported mouth | 603 | 603 | 602 |

The independent 1CDO molecular guard now matches every class, including all
three channels and three branched channels. Physicochemical properties were
disabled in the geometric panel: they do not affect memberships. Source and
input hashes, complete deltas, runtime and policy are retained. The executed
[runner](artifacts/membership_audit_2026_10_02_definitions_runner.py.txt) and
[source delta](artifacts/membership_audit_2026_10_02_definitions_source.patch.gz)
reconstruct the scientific source from `ce69d25`; subsequent changes remove
unused helpers and clarify docstrings/names without changing calculated rules.
The guard validates corpus completeness, original archive/PDB hashes, policies,
all denominators and the residual rather than treating equal counts as parity.

This is stronger than the previous 38/40 diagnostic outcome, but does not
extend sphere-support certification to its nine ambiguous/incomplete witnesses.
It also does not validate current service availability, every possible input,
individual mouth triangulation or open-feature SA/MS metrics.

## Verification limits and next decision

Ruff check and format pass repository-wide. Bounded mypy on exact arithmetic
and the two maintained audit tools passes with missing optional stubs ignored.
The larger modern geometry/components check still reports existing typing debt:
an isolated before/after comparison has 43 versus 42 diagnostics and no added
normalized messages. #86 owns the geometry portion; this is not a full typing
closure. Sphinx HTML builds with the eight previously recorded warnings (#64).

The recommended next slice after the requested pause is an explicit generic
heterogen-input contract, validated on 1HIV without residue-name special cases.
Then audit open SA/MS metrics on 1STP, keeping analytical molecular/accessible
measures distinct from current polyhedral `area`/`volume`. Individual mouth
boundaries and additional held-out proteins should precede a broad equivalence
claim. Geometry/lining agreement is now strong evidence of feasibility;
open analytical metric equivalence remains a separate, less demonstrated task.

## Completed regression verification

The scientific pytest-receptor run passes **968 tests** in 1626.26 seconds:
`test_castp3_pocket_definition.py`, `test_castp_modern_void_measurements.py`
and `test_castp_void_measurement_audit.py`. This freshly preserves the full
225-cavity/900-scalar absolute-precision panel and checks unit-bearing admission
to the existing Topography adapter. It also includes the independent 1CDO
channel/branched-channel guard. The numeric defect #89 is resolved and its
record is [archived](../archive/castp3_modern_predicate_grid.md).

Additional bounded runs pass the six molecular parity controls and archived
identity/delta tests (25 tests), explicit-policy/integer/provenance unit guards
(13 tests with the already exercised 1CDO guard deselected), the maintained
flow audit (seven tests), the new pinned forty-system evidence guard and the
reporting protocol. These are targeted CASTp checks, not a full repository or
Python 3.11/3.12 CI closure. Development now pauses at the user's request.
