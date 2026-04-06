"""Native CASTp implementation scaffold built from the classical workflow."""

from typing import Dict, List, Tuple

from topomt import pyunitwizard as puw
from topomt._private.smonitor import signal
from topomt.methods.castp_core import build_castp_feature_records, build_castp_geometry
from topomt.tools.features.pockets import get_physicochemical_properties


def _to_angstroms(value) -> float:
    if puw.is_quantity(value):
        return float(puw.get_value(value, to_unit='angstroms'))

    try:
        quantity = puw.quantity(value, 'angstroms')
        return float(puw.get_value(quantity, to_unit='angstroms'))
    except Exception:
        return float(value)


def _component_to_record(
    component: Dict,
    molsys,
    feature_type: str,
    component_index: int,
) -> Dict:
    atom_indices = sorted(int(atom_index) for atom_index in component.get('atom_indices', []))

    try:
        properties = get_physicochemical_properties(molsys, atom_indices)
    except Exception:
        properties = {}

    mouths = []
    for mouth in component.get('mouths', []):
        mouths.append(
            {
                'id': int(mouth['id']),
                'atom_indices': sorted(int(atom_index) for atom_index in mouth.get('atom_indices', [])),
                'area': float(mouth.get('area', 0.0)),
                'faces': list(mouth.get('faces', [])),
            }
        )

    return {
        'id': component_index,
        'feature_type': feature_type,
        'type': feature_type.capitalize(),
        'source': 'castp',
        'source_id': f'castp:{feature_type}:{component_index}',
        'tetrahedron_indices': list(component.get('tetrahedron_indices', [])),
        'atom_indices': atom_indices,
        'boundary_atom_indices': sorted(
            int(atom_index) for atom_index in component.get('boundary_atom_indices', [])
        ),
        'component_atom_indices': sorted(
            int(atom_index) for atom_index in component.get('component_atom_indices', [])
        ),
        'center': component.get('center'),
        'volume': float(component.get('volume', 0.0)),
        'score': float(component.get('score', component.get('volume', 0.0))),
        'n_mouths': int(component.get('n_mouths', 0)),
        'mouth_area': float(component.get('mouth_area', 0.0)),
        'mouths': mouths,
        'properties': properties,
    }


@signal(tags=['method', 'castp', 'native'])
def castp(
    molecular_system,
    selection: str = 'molecule_type == "protein"',
    structure_indices: int = 0,
    probe_radius: float = 1.4,
    radii_model: str = 'protor',
    syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
    sea_level: float = 10.0,
    epsilon: float = 1e-6,
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
    )

    raw_feature_records = build_castp_feature_records(
        geometry,
        probe_radius=probe_radius_angstroms,
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
