import subprocess
import sys
import warnings
from pathlib import Path


def test_import_topomt_does_not_replace_global_warning_formatter():
    repo_root = Path(__file__).resolve().parents[1]
    code = (
        "import warnings; "
        "original = warnings.formatwarning; "
        "import topomt; "
        "raise SystemExit(0 if warnings.formatwarning is original else 1)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_setup_logging_warning_formatter_is_scoped_to_topomt():
    from topomt.config.logging_setup import setup_logging

    original = warnings.formatwarning
    setup_logging(capture_warnings=True, simplify_warning_format=True)
    try:
        external = warnings.formatwarning("external", UserWarning, "/tmp/external.py", 1)
        topomt_file = str(Path(__file__).resolve().parents[1] / "topomt" / "dummy.py")
        internal = warnings.formatwarning("internal", UserWarning, topomt_file, 1)
    finally:
        warnings.formatwarning = original

    assert "external.py:1" in external
    assert external != "UserWarning: external\n"
    assert internal == "UserWarning: internal\n"
