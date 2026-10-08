"""Exercise actual profiling cleanup with inert science in isolated children."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CHILD = r"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import tracemalloc
import types
from zipfile import ZipFile

source, fixture, scenario = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
for name in ('numpy', 'topomt', 'topomt.dfnd', 'topomt.dfnd.data', 'topomt.dfnd.graph'):
    sys.modules[name] = types.ModuleType(name)
sys.modules['topomt'].pyunitwizard = types.SimpleNamespace(quantity=lambda *a: a[0])
system = types.SimpleNamespace(coords=[], radii=[])
sys.modules['topomt.dfnd'].synthetic = types.SimpleNamespace(
    tetrahedron=lambda **kw: system,
    hollow_sphere=lambda *a, **kw: system,
    helical_tube=lambda: system,
)
sys.modules['topomt.dfnd.data'].DFNDData = object
observed_pdb = []
def network(path):
    path = Path(path)
    assert path.read_bytes() == b'SYNTHETIC INPUT\n'
    observed_pdb.append(path)
    return object()
sys.modules['topomt.dfnd.graph'].DelaunayFlowNetwork = network
spec = importlib.util.spec_from_file_location('profile_tool', source)
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

if scenario.startswith('tracing_'):
    assert not tracemalloc.is_tracing()
    caller_owned = scenario == 'tracing_caller_preserved'
    if caller_owned:
        tracemalloc.start()
    def fail():
        raise RuntimeError('injected profiling failure')
    if scenario == 'tracing_measurement_failure':
        tool.tracemalloc.get_traced_memory = fail
        build = lambda: object()
    else:
        build = fail
    try:
        tool._measure('fixture', build)
    except RuntimeError as error:
        assert str(error) == 'injected profiling failure'
    else:
        raise AssertionError('failure not propagated')
    assert tracemalloc.is_tracing() is caller_owned, 'wrong tracing ownership after failure'
    tracemalloc.stop()
else:
    archive = fixture / 'input.zip'
    with ZipFile(archive, 'w') as output:
        if scenario != 'archive_failure':
            output.writestr('original.pdb', b'SYNTHETIC INPUT\n')
        else:
            output.writestr('not-a-pdb.txt', b'no PDB')
    tool.ZipFile = lambda *a: ZipFile(archive)
    sentinel = fixture / 'profile_memory_1crn.pdb'
    sentinel.write_bytes(b'CALLER OWNED\n')
    report = fixture / 'report.json'
    if scenario == 'output_failure':
        report.mkdir()
        (report / 'sentinel').write_bytes(b'CALLER REPORT DIRECTORY\n')
    else:
        report.write_bytes(b'CALLER PREVIOUS REPORT\n')
    created = []
    real_temporary = tempfile.TemporaryDirectory
    class ObservedTemporary(real_temporary):
        def __init__(self, *a, **kw):
            super().__init__(*a, **kw)
            created.append(Path(self.name))
        def cleanup(self):
            super().cleanup()
            assert not Path(self.name).exists()
            if scenario == 'cleanup_failure':
                raise OSError('injected cleanup error after real disposal')
    tool.TemporaryDirectory = ObservedTemporary
    def measure(name, build):
        if name == '1crn':
            build()
            if scenario == 'measurement_failure':
                raise RuntimeError('injected measurement failure')
        return dict(name=name, atoms=0, input_array_bytes=0,
                    network_and_mesh_unique_array_bytes=0,
                    second_query_added_traced_bytes=0)
    tool._measure = measure
    sys.argv = [str(source), '--output', str(report)]
    expected = {
        'measurement_failure': RuntimeError,
        'archive_failure': (IndexError, ValueError),
        'output_failure': IsADirectoryError,
        'cleanup_failure': OSError,
    }.get(scenario)
    caught = None
    try:
        tool.main()
    except Exception as error:
        caught = error
    if expected:
        assert isinstance(caught, expected), repr(caught)
    else:
        assert caught is None, repr(caught)
    assert sentinel.read_bytes() == b'CALLER OWNED\n', 'caller file overwritten'
    assert len(created) == 1 and not created[0].exists(), 'owned scratch not removed'
    assert all(not p.exists() and p.is_relative_to(created[0]) for p in observed_pdb)
    if scenario == 'success':
        assert [case['name'] for case in json.loads(report.read_text())['cases']] == [
            'tetrahedron', 'hollow_sphere', 'helical_tube', '1crn'
        ]
    elif scenario == 'output_failure':
        assert (report / 'sentinel').read_bytes() == b'CALLER REPORT DIRECTORY\n'
    else:
        assert report.read_bytes() == b'CALLER PREVIOUS REPORT\n'
"""


class TestProfileMemoryResources(unittest.TestCase):
    def run_case(self, scenario):
        with tempfile.TemporaryDirectory(prefix='topomt-profile-test-') as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    '-S',
                    '-c',
                    CHILD,
                    str(ROOT / 'devtools/dfnd/profile_memory.py'),
                    directory,
                    scenario,
                ],
                cwd=directory,
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(Path(directory).exists())

    def test_success_removes_scratch_and_preserves_caller_pdb(self):
        self.run_case('success')

    def test_measurement_failure_removes_scratch_and_preserves_caller_evidence(self):
        self.run_case('measurement_failure')

    def test_archive_failure_removes_scratch(self):
        self.run_case('archive_failure')

    def test_output_failure_keeps_caller_directory_and_removes_scratch(self):
        self.run_case('output_failure')

    def test_cleanup_failure_is_visible_after_real_disposal(self):
        self.run_case('cleanup_failure')

    def test_failed_build_releases_owned_tracing(self):
        self.run_case('tracing_build_failure')

    def test_failed_measurement_releases_owned_tracing(self):
        self.run_case('tracing_measurement_failure')

    def test_failed_build_preserves_caller_tracing(self):
        self.run_case('tracing_caller_preserved')
