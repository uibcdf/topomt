"""Decode original HOLE spherical profiles, preserving signed clearances."""

import math
import re

from topomt.provider_output import ProviderRun, _canonical_json
from topomt.third_party._protocol import artifact, finite, measurement, points_geometry
from topomt.third_party._specialist import validate_inputs
from topomt.third_party.output import ProviderRecord

from .output import HoleOutput

VERSION = '2.3.1'


def decode_report(text: str, spheres: str) -> dict:
    """Read the qualified spherical protocol; visual extension rows stay outside."""
    if (
        f'HOLE release {VERSION} ' not in text
        or not text.rstrip().endswith('HOLE: normal completion')
        or re.search(r'\bERROR\b|\*\*\*\*', text, re.I)
    ):
        raise ValueError('Unsupported, failed or incomplete original HOLE report')
    try:
        block = text.split('Control variables read:\n', 1)[1].split('\n\n', 1)[0]
        cards = {}
        for line in block.splitlines():
            key, *tokens = line.split()
            if key in cards:
                raise ValueError('Duplicate original HOLE input card')
            cards[key] = tokens
        if set(cards) != {
            'COORD',
            'RADIUS',
            'SPHPDB',
            'CPOINT',
            'CVECT',
            'SAMPLE',
            'ENDRAD',
            'RASEED',
            'SHORTO',
        }:
            raise ValueError('Unsupported HOLE calculation controls')
        query: dict = {
            'origin': [finite(x) for x in cards['CPOINT']],
            'direction': [finite(x) for x in cards['CVECT']],
            'sample_step': finite(cards['SAMPLE'][0], nonnegative=True),
            'end_radius': finite(cards['ENDRAD'][0], nonnegative=True),
            'random_seed': int(cards['RASEED'][0]),
            'length_unit': 'angstroms',
        }
        if (
            len(query['origin']) != 3
            or len(query['direction']) != 3
            or not math.isclose(
                sum(x * x for x in query['direction']), 1, abs_tol=1e-12
            )
        ):
            raise ValueError('Invalid original HOLE starting geometry')
        if (
            query['sample_step'] <= 0
            or query['end_radius'] <= 0
            or not 0 < query['random_seed'] <= 2147483647
            or cards['SHORTO'] != ['0']
        ):
            raise ValueError('Invalid original HOLE controls')
        atoms = re.findall(r'Have read\s+(\d+) atom records\.', text)
        if len(atoms) != 1 or int(atoms[0]) <= 0:
            raise ValueError('Missing original HOLE atom inventory')
        headings = list(
            re.finditer(r'^ cenxyz\.cvec\s+radius\s+cen_line_D.*$', text, re.M)
        )
        if len(headings) != 1:
            raise ValueError('Original HOLE profile heading is absent or ambiguous')
        rows = []
        for line in text[headings[0].end() :].splitlines()[1:]:
            if not line.strip():
                break
            match = re.fullmatch(
                r'\s*(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+\((sampled|mid-point)\)\s*', line
            )
            if match is None:
                raise ValueError('Malformed original HOLE profile row')
            rows.append(([finite(x) for x in match.groups()[:4]], match[5]))
        samples = [row for row, kind in rows if kind == 'sampled']
        midpoints = [row for row, kind in rows if kind == 'mid-point']
        if (
            not samples
            or len(midpoints) != len(samples) - 1
            or any(a[0][0] >= b[0][0] for a, b in zip(rows, rows[1:]))
        ):
            raise ValueError('Unordered or incomplete original HOLE profile')
        centers: dict = {}
        for line in spheres.splitlines():
            if not line.startswith('ATOM  '):
                continue
            if line[12:16].strip() != 'QSS' or line[17:20] != 'SPH':
                raise ValueError('Unsupported non-spherical HOLE point record')
            index = int(line[22:26])
            if index == -888:
                continue  # Original artificial end extensions for visualization.
            center = tuple(finite(line[start : start + 8]) for start in (30, 38, 46))
            radius = finite(line[54:60])
            if index in centers and centers[index] != (center, radius):
                raise ValueError('Conflicting original HOLE sample identifier')
            centers[index] = (center, radius)
        points = []
        for row in samples:
            candidates = [
                (point, radius)
                for point, radius in centers.values()
                if abs(sum(x * y for x, y in zip(point, query['direction'])) - row[0])
                <= 0.001
            ]
            if len(candidates) != 1 or abs(candidates[0][1] - row[1]) > 0.00501:
                raise ValueError('HOLE sphere and reported profile disagree')
            points.append(candidates[0][0])
        for a, b, left, right in zip(points, points[1:], samples, samples[1:]):
            if abs(math.dist(a, b) - (right[2] - left[2])) > 0.002:
                raise ValueError(
                    'HOLE sphere centers and centerline distances disagree'
                )
        tag = re.findall(r'Rmin=\s*(\S+)', text)
        if len(tag) != 1:
            raise ValueError('HOLE original minimum is absent')
        minimum = finite(tag[0])
        # HOGRAP reports its sampled-node minimum, separately from midpoint rows.
        if abs(minimum - min(row[1] for row in samples)) > 1e-5:
            raise ValueError('HOLE sampled profile and original minimum disagree')
    except (IndexError, KeyError, TypeError) as cause:
        raise ValueError('Incomplete original HOLE evidence') from cause
    profile = {}
    for label, values in [('sampled', samples), ('midpoints', midpoints)]:
        profile[label] = {
            name: {'value': [row[column] for row in values], 'unit': unit}
            for column, name, unit in [
                (0, 'coordinate', 'angstroms'),
                (1, 'radius', 'angstroms'),
                (2, 'signed_centerline_distance', 'angstroms'),
                (3, 'resistance_factor', 'angstroms**-1'),
            ]
        }
    return {
        'version': VERSION,
        'parameters': query,
        'atom_count': int(atoms[0]),
        'profile': profile,
        'points': points,
        'minimum_radius': minimum,
    }


def parse_output(run: ProviderRun) -> HoleOutput:
    """Return a sampled original path without asserting a swept free volume."""
    data = decode_report(
        artifact(run, 'stdout.txt').decode(), artifact(run, 'profile.sph').decode()
    )
    validate_inputs(run, ('control.in', 'radii.rad'))
    if run.metadata.get('adapter_protocol') == 'topomt.original-local@1':
        if (
            run.get_artifact('input/control.in').decode().strip()
            != artifact(run, 'stdout.txt')
            .decode()
            .split('Control variables read:\n', 1)[1]
            .split('\n\n', 1)[0]
            .strip()
        ):
            raise ValueError('HOLE captured control cards and original echo disagree')
        parameters = run.metadata.get('parameters')
        if (
            not isinstance(parameters, dict)
            or _canonical_json(data['parameters']) != _canonical_json(parameters)
            or data['version'] != run.metadata.get('version')
        ):
            raise ValueError('HOLE saved query/version disagrees with original output')
        count = sum(
            line.startswith(('ATOM  ', 'HETATM'))
            for line in run.get_artifact('input/input.pdb').decode().splitlines()
        )
        if count != data['atom_count']:
            raise ValueError('HOLE did not analyze every submitted atom')
    radii = data['profile']['sampled']['radius']['value']
    geometry = points_geometry(
        'centerline',
        data['points'],
        'Original HOLE sampled centers rounded to 0.001 angstrom; artificial end extensions excluded. Sample radii are not a certified swept volume.',
        radii if min(radii) >= 0 else None,
    )
    record = ProviderRecord(
        '1',
        'channel',
        run,
        atom_role='unavailable_lining_atom_map',
        _fields={
            'profile': data['profile'],
            'has_negative_sample_clearance': any(radius < 0 for radius in radii),
            'external_measurements': {
                'minimum_radius': measurement(
                    run,
                    data['minimum_radius'],
                    'angstroms',
                    'Rmin',
                    'stdout.txt',
                    'Original HOLE minimum over sampled centers, excluding between-plane midpoint evaluations; stochastic local optimization, not a global path certificate',
                )
            },
        },
        _geometries=(geometry,),
    )
    return HoleOutput(run, (record,))
