from typing import Any
import numpy as np
import molsysmt as msm
from . import pyunitwizard as puw
from .topography.Topography import Topography
from ._private.arg_digestion import arg_digest
from ._private.smonitor import signal
from scipy.spatial import cKDTree

@signal(tags=["api", "topography"])
@arg_digest()
def get_topography(molecular_system: Any, method: str = 'pocketeer', selection: str = 'all',
                   structure_indices: int | list[int] = 0, syntax: str = 'MolSysMT',
                   engine: str | None = None, structure_index: int | list[int] | None = None,
                   skip_digestion: bool = False, **kwargs) -> Topography:
    """
    Generate a Topography object from a molecular system using a specified method.
    """

    if engine is not None:
        method = engine

    if structure_index is not None:
        structure_indices = structure_index

    method_lower = method.lower()
    
    if method_lower == 'pocketeer':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_pocketeer(topo, **kwargs)

    elif method_lower in ['fpocket', 'fpocket4']:
        from .third_party.fpocket._native_impl import fpocket4
        topo = fpocket4(molecular_system, selection=selection, structure_indices=structure_indices, **kwargs)

    elif method_lower == 'alphaspace2':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_alphaspace2(topo, **kwargs)

    elif method_lower == 'castp':
        backend = kwargs.pop('backend', 'native')
        server = kwargs.pop('server', None)

        if str(backend).lower() == 'native' and server is None:
            topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
            topo = _run_castp(topo, **kwargs)
        else:
            from .third_party.castp.api import get_topography as get_castp_topography

            topo = get_castp_topography(
                molecular_system,
                backend=backend,
                server=server,
                selection=selection,
                structure_indices=structure_indices,
                **kwargs,
            )

    elif method_lower == 'castpfold':
        from .third_party.castp.api import get_topography as get_castp_topography

        topo = get_castp_topography(
            molecular_system,
            backend='server',
            server='castpfold',
            selection=selection,
            structure_indices=structure_indices,
            **kwargs,
        )

    elif method_lower == 'castp3':
        from .third_party.castp.api import get_topography as get_castp_topography

        topo = get_castp_topography(
            molecular_system,
            backend='server',
            server='castp3',
            selection=selection,
            structure_indices=structure_indices,
            **kwargs,
        )

    elif method_lower == 'pycasta':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        topo = _run_pycasta(topo, **kwargs)

    elif method_lower == 'dfnd':
        topo = Topography(molecular_system=molecular_system, selection=selection, structure_indices=structure_indices)
        from .dfnd.api import dfnd
        topo = dfnd(topo, **kwargs)

    else:
        raise ValueError(
            f"Unknown method {method!r}. Supported: 'pocketeer', 'fpocket', "
            "'alphaspace2', 'castp', 'castpfold', 'pycasta', 'dfnd'."
        )

    return topo

def _run_pocketeer(topo: Topography, **kwargs) -> Topography:
    implementation = kwargs.pop('implementation', 'native').lower()
    if implementation not in {'wrapper', 'native', 'topomt'}:
        raise ValueError("implementation must be 'wrapper', 'native' or 'topomt'")

    from .third_party.pocketeer.api import get_topography as get_pocketeer_topography

    return get_pocketeer_topography(
        topo.molecular_system,
        backend='library' if implementation == 'wrapper' else 'native',
        selection=topo.selection,
        structure_indices=topo.structure_indices,
        **kwargs,
    )

def _run_alphaspace2(topo: Topography, min_vertices: int = 20, **kwargs) -> Topography:
    implementation = kwargs.pop('implementation', 'native').lower()
    if implementation not in {'wrapper', 'native', 'topomt'}:
        raise ValueError("implementation must be 'wrapper', 'native' or 'topomt'")

    from .third_party.alphaspace2.library import get_topography as get_library_topography
    from .third_party.alphaspace2.native import _state_to_pocket_records, alphaspace2
    from .features.Pocket import Pocket

    if implementation == 'wrapper':
        return get_library_topography(
            topo.molecular_system,
            selection=topo.selection,
            structure_indices=topo.structure_indices,
            min_vertices=min_vertices,
            **kwargs,
        )

    result = alphaspace2(
        topo.molecular_system,
        selection=topo.selection,
        structure_indices=topo.structure_indices,
        return_atom_indices=True,
        return_state=True,
        **kwargs,
    )

    if len(result) == 6:
        clusters, vertices, radii, contacts, atom_indices, state = result
    else:
        clusters, vertices, radii, contacts, atom_indices = result
        state = None

    if state is not None:
        pocket_records = _state_to_pocket_records(state)
        for pocket_record in pocket_records:
            if len(pocket_record['alpha_sphere_centers']) < min_vertices:
                continue

            pocket_feature = Pocket(
                atom_indices=pocket_record['atom_indices'],
                center=puw.quantity(pocket_record['center'], 'nm'),
                volume=puw.quantity(pocket_record['volume'], 'nm**3'),
                score=pocket_record['score'],
                source='alphaspace2',
                source_id=f"alphaspace2:{pocket_record['pocket_index']}",
                alpha_sphere_centers=puw.quantity(pocket_record['alpha_sphere_centers'], 'nm'),
                alpha_sphere_radii=puw.quantity(pocket_record['alpha_sphere_radii'], 'nm'),
                beta_centers=puw.quantity(pocket_record['beta_centers'], 'nm'),
                beta_scores=pocket_record['beta_scores'],
                nonpolar_volume=puw.quantity(pocket_record['nonpolar_volume'], 'nm**3'),
                is_contact=pocket_record['is_contact'],
            )

            topo.add_feature(pocket_feature)

        return topo

    atom_coords = msm.get(topo.molecular_system, selection=atom_indices, coordinates=True)[0]
    atom_coords = puw.get_value(atom_coords, to_unit='nm')
    tree = cKDTree(atom_coords)

    for i, cluster in enumerate(clusters):
        if len(cluster) < min_vertices:
            continue

        cluster_vertices = vertices[cluster]
        cluster_radii = radii[cluster]
        centroid = np.mean(cluster_vertices, axis=0) if len(cluster_vertices) > 0 else None

        involved_atoms = set()
        for vertex, radius in zip(cluster_vertices, cluster_radii):
            near_atoms = tree.query_ball_point(vertex, radius + 0.02)
            involved_atoms.update([atom_indices[idx] for idx in near_atoms])

        if not involved_atoms:
            continue

        pocket_feature = Pocket(
            atom_indices=sorted(list(involved_atoms)),
            center=centroid,
            source='alphaspace2',
            source_id=f'alphaspace2:{i}',
        )

        topo.add_feature(pocket_feature)

    return topo

def _run_castp(topo: Topography, **kwargs) -> Topography:
    from .third_party.castp._native_impl import castp

    feature_records, mesh = castp(
        topo.molecular_system,
        selection=topo.selection,
        structure_indices=topo.structure_indices,
        **kwargs,
    )

    del mesh

    for feature_index, record in enumerate(feature_records, start=1):
        feature_type = record.get('feature_type', 'pocket')
        source_id = record.get('source_id', f'castp:{feature_type}:{feature_index}')

        parent_feature_id = topo.add_new_feature(
            feature_type=feature_type,
            atom_indices=sorted(record.get('atom_indices', [])),
            source='castp',
            source_id=source_id,
        )
        parent_feature = topo[parent_feature_id]

        if 'center' in record and record['center'] is not None:
            parent_feature.center = puw.quantity(record['center'], 'angstroms')
        if 'area' in record and record['area'] is not None:
            parent_feature.area = puw.quantity(record['area'], 'angstroms**2')
        if 'volume' in record and record['volume'] is not None:
            parent_feature.volume = puw.quantity(record['volume'], 'angstroms**3')
        if 'mouth_area' in record and record['mouth_area'] is not None:
            parent_feature.mouth_area = puw.quantity(record['mouth_area'], 'angstroms**2')
        if 'mouth_perimeter' in record and record['mouth_perimeter'] is not None:
            parent_feature.mouth_perimeter = puw.quantity(record['mouth_perimeter'], 'angstroms')
        if 'n_mouths' in record:
            parent_feature.n_mouths = record['n_mouths']
        if 'iT' in record:
            parent_feature.iT = record['iT']
        if 'tetrahedron_indices' in record:
            parent_feature.tetrahedron_indices = record['tetrahedron_indices']
        if 'properties' in record:
            parent_feature.properties = record['properties']
        if 'score' in record:
            parent_feature.score = record['score']

        for mouth in record.get('mouths', []):
            mouth_feature_id = topo.add_new_feature(
                feature_type='mouth',
                atom_indices=sorted(mouth.get('atom_indices', [])),
                source='castp',
                source_id=f'{source_id}:mouth:{mouth["id"]}',
                area=puw.quantity(mouth.get('area', 0.0), 'angstroms**2'),
            )
            topo.connect_features(mouth_feature_id, parent_feature_id)

    return topo

def _run_pycasta(topo: Topography, **kwargs) -> Topography:
    implementation = kwargs.pop('implementation', 'native').lower()
    if implementation not in {'wrapper', 'native', 'topomt'}:
        raise ValueError("implementation must be 'wrapper', 'native' or 'topomt'")

    from .third_party.pycasta.api import get_topography as get_pycasta_topography

    return get_pycasta_topography(
        topo.molecular_system,
        backend='library' if implementation == 'wrapper' else 'native',
        selection=topo.selection,
        structure_indices=topo.structure_indices,
        **kwargs,
    )
