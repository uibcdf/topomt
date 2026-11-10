"""Receive the bounded physical source panel without rewriting frozen evidence."""

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any


def capture_case(directory: Path, protocol_file: Path) -> dict[str, Any]:
    """Capture actual public observations and replay the retained reference.

    Parameters
    ----------
    directory, protocol_file : Path
        Frozen case directory and predeclared physical-panel protocol.

    Returns
    -------
    dict
        Detached study evidence, explicit raw nm schema and exact source identity.

    Raises
    ------
    ValueError
        Input identity or public source mapping differs from the protocol.
    """
    directory = directory.resolve()
    protocol_bytes = protocol_file.read_bytes()
    protocol = json.loads(protocol_bytes)
    case = directory.name
    input_file = directory / f'artifacts/{case}_v1/input.json'
    digest = hashlib.sha256(input_file.read_bytes()).hexdigest()
    if protocol['case'] != case or digest != protocol['input_sha256']:
        raise ValueError('Frozen input identity differs from the physical protocol')
    helper = directory.parent / 'public_study.py'
    spec = importlib.util.spec_from_file_location('physical_public_study', helper)
    if spec is None or spec.loader is None:
        raise ValueError('Public receiving helper is unavailable')
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    queries = []
    for probe in protocol['probe_angstroms']:
        topo = study.receive(directory, probe)
        types = sorted(feature.feature_type for feature in topo.values())
        queries.append(
            {
                'probe_angstroms': probe,
                'feature_types': types,
                'physical': topo.dfnd.raw['boundary_connectivity'],
                'components': topo.dfnd.raw['wet_components'],
                'tetrahedra_source_atom_indices': {
                    str(row['tetrahedron_id']): row['atom_indices']
                    for row in topo.dfnd.raw['tetrahedra']
                },
                'query': topo.dfnd.raw['parameters']['query'],
                'scientific_attribution': topo.attribution,
            }
        )
    from importlib.metadata import version

    import topomt

    root = Path(__file__).resolve().parents[2]
    return {
        'schema': 'topomt.benchlab.physical-source-receiving/1',
        'issue': 'uibcdf/topomt#151',
        'case': case,
        'source_revision': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=root, text=True
        ).strip(),
        'package_version_observed': topomt.__version__,
        'dependencies': {
            name: version(name)
            for name in ('numpy', 'scipy', 'molsysmt', 'pyunitwizard')
        },
        'input_sha256': digest,
        'protocol_sha256': hashlib.sha256(protocol_bytes).hexdigest(),
        'reference_verification': study.reference(directory),
        'queries': queries,
        'scope': 'Source-bound receiving of frozen controls, not a public installation, support matrix or held-out benchmark',
    }
