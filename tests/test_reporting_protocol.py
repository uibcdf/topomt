import subprocess
import sys
from pathlib import Path

from devtools import devguide_reports


def test_devguide_records_and_generated_indexes_are_valid():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, 'devtools/devguide_index.py', '--check'],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_resolved_guards_address_declared_tests():
    assert (
        devguide_reports.validate_guard(
            'tests/test_import.py::test_molsysviewer_topomt_exports_lifecycle_hooks'
        )
        == []
    )
    assert devguide_reports.validate_guard(
        'tests/test_import.py::test_nonexistent_lifecycle_guard'
    )
