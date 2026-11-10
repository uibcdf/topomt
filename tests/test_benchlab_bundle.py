"""Downloaded studies must carry their parent inputs and integrity manifest."""

import zipfile
from pathlib import Path

import pytest

from devtools.benchlab.study_bundle import build_bundle, verify_manifest


def test_download_bundle_recovers_parent_and_reference_helpers(tmp_path):
    root = Path(__file__).resolve().parents[1]
    output = tmp_path / 'study.zip'
    build_bundle(root, output)
    extracted = tmp_path / 'outside'
    with zipfile.ZipFile(output) as archive:
        archive.extractall(extracted)
    manifest = verify_manifest(extracted)
    assert (
        'docs/content/benchlab/synthetic/closed_shell/artifacts/closed_shell_v1/input.json'
        in manifest['files']
    )
    assert 'devtools/verify_opening_connectivity.py' in manifest['files']
    assert 'devtools/verify_closed_shell_wall_cover.py' in manifest['files']
    target = (
        extracted
        / 'docs/content/benchlab/synthetic/closed_shell/artifacts/closed_shell_v1/input.json'
    )
    target.write_text('{}')
    with pytest.raises(ValueError, match='Integrity'):
        verify_manifest(extracted)
