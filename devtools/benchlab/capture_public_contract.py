"""Receive the frozen three-case public/support panel without external engines."""

import hashlib
import json
from math import sqrt
from pathlib import Path
from typing import Any

from devtools.benchlab.capture_volume import study_module
from devtools.benchlab.public_contract import describe_public_contract


def capture_case(directory: Path, protocol_file: Path) -> dict[str, Any]:
    """Validate original input and inspect the predeclared public control rows.

    Parameters
    ----------
    directory : Path
        Frozen case directory with the original public receiving protocol.
    protocol_file : Path
        Common, committed public-contract protocol before receiving.

    Returns
    -------
    dict
        Detached actual observations, including marginal threshold outcomes.

    Raises
    ------
    ValueError
        Input identity, public support, relation or numerical units disagree.
    """
    directory = directory.resolve()
    protocol = json.loads(protocol_file.read_bytes())
    fixture = directory / f'artifacts/{directory.name}_v1/input.json'
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    if digest != protocol['input_sha256'][directory.name]:
        raise ValueError('Public receiving input differs from the frozen protocol')
    study = study_module(directory)
    controls = [
        {'name': f'control_{probe:g}A', 'probe_angstroms': probe}
        for probe in protocol['controls'][directory.name]
    ]
    if directory.name == 'regular_tetrahedron':
        for kind, radius in (
            ('gate', 5.3 / sqrt(3) - 1.7),
            ('residence', sqrt(6) * 5.3 / 4 - 1.7),
        ):
            delta = protocol['threshold_extension']['offset_angstroms']
            controls += [
                {'name': f'{kind}_{name}', 'probe_angstroms': radius + offset}
                for name, offset in [('below', -delta), ('at', 0), ('above', delta)]
            ]
    return {
        'schema': 'topomt.benchlab.public-contract-receiving/1',
        'case': directory.name,
        'protocol_sha256': hashlib.sha256(protocol_file.read_bytes()).hexdigest(),
        'input_sha256': digest,
        'controls': [
            {
                **control,
                'observation': describe_public_contract(
                    study.receive(directory, control['probe_angstroms'])
                ),
            }
            for control in controls
        ],
        'scope': protocol['qualification'],
    }
