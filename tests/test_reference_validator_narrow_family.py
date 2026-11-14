"""Complete the original narrow-probe family without altering old evidence."""

import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from devtools.reference_validator.model import Model, decode_point
from devtools.reference_validator.storage import read_record
from devtools.reference_validator.verify import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'devguide/evidence/reference_validator_power_cells_v4'


def _profiles():
    panel = read_record(BASE / 'protocol.json')
    for row in panel['profiles']:
        protocol = ROOT / row['protocol']
        assert (
            hashlib.sha256(protocol.read_bytes()).hexdigest() == row['protocol_sha256']
        )
        spec = read_record(protocol)
        (case,) = spec['cases']
        yield row['probe_angstroms'], protocol.parent, case


def test_remaining_profiles_preserve_saved_inputs_and_all_receiving_checksums():
    summary = read_record(BASE / 'family_summary.json')
    current = {row['probe']['requested']['value']: row for row in summary['profiles']}
    seen = []
    for probe, base, case in _profiles():
        seen.append(probe)
        reference = case['reference_origin']
        archive = ROOT / reference['archive']
        assert (
            hashlib.sha256(archive.read_bytes()).hexdigest()
            == reference['archive_sha256']
        )
        with zipfile.ZipFile(archive) as stream:
            raw = stream.read(reference['member'])
        assert hashlib.sha256(raw).hexdigest() == reference['member_sha256']
        assert json.loads(raw) == case['model']
        receipt = read_record(base / 'receiving/receipt.json')
        execution = read_record(base / 'execution.json')
        assert receipt['source_tree_modified'] is False
        assert receipt['source_revision'] == execution['source_revision']
        assert (
            receipt['protocol_sha256']
            == hashlib.sha256((base / 'protocol.json').read_bytes()).hexdigest()
        )
        for name, digest in receipt['files'].items():
            assert (
                hashlib.sha256((base / 'receiving' / name).read_bytes()).hexdigest()
                == digest
            )
        for name, digest in execution['files'].items():
            assert hashlib.sha256((base / name).read_bytes()).hexdigest() == digest
        assert (
            hashlib.sha256((base / 'execution.log').read_bytes()).hexdigest()
            == execution['log_sha256']
        )
        assert receipt['native_dfnd_qualification'] == 'not_changed'
        row = current[probe]
        stored = receipt['cases'][case['name']]
        assert row['model_sha256'] == stored['model_sha256']
        assert row['certificate_sha256'] == stored['certificate_sha256']
        assert row['certificate_origin'] == stored['certificate_origin']
        assert row['topology']['n_components'] == stored['n_components']
        assert row['topology']['n_boundary_patches'] == stored['n_boundary_patches']
        assert row['resources']['wall_seconds'] == execution['elapsed_seconds']
        assert row['resources']['cpu_seconds'] == execution['child_cpu_seconds']
        assert (
            row['resources']['peak_rss_kib_linux']
            == execution['child_peak_rss_kib_linux']
        )
        for reference in row['sources'].values():
            assert (
                hashlib.sha256((ROOT / reference['path']).read_bytes()).hexdigest()
                == reference['sha256']
            )
    assert seen == [1.2, 2.5]
    assert sorted(current) == [1.2, 1.4, 2.5]
    # Also protect the earlier 1.4 A row in the combined public summary.
    for row in current.values():
        sources = row['sources']
        for reference in sources.values():
            assert (
                hashlib.sha256((ROOT / reference['path']).read_bytes()).hexdigest()
                == reference['sha256']
            )
        receipt = read_record(ROOT / sources['receipt']['path'])
        (case,) = receipt['cases'].values()
        execution = read_record(ROOT / sources['execution']['path'])
        assert row['source_revision'] == receipt['source_revision']
        assert row['model_sha256'] == case['model_sha256']
        assert row['topology']['n_components'] == case['n_components']
        assert row['topology']['n_boundary_patches'] == case['n_boundary_patches']
        assert row['certificate_origin'] == case['certificate_origin']
        assert row['resources']['wall_seconds'] == execution['elapsed_seconds']
        assert row['resources']['cpu_seconds'] == execution['child_cpu_seconds']


def test_reprobe_preserves_every_source_cell_but_has_its_own_target_identity():
    for _, base, case in _profiles():
        folder = base / 'receiving' / case['name']
        source = case['saved_geometry']
        old = read_record(ROOT / source['certificate_path'])
        new = read_record(folder / 'certificate.json')
        model = Model.from_record(read_record(folder / 'model.json'))
        assert len(model.atoms) == len(old['cells']) == len(new['cells']) == 81
        assert new['model_sha256'] == model.digest
        assert new['model_sha256'] != old['model_sha256']
        for previous, current in zip(old['cells'], new['cells']):
            for key in ['atom_id', 'support', 'vertices', 'edges']:
                assert current[key] == previous[key]
        origin = read_record(base / 'receiving/receipt.json')['cases'][case['name']][
            'certificate_origin'
        ]
        assert origin['route'] == 'reprobed_geometry'
        assert origin['geometry_producer_revision'] == source['producer_revision']
        assert origin['source_model_file_sha256'] == source['model_sha256']
        assert origin['source_certificate_file_sha256'] == source['certificate_sha256']


def test_positive_anchor_path_and_negative_empty_hull_have_distinct_complete_dispositions():
    outcomes = []
    for probe, base, case in _profiles():
        folder = base / 'receiving' / case['name']
        result = read_record(folder / 'verification.json')
        assert result['topology_complete'] is True
        assert result['per_region_volume_status'] == 'not_computed'
        outcomes.append((probe, result['n_components'], result['n_boundary_patches']))
        queries = read_record(folder / 'anchors.json')
        if probe == 1.2:
            assert (
                queries['locations']['lower']['point_state']
                == queries['locations']['upper']['point_state']
                == 'free'
            )
            (pair,) = queries['pairs']
            assert pair['connected'] is True
            model = Model.from_record(read_record(folder / 'model.json'))
            assert verify(model, pair['path_certificate'])['path_validated'] is True
        else:
            assert result['regions'] == result['boundary_patches'] == []
            assert result['volume_lower'] == result['volume_upper'] == ['0', '1']
            assert queries['locations']['origin']['point_state'] == 'blocked'
            assert queries['pairs'] == []
            # Complete checked convex cells are each covered by their own ball:
            # this excludes the whole hull, rather than a set of sample points.
            model = Model.from_record(read_record(folder / 'model.json'))
            atoms = {a.source_id: a for a in model.atoms}
            for cell in read_record(folder / 'certificate.json')['cells']:
                atom = atoms[cell['atom_id']]
                assert cell['free_vertices'] == []
                assert all(
                    sum((x - c) ** 2 for x, c in zip(decode_point(v), atom.center))
                    <= (atom.radius + model.probe) ** 2
                    for v in cell['vertices']
                )
    assert outcomes == [(1.2, 1, 2), (2.5, 0, 0)]


def test_original_profiles_execute_sequentially_with_bounded_resources_and_phase_costs():
    previous_end = None
    for _, base, case in _profiles():
        execution = read_record(base / 'execution.json')
        assert execution['receiving_status'] == 'completed'
        assert execution['exit_code'] == 0 and execution['stop_reason'] is None
        assert len(execution['cpu_affinity']) == 1
        assert execution['resource_policy']['address_space_limit_bytes'] == 2 * 1024**3
        assert execution['resource_policy']['cpu_limit_seconds'] == 180
        assert execution['resource_policy']['wall_limit_seconds'] == 240
        assert all(s['host']['safe'] for s in execution['host_samples'])
        start = datetime.fromisoformat(execution['recorded_at_utc']).timestamp()
        if previous_end is not None:
            assert start >= previous_end
        previous_end = start + execution['elapsed_seconds']
        phases = read_record(base / 'receiving' / case['name'] / 'phases.json')
        assert list(phases) == [
            'model_receiving',
            'certified_geometry_reprobe',
            'saved_reading',
            'verification',
            'anchor_queries',
        ]
        assert all(
            p['wall_seconds'] >= 0 and p['cpu_seconds'] >= 0 for p in phases.values()
        )


def test_original_negative_profile_is_empty_under_fresh_independent_checking():
    folder = BASE / 'probe_2_5/receiving/original_narrow_tube_2_5'
    script = """
import sys,json
from pathlib import Path
for name in ['topomt','numpy','scipy','pyunitwizard','devtools.reference_validator.producer','devtools.reference_validator.power_cells','devtools.reference_validator.center_hull']:
 sys.modules[name]=None
from devtools.reference_validator.model import Model
from devtools.reference_validator.verify import verify
model=Model.from_record(json.loads(Path(sys.argv[1]).read_text()))
result=verify(model,json.loads(Path(sys.argv[2]).read_text()))
print(json.dumps({key:result[key] for key in ['topology_complete','n_components','n_boundary_patches','volume_lower','volume_upper']}))
"""
    r = subprocess.run(
        [
            sys.executable,
            '-c',
            script,
            str(folder / 'model.json'),
            str(folder / 'certificate.json'),
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    result = json.loads(r.stdout)
    assert result['topology_complete'] is True
    assert result['n_components'] == result['n_boundary_patches'] == 0
    assert result['volume_lower'] == result['volume_upper'] == ['0', '1']
