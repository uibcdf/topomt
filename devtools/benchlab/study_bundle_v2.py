"""Package the current source-bound reader while retaining the v1 download."""

import hashlib
import json
import zipfile
from pathlib import Path


def build_bundle(root: Path, output: Path, source_revision: str) -> dict:
    """Build a deterministic v2 ZIP with source identity and independent helpers.

    Parameters
    ----------
    root : Path
        Repository source tree containing the reviewed study files.
    output : Path
        New ZIP destination; the preserved v1 archive is never replaced.
    source_revision : str
        Full committed TopoMT source revision for this reader's environment.

    Returns
    -------
    dict
        Manifest accepted by the existing source-bundle integrity verifier.

    Raises
    ------
    ValueError
        Source identity is not a full hexadecimal Git revision.
    """
    if len(source_revision) != 40 or any(
        char not in '0123456789abcdef' for char in source_revision
    ):
        raise ValueError('A full committed source revision is required')
    files = [
        path
        for folder in ('docs/content/benchlab', 'docs/content/dfnd')
        for path in (root / folder).rglob('*')
        if path.is_file()
        and '__pycache__' not in path.parts
        and '.ipynb_checkpoints' not in path.parts
    ]
    files += list((root / 'devtools').glob('verify_*.py'))
    files += [
        root / 'devtools' / path
        for path in (
            'benchlab/public_contract.py',
            'benchlab/capture_volume.py',
            'benchlab/tube_study.py',
            'conda-envs/development_env.yaml',
            'requirements/controlled_suite_dependencies_py314.txt',
        )
    ]
    for path in ('devtools/__init__.py', 'devtools/benchlab/__init__.py'):
        if (root / path).is_file():
            files.append(root / path)
    contents = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(set(files))
    }
    contents['README_STUDY.md'] = (
        '# TopoMT three-case study — reader v2\n\n'
        'Start at docs/content/benchlab/synthetic/CASE/public_topography_v2.ipynb '
        'in a fresh Python 3.14 Jupyter kernel, working from its case directory. '
        'Use regular_tetrahedron, then closed_shell and shell_with_opening. '
        'Run All makes no server requests or original-provider executions. '
        'All inputs, parent correspondence and reference replay helpers are included.\n\n'
        'Use the source-development environment described in '
        'devtools/conda-envs/development_env.yaml; exact suite acquisition inputs are in '
        'devtools/requirements/controlled_suite_dependencies_py314.txt. '
        f'This reader is bound to TopoMT source {source_revision}. '
        'Prepare that checkout/environment separately; for example install its '
        'reviewed requirements with `python -m pip install --no-deps -r '
        'devtools/requirements/controlled_suite_dependencies_py314.txt`, then '
        '`python -m pip install --no-deps /path/to/that/topomt-checkout`. '
        'Source/environment acquisition can need network access; notebook Run All does not. '
        'Do not replace the pinned source with an unqualified released package.\n\n'
        'This is source-bound receiving, not a fully locked environment, installed '
        'release qualification or a platform matrix. Actual receiving records '
        'retain the imported module path and dependency versions. '
        'The original system/native/comparison notebooks and public reader v1 '
        'remain dated history. The separately preserved three_cases_v1.zip is unchanged.\n\n'
        'MANIFEST.json identifies every included source byte and the source revision. '
        'Verify its SHA-256 entries after extraction. Native support JSON is study '
        'evidence, not a versioned public Topography interchange format.\n'
    ).encode()
    manifest = {
        'schema': 'topomt.benchlab.download/1',
        'reader_revision': 2,
        'topomt_source_revision': source_revision,
        'scope': 'Source-bound current reader; no original engine or installed matrix claim',
        'files': {
            name: hashlib.sha256(data).hexdigest() for name, data in contents.items()
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            item = zipfile.ZipInfo(name, date_time=(2026, 11, 10, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(item, data)
        archive.writestr('MANIFEST.json', json.dumps(manifest, indent=2) + '\n')
    return manifest
