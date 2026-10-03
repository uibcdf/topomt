"""Governance stays separate from the complete supported scientific suite."""

from pathlib import Path

import yaml


def workflow():
    return yaml.load(
        (Path(__file__).resolve().parents[1] / '.github/workflows/CI.yaml').read_text(),
        Loader=yaml.BaseLoader,
    )


def test_every_pull_request_runs_the_complete_supported_suite():
    config = workflow()
    pr = config['on']['pull_request']
    assert not {'paths', 'paths-ignore'} & pr.keys()
    test = config['jobs']['test']
    assert 'continue-on-error' not in test
    cells = test['strategy']['matrix']['cfg']
    assert {(cell['os'], cell['python-version']) for cell in cells} == {
        (os, version)
        for os in ('ubuntu-latest', 'macos-15')
        for version in ('3.11', '3.12', '3.13', '3.14')
    }
    command = next(
        step['run'] for step in test['steps'] if step.get('name') == 'Run tests'
    )
    assert 'python -m pytest --receptor=ci' in command
    assert '--noconftest' not in command
    assert '-m smoke' not in command
