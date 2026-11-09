"""Prevent historical DFND limitations being presented as current claims."""

import json
import tomllib
from pathlib import Path
from typing import Any

import pytest

from devtools.comparative_findings import current_entries, validate_register

ROOT = Path(__file__).resolve().parents[1]


def example(tmp_path):
    evidence = tmp_path / 'evidence.json'
    evidence.write_text(json.dumps({'observation': 'reproduced on a fixed profile'}))
    row = {
        'id': 'boundary-connectivity',
        'kind': 'dfnd_limitation',
        'status': 'current',
        'summary': 'Whole-face clustering merges free patches.',
        'scope': 'One fixed synthetic input and probe; source profile only.',
        'owner': 'TopoMT maintainers',
        'reviewed_on': '2026-11-08',
        'discussion_url': 'https://github.com/uibcdf/topomt/discussions/154#discussioncomment-1',
        'evidence': ['evidence.json'],
        'issue': 'uibcdf/topomt#151',
    }
    return {
        'schema_version': 1,
        'hub_url': 'https://github.com/uibcdf/topomt/discussions/154',
        'findings': [row],
    }, {'uibcdf/topomt#151': {'status': 'open'}}


def test_current_limitation_cannot_survive_a_resolved_local_report(tmp_path):
    register, reports = example(tmp_path)
    reports['uibcdf/topomt#151']['status'] = 'resolved'
    errors = validate_register(register, reports, tmp_path)
    assert any('closed local report' in error for error in errors)


@pytest.mark.parametrize('reason', ['COMPLETED', 'NOT_PLANNED'])
def test_closed_remote_issue_requires_reconciliation_even_if_local_report_is_open(
    tmp_path, reason
):
    register, reports = example(tmp_path)
    snapshot = {
        'issues': {'uibcdf/topomt#151': {'state': 'CLOSED', 'state_reason': reason}}
    }
    errors = validate_register(register, reports, tmp_path, snapshot=snapshot)
    assert any('closed live issue' in error for error in errors)
    register['findings'][0]['status'] = 'needs_review'
    assert validate_register(register, reports, tmp_path, snapshot=snapshot)
    snapshot['issues']['uibcdf/topomt#151']['state'] = 'OPEN'
    assert validate_register(register, reports, tmp_path, snapshot=snapshot) == []
    assert current_entries(register) == []


def test_closed_issue_alone_cannot_prove_a_fix(tmp_path):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row['status'] = 'resolved'
    reports[row['issue']]['status'] = 'resolved'
    errors = validate_register(register, reports, tmp_path)
    assert any('fix_revision' in error for error in errors)
    assert any('regression_guard' in error for error in errors)
    assert any('resolution_scope' in error for error in errors)


def test_a_documented_persistent_limit_requires_reason_and_revisit_condition(tmp_path):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row['status'] = 'documented_limit'
    reports[row['issue']]['status'] = 'withdrawn'
    assert validate_register(register, reports, tmp_path)
    row.update(
        disposition_reason='Accepted boundary of this model, not a fix.',
        revisit_condition='Revisit when the boundary model changes.',
        disposition_evidence=['evidence.json'],
    )
    assert validate_register(register, reports, tmp_path) == []
    assert current_entries(register) == [row]


@pytest.mark.parametrize('kind', ['dfnd_limitation', 'third_party_limitation'])
def test_a_partial_issue_fix_cannot_resolve_the_entire_finding(tmp_path, kind):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row.update(
        kind=kind,
        status='resolved',
        fix_revision='a' * 40,
        regression_guard='tests/test_comparative_findings.py::test_a_partial_issue_fix_cannot_resolve_the_entire_finding',
        resolution_scope='Only the tetrahedron subcase.',
        resolution_evidence=['evidence.json'],
    )
    reports[row['issue']]['status'] = 'partial'
    errors = validate_register(register, reports, tmp_path)
    assert any('unresolved local report' in error for error in errors)


def test_advantage_requires_a_protocol_and_independent_reference(tmp_path):
    register, _ = example(tmp_path)
    row = register['findings'][0]
    row.update(kind='dfnd_advantage')
    row.pop('issue')
    errors = validate_register(register, {}, tmp_path)
    assert any('comparison_protocol' in error for error in errors)
    assert any('independent_reference' in error for error in errors)


def test_third_party_crash_is_not_a_demonstrated_limitation_without_applicability(
    tmp_path,
):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row.update(kind='third_party_limitation')
    assert any(
        'applicability_evidence' in error
        for error in validate_register(register, reports, tmp_path)
    )
    row['status'] = 'needs_review'
    assert validate_register(register, reports, tmp_path) == []


def test_live_card_and_index_must_not_keep_a_resolved_finding_current(tmp_path):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row.update(
        status='resolved',
        fix_revision='a' * 40,
        regression_guard='tests/test_comparative_findings.py::test_live_card_and_index_must_not_keep_a_resolved_finding_current',
        resolution_scope='The same fixed-input profile is corrected.',
        resolution_evidence=['evidence.json'],
    )
    reports[row['issue']]['status'] = 'resolved'
    assert validate_register(register, reports, tmp_path) == []
    snapshot: dict[str, Any] = {
        'issues': {row['issue']: {'state': 'CLOSED'}},
        'findings': {
            row['id']: {'status': 'current', 'discussion_url': row['discussion_url']}
        },
        'current_ids': [row['id']],
    }
    errors = validate_register(register, reports, tmp_path, snapshot=snapshot)
    assert any('live card' in error for error in errors)
    assert any('live current index' in error for error in errors)
    snapshot['findings'][row['id']]['status'] = 'resolved'
    snapshot['current_ids'] = []
    assert validate_register(register, reports, tmp_path, snapshot=snapshot) == []


def test_registered_resolved_history_is_excluded_from_current_claims():
    register = tomllib.loads((ROOT / 'devguide/comparative_findings.toml').read_text())
    historical = next(
        row
        for row in register['findings']
        if row['id'] == 'dfnd-length-argument-admission'
    )
    assert historical['status'] == 'resolved'
    assert historical not in current_entries(register)
    assert historical['fix_revision']
    assert all(row['kind'] != 'dfnd_advantage' for row in current_entries(register))


def test_pending_review_cannot_remain_only_in_discussions(tmp_path):
    register, _ = example(tmp_path)
    row = register['findings'][0]
    row.update(kind='third_party_limitation', status='needs_review')
    row.pop('issue')
    errors = validate_register(register, {}, tmp_path)
    assert any('owning issue/local report' in error for error in errors)


def test_pending_review_requires_an_open_local_work_item(tmp_path):
    register, reports = example(tmp_path)
    row = register['findings'][0]
    row.update(kind='third_party_limitation', status='needs_review')
    reports[row['issue']]['status'] = 'resolved'
    errors = validate_register(register, reports, tmp_path)
    assert any('closed local report' in error for error in errors)


def test_a_completed_comparison_issue_does_not_invalidate_a_scoped_advantage(tmp_path):
    register, reports = example(tmp_path)
    for name in ['protocol.json', 'reference.json']:
        (tmp_path / name).write_text('{}')
    row = register['findings'][0]
    row.update(
        kind='dfnd_advantage',
        comparison_protocol=['protocol.json'],
        independent_reference=['reference.json'],
    )
    reports[row['issue']]['status'] = 'resolved'
    snapshot = {'issues': {row['issue']: {'state': 'CLOSED'}}}
    assert validate_register(register, reports, tmp_path, snapshot=snapshot) == []
