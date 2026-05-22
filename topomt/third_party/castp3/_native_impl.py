"""Native CASTp implementation scaffold built from the classical workflow."""

from typing import Dict, List, Tuple

from topomt import pyunitwizard as puw
from topomt._private.smonitor import signal
from topomt.third_party.castp3.core.castp_core import (
    build_castp_feature_records,
    build_castp_geometry,
)
from topomt.tools.features.pockets import get_physicochemical_properties


def _to_angstroms(value) -> float:
    if puw.is_quantity(value):
        return float(puw.get_value(value, to_unit='angstroms'))

    try:
        quantity = puw.quantity(value, 'angstroms')
        return float(puw.get_value(quantity, to_unit='angstroms'))
    except Exception:
        return float(value)


def _feature_record_type(feature_type: str) -> str:
    """Return the canonical record label for a CASTp feature type."""

    if feature_type == 'branched_channel':
        return 'BranchedChannel'
    return feature_type.capitalize()


def _component_to_record(
    component: Dict,
    molsys,
    feature_type: str,
    component_index: int,
) -> Dict:
    def _sorted_int_tuples(values, tuple_size: int) -> List[Tuple[int, ...]]:
        tuples = []
        for value in values:
            tuples.append(
                tuple(
                    int(item)
                    for item in sorted(value[:tuple_size])
                )
            )
        return sorted(tuples)

    atom_indices = sorted(int(atom_index) for atom_index in component.get('atom_indices', []))

    try:
        properties = get_physicochemical_properties(molsys, atom_indices)
    except Exception:
        properties = {}

    topological_mouths = []
    for mouth in component.get('mouths', []):
        topological_mouths.append(
            {
                'id': int(mouth['id']),
                'atom_indices': sorted(
                    int(atom_index) for atom_index in mouth.get('atom_indices', [])
                ),
                'area': float(mouth.get('area', 0.0)),
                'perimeter': float(mouth.get('perimeter', 0.0)),
                'faces': list(mouth.get('faces', [])),
                'triangle_indices': sorted(
                    int(triangle_index) for triangle_index in mouth.get('triangle_indices', [])
                ),
            }
        )

    mouths = []
    if topological_mouths:
        mouth_atom_indices = sorted(
            {
                int(atom_index)
                for mouth in topological_mouths
                for atom_index in mouth.get('atom_indices', [])
            }
        )
        mouth_faces = [
            face
            for mouth in topological_mouths
            for face in mouth.get('faces', [])
        ]
        mouth_triangle_indices = sorted(
            {
                int(triangle_index)
                for mouth in topological_mouths
                for triangle_index in mouth.get('triangle_indices', [])
            }
        )
        mouths.append(
            {
                'id': 1,
                'atom_indices': mouth_atom_indices,
                'area': sum(float(mouth.get('area', 0.0)) for mouth in topological_mouths),
                'perimeter': sum(
                    float(mouth.get('perimeter', 0.0)) for mouth in topological_mouths
                ),
                'faces': mouth_faces,
                'triangle_indices': mouth_triangle_indices,
            }
        )

    return {
        'id': component_index,
        'feature_type': feature_type,
        'type': _feature_record_type(feature_type),
        'source': 'castp',
        'source_id': f'castp:{feature_type}:{component_index}',
        'iT': [
            int(index)
            for index in component.get('iT', component.get('tetrahedron_indices', []))
        ],
        'tetrahedron_indices': [int(index) for index in component.get('tetrahedron_indices', [])],
        'atom_indices': atom_indices,
        'boundary_atom_indices': sorted(
            int(atom_index) for atom_index in component.get('boundary_atom_indices', [])
        ),
        'component_atom_indices': sorted(
            int(atom_index) for atom_index in component.get('component_atom_indices', [])
        ),
        'experimental_peripheral_atom_indices': sorted(
            int(atom_index)
            for atom_index in component.get('experimental_peripheral_atom_indices', [])
        ),
        'center': component.get('center'),
        'area': float(component.get('area', 0.0)),
        'volume': float(component.get('volume', 0.0)),
        'score': float(component.get('score', component.get('volume', 0.0))),
        'n_mouths': int(component.get('n_mouths', 0)),
        'mouth_area': float(component.get('mouth_area', 0.0)),
        'mouth_perimeter': float(component.get('mouth_perimeter', 0.0)),
        'mouths': mouths,
        'topological_mouths': topological_mouths,
        'iF': _sorted_int_tuples(component.get('iF', []), 3),
        'rF': _sorted_int_tuples(component.get('rF', []), 3),
        'iE': _sorted_int_tuples(component.get('iE', []), 2),
        'rE': _sorted_int_tuples(component.get('rE', []), 2),
        'iV': sorted(int(vertex_index) for vertex_index in component.get('iV', [])),
        'rV': sorted(int(vertex_index) for vertex_index in component.get('rV', [])),
        'properties': properties,
    }


@signal(tags=['method', 'castp', 'native'])
def castp(
    molecular_system,
    selection: str = 'molecule_type in ["protein", "peptide"]',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    radii_model: str = 'castp_param',
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
    sea_level: float = 10.0,
    epsilon: float = 1e-6,
    alpha_rank: int | None = None,
    beta_rank: int | None = None,
    probe_limited_depth: bool = False,
    peripheral_atom_expansion_steps: int = 0,
    alpha_boundary_epsilon_length: float = 0.0,
    alpha_boundary_face_epsilon_rank: int = 0,
) -> Tuple[List[Dict], object]:
    """Detect topographic features through the native CASTp workflow scaffold."""

    del syntax, skip_digestion, sea_level, epsilon

    probe_radius_angstroms = _to_angstroms(probe_radius)

    geometry = build_castp_geometry(
        molecular_system,
        selection=selection,
        structure_indices=structure_indices,
        solvent_radius=probe_radius_angstroms,
        radii_model=radii_model,
        alpha_boundary_epsilon_length=float(alpha_boundary_epsilon_length),
    )

    raw_feature_records = build_castp_feature_records(
        geometry,
        probe_radius=probe_radius_angstroms,
        alpha_rank=alpha_rank,
        beta_rank=beta_rank,
        probe_limited_depth=bool(probe_limited_depth),
        peripheral_atom_expansion_steps=int(peripheral_atom_expansion_steps),
        alpha_boundary_face_epsilon_rank=int(alpha_boundary_face_epsilon_rank),
    )

    feature_records = []
    for component in raw_feature_records:
        feature_records.append(
            _component_to_record(
                component,
                molecular_system,
                feature_type=component['feature_type'],
                component_index=int(component['id']),
            )
        )
    feature_records.sort(key=lambda record: record['volume'], reverse=True)

    return feature_records, geometry.mesh
