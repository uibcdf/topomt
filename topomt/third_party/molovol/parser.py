"""Decode the reviewed isolated-structure MoloVol 1.2.0 report protocol."""

import hashlib
import math
import re
from collections import Counter
from decimal import Decimal
from typing import Any

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import finite, measurement, points_geometry
from topomt.third_party.output import ProviderRecord

from .output import MoloVolOutput

VERSION = '1.2.0'
FIELDS = {
    'Van der Waals volume': 'van_der_waals_volume',
    'Probe excluded void volume': 'probe_excluded_void_volume',
    'Molecular volume': 'molecular_volume',
    'Probe core volume': 'probe_core_volume',
    'Small probe core volume': 'probe_core_volume',
    'Probe shell volume': 'probe_shell_volume',
    'Small probe shell volume': 'probe_shell_volume',
    'Small probe occupied volume': 'probe_occupied_volume',
    'Large probe shell volume': 'large_probe_shell_volume',
    'Van der Waals surface': 'van_der_waals_surface',
    'Probe excluded surface': 'probe_excluded_surface',
    'Small probe excluded surface': 'probe_excluded_surface',
    'Probe accessible surface': 'probe_accessible_surface',
    'Small probe accessible surface': 'probe_accessible_surface',
    'Molecular surface': 'molecular_surface',
}


def _physical(token: str, unit: str, source: str) -> dict[str, Any]:
    return {
        'value': finite(token, nonnegative=True),
        'unit': unit,
        'source_field': source,
        'original_token': token,
    }


def _field(text: str, name: str) -> str:
    matches = re.findall(r'^' + re.escape(name) + r':\s*(.+)$', text, re.M)
    if len(matches) != 1:
        raise ValueError(f'MoloVol requires exactly one {name} field')
    return matches[0].strip()


def _length_field(text: str, name: str) -> dict[str, Any]:
    match = re.fullmatch(r'(\S+) A', _field(text, name))
    if match is None:
        raise ValueError(f'MoloVol {name} must explicitly report angstroms')
    return _physical(match[1], 'angstroms', name)


def decode_report(text: str) -> dict[str, Any]:
    """Decode original tokens with fixed units, preserving outside and absent data."""
    if (
        'MoloVol program: calculation results report' not in text
        or _field(text, 'version') != VERSION
        or not text.rstrip().endswith('rebuild')
        or 'Maximum number of cavities reached' in text
    ):
        raise ValueError('Unsupported, incomplete or cavity-limited MoloVol report')
    if _field(text, 'Crystal unit cell analysis') != 'No':
        raise ValueError('This MoloVol route admits isolated structures only')
    mode = _field(text, 'Probe mode')
    if mode not in {'one probe', 'two probes'}:
        raise ValueError('Unsupported MoloVol probe mode')
    parameters: dict[str, Any] = {
        'probe_radius': _length_field(
            text, 'Probe radius' if mode == 'one probe' else 'Small probe radius'
        ),
        'grid_step': _length_field(text, 'Grid resolution'),
        'octree_depth': int(_field(text, 'Optimization depth')),
        'calculate_surfaces': '// Total Surface Areas calculated //' in text,
    }
    if (
        parameters['octree_depth'] < 0
        or parameters['probe_radius']['value'] <= 0
        or parameters['grid_step']['value'] <= 0
    ):
        raise ValueError('Invalid MoloVol reported calculation parameters')
    if mode == 'two probes':
        parameters['large_probe_radius'] = _length_field(text, 'Large probe radius')
        if (
            parameters['large_probe_radius']['value']
            <= parameters['probe_radius']['value']
        ):
            raise ValueError('MoloVol large probe must exceed the small probe')
    radii = {}
    for symbol, token in re.findall(
        r'^([A-Z][a-z]?(?:\d*[+-])?)\s*:\s*(\S+) A$', text, re.M
    ):
        if symbol in radii:
            raise ValueError('Duplicate MoloVol element radius')
        radii[symbol] = _physical(token, 'angstroms', f'Elements radii/{symbol}')
        if radii[symbol]['value'] <= 0:
            raise ValueError('Invalid MoloVol effective element radius')
    if not radii:
        raise ValueError('MoloVol effective element radii are absent')

    measures = {}
    for line in text.splitlines():
        match = re.fullmatch(r'(.+?):\s+(\S+)\s+(A\^[23])', line.strip())
        if match is None or match[1] not in FIELDS:
            continue
        label, token, original_unit = match.groups()
        key = FIELDS[label]
        if original_unit != ('A^3' if key.endswith('volume') else 'A^2'):
            raise ValueError('MoloVol measure dimension disagrees with its field')
        if key == 'molecular_volume' and key in measures:
            key = 'molecular_volume_with_isolated_cavities'
            label += ' [with isolated cavities]'
        if key in measures:
            raise ValueError('Duplicate original MoloVol measure')
        measures[key] = _physical(
            token, 'angstroms**3' if original_unit == 'A^3' else 'angstroms**2', label
        )
    required = {
        'van_der_waals_volume',
        'probe_excluded_void_volume',
        'molecular_volume',
        'molecular_volume_with_isolated_cavities',
        'probe_shell_volume',
    }
    if mode == 'two probes':
        required |= {
            'probe_core_volume',
            'probe_occupied_volume',
            'large_probe_shell_volume',
        }
    if parameters['calculate_surfaces']:
        required |= {
            'van_der_waals_surface',
            'probe_excluded_surface',
            'probe_accessible_surface',
        }
    if not required <= measures.keys():
        raise ValueError('Required MoloVol measures are absent')
    if mode == 'one probe' and not _field(text, 'Probe core volume').startswith(
        'No physical meaning,'
    ):
        raise ValueError('MoloVol exterior core volume must remain undefined')

    regions: list[dict[str, Any]] = []
    lines = text.splitlines()
    headings = [i for i, line in enumerate(lines) if line.startswith('Cavity ID ')]
    if '// Cavities data //' in text:
        if len(headings) != 1:
            raise ValueError('MoloVol cavity table is absent or duplicated')
        surface = parameters['calculate_surfaces']
        heading, units = lines[headings[0]], lines[headings[0] + 1]
        if (
            'Cavity center coordinates (A)' not in heading
            or units.count('Volume (A^3)') != 2
            or units.count('Surface (A^2)') != (2 if surface else 0)
            or re.search(r'\bx\s+y\s+z$', units) is None
        ):
            raise ValueError('MoloVol cavity columns have unsupported units/axes')
        for line in lines[headings[0] + 2 :]:
            if not line.strip():
                break
            cells = line.split()
            if len(cells) != (9 if surface else 7) or not cells[0].isdecimal():
                raise ValueError('Malformed MoloVol cavity row')
            identity = int(cells[0])
            offset = 5 if surface else 3
            kind = cells[offset]
            if identity != len(regions) + 1 or kind not in (
                {'Outside', 'Isolated'}
                if mode == 'one probe'
                else {'Isolated', 'Pocket', 'Tunnel'}
            ):
                raise ValueError('Invalid MoloVol cavity identity/type')
            row: dict[str, Any] = {
                'source_id': str(identity),
                'reported_type': kind,
                'original_tokens': cells,
                'center': {
                    'value': [finite(x) for x in cells[offset + 1 :]],
                    'unit': 'angstroms',
                },
            }
            for index, key in [(1, 'occupied_volume'), (2, 'accessible_volume')]:
                if kind == 'Outside':
                    if cells[index] != 'Outside':
                        raise ValueError(
                            'MoloVol Outside volume must remain unavailable'
                        )
                    row[key] = None
                else:
                    row[key] = _physical(
                        cells[index], 'angstroms**3', f'Cavity {identity}/{key}'
                    )
            if surface:
                for index, key in [(3, 'excluded_surface'), (4, 'accessible_surface')]:
                    row[key] = _physical(
                        cells[index], 'angstroms**2', f'Cavity {identity}/{key}'
                    )
            regions.append(row)
        if not regions:
            raise ValueError('MoloVol reports a cavity table without rows')
    if sum(row['reported_type'] == 'Outside' for row in regions) > 1:
        raise ValueError('Duplicate MoloVol Outside region')
    operands = [
        measures['molecular_volume'],
        measures['molecular_volume_with_isolated_cavities'],
    ]
    isolated = [
        row['occupied_volume'] for row in regions if row['reported_type'] == 'Isolated'
    ]
    residual = (
        operands[1]['value']
        - operands[0]['value']
        - math.fsum(item['value'] for item in isolated)
    )
    rounding = math.fsum(
        float(Decimal(10) ** int(Decimal(item['original_token']).as_tuple().exponent))
        / 2
        for item in [*operands, *isolated]
    )
    if abs(residual) > rounding + 1e-9:
        raise ValueError(
            'MoloVol isolated-region and total volumes disagree beyond reported precision'
        )
    formula = _field(text, 'Chemical formula')
    if re.fullmatch(r'(?:[A-Z][a-z]?\d*)+', formula) is None:
        raise ValueError('Unsupported original chemical formula')
    return {
        'version': VERSION,
        'chemical_formula': formula,
        'probe_mode': mode,
        'parameters': parameters,
        'element_radii': radii,
        'measurements': measures,
        'regions': regions,
    }


def report_data(run: ProviderRun) -> tuple[str, str, dict[str, Any]]:
    names = [
        name
        for name, _ in run.artifacts
        if name.startswith('output/')
        and '_MoloVol-report_grid-' in name
        and name.endswith('.txt')
    ]
    if len(names) != 1:
        raise ValueError('MoloVol requires exactly one original calculation report')
    name = names[0]
    text = run.get_artifact(name).decode('utf-8')
    return name.removeprefix('output/'), text, decode_report(text)


def reported_equal(packet: dict, expected: float) -> bool:
    """Compare the original six-significant-digit echo, not exact input bytes."""
    return packet['value'] == float(format(expected, '.6g'))


def validate_query(data: dict, parameters: dict, radii: dict, counts: dict) -> None:
    query = data['parameters']
    large = parameters.get('large_probe_radius')
    formula = {
        symbol: int(number or '1')
        for symbol, number in re.findall(
            r'([A-Z][a-z]?)(\d*)', data['chemical_formula']
        )
    }
    if not (
        data['probe_mode'] == ('two probes' if large is not None else 'one probe')
        and reported_equal(query['probe_radius'], parameters['probe_radius'])
        and reported_equal(query['grid_step'], parameters['grid_step'])
        and query['octree_depth'] == parameters['octree_depth']
        and query['calculate_surfaces'] == parameters['calculate_surfaces']
        and (large is None or reported_equal(query['large_probe_radius'], large))
        and data['element_radii'].keys() == radii.keys()
        and all(
            reported_equal(data['element_radii'][symbol], radius)
            for symbol, radius in radii.items()
        )
        and formula == counts
    ):
        raise ValueError(
            'MoloVol reported query, radii or atom model disagrees with submitted input'
        )


def validate_saved_evidence(run: ProviderRun, data: dict) -> None:
    metadata = run.metadata
    if metadata.get('adapter_protocol') != 'topomt.original-local@1':
        return  # Raw report fixtures do not assert a source-bound execution.
    try:
        for filename, key in [
            ('elements.txt', 'elements_effective'),
            ('elements_source.txt', 'elements_source'),
        ]:
            raw = run.get_artifact('input/' + filename)
            if hashlib.sha256(raw).hexdigest() != metadata[key]['sha256']:
                raise ValueError('MoloVol saved element-resource fingerprint disagrees')
        effective = {}
        for line in run.get_artifact('input/elements.txt').decode().splitlines():
            cells = line.split()
            if cells and cells[0].isdecimal():
                if len(cells) != 4 or cells[1] in effective:
                    raise ValueError('MoloVol saved element table is malformed')
                effective[cells[1]] = finite(cells[2], nonnegative=True)
        counts = Counter(
            line[76:78].strip()
            for line in run.get_artifact('input/input.pdb').decode().splitlines()
            if line.startswith(('ATOM  ', 'HETATM'))
        )
        if counts != metadata['element_counts'] or any(
            effective[symbol] != radius
            for symbol, radius in metadata['effective_radii'].items()
        ):
            raise ValueError('MoloVol saved input and effective element model disagree')
        validate_query(
            data,
            metadata['parameters'],
            metadata['effective_radii'],
            metadata['element_counts'],
        )
    except (KeyError, TypeError) as cause:
        raise ValueError('MoloVol source-bound evidence is incomplete') from cause


def external_measurements(run: ProviderRun, fields: dict, filename: str) -> dict:
    return {
        key: measurement(
            run,
            packet['value'],
            packet['unit'],
            packet['source_field'],
            filename,
            f'Original MoloVol {key}; probe-core accessible and probe-occupied measures retain distinct definitions; voxel approximation at the recorded grid/depth',
        )
        for key, packet in fields.items()
        if packet is not None
    }


def parse_output(run: ProviderRun) -> MoloVolOutput:
    """Keep internal region rows and preserve the complete original report."""
    filename, _, data = report_data(run)
    validate_saved_evidence(run, data)
    records = []
    for row in data['regions']:
        if row['reported_type'] == 'Outside':
            continue
        quantities = {
            key: row[key]
            for key in (
                'occupied_volume',
                'accessible_volume',
                'excluded_surface',
                'accessible_surface',
            )
            if key in row
        }
        records.append(
            ProviderRecord(
                row['source_id'],
                'cavity',
                run,
                atom_role='unavailable_region_atom_map',
                _fields={
                    'reported_type': row['reported_type'],
                    'original': row,
                    'external_measurements': external_measurements(
                        run, quantities, filename
                    ),
                },
                _geometries=(
                    points_geometry(
                        'region_center',
                        [row['center']['value']],
                        'Original MoloVol midpoint of region bounds; not a complete region support or a certified collision-free point',
                    ),
                ),
            )
        )
    return MoloVolOutput(run, tuple(records))
