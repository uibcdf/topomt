# Provider pocket output checkpoint

Updated: 2026-09-30. Workstream: **paused by the user after initial provider/viewer delivery**.
Implementation owner: [#65](https://github.com/uibcdf/topomt/issues/65).
Exhaustive provider fidelity: [#19](https://github.com/uibcdf/topomt/issues/19) and
[third_party_results_checkpoint.md](third_party_results_checkpoint.md).

## Accepted direction and precedence

TopoMT must permanently offer pockets detected by every supported external
method to MolSysViewer, DockingMT and PharmacophoreMT. Provider-specific output
classes are the provisional representation. Future Topography integration
preserves the original results and shared pocket access.

DFND remains the native semantic reference for
[Topography](topography_conceptual_contract.md). Its consolidation and the full
#60–#62 runtime gates are **not prerequisites** for external-provider delivery.
#63 remains future canonical admission. This checkpoint takes precedence over
older roadmap/status wording that schedules DFND or viewer hardening first.
Viewer addon adoption has been explicitly resumed under #66; see the
[viewer checkpoint](provider_output_viewer_checkpoint.md). Concrete DockingMT
and PharmacophoreMT adoption and native provider-method parity review remain deferred.

The TcTIM pilot needs useful, inspectable comparative pockets before the final
general model is complete. It does not justify inventing cross-system
correspondence, binding claims, or canonical geometry from incomplete exports.

## Implemented output boundary

`topomt.get_provider_output(..., method=..., backend=...)` returns one of:

| Class | Original routes | Provider-specific evidence |
| --- | --- | --- |
| `FpocketOutput` | CLI, persisted files | Info fields; atom serials; sphere PQR identity/type/charge; original PDB/PQR bytes. |
| `PocketeerOutput` | Python library | Original JSON/masks; residues; ordered spheres and defining-atom maps; reported volume/score/SASA. |
| `AlphaSpace2Output` | Python library | Receptor and optional binder; alpha/beta sites; full snapshot and exports; original contact/weighted occupancy. |
| `PyCASTAOutput` | Python library | Returned JSON and native files; original tetrahedron indexing; representative point/ranking/depth/validation. |
| `CASTpOutput` | CASTp/CASTpFold servers, persisted files | Original archive/files; all pocket rows; SA/MS definitions; auxiliary mouth aggregates and source-parent links. |

Defaults select original execution: CLI, library, or server. Local reproductions
are not silently substituted. Existing `get_topography` and provider
`get_pockets` signatures/defaults remain compatible.

The initial private bridge reuses existing adapters' transient Topography
objects. Returned output/record classes contain no Topography ownership or live
molecular-system reference. Replacing the bridge with direct provider parsing
can proceed per provider without waiting for DFND or changing pocket access.
This is a delivery boundary, not a claim that every original field has already
passed exhaustive parity.

## Shared consumer contract, version 1

- `output.run`: immutable ProviderRun with exact artifacts and execution/input
  metadata. `run.save`/`ProviderRun.load` round-trip original evidence, not the
  complete provisional output object. Parsed-library-output reconstruction from
  bundles without the engine is a subsequent provider-specific capability.
- `output.records`: ordered detached provider records, including auxiliary
  CASTp mouth aggregates. `output.pockets` returns all pocket rows; legacy
  inferred void/channel labels do not remove a provider-reported pocket.
- `record.source_id`, `run_id`, `atom_indices`, `atom_labels`, `atom_role`,
  `parent_source_ids`: attributed identities/membership; indices address the
  source molecular system, not an implied universal atom namespace. None means
  unavailable mapping, while an empty tuple is an available empty membership.
- `record.fields`: defensive copies of parsed provider-specific fields, with
  explicit `legacy_feature_type`. Raw fields retain existing source conventions;
  consumers use `record.measurements` for attributed physical quantities.
- `record.geometries`: declared `member_atoms`, `alpha_spheres` or `beta_sites`
  when available. Coordinates/radii are PyUnitWizard length quantities in nm;
  no `exact_region` is fabricated. A missing key means unavailable representation.
  Pocketeer retains residue-mask membership separately from an additional
  `lining_atoms` representation derived from the union of sphere-defining atoms.
  pyCASTA membership identifies region tetrahedron vertices, not a surface mesh.
- `output.input_coordinates`: detached source-system frame coordinates when
  available. These can retain more atoms and precision than the submitted PDB;
  exact submitted bytes and selection/frame metadata remain in `run`.

Geometry records are immutable tuples; returned quantities/dictionaries cannot
mutate retained evidence. Provider measurements keep their original meanings.
CASTp mouth multiplicity does not localize separate openings. AlphaSpace2
weighted contact occupancy does not become a geometric intersection.

MolSysViewer can consume membership and points/spheres; DockingMT can construct
a declared search region from supported evidence; PharmacophoreMT can consume
membership/geometry for its own models. A derived box or proxy is a consumer
derivation, not the provider's exact pocket region. The TopoMT-owned MolSysViewer
addon now has explicit attachment/rendering helpers under #66. Concrete DockingMT
and PharmacophoreMT integration remains separate, deferred work.

## Evidence and next steps

The user requested a pause after this initial integration. The sequence below
is for a future explicitly resumed turn, not a current work instruction.

Test-first evidence is in `tests/test_provider_pocket_outputs.py`. The first red
run found absent entry points and a source-index bug: fpocket mapped a selection
against the already reduced system. The adapter now maps the original source.
CASTp server adapters now retain selection/frame and submitted-to-source atom
maps; detached outputs remap selected-system indices into the caller's source
system. The selected-server regression checks membership and geometry together.
Final passing selectors and hosted commit evidence are recorded at closure of
#65. Local checks do not certify live CASTp services or a green release matrix.

Initial output delivery is implemented, with resolution in
[the archived report](archive/provider_pocket_outputs.md). Final local guard
and installed-engine comparators passed 40 tests; shared guard/CASTp/reporting
checks passed 42 with three absent optional engines skipped. Ruff and 12-file
scoped mypy passed. Changed guides render without diagnostics; full public HTML
retains the 11 pre-existing diagnostics in #64. Six upstream AlphaSpace2
undefined-ratio warnings remain visible in the installed comparisons. Exact
publication/hosted evidence is retained in #65 rather than claiming that these
checks complete the broader #19 parity program.

Resume from this checkpoint, then:

1. Resume from the [provider-output viewer checkpoint](provider_output_viewer_checkpoint.md)
   for MolSysViewer adoption and a real selected-receptor workflow. Concrete
   DockingMT and PharmacophoreMT adoption remains deferred.
2. Complete provider-specific field/route fidelity and saved-library-output
   reconstruction with the retained upstream fixtures. Keep #19's existing
   20/100 engineering denominator unchanged until its own milestones pass.
3. Validate live CASTp/CASTpFold service availability separately from deterministic
   archive parsing and mocked transport.
4. Build DFND comparisons using these original results, then undertake the
   deferred public Topography gates and native provider-method review under
   their own acceptance criteria.
