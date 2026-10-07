"""Guard actual shared operations against TopoMT declaration regressions."""

import io
import json
import shutil
import sys
import tarfile
import tempfile
import tomllib
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'devtools'))
from check_dependency_routes import load_sdk  # noqa: E402 — owner tool path above

PLAN = 'devtools/conda-build/release_plan.example.toml'
RESOURCES = 'devtools/conda-build/resources.toml'


class TestDistributionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.routes = load_sdk()
        from devtools.scripts import noarch_conda, verify_installed_matrix

        cls.noarch = noarch_conda
        cls.matrix = verify_installed_matrix

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='topomt-controls-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for name in (
            'pyproject.toml',
            '.github',
            'devtools/conda-build',
            'devtools/conda-envs',
            'devtools/requirements',
            'devtools/dependency_routes.toml',
            'topomt',
            'molsysviewer_topomt',
        ):
            source, target = ROOT / name, self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(
                    source, target, ignore=shutil.ignore_patterns('__pycache__')
                )
            else:
                shutil.copy2(source, target)
        self.plan, self.inventory = self.noarch.inspect_recipe(
            self.root, PLAN, RESOURCES
        )

    def payload(self):
        entries = {
            name: b'# synthetic administrative payload\n'
            for name in self.inventory['required_paths']
        }
        entries[self.inventory['version_file']] = (
            '__version__ = "' + self.plan['version'] + '"\n'
        ).encode()
        entries['info/index.json'] = json.dumps(
            {
                'name': 'topomt',
                'version': self.plan['version'],
                'build': 'py_2',
                'build_number': 2,
                'subdir': 'noarch',
                'depends': self.inventory['expected_run'],
            }
        ).encode()
        entries['info/link.json'] = b'{"noarch": {"type": "python"}}'
        entries['site-packages/topomt-0.0.0.dist-info/METADATA'] = (
            b'Name: topomt\nVersion: 0.0.0\n'
        )
        return entries

    def validate(self, entries):
        archive_path = self.root / 'topomt-0.0.0-py_2.tar.bz2'
        with tarfile.open(archive_path, 'w:bz2') as archive:
            for name, content in entries.items():
                member = tarfile.TarInfo(name)
                member.size = len(content)
                archive.addfile(member, io.BytesIO(content))
        return self.noarch.inspect_artifact(archive_path, self.plan, self.inventory)

    def test_complete_current_core_data_and_private_resources_are_inventoried(self):
        expected = {
            'site-packages/' + str(path.relative_to(self.root))
            for package in ('topomt', 'molsysviewer_topomt')
            for path in (self.root / package).rglob('*')
            if path.is_file()
        }
        expected.add('site-packages/topomt/_version.py')
        self.assertEqual(set(self.inventory['required_paths']), expected)
        self.validate(self.payload())

    def test_missing_private_diagnostic_and_new_scientific_modules_fail_archive_validation(
        self,
    ):
        for name in (
            '_smonitor.py',
            'dfnd/centerline.py',
            'third_party/output.py',
        ):
            entries = self.payload()
            del entries['site-packages/topomt/' + name]
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.validate(entries)

    def test_missing_viewer_addon_fails_archive_validation(self):
        entries = self.payload()
        del entries['site-packages/molsysviewer_topomt/addon.py']
        with self.assertRaises(ValueError):
            self.validate(entries)

    def test_non_python_reference_assets_have_explicit_package_data(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        package_data = project['tool']['setuptools']['package-data']
        self.assertIn('README.md', package_data['topomt._private.citation'])
        self.assertIn('**', package_data['topomt.third_party.fpocket.testdata'])

    def test_missing_committed_runtime_dataset_fails_archive_validation(self):
        entries = self.payload()
        del entries['site-packages/topomt/data/README.md']
        with self.assertRaises(ValueError):
            self.validate(entries)

    def test_stale_embedded_version_is_rejected(self):
        entries = self.payload()
        entries[self.inventory['version_file']] = b'__version__ = "0.0.1"\n'
        with self.assertRaises(ValueError):
            self.validate(entries)

    def test_nglview_is_tooling_not_a_required_package_dependency(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())['project']
        self.assertNotIn('nglview', project['dependencies'])
        self.assertNotIn(
            'nglview', (ROOT / 'devtools/conda-build/meta.yaml').read_text()
        )
        production = yaml.safe_load(
            (ROOT / 'devtools/conda-envs/production_env.yaml').read_text()
        )
        self.assertNotIn('nglview', production['dependencies'])
        for name in (
            'development_env',
            'docs_env',
            'test_env',
            'test_env_py313',
            'test_env_py314',
        ):
            environment = yaml.safe_load(
                (ROOT / f'devtools/conda-envs/{name}.yaml').read_text()
            )
            self.assertIn('nglview', environment['dependencies'])

    def test_recipe_cannot_omit_a_required_runtime_provider(self):
        path = self.root / 'devtools/conda-build/meta.yaml'
        path.write_text(path.read_text().replace('    - depdigest>=0.12.0\n', ''))
        with self.assertRaises(ValueError):
            self.noarch.inspect_recipe(self.root, PLAN, RESOURCES)

    def test_package_discovery_excludes_test_and_checked_out_sdk_namespaces(self):
        project = tomllib.loads((ROOT / 'pyproject.toml').read_text())
        self.assertEqual(
            project['tool']['setuptools']['packages']['find']['include'],
            ['topomt*', 'molsysviewer_topomt*'],
        )
        from setuptools import find_namespace_packages

        temporary = self.root / '.molsyssuite'
        (temporary / 'devtools/scripts').mkdir(parents=True)
        (self.root / 'tests/extra').mkdir(parents=True)
        packages = find_namespace_packages(
            where=str(self.root), include=['topomt*', 'molsysviewer_topomt*']
        )
        self.assertTrue(packages)
        self.assertTrue(
            all(
                name == 'topomt'
                or name.startswith('topomt.')
                or name == 'molsysviewer_topomt'
                or name.startswith('molsysviewer_topomt.')
                for name in packages
            )
        )
        self.assertIn('topomt.dfnd', packages)
        self.assertIn('molsysviewer_topomt.render', packages)

    def test_all_routes_source_roles_and_contexts_use_the_shared_preflight(self):
        result = self.routes.audit(self.root)
        self.assertEqual(result['qualification'], 'declared-only')
        self.assertEqual(len(result['routes']), 19)
        self.assertEqual(len(result['contexts']), 7)
        self.assertEqual(len(result['source_routes']), 12)
        integrations = {
            s['name'] for s in result['source_routes'] if s['role'] == 'integration'
        }
        self.assertEqual(integrations, {'molsysviewer'})

    def test_missing_public_dependency_cannot_hide_behind_fixed_scientific_sources(
        self,
    ):
        path = self.root / 'devtools/conda-envs/production_env.yaml'
        path.write_text(path.read_text().replace('- smonitor\n', ''))
        with self.assertRaisesRegex(ValueError, 'production_env.yaml.*smonitor'):
            self.routes.audit(self.root)

    def test_changed_git_manifests_require_explicit_reinspection(self):
        for filename in (
            'controlled_suite_dependencies.txt',
            'controlled_suite_dependencies_py314.txt',
        ):
            path = self.root / 'devtools/requirements' / filename
            original = path.read_text()
            path.write_text(
                original.replace('4b5e5c5a46e3c8a4dc46461ce72937f9a7dfbdae', 'main')
            )
            with (
                self.subTest(filename=filename),
                self.assertRaisesRegex(ValueError, 'source input changed'),
            ):
                self.routes.audit(self.root)
            path.write_text(original)

    def test_unreviewed_inline_source_command_drift_is_rejected(self):
        path = self.root / '.github/workflows/CI.yaml'
        path.write_text(
            path.read_text().replace('3bcfaf4d50df6c84ebd14505790ed5221543e5de', 'main')
        )
        with self.assertRaisesRegex(ValueError, 'reviewed workflow changed'):
            self.routes.audit(self.root)

    def test_source_roles_and_duplicate_context_revisions_fail_closed(self):
        path = self.root / 'devtools/dependency_routes.toml'
        original = path.read_text()
        changes = (
            original.replace('role = "integration"', 'role = "required-runtime"', 1),
            original.replace(
                '"smonitor-base", "depdigest-base"',
                '"smonitor-base", "smonitor-3.14", "depdigest-base"',
                1,
            ),
        )
        for changed in changes:
            path.write_text(changed)
            with self.assertRaises(ValueError):
                self.routes.audit(self.root)
        path.write_text(original)

    def test_actual_editables_cannot_be_mistaken_for_selected_git_origins(self):
        class Editable:
            version = '1.0.0'

            def read_text(self, name):
                return json.dumps(
                    {
                        'url': 'file:///unrelated/local/source',
                        'dir_info': {'editable': True},
                    }
                )

        with self.assertRaisesRegex(ValueError, 'reviewed root Git'):
            self.routes.audit(
                self.root,
                context='ci-3.14',
                check_installed=True,
                python_version='3.14.7',
                distribution_for=lambda name: Editable(),
            )

    def test_eight_installed_cells_require_both_provenance_checks_and_science(self):
        descriptor = self.inventory['installed_gate']
        expected = self.matrix.expected_jobs(descriptor)
        self.assertEqual(len(expected), 9)
        self.assertEqual(
            descriptor['python_versions'], ['3.11', '3.12', '3.13', '3.14']
        )
        self.assertEqual(descriptor['platforms'], ['linux-64', 'osx-arm64'])
        self.assertEqual(
            descriptor['required_steps'],
            [
                'Install exact artifact',
                'Validate installed files',
                'Run installed tests',
                'Recheck dependency provenance after installed tests',
            ],
        )

    def test_candidate_requires_twelve_executed_jobs_and_installed_preflight_before_science(
        self,
    ):
        self.assertEqual(sum(len(jobs) for jobs in self.plan['gate_jobs'].values()), 12)
        workflow = yaml.safe_load((ROOT / '.github/workflows/CI.yaml').read_text())
        science = workflow['jobs']['test']['steps']
        names = [step.get('name') for step in science]
        self.assertLess(
            names.index('Check dependency routes and installed Git context'),
            names.index('Run tests'),
        )
        for job, steps in self.plan['gate_jobs']['.github/workflows/CI.yaml'].items():
            if job.startswith('Test on '):
                self.assertIn(
                    'Check dependency routes and installed Git context', steps
                )
                self.assertIn('Run tests', steps)
        self.assertNotIn(
            'devtools/tests',
            next(step['run'] for step in science if step.get('name') == 'Run tests'),
        )
        admin = {step.get('name') for step in workflow['jobs']['governance']['steps']}
        self.assertTrue(
            set(
                self.plan['gate_jobs']['.github/workflows/CI.yaml'][
                    'Reporting and CI governance on Linux Python 3.14'
                ]
            )
            <= admin
        )

    def test_qualification_commit_is_separate_from_original_producer_and_file_identity(
        self,
    ):
        text = (ROOT / '.github/workflows/promote_conda_package.yaml').read_text()
        self.assertIn('qualification_sha: ${{ inputs.qualification_sha }}', text)
        self.assertIn('candidate_sha: ${{ inputs.candidate_sha }}', text)
        self.assertIn('sha256: ${{ inputs.sha256 }}', text)
        self.assertFalse((ROOT / 'devtools/conda-build/release_plan.toml').exists())
        self.assertEqual(self.plan['version'], '0.0.0')


if __name__ == '__main__':
    unittest.main()
