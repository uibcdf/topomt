#!/usr/bin/env python3
"""
Unified Conda/Mamba environment manager for TopoMT.

Replaces:
- devtools/start_dev_env.sh
- devtools/conda-envs/create_conda_env.py
- devtools/conda-envs/update_conda_env.py

Usage:
    python devtools/conda_env_manager.py create [--env-yaml FILE] [--env-name NAME] [--python 3.12]
    python devtools/conda_env_manager.py update [--env-yaml FILE] [--env-name NAME]
    python devtools/conda_env_manager.py dev [--env-yaml FILE] [--env-name NAME] [--python 3.12] [--no-editable]
"""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

try:
    import yaml
except ImportError:
    raise SystemExit('PyYAML required: install it via conda/mamba install pyyaml')

# Possible roots and YAML candidates
REPO_ROOTS = [
    Path.cwd(),
    Path(__file__).resolve().parent,
    Path(__file__).resolve().parent.parent,
]
ENV_CANDIDATES = [
    'development_env.yaml',
    'dev_env.yaml',
    'conda-envs/development_env.yaml',
    'conda-envs/docs_env.yaml',
]


def find_env_yaml(path_arg: str | None) -> Path:
    """Find a YAML file describing the environment."""
    if path_arg:
        p = Path(path_arg).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(p)
        return p

    env_var = os.environ.get('USER_ENV_YAML')
    if env_var:
        p = Path(env_var).expanduser().resolve()
        if p.exists():
            return p

    for root in REPO_ROOTS:
        for rel in ENV_CANDIDATES:
            candidate = (
                root / 'devtools' / rel
                if not rel.startswith('conda-envs')
                else root / 'devtools' / rel
            )
            if candidate.exists():
                return candidate

    raise SystemExit('Could not locate any conda environment YAML file.')


def load_yaml_override_python(yaml_path: Path, python_version: str | None) -> dict:
    """Load the YAML file and optionally override the Python version."""
    with yaml_path.open() as f:
        data = yaml.safe_load(f)
    if not python_version:
        return data
    spec = f'python {python_version}*'
    deps = data.get('dependencies', [])
    for i, dep in enumerate(deps):
        if isinstance(dep, str) and dep.startswith('python'):
            deps[i] = spec
            break
    else:
        deps.insert(0, spec)
    data['dependencies'] = deps
    return data


def write_tmp_yaml(data: dict, name: str = 'tmp_env.yaml') -> Path:
    tmp = Path.cwd() / name
    with tmp.open('w') as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return tmp


def find_pm() -> tuple[str, str]:
    """Return path and name of the environment manager (micromamba, mamba, conda)."""
    for pm in ('micromamba', 'mamba', 'conda'):
        path = shutil.which(pm)
        if path:
            return path, pm
    raise SystemExit('No conda/mamba/micromamba executable found in PATH.')


def run(cmd: list[str]) -> None:
    print('[cmd]', ' '.join(cmd))
    subprocess.check_call(cmd)


def env_exists(pm: str, env_name: str) -> bool:
    out = subprocess.check_output([pm, 'env', 'list'], text=True)
    return any(env_name in line.split() for line in out.splitlines())


def create_env(pm: str, pm_type: str, env_name: str, yaml_file: Path) -> None:
    if pm_type == 'micromamba':
        run([pm, 'create', '-y', '-n', env_name, '-f', str(yaml_file)])
    else:
        run([pm, 'env', 'create', '-n', env_name, '-f', str(yaml_file)])


def update_env(pm: str, pm_type: str, env_name: str, yaml_file: Path) -> None:
    if pm_type == 'micromamba':
        run([pm, 'env', 'update', '-n', env_name, '-f', str(yaml_file)])
    else:
        run([pm, 'env', 'update', '-n', env_name, '-f', str(yaml_file), '--prune'])


def install_editable(pm: str, env_name: str) -> None:
    run(
        [
            pm,
            'run',
            '-n',
            env_name,
            'python',
            '-m',
            'pip',
            'install',
            '--no-deps',
            '-e',
            '.',
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description='Unified Conda/Mamba environment manager for TopoMT.'
    )
    parser.add_argument(
        'command', choices=['create', 'update', 'dev'], help='Action to perform.'
    )
    parser.add_argument(
        '--env-yaml', help='Path to environment YAML (auto-detected if omitted).'
    )
    parser.add_argument(
        '--env-name', default='topomt', help='Name of the conda environment.'
    )
    parser.add_argument('--python', help='Override Python version, e.g. 3.12.')
    parser.add_argument(
        '--no-editable',
        action='store_true',
        help='Skip installing the package in editable mode.',
    )
    args = parser.parse_args()

    yaml_path = find_env_yaml(args.env_yaml)
    data = load_yaml_override_python(yaml_path, args.python)
    tmp_yaml = write_tmp_yaml(data)

    pm_path, pm_type = find_pm()

    if args.command == 'create':
        create_env(pm_path, pm_type, args.env_name, tmp_yaml)
    elif args.command == 'update':
        update_env(pm_path, pm_type, args.env_name, tmp_yaml)
    elif args.command == 'dev':
        if env_exists(pm_path, args.env_name):
            update_env(pm_path, pm_type, args.env_name, tmp_yaml)
        else:
            create_env(pm_path, pm_type, args.env_name, tmp_yaml)
        if not args.no_editable:
            install_editable(pm_path, args.env_name)

    print(
        f"[ok] Environment '{args.env_name}' ready. Activate it with:\n  conda activate {args.env_name}"
    )


if __name__ == '__main__':
    main()
