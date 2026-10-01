"""Independent sphere geometry guards for the offline radius audit."""

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest

from devtools.castp.audit_castp3_radii import (
    audit_archive,
    audit_bulb_contacts,
    parse_contribution_atom_serials,
    summarize_audits,
)
from topomt.third_party.castp3.core.castp_core.geometry import (
    _castp3_protor_radii_for_labels,
)


def _orthosphere_atoms(radii, center):
    directions = np.asarray([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]])
    directions = directions / np.sqrt(3)
    distances = np.sqrt((np.asarray(radii) + 1.4) ** 2 + 0.9**2)
    return center + directions * distances[:, None]


def test_radius_audit_observes_four_independent_power_contacts():
    radii = np.asarray([1.88, 1.64, 1.42, 1.46])
    center = np.asarray([12.2345, -8.8765, 4.5432])
    result = audit_bulb_contacts(
        _orthosphere_atoms(radii, center), radii, center, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'compatible'
    assert result['contacts'] == [0, 1, 2, 3]
    assert result['candidates'] == []


def test_radius_audit_finds_unanticipated_oxygen_radius_without_label_filter():
    standard = np.asarray([1.88, 1.64, 1.42, 1.46])
    actual = standard.copy()
    actual[3] = 1.39
    center = np.zeros(3)
    result = audit_bulb_contacts(
        _orthosphere_atoms(actual, center), standard, center, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'single_candidate'
    assert result['contacts'] == [0, 1, 2]
    candidate = result['candidates'][0]
    assert candidate['index'] == 3
    assert candidate['radius_interval']['unit'] == 'angstrom'
    assert candidate['radius_interval']['lower'] < 1.39
    assert candidate['radius_interval']['upper'] > 1.39


def test_radius_audit_keeps_multiple_candidates_ambiguous():
    standard = np.asarray([1.88, 1.64, 1.42, 1.46])
    actual = standard.copy()
    actual[3] = 1.53
    center = np.zeros(3)
    points = _orthosphere_atoms(actual, center)
    points = np.vstack([points, -points[3]])
    result = audit_bulb_contacts(
        points, np.append(standard, standard[3]), center, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'ambiguous'
    assert {item['index'] for item in result['candidates']} == {3, 4}


def test_radius_audit_rejects_a_bulb_with_an_interior_atom():
    radii = np.asarray([1.88, 1.64, 1.42, 1.46])
    center = np.zeros(3)
    points = np.vstack([_orthosphere_atoms(radii, center), center])
    result = audit_bulb_contacts(
        points, np.append(radii, 1.42), center, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'conflict'


def test_radius_audit_rejects_coplanar_contacts_as_tetrahedral_evidence():
    radius = np.sqrt(2.82**2 + 0.9**2)
    points = radius * np.asarray([[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]])
    result = audit_bulb_contacts(
        points, np.full(4, 1.42), np.zeros(3), 0.9, probe_radius=1.4
    )
    assert result['status'] == 'unresolved'


def test_radius_audit_rounding_bounds_cover_an_independently_rounded_center():
    radii = np.asarray([1.88, 1.64, 1.42, 1.46])
    exact = np.asarray([12.234549, -8.876549, 4.543249])
    printed = np.round(exact, 4)
    result = audit_bulb_contacts(
        _orthosphere_atoms(radii, exact), radii, printed, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'compatible'


def test_radius_audit_does_not_infer_one_change_with_only_two_anchors():
    standard = np.asarray([1.88, 1.64, 1.42, 1.46])
    actual = standard.copy()
    actual[2:] -= 0.07
    center = np.zeros(3)
    result = audit_bulb_contacts(
        _orthosphere_atoms(actual, center), standard, center, 0.9, probe_radius=1.4
    )
    assert result['status'] == 'unresolved'
    assert result['candidates'] == []


def test_radius_audit_rejects_invalid_probe():
    with pytest.raises(ValueError, match='probe'):
        audit_bulb_contacts(np.zeros((4, 3)), np.ones(4), np.zeros(3), 1, -1)


def test_pinned_radius_audit_observes_other_oxygen_labels():
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1hew.zip'
    )
    result = audit_archive(archive)
    standard = result['profiles']['protor']
    server = result['profiles']['castp3_protor']
    assert standard['bulb_statuses'] == {'compatible': 86, 'single_candidate': 2}
    assert server['bulb_statuses'] == {'compatible': 88}
    observed = server['observed_atoms']
    assert observed['SER:OG']
    assert observed['ALA:O']
    assert {item['label'] for item in standard['single_change_candidates']} == {
        'ASP:OD1'
    }


def test_pinned_radius_audit_covers_amide_and_hydroxyl_controls():
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1ifb.zip'
    )
    result = audit_archive(archive)
    server = result['profiles']['castp3_protor']
    assert server['bulb_statuses'] == {'compatible': 246}
    assert server['observed_atoms']['GLN:OE1']
    assert server['observed_atoms']['THR:OG1']
    assert server['observed_atoms']['TYR:OH']


def test_radius_summary_distinguishes_presence_from_observation():
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1hew.zip'
    )
    summary = summarize_audits([audit_archive(archive)])
    assert summary['archive_count'] == 1
    assert summary['bulb_count'] == 88
    assert summary['label_coverage']['ASN:OD1']['present_atoms'] > 0
    assert summary['label_coverage']['ASN:OD1']['observed_castp3_protor'] == 0
    assert summary['label_coverage']['SER:OG']['observed_castp3_protor'] > 0


def test_contribution_identity_rejects_a_mismatched_atom_label():
    pdb = b'ATOM     72  CD1 TRP A 109     -20.029  50.761  61.248  1.00 17.72           C  \n'
    with pytest.raises(ValueError, match='identity'):
        parse_contribution_atom_serials(b'ATOM,72,CD2,TRP,A,109\n', pdb)


def test_contribution_identity_accepts_joined_chain_and_large_residue_number():
    pdb = b'ATOM   2420  N   GLU B1159      15.234   0.062 -17.512  1.00 49.38           N  \n'
    assert parse_contribution_atom_serials(
        b'# No cusp correction.\nATOM,2420,N,GLU,B1159,2418,43.6696\n', pdb
    ) == {2420}


def test_contribution_membership_resolves_terminal_interior_conflict():
    archive = (
        Path(__file__).resolve().parents[3] / 'topomt/data/CASTpFold_server/1bid.zip'
    )
    raw = audit_archive(archive)
    selected = audit_archive(archive, atom_source='contributions')
    assert raw['profiles']['castp3_protor']['bulb_statuses']['conflict'] == 2
    assert selected['profiles']['castp3_protor']['bulb_statuses'] == {
        'compatible': sum(raw['profiles']['castp3_protor']['bulb_statuses'].values())
    }
    assert selected['skipped_atoms']['absent_from_contributions'] == 1
    assert selected['archive_sha256'] == raw['archive_sha256']
    assert selected['contributions_sha256']


def test_pinned_radius_summary_accounts_for_all_archived_inputs():
    root = Path(__file__).resolve().parents[3]
    summary = json.loads(
        (root / 'devguide/castp/artifacts/radius_audit_2026_10_01.json').read_text()
    )
    archives = {
        path.stem: path
        for path in (root / 'topomt/data/CASTpFold_server').glob('*.zip')
    }
    assert len(archives) == summary['archive_count'] == 89
    assert {case['case'] for case in summary['cases']} == archives.keys()
    for case in summary['cases']:
        assert (
            hashlib.sha256(archives[case['case']].read_bytes()).hexdigest()
            == case['archive_sha256']
        )
    for counts in summary['profile_statuses'].values():
        assert sum(counts.values()) == summary['bulb_count'] == 59080
    assert len(summary['castp3_protor_candidates']) == 3


def test_contribution_radius_summary_guards_all_input_hashes_and_terminal_observations():
    root = Path(__file__).resolve().parents[3]
    summary = json.loads(
        (
            root / 'devguide/castp/artifacts/contribution_radius_audit_2026_10_01.json'
        ).read_text()
    )
    assert summary['archive_count'] == 89
    assert summary['profile_statuses']['castp3_protor'] == {'compatible': 59080}
    for case in summary['cases']:
        path = root / f'topomt/data/CASTpFold_server/{case["case"]}.zip'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == case['archive_sha256']
        with ZipFile(path) as archive:
            member = next(
                name for name in archive.namelist() if name.endswith('.contrib.csv')
            )
            assert (
                hashlib.sha256(archive.read(member)).hexdigest()
                == case['contributions_sha256']
            )
    observations = summary['terminal_atom_inclusion']['observations']
    assert len(observations) == 87
    assert sum(row['listed'] for row in observations) == 12
    assert {row['group'] for row in observations if row['listed']} == {'GLY', 'LEU'}


@pytest.mark.parametrize(
    'case,feature_id,bulb_id,serials',
    [
        ('1a4j', 3, 116, (1486, 1494, 1498, 1668)),
        ('1a4j', 3, 159, (1494, 1498, 1648, 1668)),
        ('1cdo', 39, 2, (5438, 5600, 5435, 5607)),
    ],
)
def test_terminal_oxygen_hypothesis_reconstructs_independent_archived_bulbs(
    case, feature_id, bulb_id, serials
):
    """Conditional four-support reconstruction does not change radius policy."""
    root = Path(__file__).resolve().parents[3]
    with ZipFile(root / f'topomt/data/CASTpFold_server/{case}.zip') as archive:
        pdb = archive.read(
            next(name for name in archive.namelist() if name.endswith('.pdb'))
        ).decode()
        bulbs = json.loads(
            archive.read(
                next(name for name in archive.namelist() if name.endswith('.bulb.json'))
            )
        )
    rows = {
        int(line[6:11]): line
        for line in pdb.splitlines()
        if line.startswith(('ATOM', 'HETATM'))
    }
    support = [rows[serial] for serial in serials]
    points = np.asarray(
        [
            [float(line[start:end]) for start, end in ((30, 38), (38, 46), (46, 54))]
            for line in support
        ]
    )
    base = _castp3_protor_radii_for_labels(
        np.asarray([line[17:20].strip() for line in support]),
        np.asarray([line[12:16].strip() for line in support]),
        np.asarray([line[76:78].strip() for line in support]),
        np.zeros(4, dtype=int),
    )
    assert base[-1] == 1.50
    bulb = bulbs[feature_id - 1][bulb_id]
    printed = np.asarray([bulb['c'][axis] for axis in 'xyz'])
    reconstructed = []
    for terminal_radius in (1.46, 1.50):
        radii = base.copy()
        radii[-1] = terminal_radius
        weights = (radii + 1.4) ** 2
        center = np.linalg.solve(
            2 * (points[1:] - points[0]),
            np.sum(points[1:] ** 2, axis=1)
            - np.dot(points[0], points[0])
            - weights[1:]
            + weights[0],
        )
        radius = np.sqrt(np.dot(center - points[0], center - points[0]) - weights[0])
        reconstructed.append(
            max(np.max(np.abs(center - printed)), abs(radius - bulb['r']))
        )
    assert reconstructed[0] > 0.001
    assert reconstructed[1] <= 0.000050001
