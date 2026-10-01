"""Test the CLI dependency boundary without importing scientific orchestration.

Normal suite runs use the real package already loaded by conftest. Standalone
--noconftest runs isolate its package namespaces while loading the actual runner,
dependency configuration and SMonitor catalog from this checkout.
"""

import importlib
import importlib.machinery
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import depdigest.core.checker as checker
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def runner(monkeypatch):
    for name in (
        'topomt',
        'topomt._private',
        'topomt.third_party',
        'topomt.third_party.fpocket',
    ):
        if name not in sys.modules:
            package = ModuleType(name)
            package.__path__ = [str(ROOT.joinpath(*name.split('.')))]
            package.__spec__ = importlib.machinery.ModuleSpec(
                name, loader=None, is_package=True
            )
            monkeypatch.setitem(sys.modules, name, package)
    return importlib.import_module('topomt.third_party.fpocket.runner')


def test_fpocket_declares_executable_and_truthful_routes(runner):
    from topomt._depdigest import LIBRARIES

    assert LIBRARIES['fpocket'] == {
        'type': 'soft',
        'kind': 'executable',
        'executable': 'fpocket',
        'pypi': None,
        'conda': 'fpocket',
        'channel': 'conda-forge',
    }


def test_missing_custom_command_fails_before_execution(runner, monkeypatch, tmp_path):
    command = str(tmp_path / 'absent_fpocket')
    checked = []

    def missing(actual):
        checked.append(actual)
        return None

    def forbid_execution(*args, **kwargs):
        raise AssertionError('missing command must fail before execution')

    monkeypatch.setattr(checker.shutil, 'which', missing)
    monkeypatch.setattr(runner.subprocess, 'run', forbid_execution)
    with pytest.raises(runner.FpocketError) as caught:
        runner.run_fpocket(tmp_path / 'input.pdb', fpocket_cmd=command)
    assert checked == [command]
    assert caught.value.code == 'ExecutableNotFoundError'
    assert caught.value.extra['executable'] == command
    assert 'conda install -c conda-forge fpocket' in str(caught.value)
    assert 'pip install' not in str(caught.value)
    assert type(caught.value)(*caught.value.args).args == caught.value.args


def test_custom_command_does_not_require_default_fpocket(runner, monkeypatch, tmp_path):
    command = str(tmp_path / 'configured_fpocket')
    checked = []
    pdb_file = tmp_path / 'input.pdb'
    expected = tmp_path / 'input_out'

    def available(actual):
        checked.append(actual)
        return command if actual == command else None

    def execute(args, **kwargs):
        assert args == [command, '-f', str(pdb_file.resolve()), '--flag']
        assert kwargs['cwd'] == tmp_path.resolve()
        assert kwargs['check'] is True
        expected.mkdir()

    monkeypatch.setattr(checker.shutil, 'which', available)
    monkeypatch.setattr(runner.subprocess, 'run', execute)
    assert (
        runner.run_fpocket(pdb_file, fpocket_cmd=command, extra_args=['--flag'])
        == expected
    )
    assert checked == [command]


def test_missing_working_directory_keeps_original_error(runner, monkeypatch, tmp_path):
    original = FileNotFoundError('working directory is absent')
    monkeypatch.setattr(checker.shutil, 'which', lambda actual: actual)

    def fail(*args, **kwargs):
        raise original

    monkeypatch.setattr(runner.subprocess, 'run', fail)
    with pytest.raises(FileNotFoundError) as caught:
        runner.run_fpocket(tmp_path / 'input.pdb', workdir=tmp_path / 'absent')
    assert caught.value is original


def test_execution_failure_keeps_fpocket_error_and_cause(runner, monkeypatch, tmp_path):
    original = subprocess.CalledProcessError(7, ['fpocket'], stderr='engine failed')
    monkeypatch.setattr(checker.shutil, 'which', lambda actual: actual)

    def fail(*args, **kwargs):
        raise original

    monkeypatch.setattr(runner.subprocess, 'run', fail)
    with pytest.raises(runner.FpocketError, match='code 7') as caught:
        runner.run_fpocket(tmp_path / 'input.pdb')
    assert caught.value.__cause__ is original
    assert 'engine failed' in str(caught.value)


def test_provider_internal_import_failure_is_not_engine_absence(
    runner, monkeypatch, tmp_path
):
    original = ImportError('internal provider failure')

    def fail(actual):
        raise original

    monkeypatch.setattr(checker.shutil, 'which', fail)
    with pytest.raises(ImportError) as caught:
        runner.run_fpocket(tmp_path / 'input.pdb')
    assert caught.value is original
