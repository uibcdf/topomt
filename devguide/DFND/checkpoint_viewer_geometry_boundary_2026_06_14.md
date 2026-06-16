# Viewer Geometry Boundary Checkpoint - 2026-06-14

## Decision

TopoMT viewer renderers share viewer-neutral, structurally immutable geometry payloads. Geometry and identity are separate fields:

- coordinates are bare numerical tuples with a mandatory unit;
- `EntityRef` carries structured identity such as tetrahedron IDs, molecular-system atom indices, `support_key`, and `component_key`;
- extractors build on the public DFND selectors and index-space helpers;
- small final adapters attach PyUnitWizard quantities and always call MolSysViewer with `skip_digestion=True`.

Renderers remain responsible for scientific selection and visual style. Geometry extractors and adapters do not decide component membership, classification, or presentation policy.

## Implemented Slices

- Added `PointGeometry`, `SphereGeometry`, `RingGeometry`, `SegmentGeometry`, `TetrahedraGeometry`, `IndexedTriangleGeometry`, `IndexedEdgeGeometry`, and `EntityRef`.
- Added canonical extractors for tetrahedron centers, DFN graph segments, tetrahedra, faces, and edges, built on the public DFND selectors.
- Migrated nodes and links in `show_dfn_graph()` and component `representation="graph"` to shared extractors and final adapters.
- Migrated general and component tetrahedron rendering to one canonical tetrahedron payload.
- Migrated coast-face rendering and tetrahedron face/edge pick metadata to canonical indexed face/edge payloads.
- Migrated residence, alpha, probe-center, and affinity-sphere representations to canonical component sphere extractors and final adapters.
- Migrated cloud, pipe fallback, and envelope blobs to the same canonical residence-sphere geometry.
- Migrated envelope mouth caps from ad-hoc external-link triplets to canonical `face_ids` and indexed-triangle geometry.
- Migrated public-feature pocket blobs and marker points to canonical geometry carrying stable `feature_id` references in the payload unit (`nm`).
- Migrated centerline tubes and rings, mouth rings, and dry-scaffold segments to canonical geometry and final adapters.
- Component graph references retain `support_key` and `component_key`; face and edge metadata carry JSON-serializable structured `entity_ref` payloads.
- The diagnostic context action no longer parses hover labels with regular expressions. It consumes structured `entity_refs` or resolves selected shape atoms through the simplex selectors.

## Verified Invariants

- The full DFN graph and component graph produce identical coordinates, units, tetrahedron references, and internal-link geometry for the same nodes.
- Requested tetrahedron order is preserved by the canonical extractor.
- Indexed tetrahedra, faces, and edges declare the `mesh_local` pick-index space explicitly.
- Stable `face_id` filtering is independent from tetrahedron filtering.
- Geometry payload units are mandatory.
- Final point, sphere-set, uniform-sphere, segment, tetrahedron, and indexed-triangle adapters always disable argument digestion.
- Residence and alpha-sphere renderers emit the exact centers and radii returned by their canonical extractors.
- Blob renderers emit the canonical residence-sphere centers and radii.
- Mouth caps emit the canonical face geometry selected by their external-link `face_ids`.
- Public-feature blobs and markers carry stable feature references and preserve scalar marker tags.
- Centerline stations use the corresponding tetrahedron ID, scoped by `component_key`.
- Mouth rings use `external_link_key`, with external-link support and component keys.
- Dry-scaffold edges use a canonical sorted molecular-system atom pair, scoped by component support and component keys.
- Diagnostic identity does not depend on presentation text.

## WP-18 Status

VIEW-012 is verified locally. Active TopoMT renderers now extract scientific geometry through the viewer-neutral payload boundary and emit it through final adapters. The specialized identity contracts are:

- centerline station: the station's tetrahedron ID plus `component_key`;
- mouth ring: `external_link_key` plus its support and component keys;
- dry-scaffold edge: canonical sorted molecular-system atom pair plus component support and component keys.

The remaining work belongs to the MolSysViewer host boundary, not VIEW-012: direct frontend transport of arbitrary `entity_refs` and elimination of host-side digestion warnings for already-normalized shape options. It is recorded in `../molsysviewer/devguide/pending_proposals/generic_geometry_payloads_and_entity_refs.md`.

## Ownership Boundary

DFND selectors, scientific membership, entity identity, and DFND-specific extractors remain in TopoMT / MolSysViewer-TopoMT. Generic immutable geometry payload types, final shape adapters, explicit index-space transport, and host delivery of structured `entity_refs` are candidates for MolSysViewer. This split is recorded in `../molsysviewer/devguide/pending_proposals/generic_geometry_payloads_and_entity_refs.md`.

MolSysViewer interactions currently expose shape tags, labels, and selected atoms, but not arbitrary per-shape entity references. TopoMT therefore resolves current picked simplices from structured atom selections. A future host API may transport `entity_refs` directly.
