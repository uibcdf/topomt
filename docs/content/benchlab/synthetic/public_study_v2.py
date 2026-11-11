"""Current portable study receiving; original inputs and v1 history stay frozen."""

import hashlib
import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any

_spec = importlib.util.spec_from_file_location(
    'benchlab_frozen_reader_v1', Path(__file__).with_name('public_study.py')
)
if _spec is None or _spec.loader is None:
    raise RuntimeError('The preserved input receiving helper is missing')
_frozen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_frozen)
receive = _frozen.receive
read = _frozen.read
quantity = _frozen.quantity


@contextmanager
def _study_tools():
    root = Path(__file__).resolve().parents[4]
    previous = sys.path[:]
    try:
        sys.path[:0] = [str(root), str(root / 'devtools')]
        yield
    finally:
        sys.path[:] = previous


def inspect(topo: Any) -> dict:
    """Check source-mapped support, public relations, dry banks and native depth."""
    with _study_tools():
        from devtools.benchlab.public_contract import describe_public_contract

        return describe_public_contract(topo)


def references(directory: Path) -> dict:
    """Replay existing independent certificates, without generating new answers."""
    with _study_tools():
        result = {'original_control': _frozen.reference(directory)}
        if directory.name == 'closed_shell':
            from devtools.verify_small_probe_regions import verify_region_certificate

            folder = directory / 'artifacts/small_probe_boundary_v2'
            result['small_probe'] = verify_region_certificate(
                directory / 'artifacts/closed_shell_v1/input.json',
                folder / 'protocol.json',
                read(folder / 'certificate.json'),
            )
        if directory.name != 'regular_tetrahedron':
            from devtools.verify_origin_access_bracket import verify_access_bracket

            version = 1 if directory.name == 'closed_shell' else 2
            folder = directory / f'artifacts/access_bracket_v{version}'
            result['access_bracket'] = verify_access_bracket(
                directory / f'artifacts/{directory.name}_v1/input.json',
                folder / 'protocol.json',
                read(folder / 'certificate.json'),
            )
        return result


def volumes(directory: Path) -> dict:
    """Recompute declared public volumes and compare with retained independent bounds."""
    with _study_tools():
        from devtools.benchlab.capture_volume import encode_quantities, origin_component
        from topomt import pyunitwizard as puw

        folder = directory / 'artifacts/volume_study_v1'
        protocol = read(folder / 'protocol.json')
        reference = read(folder / 'independent_reference.json')
        if (
            reference['protocol_sha256']
            != hashlib.sha256((folder / 'protocol.json').read_bytes()).hexdigest()
        ):
            raise ValueError('Independent volume reference belongs to another protocol')
        rows = []
        topographies = {}
        for domain, independent in zip(
            protocol['domains'], reference['domains'], strict=True
        ):
            if domain['id'] != independent['domain_id']:
                raise ValueError('Independent volume domain identity differs')
            probe = domain['probe_angstroms']
            if probe not in topographies:
                topographies[probe] = receive(directory, probe)
            topo = topographies[probe]
            component = origin_component(topo)
            for observable in ('bare_empty', 'probe_center'):
                measured = topo.dfnd.solvent_volume_measurement(
                    component.component_id,
                    region=domain['region'],
                    observable=observable,
                    **protocol['native_controls'],
                )
                actual = measured['support']['tetrahedra_source_atom_indices']
                if {tuple(sorted(tet)) for tet in actual} != {
                    tuple(sorted(tet))
                    for tet in domain['tetrahedra_source_atom_indices']
                }:
                    raise ValueError(
                        'Current volume domain differs from the frozen support'
                    )
                interval = [
                    float(puw.get_value(v, to_unit='nm**3'))
                    for v in measured['interval']
                ]
                expected = independent['reference'][observable]['interval']
                overlap = max(interval[0], expected[0]) <= min(interval[1], expected[1])
                rows.append(
                    {
                        'domain': domain['id'],
                        'observable': observable,
                        'volume_angstrom3': float(
                            puw.get_value(measured['volume'], to_unit='angstrom**3')
                        ),
                        'interval_angstrom3': [v * 1000 for v in interval],
                        'independent_overlap': overlap,
                        'measurement': encode_quantities(measured),
                    }
                )
        return {
            'rows': rows,
            'target_met': all(row['independent_overlap'] for row in rows),
        }
