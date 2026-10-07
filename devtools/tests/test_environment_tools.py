"""Guard first shared environment-tool adoption and owner selection."""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'devtools'))
from check_dependency_routes import SDK_SHA, load_sdk  # noqa: E402 — owner path


class TestEnvironmentTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tools = load_sdk('conda_environment_tools')

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='topomt-environment-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in (
            'pyproject.toml',
            'devtools/requirements.yaml',
            'devtools/environment_tools.toml',
            'devtools/dependency_routes.toml',
            'devtools/conda-envs',
            'devtools/conda-build',
            'devtools/requirements',
        ):
            source, target = ROOT / name, self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(
                    source, target, ignore=shutil.ignore_patterns('__pycache__')
                )
            else:
                shutil.copy2(source, target)

    def snapshot(self):
        return {
            str(p.relative_to(self.root)): p.read_bytes()
            for p in self.root.rglob('*')
            if p.is_file()
        }

    def test_profile_selects_five_outputs_and_preserves_science_recipe_and_sources(
        self,
    ):
        before = self.snapshot()
        documents = self.tools.environment_documents(self.root)
        self.assertEqual(
            set(documents),
            {
                f'devtools/conda-envs/{name}_env.yaml'
                for name in ('production', 'development', 'docs', 'setup', 'build')
            },
        )
        self.tools.generate(self.root, check=True)
        self.assertEqual(before, self.snapshot())
        protected = [
            'devtools/conda-build/meta.yaml',
            'devtools/conda-build/release_plan.example.toml',
            *[
                f'devtools/conda-envs/{name}.yaml'
                for name in (
                    'test_env',
                    'test_env_py313',
                    'test_env_py314',
                    'importable_env',
                )
            ],
            *[
                str(p.relative_to(self.root))
                for p in self.root.glob('devtools/requirements/*.txt')
            ],
        ]
        self.tools.generate(self.root)
        for name in protected:
            self.assertEqual(before[name], (self.root / name).read_bytes())

    def test_metadata_floor_propagates_to_all_generated_runtime_environments(self):
        project = self.root / 'pyproject.toml'
        project.write_text(project.read_text().replace('"numpy",', '"numpy>=2.1,<3",'))
        for name in ('production', 'development', 'docs'):
            document = yaml.safe_load(
                self.tools.environment_documents(self.root)[
                    f'devtools/conda-envs/{name}_env.yaml'
                ]
            )
            self.assertIn('numpy<3,>=2.1', document['dependencies'])

    def test_drift_and_late_invalid_tooling_fail_without_writing(self):
        path = self.root / 'devtools/conda-envs/production_env.yaml'
        path.write_text(path.read_text().replace('- depdigest>=0.12.0\n', ''))
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'differ'):
            self.tools.generate(self.root, check=True)
        self.assertEqual(before, self.snapshot())
        groups = self.root / 'devtools/requirements.yaml'
        groups.write_text(
            groups.read_text().replace(
                'anaconda-client, conda-build', 'python=3.7, conda-build'
            )
        )
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'metadata/context'):
            self.tools.generate(self.root)
        self.assertEqual(before, self.snapshot())

    def test_routine_minor_and_specialized_source_minors_are_checked(self):
        path = 'devtools/conda-envs/development_env.yaml'
        with self.assertRaisesRegex(ValueError, 'routine'):
            self.tools.selected_environment(self.root, path, '3.13')
        selected = self.tools.selected_environment(self.root, path, '3.14')
        self.assertEqual('python>=3.14,<3.15', selected['dependencies'][0])
        with self.assertRaises(ValueError):
            self.tools.selected_environment(
                self.root, 'devtools/conda-envs/test_env_py313.yaml', '3.14'
            )
        selected = self.tools.selected_environment(
            self.root, 'devtools/conda-envs/test_env_py313.yaml', '3.13'
        )
        self.assertIn('ambermd', selected['channels'])
        self.assertNotIn('molsysmt', selected['dependencies'])

    def test_invalid_manager_is_rejected_before_any_real_environment_operation(self):
        before = self.snapshot()
        with (
            patch.object(self.tools.shutil, 'which', return_value=None),
            patch.object(
                self.tools.subprocess,
                'run',
                side_effect=AssertionError('manager invoked'),
            ),
            self.assertRaisesRegex(ValueError, 'manager'),
        ):
            self.tools.apply_environment(
                self.root,
                'devtools/conda-envs/production_env.yaml',
                '3.14',
                manager='missing',
                name='test-new',
            )
        self.assertEqual(before, self.snapshot())

    def test_all_legacy_entry_points_are_inert_when_imported(self):
        for relative in (
            'devtools/broadcast_requirements.py',
            'devtools/conda_env_manager.py',
        ):
            spec = importlib.util.spec_from_file_location(
                'inert_owner_' + Path(relative).stem, ROOT / relative
            )
            module = importlib.util.module_from_spec(spec)
            with (
                self.subTest(relative=relative),
                patch.object(sys, 'argv', ['tool', '--invalid']),
                patch.object(
                    Path, 'write_text', side_effect=AssertionError('write at import')
                ),
                patch.object(
                    subprocess, 'run', side_effect=AssertionError('manager at import')
                ),
            ):
                spec.loader.exec_module(module)

    def test_sdk_loader_refuses_a_different_commit(self):
        with (
            patch(
                'check_dependency_routes.subprocess.check_output',
                side_effect=['a' * 40, ''],
            ),
            self.assertRaisesRegex(ValueError, 'immutable'),
        ):
            load_sdk('conda_environment_tools')
        self.assertEqual(SDK_SHA, '8f00e6d9de943b6e4710ea62936e2ebea00fad24')

    def test_cli_check_runs_from_outside_owner_without_importing_science(self):
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / 'devtools/broadcast_requirements.py'),
                '--check',
            ],
            cwd='/tmp',
            env=os.environ.copy(),
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn('"changed": []', result.stdout)


if __name__ == '__main__':
    unittest.main()
