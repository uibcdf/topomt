# Third-party results and descriptor parity plan

Status: active
Owner: TopoMT
Created: 2026-09-26
Tracking issue: [#19](https://github.com/uibcdf/topomt/issues/19)
Progress: [third_party_results_checkpoint.md](third_party_results_checkpoint.md)

## Objective

Scheduling update (2026-09-30): [provider pocket outputs](provider_pocket_output_checkpoint.md)
are the immediate delivery, owned by #65. Each provider's own provisional
result contract preserves its evidence and offers shared pocket access.
Topography mappings below are the eventual canonical destination and existing
compatibility path, not a prerequisite to exposing these outputs. DFND and
#60–#62 consolidation remain deferred. This does not waive exhaustive parity
or change the checkpoint's progress denominator.

TopoMT must retain every useful topographic result returned by Pocketeer,
fpocket, AlphaSpace2, CASTp/CASTpFold, and pyCASTA. Each calculable geometric or
physicochemical measurement must eventually have a TopoMT calculation that can
be compared with the third-party value under the same definition and inputs.

The work has two linked outputs:

1. A normalized measurement on the appropriate `Topography` feature, with
   quantity, units, definition, provider identity, and an original-field link.
2. A separate provider-run record that retains exact files or a complete
   structured snapshot of library output, input identity, parameters, atom
   mapping, and checksums. It must remain recoverable after temporary work
   directories disappear.

## Measurement contract

The measurement identity is `(feature, quantity, definition, provider run)`.
Names alone do not imply equivalence. In particular, fpocket Monte Carlo
pocket volume, CASTp solvent-accessible volume, CASTp molecular-surface volume,
and AlphaSpace2 alpha-space volume have different definitions. Reported values
must never be replaced by a convenient proxy, such as using volume as a score.

Each measurement records:

- value and original unit, plus a PyUnitWizard-normalized quantity when physical;
- provider, backend, version or revision, run ID, and original feature ID;
- definition and algorithm parameters, including radii and selection rules;
- original field/artifact reference and the atom-index coordinate system;
- status: `external_only`, `topomt_available`, or `comparison_validated`;
- a TopoMT issue URL whenever the same calculable definition is not available.

Dimensionless scores also need a definition. A property requiring a ligand,
atom typing, or a provider-specific trained model must name those inputs.
Database annotations and other non-reproducible labels remain attributed
external data rather than being advertised as structure-derived calculations.

Existing TopoMT and MolSysMT helpers are candidates for reuse, not automatic
proof of method equivalence. For example, whole-molecule SASA is not by itself
fpocket's pocket total/polar/apolar SASA.

## Provider-run record

The [attribute-origin register](third_party_attribute_origins.md) identifies
feature attributes whose score, typing, normalization, or index space belongs
to a particular application. General geometric descriptors keep neutral names;
their reported definitions and source artifacts remain attached to measurements.

One immutable record belongs to each execution or imported artifact set. It
stores the exact submitted structure, native output files or library-result
snapshot, original units, parameters, backend/version, source IDs, input and
artifact SHA-256 hashes, and mapping from provider atoms to the original
molecular system. Features link to this record by run ID and source ID.

Small metadata is queryable in memory. Original bytes remain in a distinct
artifact collection; they are not copied into every feature. Export must create
a portable bundle with relative paths and integrity checks. Loading a missing
or changed artifact must raise a clear error. Never retain a path inside a
temporary directory as the only copy. Do not use pickle for upstream objects;
extract documented fields and arrays into a versioned JSON/binary snapshot.

## Inventory and provider work

| Provider | Initial measurement families | Original result to preserve |
|---|---|---|
| Pocketeer | volume, score, per-sphere radius and SASA | pocket residues/mask, defining atoms, sphere identities and geometry |
| fpocket | total/polar/apolar SASA, volume, hull volume, hydrophobicity, polarity, charge, density, druggability | `_info.txt`, pocket atom PDB and sphere PQR, all parsed fields |
| AlphaSpace2 | pocket and nonpolar volumes, beta/probe scores, overlap/contact | snapshot pocket/alpha/beta arrays and available typing |
| CASTp/CASTpFold | SA/MS area and volume, mouth area/perimeter, atom contributions | `.poc`, `.pocInfo`, `.mouth`, `.mouthInfo`, optional CSV/JSON and exact server ZIP |
| pyCASTA | volume, depth, ranking, mouth geometry and ligand distances | result arrays/JSON, tetrahedron identity, validation inputs and outcome |

The inventory must identify each output field's level: run, feature, mouth
aggregate, individual mouth, sphere, residue, or atom. CASTp `.mouth` records
can aggregate several openings for one pocket; no individual mouth may be
invented from such an aggregate. pyCASTA depth and tetrahedron indices need
scientific validation before being treated as correct geometric reference.

## Delivery sequence

### 1. Contract and fpocket pilot

- Add a provider-run record with exact artifact bytes, a portable round trip,
  and per-feature source links.
- Capture fpocket CLI output before its temporary directory is removed; use
  the same path for loading persisted fpocket output.
- Add selected reported fpocket quantities with units and field references.
- Open one calculation issue per distinct missing measurement definition.
- Retain existing feature attributes as compatibility aliases during migration.

Gate: a real fpocket fixture retains and recovers its input and output files,
its pocket values are correctly unitized, and corrupt/missing bundles fail.

The initial fpocket slice exposes `topography.provider_runs` and
`pocket.external_measurements`. A run's exact files can be retrieved by
`run.get_artifact('output/3LKF_info.txt')` or saved with `run.save(path)` and
loaded with `ProviderRun.load(path)` from `topomt.provider_output`. All 19
scalar fields in the 3LKF and 1TCD info reports have attributed measurement
records; the three SASA aliases are PyUnitWizard quantities in square
angstroms. The fpocket info file omits unit labels, so physical units are
inferred from its angstrom-coordinate calculations. Reported numbers remain
separate from TopoMT calculations. Pocket PDB/PQR header values remain in
`pocket.provider_raw_fields` and the original files; sphere IDs, charge-column
values, types, and geometry are also exposed. See the
[fpocket inventory](fpocket4/external_output_inventory.md) for the remaining
atom, sphere-definition, build-identity, and parity audits.

### 2. Complete external adapters

Map all remaining documented provider fields; record explicit unhandled-field
failures in fixtures. Correct Pocketeer residue-versus-lining atoms, AlphaSpace2
state losses, CASTp mouth aggregation and optional artifacts, and pyCASTA
import/triangulation mapping. Pin versions and compare clean installations.

Gate: each fixture has a field inventory where every useful topographic field
is mapped to a measurement, feature, relation, atom, residue, or run property.
Unrelated fields may remain only in the original record with an explicit
reason.

### 3. Reproduce measurements

Implement missing calculations in TopoMT or reuse exactly equivalent MolSysMT
capabilities. Link a dedicated issue to each missing definition when its
third-party value is first mapped. Each issue specifies inputs, formula,
units, reference artifacts, tolerances, and a pytest acceptance test.

Gate: independent TopoMT values can be compared with pinned provider outputs
without changing the provider's reported value or definition.

### 4. Server and release validation

Keep deterministic ZIP fixtures in routine tests and run public-structure
server smoke tests separately. Validate multiple chains, ligands, selections,
renumbered PDB files, and structure indices. Document which providers report
pockets, voids, channels, or interfaces and which classifications TopoMT infers.

### 5. Final exhaustive provider parity regression suite

Build a separate, version-pinned test matrix for **each** provider and each
supported route (local executable, Python package, or server). Reference
artifacts must be produced by the upstream tool, retained unchanged with
checksums, version, invocation, parameters, and input structure. A curated
expected-results manifest must be checked against those artifacts independently
of the TopoMT adapter so an adapter cannot validate itself.

For every documented useful output field in the provider's field inventory,
the tests must assert an exact original-artifact reference and a `Topography`
mapping at the correct feature, relation, atom, residue, or run level. Numeric
fields must have typed values and units when physical. Fields unrelated to
molecular topography may remain solely in the original provider record, with
an explicit reason. Compare original and TopoMT-exposed feature counts, IDs,
atom/residue membership, provider-reported classifications, geometry,
relations, scores, areas, volumes, units, and provider-specific descriptors.
Text and discrete identities must match exactly;
floating-point values need a stated field-specific tolerance justified by
parsing or unit conversion. Compare arrays by identity/order where meaningful,
and otherwise by a documented matching rule. If TopoMT infers a classification
that the provider does not report, test its provenance separately. A mere
count match is insufficient.

Include representative and adversarial structures: several chains, ligands,
altlocs, missing atoms, renumbered serials, selections, multiple frames where
supported, empty results, multiple mouths, and overlapping pockets. Exercise
both direct provider execution and loading its saved output. Test source links,
bundle round trips, checksum failures, missing optional artifacts, and
temporary-directory cleanup. Pin seeds for stochastic tools, or use justified
statistical/tolerance checks against repeat upstream runs. Keep deterministic
fixtures in routine CI across Python 3.11–3.13; run live server checks in a
separate scheduled or manual job and record the last successful date. A mocked
server response proves parsing only, not live service availability.
Local agent runs use `pytest --receptor=llm`; hosted CI uses
`pytest --receptor=ci` without weakening the ordinary test selection or
coverage gate. Inspect relevant GitHub Actions results with `gh run-receptor`
and keep their commit SHA distinct from the current local working tree.

The plan is complete only when this suite passes for Pocketeer, fpocket,
AlphaSpace2, CASTp/CASTpFold, and pyCASTA, the field inventories have no silent
gaps, and documented external-engine results exposed by TopoMT agree with the
original provider output within their declared comparison rules.

## Handoff to the native provider-method review

After the external-result plan passes its final gate, review TopoMT's own
implementations of the corresponding algorithms. This is a **separate next
phase**, tracked in [native_methods_plan.md](native_methods_plan.md). It does
not change the 100-point denominator or the currently verified percentage in
[third_party_results_checkpoint.md](third_party_results_checkpoint.md).
Individual descriptor calculations in step 3 above are prerequisites and
useful building blocks; they do not by themselves validate a complete native
pocket-detection algorithm.

The review must include fpocket, CASTp/CASTp3, Pocketeer, pyCASTA, and
AlphaSpace2 because each has a local method path. For each one, inventory the
actual route exposed by `get_topography`, distinguish local algorithm code
from CLI/library/server execution, and compare the local route against the
versioned original output already captured in this phase. Audit input atom
selection and ordering, probe/radius policy, geometric stages, feature and
mouth identities, atom membership, classifications, all reported descriptors,
units, failure cases, performance, and independence from the upstream runtime.
Record known divergence as an explicit TopoMT variant rather than calling it
provider parity. Keep the external routes available for users and for future
regression comparisons.

The native review starts from a field and stage matrix with a reproducible
reference run, a concrete pytest selector, and a decision per provider:
retain and harden the existing local implementation, implement missing stages,
or keep a local route explicitly experimental. The review is accepted only
when those decisions and their evidence are recorded in the native-method
checkpoint; implementation work follows its own gates. DFND remains TopoMT's
independent native method, with its own semantics and validation.

## Issue policy

Use one English-language GitHub issue for each missing calculable measurement
*definition*, not one issue per pocket or input structure. A shared issue is
valid across providers only after their definitions are shown equivalent.
The issue identifies the provider fixture, source field, required inputs,
formula/algorithm, units, present TopoMT capability, and acceptance selector.
Link the issue from the measurement registry. Close it only after the local
calculation and a meaningful comparison test pass. Use [#8](https://github.com/uibcdf/topomt/issues/8)
as the external-tool research index, not as a substitute for implementation
issues.

## Non-negotiable checks

- No silent descriptor, geometry, or unit loss in the covered fixture.
- No assumption that two same-named provider quantities are equivalent.
- No stale temporary-path provenance.
- No claim of CASTp server operation from mocked transport alone.
- No claim of native scientific parity from feature counts alone.
