"""Viewer-neutral geometry payloads and DFND geometry extractors."""

from dataclasses import dataclass
from typing import Any

import numpy as np

from topomt.dfnd.centerline import channel_skeleton
from topomt.dfnd.selectors import select_edges, select_faces, select_tetrahedra

from .index_spaces import MESH_LOCAL, MOLECULAR_SYSTEM, atom_indices


def _points(values) -> tuple[tuple[float, float, float], ...]:
    array = np.asarray(values, dtype=float)
    if array.size == 0:
        return ()
    if array.ndim != 2 or array.shape[1] != 3:
        raise ValueError('Geometry coordinates must have shape (n, 3).')
    return tuple(tuple(float(value) for value in point) for point in array)


@dataclass(frozen=True)
class EntityRef:
    """Structured identity carried separately from geometric coordinates."""

    kind: str
    entity_id: Any
    tetrahedron_ids: tuple[int, ...] = ()
    atom_indices: tuple[int, ...] = ()
    atom_index_space: str = MOLECULAR_SYSTEM
    support_key: str | None = None
    component_key: str | None = None


def entity_ref_payload(ref: EntityRef) -> dict[str, Any]:
    """Return a JSON-serializable structured entity reference."""
    return {
        'kind': ref.kind,
        'entity_id': ref.entity_id,
        'tetrahedron_ids': list(ref.tetrahedron_ids),
        'atom_indices': list(ref.atom_indices),
        'atom_index_space': ref.atom_index_space,
        'support_key': ref.support_key,
        'component_key': ref.component_key,
    }


@dataclass(frozen=True)
class PointGeometry:
    """Viewer-neutral point geometry with mandatory units and entity references."""

    coordinates: tuple[tuple[float, float, float], ...]
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('PointGeometry.unit is required.')
        object.__setattr__(self, 'coordinates', _points(self.coordinates))
        object.__setattr__(self, 'refs', tuple(self.refs))
        if len(self.coordinates) != len(self.refs):
            raise ValueError('PointGeometry requires one entity reference per point.')


@dataclass(frozen=True)
class SphereGeometry:
    """Viewer-neutral spheres with mandatory units and entity references."""

    centers: tuple[tuple[float, float, float], ...]
    radii: tuple[float, ...]
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('SphereGeometry.unit is required.')
        centers = _points(self.centers)
        radii = tuple(float(value) for value in self.radii)
        refs = tuple(self.refs)
        if not (len(centers) == len(radii) == len(refs)):
            raise ValueError(
                'SphereGeometry requires one radius and reference per center.'
            )
        if any(radius < 0.0 for radius in radii):
            raise ValueError('SphereGeometry radii must be non-negative.')
        object.__setattr__(self, 'centers', centers)
        object.__setattr__(self, 'radii', radii)
        object.__setattr__(self, 'refs', refs)


@dataclass(frozen=True)
class RingGeometry:
    """Viewer-neutral oriented rings with mandatory units and references."""

    centers: tuple[tuple[float, float, float], ...]
    normals: tuple[tuple[float, float, float], ...]
    radii: tuple[float, ...]
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('RingGeometry.unit is required.')
        centers = _points(self.centers)
        normals = _points(self.normals)
        radii = tuple(float(value) for value in self.radii)
        refs = tuple(self.refs)
        if not (len(centers) == len(normals) == len(radii) == len(refs)):
            raise ValueError('RingGeometry requires aligned fields.')
        object.__setattr__(self, 'centers', centers)
        object.__setattr__(self, 'normals', normals)
        object.__setattr__(self, 'radii', radii)
        object.__setattr__(self, 'refs', refs)


@dataclass(frozen=True)
class SegmentGeometry:
    """Viewer-neutral line-segment geometry."""

    starts: tuple[tuple[float, float, float], ...]
    ends: tuple[tuple[float, float, float], ...]
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('SegmentGeometry.unit is required.')
        object.__setattr__(self, 'starts', _points(self.starts))
        object.__setattr__(self, 'ends', _points(self.ends))
        object.__setattr__(self, 'refs', tuple(self.refs))
        if not (len(self.starts) == len(self.ends) == len(self.refs)):
            raise ValueError('SegmentGeometry requires one reference per segment.')

    @property
    def coordinate_pairs(self) -> tuple[tuple[tuple[float, float, float], ...], ...]:
        return tuple(zip(self.starts, self.ends, strict=True))


@dataclass(frozen=True)
class TetrahedraGeometry:
    """Viewer-neutral tetrahedra with explicit mesh-local pick indices."""

    coordinates: tuple[tuple[tuple[float, float, float], ...], ...]
    atom_quads: tuple[tuple[int, int, int, int], ...]
    atom_index_space: str
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('TetrahedraGeometry.unit is required.')
        if self.atom_index_space != MESH_LOCAL:
            raise ValueError(
                'TetrahedraGeometry atom quads must use mesh_local indices.'
            )
        quads = tuple(tuple(int(value) for value in quad) for quad in self.atom_quads)
        if any(len(quad) != 4 for quad in quads):
            raise ValueError('TetrahedraGeometry atom quads must contain four indices.')
        coordinates = tuple(_points(tetrahedron) for tetrahedron in self.coordinates)
        if coordinates and len(coordinates) != len(quads):
            raise ValueError('TetrahedraGeometry coordinates must match atom quads.')
        if len(quads) != len(self.refs):
            raise ValueError(
                'TetrahedraGeometry requires one reference per tetrahedron.'
            )
        object.__setattr__(self, 'coordinates', coordinates)
        object.__setattr__(self, 'atom_quads', quads)
        object.__setattr__(self, 'refs', tuple(self.refs))


@dataclass(frozen=True)
class IndexedTriangleGeometry:
    """Triangle geometry with explicit mesh-local pick triplets."""

    coordinates: tuple[tuple[tuple[float, float, float], ...], ...]
    atom_triplets: tuple[tuple[int, int, int], ...]
    atom_index_space: str
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('IndexedTriangleGeometry.unit is required.')
        if self.atom_index_space != MESH_LOCAL:
            raise ValueError('IndexedTriangleGeometry indices must use mesh_local.')
        triplets = tuple(
            tuple(int(value) for value in item) for item in self.atom_triplets
        )
        if any(len(item) != 3 for item in triplets):
            raise ValueError('IndexedTriangleGeometry requires atom triplets.')
        coordinates = tuple(_points(item) for item in self.coordinates)
        if (coordinates and len(coordinates) != len(triplets)) or len(triplets) != len(
            self.refs
        ):
            raise ValueError('IndexedTriangleGeometry fields must have equal length.')
        object.__setattr__(self, 'coordinates', coordinates)
        object.__setattr__(self, 'atom_triplets', triplets)
        object.__setattr__(self, 'refs', tuple(self.refs))


@dataclass(frozen=True)
class IndexedEdgeGeometry:
    """Edge geometry with explicit mesh-local pick pairs."""

    coordinates: tuple[tuple[tuple[float, float, float], ...], ...]
    atom_pairs: tuple[tuple[int, int], ...]
    atom_index_space: str
    unit: str
    refs: tuple[EntityRef, ...]

    def __post_init__(self) -> None:
        if not self.unit:
            raise ValueError('IndexedEdgeGeometry.unit is required.')
        if self.atom_index_space != MESH_LOCAL:
            raise ValueError('IndexedEdgeGeometry indices must use mesh_local.')
        pairs = tuple(tuple(int(value) for value in item) for item in self.atom_pairs)
        if any(len(item) != 2 for item in pairs):
            raise ValueError('IndexedEdgeGeometry requires atom pairs.')
        coordinates = tuple(_points(item) for item in self.coordinates)
        if (coordinates and len(coordinates) != len(pairs)) or len(pairs) != len(
            self.refs
        ):
            raise ValueError('IndexedEdgeGeometry fields must have equal length.')
        object.__setattr__(self, 'coordinates', coordinates)
        object.__setattr__(self, 'atom_pairs', pairs)
        object.__setattr__(self, 'refs', tuple(self.refs))


def _dfnd_mesh(source):
    data = getattr(source, 'dfnd', source)
    mesh = getattr(data, 'mesh', None)
    if mesh is None:
        raise ValueError('source does not expose a DFND mesh')
    return mesh


def tetrahedron_centers(
    source, tetrahedron_ids=None, *, component_refs: dict[int, EntityRef] | None = None
) -> PointGeometry:
    """Return canonical DFND tetrahedron barycentres in mesh-kernel units."""
    mesh = _dfnd_mesh(source)
    coords = np.asarray(mesh.atoms.coords, dtype=float)
    records = select_tetrahedra(source, tetrahedron_ids=tetrahedron_ids)
    if tetrahedron_ids is not None:
        requested = (
            [int(tetrahedron_ids)]
            if isinstance(tetrahedron_ids, int)
            else [int(value) for value in tetrahedron_ids]
        )
        by_id = {int(record['tetrahedron_id']): record for record in records}
        records = [by_id[value] for value in requested if value in by_id]
    refs = []
    centers = []
    for record in records:
        tetrahedron_id = int(record['tetrahedron_id'])
        local = [int(value) for value in record['local_atom_indices']]
        centers.append(coords[local].mean(axis=0))
        refs.append(
            (component_refs or {}).get(
                tetrahedron_id,
                EntityRef(
                    kind='tetrahedron',
                    entity_id=tetrahedron_id,
                    tetrahedron_ids=(tetrahedron_id,),
                    atom_indices=tuple(
                        atom_indices(
                            record.get('atom_indices', ()), space=MOLECULAR_SYSTEM
                        )
                    ),
                ),
            )
        )
    return PointGeometry(tuple(centers), unit='nm', refs=tuple(refs))


def _feature_ref(feature: dict[str, Any]) -> EntityRef:
    return EntityRef(
        kind='feature',
        entity_id=feature.get('feature_id'),
        atom_indices=tuple(int(value) for value in feature.get('atom_indices', ())),
        atom_index_space=feature.get('atom_index_space', MOLECULAR_SYSTEM),
    )


def feature_center_geometry(feature: dict[str, Any]) -> PointGeometry:
    """Return one canonical marker point for a normalized feature record."""
    center = feature.get('center')
    if center is None:
        return PointGeometry((), unit='nm', refs=())
    return PointGeometry((center,), unit='nm', refs=(_feature_ref(feature),))


def feature_sphere_geometry(feature: dict[str, Any]) -> SphereGeometry:
    """Return canonical spheres for a normalized feature record."""
    centers = feature.get('sphere_centers') or ()
    radii = feature.get('sphere_radii') or ()
    ref = _feature_ref(feature)
    return SphereGeometry(
        tuple(centers), tuple(radii), 'nm', tuple(ref for _ in centers)
    )


def _component_tetrahedron_ids(component, *, use_resident_nodes: bool) -> list[int]:
    if use_resident_nodes and hasattr(component, 'resident_node_indices'):
        values = component.resident_node_indices
    else:
        values = component.node_indices
    return [int(value) for value in values]


def _component_tetrahedron_ref(record, component) -> EntityRef:
    tetrahedron_id = int(record['tetrahedron_id'])
    return EntityRef(
        kind='tetrahedron',
        entity_id=tetrahedron_id,
        tetrahedron_ids=(tetrahedron_id,),
        atom_indices=tuple(
            atom_indices(record.get('atom_indices', ()), space=MOLECULAR_SYSTEM)
        ),
        support_key=getattr(component, 'support_key', None),
        component_key=getattr(component, 'component_key', None),
    )


def component_residence_sphere_geometry(
    source, component, *, use_resident_nodes: bool = True
) -> SphereGeometry:
    """Return maximum-clearance residence spheres for one DFND component."""
    tetrahedron_ids = _component_tetrahedron_ids(
        component, use_resident_nodes=use_resident_nodes
    )
    records = select_tetrahedra(source, tetrahedron_ids=tetrahedron_ids)
    by_id = {int(record['tetrahedron_id']): record for record in records}
    centers, radii, refs = [], [], []
    for tetrahedron_id in tetrahedron_ids:
        record = by_id.get(tetrahedron_id)
        if record is None or 'center' not in record or 'R_residence' not in record:
            continue
        centers.append(record['center'])
        radii.append(record['R_residence'])
        refs.append(_component_tetrahedron_ref(record, component))
    return SphereGeometry(tuple(centers), tuple(radii), 'nm', tuple(refs))


def component_alpha_sphere_geometry(
    source, component, *, use_resident_nodes: bool = True
) -> SphereGeometry:
    """Return Delaunay circumspheres for one DFND component."""
    tetrahedron_ids = _component_tetrahedron_ids(
        component, use_resident_nodes=use_resident_nodes
    )
    records = select_tetrahedra(source, tetrahedron_ids=tetrahedron_ids)
    by_id = {int(record['tetrahedron_id']): record for record in records}
    mesh = _dfnd_mesh(source)
    alpha_centers = np.asarray(mesh.delaunay.alpha_sphere_centers, dtype=float)
    alpha_radii = np.asarray(mesh.delaunay.alpha_sphere_radii, dtype=float)
    centers, radii, refs = [], [], []
    for tetrahedron_id in tetrahedron_ids:
        record = by_id.get(tetrahedron_id)
        if record is None:
            continue
        centers.append(alpha_centers[tetrahedron_id])
        radii.append(alpha_radii[tetrahedron_id])
        refs.append(_component_tetrahedron_ref(record, component))
    return SphereGeometry(tuple(centers), tuple(radii), 'nm', tuple(refs))


def probe_sphere_geometry(
    residence_geometry: SphereGeometry, probe_radius: float
) -> SphereGeometry:
    """Return probe-sized spheres at residence centers that fit the probe."""
    radius = float(probe_radius)
    selected = [
        index
        for index, residence_radius in enumerate(residence_geometry.radii)
        if residence_radius >= radius
    ]
    return SphereGeometry(
        tuple(residence_geometry.centers[index] for index in selected),
        tuple(radius for _ in selected),
        residence_geometry.unit,
        tuple(residence_geometry.refs[index] for index in selected),
    )


def _centerline_normals(centers) -> tuple[tuple[float, float, float], ...]:
    points = np.asarray(centers, dtype=float)
    normals = []
    for index in range(len(points)):
        if index == 0:
            tangent = points[1] - points[0]
        elif index == len(points) - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[index + 1] - points[index - 1]
        if not np.any(tangent):
            tangent = np.array([0.0, 0.0, 1.0])
        normals.append(tangent)
    return _points(normals)


def component_centerline_geometry(source, component) -> tuple[SphereGeometry, int]:
    """Return an ordered channel skeleton whose stations reference tetrahedra."""
    data = getattr(source, 'dfnd', source)
    skeleton = channel_skeleton(data.raw, component.raw_record)
    if skeleton is None:
        return SphereGeometry((), (), 'nm', ()), -1
    records = select_tetrahedra(source, tetrahedron_ids=skeleton['tetra_path'])
    by_id = {int(record['tetrahedron_id']): record for record in records}
    refs = tuple(
        _component_tetrahedron_ref(by_id[int(tetrahedron_id)], component)
        for tetrahedron_id in skeleton['tetra_path']
    )
    refs = tuple(
        EntityRef(
            kind='centerline_station',
            entity_id=ref.entity_id,
            tetrahedron_ids=ref.tetrahedron_ids,
            atom_indices=ref.atom_indices,
            atom_index_space=ref.atom_index_space,
            support_key=ref.support_key,
            component_key=ref.component_key,
        )
        for ref in refs
    )
    geometry = SphereGeometry(
        tuple(skeleton['centers']), tuple(skeleton['station_radii']), 'nm', refs
    )
    return geometry, int(skeleton['station_bottleneck_index'])


def centerline_ring_geometry(source, component) -> RingGeometry:
    """Return one oriented clearance ring per centerline station."""
    geometry, _ = component_centerline_geometry(source, component)
    if not geometry.centers:
        return RingGeometry((), (), (), 'nm', ())
    return RingGeometry(
        geometry.centers,
        _centerline_normals(geometry.centers),
        geometry.radii,
        geometry.unit,
        geometry.refs,
    )


def mouth_ring_geometry(source, component) -> RingGeometry:
    """Return one oriented ring per external link of a component."""
    data = getattr(source, 'dfnd', source)
    mesh = _dfnd_mesh(source)
    coords = np.asarray(mesh.atoms.coords, dtype=float)
    global_to_local = {
        int(global_id): local for local, global_id in enumerate(mesh.atoms.index_map)
    }
    links = {
        link['external_link_id']: link for link in data.raw.get('external_links', [])
    }
    component_center = (
        np.asarray(component.center, dtype=float)
        if component.center is not None
        else None
    )
    centers, normals, radii, refs = [], [], [], []
    for link_id in getattr(component, 'external_link_ids', ()):
        link = links.get(link_id)
        if link is None:
            continue
        local = [
            global_to_local[int(atom)]
            for atom in link.get('atom_indices', ())
            if int(atom) in global_to_local
        ]
        if not local:
            continue
        center = coords[local].mean(axis=0)
        normal = (
            center - component_center
            if component_center is not None
            else np.array([0.0, 0.0, 1.0])
        )
        if not np.any(normal):
            normal = np.array([0.0, 0.0, 1.0])
        centers.append(center)
        normals.append(normal)
        radii.append(link.get('R_gate_min', 0.1))  # nm fallback (~1 angstrom)
        refs.append(
            EntityRef(
                kind='external_link',
                entity_id=link.get('external_link_key', link_id),
                atom_indices=tuple(
                    int(value) for value in link.get('atom_indices', ())
                ),
                support_key=link.get('external_link_support_key'),
                component_key=component.component_key,
            )
        )
    return RingGeometry(
        tuple(centers), tuple(normals), tuple(radii), 'nm', tuple(refs)
    )


def scaffold_geometry(source, component) -> SegmentGeometry:
    """Return a dry-component MST with canonical global-atom-pair identity."""
    from scipy.sparse.csgraph import minimum_spanning_tree
    from scipy.spatial.distance import pdist, squareform

    mesh = _dfnd_mesh(source)
    coords = np.asarray(mesh.atoms.coords, dtype=float)
    global_to_local = {
        int(global_id): local for local, global_id in enumerate(mesh.atoms.index_map)
    }
    global_atoms = [
        int(value) for value in component.atom_indices if int(value) in global_to_local
    ]
    if len(global_atoms) < 2:
        return SegmentGeometry((), (), 'nm', ())
    local_atoms = [global_to_local[value] for value in global_atoms]
    points = coords[local_atoms]
    mst = minimum_spanning_tree(squareform(pdist(points))).tocoo()
    starts, ends, refs = [], [], []
    for row, col in zip(mst.row, mst.col, strict=True):
        pair = tuple(sorted((global_atoms[int(row)], global_atoms[int(col)])))
        starts.append(points[int(row)])
        ends.append(points[int(col)])
        refs.append(
            EntityRef(
                kind='scaffold_edge',
                entity_id=pair,
                atom_indices=pair,
                support_key=component.support_key,
                component_key=component.component_key,
            )
        )
    return SegmentGeometry(tuple(starts), tuple(ends), 'nm', tuple(refs))


def _face_ref(face: dict[str, Any]) -> EntityRef:
    owner = int(face['owner_tetrahedron_id'])
    neighbor = int(face.get('neighbor_tetrahedron_id', -1))
    return EntityRef(
        kind='face',
        entity_id=face.get('face_id'),
        tetrahedron_ids=tuple(
            tetrahedron_id
            for tetrahedron_id in (owner, neighbor)
            if tetrahedron_id >= 0
        ),
        atom_indices=tuple(
            atom_indices(face.get('atom_indices', ()), space=MOLECULAR_SYSTEM)
        ),
    )


def dfn_graph_segments(
    source,
    tetrahedron_ids,
    *,
    mouth_stub_nm: float = 0.2,  # cylinder length beyond the boundary face (~2 angstrom)
    include_mouths: bool = True,
) -> tuple[SegmentGeometry, SegmentGeometry]:
    """Return canonical internal transit links and external mouth stubs."""
    selected_ids = {int(value) for value in tetrahedron_ids}
    centers = tetrahedron_centers(source, sorted(selected_ids))
    center_by_id = {
        int(ref.entity_id): np.asarray(point)
        for point, ref in zip(centers.coordinates, centers.refs, strict=True)
    }
    coords = np.asarray(_dfnd_mesh(source).atoms.coords, dtype=float)
    edge_starts, edge_ends, edge_refs = [], [], []
    mouth_starts, mouth_ends, mouth_refs = [], [], []

    for face in select_faces(source):
        owner = int(face['owner_tetrahedron_id'])
        neighbor = int(face.get('neighbor_tetrahedron_id', -1))
        if owner not in selected_ids:
            continue
        if neighbor >= 0:
            if (
                neighbor in selected_ids
                and owner < neighbor
                and face.get(
                    'transit_edge', face.get('permeability_state') == 'permeable'
                )
            ):
                edge_starts.append(center_by_id[owner])
                edge_ends.append(center_by_id[neighbor])
                edge_refs.append(_face_ref(face))
            continue
        if not include_mouths or face.get('permeability_state') != 'permeable':
            continue

        local_atoms = [int(value) for value in face.get('face_atoms_local', ())]
        if len(local_atoms) != 3:
            continue
        triangle = coords[local_atoms]
        normal = np.cross(triangle[1] - triangle[0], triangle[2] - triangle[0])
        length = np.linalg.norm(normal)
        if length < 1e-9:
            continue
        normal = normal / length
        origin = center_by_id[owner]
        face_centroid = triangle.mean(axis=0)
        if np.dot(normal, face_centroid - origin) < 0:
            normal = -normal
        mouth_starts.append(origin)
        mouth_ends.append(face_centroid + normal * mouth_stub_nm)
        mouth_refs.append(_face_ref(face))

    return (
        SegmentGeometry(
            tuple(edge_starts), tuple(edge_ends), 'nm', tuple(edge_refs)
        ),
        SegmentGeometry(
            tuple(mouth_starts), tuple(mouth_ends), 'nm', tuple(mouth_refs)
        ),
    )


def tetrahedra_geometry(source, tetrahedron_ids=None) -> TetrahedraGeometry:
    """Return canonical tetrahedra and their mesh-local pick indices."""
    records = select_tetrahedra(source, tetrahedron_ids=tetrahedron_ids)
    if tetrahedron_ids is not None:
        requested = (
            [int(tetrahedron_ids)]
            if isinstance(tetrahedron_ids, int)
            else [int(value) for value in tetrahedron_ids]
        )
        by_id = {int(record['tetrahedron_id']): record for record in records}
        records = [by_id[value] for value in requested if value in by_id]
    mesh = getattr(getattr(source, 'dfnd', source), 'mesh', None)
    coords = None if mesh is None else np.asarray(mesh.atoms.coords, dtype=float)
    quads, tetra_coords, refs = [], [], []
    for record in records:
        quad = tuple(int(value) for value in record.get('local_atom_indices', ()))
        if len(quad) != 4:
            continue
        tetrahedron_id = int(record['tetrahedron_id'])
        quads.append(quad)
        if coords is not None:
            tetra_coords.append(coords[list(quad)])
        refs.append(
            EntityRef(
                kind='tetrahedron',
                entity_id=tetrahedron_id,
                tetrahedron_ids=(tetrahedron_id,),
                atom_indices=tuple(
                    atom_indices(record.get('atom_indices', ()), space=MOLECULAR_SYSTEM)
                ),
            )
        )
    return TetrahedraGeometry(
        tuple(tetra_coords), tuple(quads), MESH_LOCAL, 'nm', tuple(refs)
    )


def face_geometry(
    source,
    tetrahedron_ids=None,
    *,
    face_ids=None,
    permeability_states=None,
) -> IndexedTriangleGeometry:
    """Return canonical DFND faces touching selected tetrahedra."""
    selected = (
        None if tetrahedron_ids is None else {int(value) for value in tetrahedron_ids}
    )
    selected_faces = None if face_ids is None else {int(value) for value in face_ids}
    try:
        coords = np.asarray(_dfnd_mesh(source).atoms.coords, dtype=float)
    except ValueError:
        coords = None
    triangles, triplets, refs = [], [], []
    for face in select_faces(source, permeability_state=permeability_states):
        if (
            selected_faces is not None
            and int(face.get('face_id', -1)) not in selected_faces
        ):
            continue
        owner = int(face['owner_tetrahedron_id'])
        neighbor = int(face.get('neighbor_tetrahedron_id', -1))
        if selected is not None and owner not in selected and neighbor not in selected:
            continue
        triplet = tuple(int(value) for value in face.get('face_atoms_local', ()))
        if len(triplet) != 3:
            continue
        triplets.append(triplet)
        if coords is not None:
            triangles.append(coords[list(triplet)])
        refs.append(_face_ref(face))
    return IndexedTriangleGeometry(
        tuple(triangles), tuple(triplets), MESH_LOCAL, 'nm', tuple(refs)
    )


def edge_geometry(source, tetrahedron_ids=None) -> IndexedEdgeGeometry:
    """Return canonical DFND edges touching selected tetrahedra."""
    try:
        coords = np.asarray(_dfnd_mesh(source).atoms.coords, dtype=float)
    except ValueError:
        coords = None
    segments, pairs, refs = [], [], []
    for edge in select_edges(source, tetrahedron_ids=tetrahedron_ids):
        pair = tuple(int(value) for value in edge.get('local_atom_indices', ()))
        if len(pair) != 2:
            continue
        pairs.append(pair)
        if coords is not None:
            segments.append(coords[list(pair)])
        refs.append(
            EntityRef(
                kind='edge',
                entity_id=edge.get('edge_id'),
                tetrahedron_ids=tuple(
                    int(value) for value in edge.get('tetrahedron_ids', ())
                ),
                atom_indices=tuple(
                    atom_indices(edge.get('atom_indices', ()), space=MOLECULAR_SYSTEM)
                ),
            )
        )
    return IndexedEdgeGeometry(
        tuple(segments), tuple(pairs), MESH_LOCAL, 'nm', tuple(refs)
    )
