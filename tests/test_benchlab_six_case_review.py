"""The review retains all selected public profiles and original evidence bytes."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/content/benchlab/synthetic/artifacts/six_case_review_v1'


def test_review_receipt_retains_frozen_models_and_actual_public_profiles():
    protocol = json.loads((EVIDENCE / 'protocol.json').read_text())
    summary = json.loads((EVIDENCE / 'summary.json').read_text())
    with zipfile.ZipFile(EVIDENCE / 'receiving.zip') as archive:
        manifest = json.loads(archive.read('MANIFEST.json'))
        for name, expected in manifest['files'].items():
            assert hashlib.sha256(archive.read(name)).hexdigest() == expected
        receipt_bytes = archive.read('receiving/receipt.json')
        assert receipt_bytes == (EVIDENCE / 'receiving_receipt.json').read_bytes()
        receipt = json.loads(receipt_bytes)
        assert receipt['frozen_files_unchanged'] == len(protocol['frozen_files'])
        profiles = 0
        for case in protocol['cases']:
            name = case['name']
            observations = json.loads(archive.read(f'receiving/{name}.json'))
            assert observations['input_sha256'] == case['input_sha256']
            assert observations['source_revision'] == receipt['source_revision']
            assert [r['probe_angstroms'] for r in observations['observations']] == (
                case['probes_angstroms']
            )
            for row in observations['observations']:
                observed = row['public_observation']
                inventory = observed['node_inventory']
                assert (
                    inventory['wet_nodes'] + inventory['dry_nodes']
                    == (inventory['total'])
                )
                witnesses = row['residence_witnesses']
                assert len(witnesses['witnesses']) == sum(
                    len(c['resident_node_indices']) for c in observed['wet_components']
                )
                assert witnesses['component_existence'] == (
                    'not_determined_by_point_checks'
                )
                if observed['physical_boundary']['status'] == 'unresolved':
                    assert observed['physical_boundary']['n_patches'] is None
                credit = row['topography_attribution']
                assert credit['producer']['name'] == 'TopoMT'
                assert credit['references']
                profiles += 1
        assert profiles == summary['profile_count'] == 19
        assert len(protocol['cases']) == len(summary['cases']) == 6
    for relative, expected in protocol['frozen_files'].items():
        with (ROOT / relative).open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == expected
