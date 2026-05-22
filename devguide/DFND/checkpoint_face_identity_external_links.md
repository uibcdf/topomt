# DFND Face Identity and External-Link Checkpoint

This checkpoint records the face-identity hardening pass for DFND.

## Issue Found

The new DFND face-identity tests exposed a real substrate bug in
`DelaunayMesh`: local face indices were interpreted on sorted simplex atom
indices, while SciPy `Delaunay.neighbors[:, face_index]` is indexed by the
original oriented simplex order.

That meant `get_face_atoms(simplex_index, face_index)` could return an atom
triple that did not correspond to the neighbor relation for that face. This is
critical for DFND because `R_gate`, face records, external links, and derived
mouth descriptors all depend on exact face identity.

## Correction

`DelaunayMesh.get_simplex_faces()` and `DelaunayMesh.get_face_atoms()` now use
`oriented_simplices` for local face indexing, matching the SciPy neighbor
convention. The returned face atom triples remain sorted for stable identity and
hashing.

This matches the existing `WeightedDelaunayMesh` behavior.

## Tests Added

`tests/test_dfnd_graph_contract.py` now checks that:

- every raw face record is traceable to `mesh.get_face_atoms(...)` and
  `mesh.get_face_index(...)`;
- shared faces have exactly one global `face_id` and matching `R_gate` values
  on both tetrahedron-owner records;
- boundary external links reference existing boundary face records;
- external-link atoms contain the atoms of all linked boundary faces.

These tests are engineering identity checks. They do not validate whether DFND
finds biologically correct cavities.
