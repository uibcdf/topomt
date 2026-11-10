"""Freeze actual public carrier supports before independent volume integration."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np


def study_module(directory: Path) -> Any:
    """Load the maintained portable public receiving helper for this collection."""
    spec = importlib.util.spec_from_file_location(
        'volume_public_study', directory.parent / 'public_study.py'
    )
    if spec is None or spec.loader is None:
        raise ValueError('The public study helper is unavailable')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def origin_component(topo: Any) -> Any:
    """Select an actual wet component containing the original coordinate origin.

    The direct simplex test selects a declared integration support; it does not
    certify that this carrier equals the physical origin-connected free region.
    """
    network = topo.dfnd.network
    matches = []
    for component in topo.dfnd.dfn.components.values():
        if component.side != 'wet':
            continue
        for node in component.resident_node_indices:
            cell = network.atom_coords[network.tetra_atoms[node]]
            bary = np.linalg.solve((cell[1:] - cell[0]).T, -cell[0])
            if np.min(bary) >= -1e-10 and bary.sum() <= 1 + 1e-10:
                matches.append(component)
                break
    if len(matches) != 1:
        raise ValueError('The original origin must select exactly one wet support')
    return matches[0]


def prepare_case(
    directory: Path, probes: list[float], regions: list[str]
) -> dict[str, Any]:
    """Freeze source-mapped domains and numerical criteria before new integration.

    Parameters
    ----------
    directory : Path
        Existing unchanged synthetic case directory.
    probes : list of float
        Explicit known control probes in angstroms.
    regions : list of str
        Selected resident/transit supports to receive.

    Returns
    -------
    dict
        Protocol with original input identity and actual selected tetrahedra.
        No new volume estimate, sample or reference answer is an input.

    Raises
    ------
    ValueError
        A support is unavailable or the source correspondence is inconsistent.
    """
    directory = directory.resolve()
    root = Path(__file__).resolve().parents[2]
    common_file = root / 'devguide/DFND/volume_validation_protocol_v1.json'
    common = json.loads(common_file.read_bytes())
    input_file = directory / f'artifacts/{directory.name}_v1/input.json'
    digest = hashlib.sha256(input_file.read_bytes()).hexdigest()
    if digest != common['input_sha256'][directory.name]:
        raise ValueError('The volume input differs from the common frozen protocol')
    study = study_module(directory)
    domains = []
    source_atoms = None
    for probe in probes:
        topo = study.receive(directory, probe)
        component = origin_component(topo)
        source_atoms = topo.input_context.atom_indices.tolist()
        for region in regions:
            if region not in {'resident', 'transit'}:
                raise ValueError('Unknown finite carrier support')
            nodes = list(component.resident_node_indices)
            if region == 'transit':
                nodes += list(component.transit_connector_node_indices)
            nodes = sorted(set(map(int, nodes)))
            if not nodes:
                raise ValueError('This frozen integration domain is empty')
            network = topo.dfnd.network
            domains.append(
                {
                    'id': f'{probe:g}A_{region}',
                    'probe_angstroms': probe,
                    'region': region,
                    'native_component_id_at_freeze': component.component_id,
                    'source_id_at_freeze': topo.input_context.source_id,
                    'result_key_at_freeze': topo.dfnd.raw['parameters']['result_key'],
                    'tetrahedron_ids_at_freeze': nodes,
                    'tetrahedra_source_atom_indices': network.atom_indices_map[
                        network.tetra_atoms[nodes]
                    ].tolist(),
                    'query_at_freeze': topo.dfnd.raw['parameters']['query'],
                }
            )
    return {
        'schema': 'topomt.benchlab.volume-domain-protocol/1',
        'date': '2026-11-10',
        'issue': 'uibcdf/topomt#75',
        'case': directory.name,
        'input_sha256': digest,
        'common_protocol_sha256': hashlib.sha256(common_file.read_bytes()).hexdigest(),
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'source_atom_indices': source_atoms,
        'domains': domains,
        'reference_controls': common['independent_reference'],
        'native_controls': {
            'method': 'mc',
            'n_samples': 40000,
            'seed': 0,
            'confidence_level': 0.95,
        },
        'observables': ['carrier', 'bare_empty', 'probe_center'],
        'scope': 'Frozen native integration supports, not independent truth for global free-space membership; no global accessible-volume claim',
    }
