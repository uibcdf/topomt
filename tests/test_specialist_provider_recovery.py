"""Source-bound specialist recovery and optional attribution regression controls."""

import importlib
import json
import subprocess
import sys
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path

import pytest

import topomt as tmt
from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun

DATA = Path(__file__).parent / 'data/original_local'
CASES = [
    ('hole', 'hole.zip', 'hole/input.pdb'),
    ('pisa', 'pisa.zip', 'pisa/input.pdb'),
    ('pisa', 'pisa-empty.zip', 'pisa/empty_input.pdb'),
    ('povme', 'povme-positive.zip', 'pisa/input.pdb'),
    ('povme', 'povme-empty.zip', 'pisa/input.pdb'),
    ('povme', 'povme-outside.zip', 'pisa/input.pdb'),
]
PAPERS = {
    'hole': 'doi:10.1016/S0006-3495(93)81293-1',
    'pisa': 'doi:10.1016/j.jmb.2007.05.022',
    'povme': 'doi:10.1021/ct500381c',
}


def bundle(provider, name):
    return DATA / provider / name


@pytest.mark.parametrize('provider,name,source', CASES)
@pytest.mark.parametrize('policy', [['nm', 'ps'], ['pm', 'fs']])
def test_original_specialist_saved_reading_is_engine_independent(
    provider, name, source, policy, monkeypatch
):
    import ackredit

    def forbidden(*args, **kwargs):
        pytest.fail('Saved reading attempted scientific execution')

    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    with puw.context(standard_units=policy), ackredit.session('read saved specialist'):
        output = tmt.load_provider_output(
            bundle(provider, name), molecular_system=str(DATA / source)
        )
        assert output.run.provider == provider
        assert output.attribution['status'] == 'recorded'
        assert PAPERS[provider] in {
            entry['item']['id'] for entry in output.attribution['references']
        }
        assert tmt.cite(output)
        assert ackredit.get_attribution().to_dict()['items'] == []
        if provider == 'povme':
            volume = output.regions[0].measurements['volume']
            assert (
                puw.get_value(volume.value, to_unit='angstroms**3')
                == volume.original_value
            )


@pytest.mark.parametrize('provider,name,source', [CASES[0], CASES[1], CASES[3]])
def test_specialist_fresh_reader_needs_no_engines_or_recorder(provider, name, source):
    code = """
import importlib.abc,sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self,fullname,path=None,target=None):
        if fullname.split('.')[0] in {'ackredit','povme','pymolecule','pydantic','loguru','ray'} or fullname in {'topomt.third_party.hole.runner','topomt.third_party.pisa.runner','topomt.third_party.povme.runner'}:
            raise ModuleNotFoundError('Blocked optional engine dependency',name=fullname)
sys.meta_path.insert(0,Block())
import topomt as tmt
result=tmt.load_provider_output(sys.argv[1],molecular_system=sys.argv[2])
assert result.attribution['status']=='recorded'
assert not any(name in sys.modules for name in ['ackredit','povme','pymolecule','ray'])
"""
    subprocess.run(
        [sys.executable, '-c', code, str(bundle(provider, name)), str(DATA / source)],
        check=True,
        timeout=30,
    )


@pytest.mark.parametrize('provider,name,source', [CASES[0], CASES[1], CASES[3]])
@pytest.mark.parametrize('mutation', ['fingerprint', 'missing_input', 'query'])
def test_specialist_saved_evidence_refuses_input_or_query_conflicts(
    provider, name, source, mutation
):
    run = ProviderRun.load(bundle(provider, name))
    metadata = run.metadata
    key = next(iter(metadata['input_fingerprints']))
    if mutation == 'fingerprint':
        metadata['input_fingerprints'][key] = '0' * 64
    elif mutation == 'missing_input':
        run = replace(
            run,
            artifacts=tuple(
                (name, data) for name, data in run.artifacts if name != 'input/' + key
            ),
        )
    elif provider == 'hole':
        metadata['parameters']['sample_step'] = 0.25
    elif provider == 'pisa':
        metadata['assembly_policy'] = 'predicted'
    else:
        run = replace(
            run,
            artifacts=tuple(
                (name, data.replace(b'"angstroms**3"', b'"nm**3"'))
                if name == 'output/engine_identity.json'
                else (name, data)
                for name, data in run.artifacts
            ),
        )
    run = replace(run, metadata_json=json.dumps(metadata))
    with pytest.raises(ValueError):
        importlib.import_module(f'topomt.third_party.{provider}.parser').parse_output(
            run
        )


def replay(monkeypatch, provider):
    name = {'hole': 'hole.zip', 'pisa': 'pisa.zip', 'povme': 'povme-positive.zip'}[
        provider
    ]
    original = ProviderRun.load(bundle(provider, name))
    runner = importlib.import_module(f'topomt.third_party.{provider}.runner')

    def execute(pdb, output, options):
        additional = {}
        for name, data in original.artifacts:
            if (
                name.startswith('output/')
                and name != 'output/topomt_source_context.json'
            ):
                path = output / name.removeprefix('output/')
                path.parent.mkdir(exist_ok=True, parents=True)
                path.write_bytes(data)
            if name.startswith('input/') and name != 'input/input.pdb':
                relative = name.removeprefix('input/')
                path = output / relative
                path.write_bytes(data)
                additional[relative] = path
        return original.metadata, additional

    monkeypatch.setattr(runner, 'ensure_available', lambda options: None)
    monkeypatch.setattr(runner, 'run', execute)
    options = {}
    if provider == 'hole':
        options = {
            'origin': puw.quantity([0, 0, 0], 'angstroms'),
            'direction': [0, 0, 1],
            'end_radius': 7.0,
        }
    if provider == 'povme':
        options = {
            'inclusion_regions': [
                {
                    'shape': 'box',
                    'center': puw.quantity([0, 2.5, 5.5], 'angstroms'),
                    'lengths': puw.quantity([6, 7, 9], 'angstroms'),
                }
            ],
            'grid_step': 1.0,
            'distance_cutoff': 0,
            'convex_hull_exclusion': False,
            'contiguous_points_criteria': 0,
        }
    source = DATA / ('hole/input.pdb' if provider == 'hole' else 'pisa/input.pdb')
    return source, options, runner


@pytest.mark.parametrize('provider', ['hole', 'pisa', 'povme'])
@pytest.mark.parametrize('state', ['absent', 'failed'])
def test_optional_specialist_attribution_preserves_science(
    monkeypatch, provider, state
):
    """Replay original artifacts to test the host wrapper, not engine execution."""
    import ackredit

    from topomt import _ackredit

    source, options, _ = replay(monkeypatch, provider)
    if state == 'absent':
        monkeypatch.setattr(_ackredit, 'backend', lambda: None)
    else:
        monkeypatch.setattr(ackredit, 'track_item', lambda *args, **kwargs: 1 / 0)
    with (
        ackredit.session('optional recorder'),
        pytest.warns(Warning) if state == 'failed' else nullcontext(),
    ):
        result = tmt.get_provider_output(str(source), method=provider, **options)
    assert result.records
    assert result.attribution['status'] == (
        'unavailable' if state == 'absent' else 'failed'
    )
    assert PAPERS[provider] in {
        entry['item']['id'] for entry in result.attribution['references']
    }


@pytest.mark.parametrize('provider', ['hole', 'pisa', 'povme'])
def test_failed_specialist_retains_failed_run_without_completion_credit(
    monkeypatch, tmp_path, provider
):
    import ackredit

    from topomt.third_party._execution import ProviderExecutionError

    source, options, runner = replay(monkeypatch, provider)

    def fail(pdb, output, options):
        (output / 'stderr.txt').write_text('Controlled original failure')
        raise ProviderExecutionError(provider=provider, reason='controlled failure')

    monkeypatch.setattr(runner, 'run', fail)
    with ackredit.session('failed original'):
        with pytest.raises(ProviderExecutionError) as caught:
            tmt.get_provider_output(str(source), method=provider, **options)
        assert PAPERS[provider] not in {
            item['id'] for item in ackredit.get_attribution().to_dict()['items']
        }
    assert caught.value.run.metadata['execution_status'] == 'failed'
    target = tmp_path / 'failed.zip'
    caught.value.run.save(target)
    with pytest.raises(ValueError):
        tmt.load_provider_output(target, molecular_system=str(source))


@pytest.mark.parametrize('provider,name,source', [CASES[0], CASES[1], CASES[3]])
def test_specialist_saved_source_coordinates_cannot_be_substituted(
    provider, name, source
):
    import molsysmt as msm

    changed = msm.convert(str(DATA / source), to_form='molsysmt.MolSys')
    msm.set(
        changed,
        coordinates=msm.get(changed, coordinates=True)
        + puw.quantity([0.2, 0, 0], 'nm'),
    )
    with pytest.raises(ValueError, match='coordinates'):
        tmt.load_provider_output(bundle(provider, name), molecular_system=changed)
