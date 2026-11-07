# CASTp original files: source binding and recovery — 2026-11-06

Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101). Exhaustive
provider fidelity remains under [#19](https://github.com/uibcdf/topomt/issues/19);
component qualification and full-suite backlog retain #16/#58. This continues
the [file-input checkpoint](file_input_checkpoint_2026_11_06.md). It qualifies
source code and declared file correspondence, not live service execution,
prepared-receptor receiving or an installed distribution.

## Public contract

`get_provider_output(..., method='castp', backend='files')` keeps standalone
original-file imports. Supplying an external molecular system now requires
`source_atom_indices`: one full-source index per original result-PDB atom row,
in that row order. A known MolSysMT operation report can supply the map; TopoMT
does not infer correspondence. `selection`, `structure_indices`, `syntax` and
`chemical_state` describe the existing source. Maps retain their order and must
cover the selection exactly once. Source-free selectors are rejected before IO.

The source-bound import admits one coordinate frame and the existing unambiguous
reference state. It checks PDB atom/residue/chain identity, declared elements
and coordinates at 0.00051 angstrom tolerance. Alternate-location and insertion-
code rows are outside this initial binding profile. Occupancy and B-factor
changes are not atom identities: the real Fold `1psn` export has membership
occupancies different from its PDB and remains valid. No chemical preparation,
missing bond inference, state switching or atom matcher is introduced.

ZIP/directory discovery retains its coherent-family rule. Individually selected
files retain their explicit names even when stems differ. The binding records
the selected artifact roles and whether they were discovered or explicitly
supplied. Original PDB, membership and measurement rows must agree; duplicate
membership rows, duplicate measurement IDs and references to unknown atoms are invalid.

Saving `output.run` preserves the full source frame/identities, reference-state
facts, map and exact original artifacts. The first addition of source context
creates a new content-derived run ID. Recovery with `bundle_file` requires the
full source and uses the saved selectors; overrides are rejected by ArgDigest.
It checks all source atoms, including excluded ones, at 1e-12 nm tolerance,
and retains the bound run ID, metadata, artifacts, relationships and measures.
Original ZIP payloads must agree byte-for-byte with retained output artifacts;
a newly rehashed bundle cannot silently contradict that witness. Manifest
integrity does not authenticate an external server calculation.

Historical unbound bundles are not upgraded by inference. Reimport original
files with a known source correspondence first. Live server wrappers remain a
separate context/availability boundary. Conflicting CASTp3/Fold aliases and
explicit server/backend choices now fail before delegating or contacting a
service. Native methods are not substituted.

## Shared portable evidence

`ProviderRun` schema 1 now rejects duplicate JSON keys, noninteger schema tags,
unexpected or missing manifest fields, invalid checksum/context types and
noncanonical artifact names. Saving an incoherent run fails before opening the
destination. Valid schema-1 bundles retain their IDs and bytes; no schema
migration or scientific field reinterpretation is performed.

The shared change has 84 new schema controls, including correctly rehashed
negative manifests. Four genuine retained fpocket/Pocketeer/AlphaSpace2/pyCASTA
bundles pass exact save/load identity checks. Current source also reconstructs
the retained 11-pocket Pocketeer result with original providers blocked.

## Source evidence and limits

The tests-only [fixture manifest](../../tests/data/castp_source_binding.manifest.json)
describes an unchanged original `2pk4.pdb`, reverse atom order, two interleaved
auxiliary atoms, and two frames. Frame 0 is translated; frame 1 matches the
export. The source has 747 atoms, the map covers 745, and indices 1/3 are
excluded. Public MolSysMT operations and their reports establish correspondence.
This analytical fixture is not a chemically prepared receptor.

Fixture generation uses MolSysMT `00abb958f`; the H5MSM reads back under public
0.23.0 with identical identities, bonds, charges and coordinates. Its H5 SHA-256
is `d97596013c1f953ec3165198fa2d886630b41fa24689a52c15c18eb338874c2b`.
The two versions return connectivity completeness as a scalar and a one-item
list respectively. Existing chemical-context fingerprints distinguish those
representations. Their cross-version equivalence is not silently inferred.

The new source controls include 63 CASTp cases and 82 argument/route cases.
They cover both unit policies, all 13 original measurement columns, full-source
immutability, correctly rehashed semantic mutations, coincident-coordinate
identity swaps, individual files, Fold occupancies, retained raw server ZIPs,
and fresh-process recovery with original engines and network calls blocked.
MolSysMT's MDTraj availability queries are distinguished from imports;
MDTraj is not loaded. Failed guard-development attempts remain in the evidence.

Four explicit source controls import CASTp3/Fold `2pk4` under nm/ps and pm/fs,
recover seven pockets and three mouth aggregates each, and preserve each saved
run. Independent captures can have different IDs because the fingerprint covers
serialized source coordinates, including unit-conversion rounding. Their
physical comparisons use the declared tolerances; IDs are not forced to match.

The final integrated source selection passes **388 cases**, with four original-
engine absence skips. Distribution/reporting contracts separately pass **20**
cases; Ruff checks all **479** Python files and local mypy passes for nine
runtime modules. The complete headless HTML build succeeds with 11 existing
warnings in unchanged documents. Instruction routes and generated report indexes
also pass. These source checks do not establish an installed distribution gate.

The [evidence receipt](evidence/castp_source_bound_20261106.json) identifies source
producer `bffc26b` and its [430,880-byte archive](evidence/castp_source_bound_20261106.zip).
All 52 payloads have verified hashes and CRCs; source/test snapshots match that
producer. It retains accepted bundles, validation commands/results, scientific
controls and failed observations. The public working prefix
also exposed seven failures in old AlphaSpace2 controls caused by the recorded
MolSysMT getter-shape difference; those failed observations are retained. In
the corresponding controlled dependency prefix, the affected saved-reader
selection passes 104 cases with four original-engine absence skips. Another 49
Pocketeer controls require original execution and remain unexecuted here; the
retained Pocketeer adapter control is separate evidence. These results do not
qualify public-only cross-version acquisition or current sibling mains.

## Continuation and delivery

Prepared public PharmacophoreMT consumption, live server source admission and
an exact installed CASTp receiving candidate remain under #101. Atomic
contributions, bulb typing and exhaustive fidelity remain under #19. Full-suite,
support-matrix and public-delivery obligations are unchanged. No affinity,
binding-site relevance or exact closed pocket region is inferred.

The principal maintainer authorized direct commits/pushes and requested
`[skip ci]` on incremental commits. Applicable local checks accompany this
checkpoint; remote CI is deferred to a separate validation checkpoint. No
release or full-matrix claim follows from that skip. No working-environment
package was installed. The owned `.cache/castp-handoff/` workspace remains for
the receiving continuation; review it at the next checkpoint or 2026-11-13.
