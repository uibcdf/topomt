"""Analytical protocol controls; these tests never execute original detectors."""

import importlib
import subprocess

import molsysmt as msm
import numpy as np
import pytest

import topomt as tmt
from tests.methods.pycasta.test_input_context import source
from tests.test_new_provider_parsers import caver_csv, grid_line
from topomt import pyunitwizard as puw
from topomt.third_party._execution import ProviderExecutionError

__all__ = ['source']


@pytest.fixture(params=['pykvfinder', 'ghecom', 'caver', 'p2rank'])
def protocol_case(request, source, monkeypatch):
    provider = request.param
    runner = importlib.import_module(f'topomt.third_party.{provider}.runner')

    def run(pdb, output, options):
        # Deliberately analytical bytes, not claimed as original detection.
        files = {
            'pykvfinder': {
                'results.toml': '[RESULTS.VOLUME]\nKAA=2.16\n[RESULTS.AREA]\nKAA=1.0\n',
                'cavities.pdb': grid_line(),
            },
            'ghecom': {
                'pockets.pdb': 'REMARK Ncluster 1\nREMARK grid_width 1.0\n#REMARK CLUSTER[1] NVOXEL 1\nMODEL        1\n'
                + grid_line(label='GRD', cluster=64)
                + 'ENDMDL\n'
            },
            'caver': {'analysis/tunnel_profiles.csv': caver_csv()},
            'p2rank': {
                'input.pdb_predictions.csv': 'name,rank,score,probability,sas_points,surf_atoms,center_x,center_y,center_z,residue_ids,surf_atom_ids\na,1,2,.5,1,1,0,0,0,A_1,1\n'
            },
        }[provider]
        for name, text in files.items():
            path = output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
        return {'evidence_kind': 'analytical_protocol_fixture'}, {}

    monkeypatch.setattr(runner, 'run', run)
    if hasattr(runner, 'ensure_available'):
        monkeypatch.setattr(runner, 'ensure_available', lambda options: None)
    options = (
        {'origin': puw.quantity([1, 2, 3], 'angstroms')} if provider == 'caver' else {}
    )
    output = tmt.get_provider_output(
        source,
        method=provider,
        selection=[0, 2, 4],
        structure_indices=1,
        chemical_state=1,
        **options,
    )
    return provider, source, output, runner


@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_new_provider_recovery_is_source_bound_and_engine_free(
    protocol_case, tmp_path, monkeypatch, policy
):
    provider, source, original, _ = protocol_case
    path = tmp_path / 'original.zip'
    original.save(path)

    def forbidden(*args, **kwargs):
        pytest.fail('Saved reconstruction attempted original execution')

    monkeypatch.setattr(subprocess, 'run', forbidden)
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    assert original.run.metadata['selected_atom_indices'] == [0, 2, 4]
    with puw.context(standard_units=[*policy, 'radians']):
        recovered = tmt.load_provider_output(path, molecular_system=source)
        assert recovered.run == original.run
        assert [r.record_kind for r in recovered.records] == [
            r.record_kind for r in original.records
        ]
        assert [r.source_id for r in recovered.records] == [
            r.source_id for r in original.records
        ]
        np.testing.assert_allclose(
            puw.get_value(recovered.input_coordinates, to_unit='nm'),
            puw.get_value(original.input_coordinates, to_unit='nm'),
        )
        for before, after in zip(original.records, recovered.records, strict=True):
            assert before.geometries == after.geometries
            for name, value in before.measurements.items():
                assert value.original_value == after.measurements[name].original_value
    changed = msm.copy(source)
    msm.set(
        changed,
        coordinates=msm.get(changed, coordinates=True) + puw.quantity([1, 0, 0], 'nm'),
    )
    with pytest.raises(ValueError, match='coordinates'):
        tmt.load_provider_output(path, molecular_system=changed)


def test_failed_original_keeps_inspectable_bytes_and_cannot_be_recovered(
    protocol_case, tmp_path, monkeypatch
):
    provider, source, _, runner = protocol_case

    def fail(pdb, output, options):
        (output / 'stdout.txt').write_text('Original failure receipt\n')
        raise ProviderExecutionError(provider=provider, reason='controlled failure')

    monkeypatch.setattr(runner, 'run', fail)
    options = (
        {'origin': puw.quantity([1, 2, 3], 'angstroms')} if provider == 'caver' else {}
    )
    with pytest.raises(ProviderExecutionError) as caught:
        tmt.get_provider_output(source, method=provider, **options)
    failed = caught.value.run
    assert failed is not None and failed.metadata['execution_status'] == 'failed'
    assert failed.get_artifact('output/stdout.txt') == b'Original failure receipt\n'
    path = tmp_path / 'failure.zip'
    failed.save(path)
    with pytest.raises(ValueError, match='protocol'):
        tmt.load_provider_output(path, molecular_system=source)


def test_rejected_original_result_keeps_failed_receipt_and_auxiliary_input(
    protocol_case, tmp_path, monkeypatch
):
    provider, source, _, runner = protocol_case

    def invalid(pdb, output, options):
        (output / 'stdout.txt').write_text('Original process completed\n')
        extra = pdb.parent / 'settings.txt'
        extra.write_text('Original auxiliary input\n')
        return {'returncode': 0}, {'settings.txt': extra}

    monkeypatch.setattr(runner, 'run', invalid)
    options = (
        {'origin': puw.quantity([1, 2, 3], 'angstroms')} if provider == 'caver' else {}
    )
    with pytest.raises(
        ProviderExecutionError, match='original result is invalid'
    ) as caught:
        tmt.get_provider_output(source, method=provider, **options)
    failed = caught.value.run
    assert failed is not None
    assert failed.metadata['execution_status'] == 'failed'
    assert failed.metadata['failure_stage'] == 'result_validation'
    assert failed.metadata['returncode'] == 0
    assert failed.get_artifact('output/stdout.txt') == b'Original process completed\n'
    assert failed.get_artifact('input/settings.txt') == b'Original auxiliary input\n'
    assert failed.metadata['selected_atom_indices']
    assert failed.get_artifact('output/topomt_source_context.json')
    path = tmp_path / 'invalid.zip'
    failed.save(path)
    with pytest.raises(ValueError, match='protocol'):
        tmt.load_provider_output(path, molecular_system=source)
