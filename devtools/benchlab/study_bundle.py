"""Build the source-bound three-case study download without executing science."""

import hashlib
import json
import zipfile
from pathlib import Path


def build_bundle(root: Path, output: Path) -> dict:
    """Package published study sources, reference checkers and environment inputs."""
    files = [
        path
        for folder in ('docs/content/benchlab', 'docs/content/dfnd')
        for path in (root / folder).rglob('*')
        if path.is_file()
        and '__pycache__' not in path.parts
        and '.ipynb_checkpoints' not in path.parts
    ]
    files += [
        root / 'devtools' / name
        for name in (
            'verify_closed_shell_wall_cover.py',
            'verify_opening_connectivity.py',
            'verify_tetrahedron_boundary.py',
            'conda-envs/development_env.yaml',
            'requirements/controlled_suite_dependencies_py314.txt',
        )
    ]
    guide = (
        '# TopoMT three-case study\n\n'
        'Use the qualified TopoMT Python 3.14 source-development environment. '
        'Environment inputs and exact suite source pins are included under devtools/. '
        'They describe the tested source route, not a newly qualified public installation.\n\n'
        'Open docs/content/benchlab/synthetic/CASE/topography.ipynb in Jupyter; '
        'run from that notebook directory in a fresh kernel. Start with regular_tetrahedron, '
        'then closed_shell and shell_with_opening. Original providers and servers are not run. '
        'The closed parent is included for the opening subset. The older notebooks are '
        'frozen history: the new topography stage links their current dispositions.\n\n'
        'MANIFEST.json identifies every included source byte. Source dependency acquisition '
        'may require network access when preparing an environment; Run All does not.\n'
    ).encode()
    contents = {
        str(path.relative_to(root)): path.read_bytes() for path in sorted(set(files))
    }
    contents['README_STUDY.md'] = guide
    manifest = {
        'schema': 'topomt.benchlab.download/1',
        'scope': 'Source-bound reader study; no original-provider execution or installed matrix claim',
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


def verify_manifest(root: Path) -> dict:
    """Verify the unpacked source bundle before the receiving execution."""
    root = root.resolve()
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    if manifest.get('schema') != 'topomt.benchlab.download/1':
        raise ValueError('Unrecognized study manifest')
    for name, expected in manifest['files'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f'Integrity: missing or invalid study file {name}')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f'Integrity: changed study file {name}')
    return manifest
