"""Preserve original ROI-restricted grid volume, separately from cavity detection."""

import csv
import io
import math
import re

import numpy as np

from topomt.provider_output import ProviderRun, _canonical_json
from topomt.third_party._protocol import (
    artifact,
    finite,
    measurement,
    pdb_points,
    points_geometry,
)
from topomt.third_party._saved_json import read_json
from topomt.third_party._specialist import validate_inputs
from topomt.third_party.output import ProviderGeometry, ProviderRecord

from .output import PovmeOutput


def _points_npy(data: bytes) -> np.ndarray:
    stream = io.BytesIO(data)
    version = np.lib.format.read_magic(stream)
    if version not in {(1, 0), (2, 0)}:
        raise ValueError('Unsupported original POVME NPY format')
    reader = (
        np.lib.format.read_array_header_1_0
        if version == (1, 0)
        else np.lib.format.read_array_header_2_0
    )
    shape, fortran, dtype = reader(stream)
    if (
        len(shape) != 2
        or type(shape[0]) is not int
        or shape[0] < 0
        or shape[1] != 3
        or dtype != np.dtype('float64')
        or fortran
        or shape[0] * 24 != len(data) - stream.tell()
    ):
        raise ValueError('POVME point-field header/data dimensions disagree')
    return np.frombuffer(data, dtype=dtype, offset=stream.tell()).reshape(shape)


def parse_output(run: ProviderRun) -> PovmeOutput:
    """Keep one original analyzed region, including an evaluated zero volume."""
    receipt = read_json(artifact(run, 'engine_identity.json'), provider='povme')
    if (
        receipt.get('schema') != 'topomt.povme-worker@1'
        or receipt.get('status') != 'completed'
        or receipt.get('version') not in {'2.2.2', '2.2.2+uibcdf.1'}
    ):
        raise ValueError('Unsupported or incomplete original POVME worker receipt')
    if receipt.get('protocol_units') != {
        'length': 'angstroms',
        'volume': 'angstroms**3',
    }:
        raise ValueError('POVME receipt has unsupported physical units')
    config = receipt['configuration']
    if (
        config.get('use_ray') is not False
        or type(config.get('n_cores')) is not int
        or config['n_cores'] != 1
    ):
        raise ValueError('POVME receipt must establish serial execution')
    validate_inputs(run, ('configuration.json',))
    if run.metadata.get('adapter_protocol') == 'topomt.original-local@1':
        requested = read_json(
            run.get_artifact('input/configuration.json'), provider='povme'
        )
        if (
            _canonical_json({key: config.get(key) for key in requested})
            != _canonical_json(requested)
            or run.metadata.get('version') != receipt['version']
        ):
            raise ValueError(
                'POVME saved configuration/version disagrees with original execution'
            )
    rows = list(csv.reader(io.StringIO(artifact(run, 'volumes.csv').decode())))
    if (
        len(rows) != 2
        or rows[0] != ['frame_idx', 'volume']
        or len(rows[1]) != 2
        or rows[1][0] != '1'
    ):
        raise ValueError('POVME requires one complete original frame-volume row')
    volume = finite(rows[1][1], nonnegative=True)
    returned = receipt.get('original_result')
    if (
        not isinstance(returned, dict)
        or set(returned) != {'1'}
        or finite(returned['1'], nonnegative=True) != volume
    ):
        raise ValueError('POVME original returned and saved volumes disagree')
    step = finite(config['grid_spacing'], nonnegative=True)
    if step <= 0:
        raise ValueError('POVME grid spacing must be positive')
    initial = _points_npy(artifact(run, 'point_field.pdb.npy'))
    if (
        initial.ndim != 2
        or initial.shape[1] != 3
        or not np.isfinite(initial).all()
        or type(receipt['initial_point_count']) is not int
        or len(initial) != receipt['initial_point_count']
    ):
        raise ValueError('POVME original input grid and receipt disagree')
    geometries: tuple[ProviderGeometry, ...] = ()
    status = receipt['point_support_status']
    if status == 'reported':
        original = artifact(run, 'frame_1.pdb')
        heading = re.match(
            rb'REMARK Frame 1\nREMARK Volume = (\S+) Cubic Angstroms\n', original
        )
        if heading is None or finite(heading[1], nonnegative=True) != volume:
            raise ValueError('POVME point-field volume/header units disagree')
        if not original.rstrip().endswith(b'END'):
            raise ValueError('POVME retained-point PDB is incomplete')
        points = [row[2] for row in pdb_points(original)]
        count = len(points)
        geometries = (
            points_geometry(
                'retained_grid_points',
                points,
                'Original surviving POVME grid centers rounded to PDB precision; ROI-restricted sample support, not a closed continuous cavity boundary',
            ),
        )
    elif status == 'not_written_by_original':
        if 'output/frame_1.pdb' in dict(run.artifacts):
            raise ValueError('POVME point-support availability disagrees with files')
        count = len(initial)
    else:
        raise ValueError('Unknown original POVME point-support status')
    if not math.isclose(volume, count * step**3, rel_tol=1e-12, abs_tol=1e-9):
        raise ValueError('POVME original point count and grid volume disagree')
    diagnostics = read_json(artifact(run, 'diagnostics.json'), provider='povme')
    if diagnostics != {'errors': []}:
        raise ValueError('POVME error fallback is not an evaluated-empty result')
    record = ProviderRecord(
        'frame:1',
        'region',
        run,
        atom_role='unavailable_region_atom_map',
        _fields={
            'configuration': config,
            'protocol_units': receipt['protocol_units'],
            'point_support_status': status,
            'external_measurements': {
                'volume': measurement(
                    run,
                    volume,
                    'angstroms**3',
                    'volume',
                    'volumes.csv',
                    'Original number of surviving ROI grid points times grid spacing cubed; atom-surface cutoff, optional hull and seed/connectivity rules are retained, without automatic pocket detection',
                )
            },
        },
        _geometries=geometries,
    )
    return PovmeOutput(run, (record,))
