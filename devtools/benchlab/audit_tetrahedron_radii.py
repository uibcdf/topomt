"""Audit one frozen case through original input readers, with no kernel changes.

Review resources before invoking this case-specific script. Use one OS CPU and
the protocol's process memory limit. Existing output directories are refused.
The resulting capsules are input-reader evidence, not topography provider runs.
"""

import argparse
import csv
import hashlib
import io
import json
import os
import subprocess
import tempfile
from pathlib import Path

import molsysmt as msm
import numpy as np
from pyunitwizard import QuantityRecord

from topomt import pyunitwizard as puw
from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import pdb_points

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / 'docs/content/benchlab/synthetic/regular_tetrahedron'
AUDIT = CASE / 'artifacts/radius_audit_v1'
HEADER = 'serial\tname\telement\tradius_angstrom\tx_angstrom\ty_angstrom\tz_angstrom'


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _record(data: np.ndarray | float, unit: str, field: str) -> dict:
    return QuantityRecord.from_quantity(puw.quantity(data, unit), field=field).to_dict()


def _launch(command: list[str], directory: Path, name: str) -> int:
    environment = dict(os.environ)
    for key in (
        'OMP_NUM_THREADS',
        'OPENBLAS_NUM_THREADS',
        'MKL_NUM_THREADS',
        'NUMEXPR_NUM_THREADS',
        'OMP_THREAD_LIMIT',
    ):
        environment[key] = '1'
    with (
        (directory / f'{name}.txt').open('wb') as stdout,
        (directory / f'{name}.stderr.txt').open('wb') as stderr,
    ):
        result = subprocess.run(
            command,
            cwd=directory,
            env=environment,
            stdout=stdout,
            stderr=stderr,
            timeout=20,
            check=False,
        )
    return result.returncode


def _read_original(method: str, output: Path) -> tuple[np.ndarray, np.ndarray]:
    if method == 'ghecom':
        text = (output / 'assigned.pdb').read_text()
        if 'Occupancy [55-60] : Radius of the atom' not in text:
            raise ValueError('Original GHECOM radius annotation is absent')
        pdb_rows = [line for line in text.splitlines() if line.startswith('ATOM  ')]
        radii = np.array([float(line[54:60]) for line in pdb_rows])
        # Read provider-specific geometric output, not a general molecular file.
        # GHECOM emits nonnumeric REMARK metadata (molsysmt#654).
        xyz = np.array([point for _, _, point in pdb_points(text.encode())])
    else:
        text = (output / 'stdout.txt').read_text()
        start = text.index(HEADER)
        table_rows = list(csv.DictReader(io.StringIO(text[start:]), delimiter='\t'))
        if any(row['element'] != 'C' for row in table_rows):
            raise ValueError('Original CAVER reader did not identify carbon')
        radii = np.array([float(row['radius_angstrom']) for row in table_rows])
        xyz = np.array(
            [[float(row[axis + '_angstrom']) for axis in 'xyz'] for row in table_rows]
        )
    if (
        radii.shape != (4,)
        or xyz.shape != (4, 3)
        or not np.isfinite(radii).all()
        or np.any(radii <= 0)
    ):
        raise ValueError('Original audit must contain four finite positive radii')
    return radii, xyz


def main() -> int:
    """Execute the declared paired reader audit into a new directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tools', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    protocol = json.loads((AUDIT / 'protocol.json').read_text())
    for relative, expected in protocol['preserved_files'].items():
        if _sha(CASE / relative) != expected:
            raise ValueError(f'Previous evidence changed: {relative}')
    locations = json.loads(args.tools.read_text())
    if set(locations) != {'ghecom_cmd', 'caver_home', 'java_cmd', 'javac_cmd'}:
        raise ValueError(
            'Only the four required executable/distribution location keys are accepted'
        )
    paths = {key: Path(path).resolve() for key, path in locations.items()}
    jar = paths['caver_home'] / 'caver.jar'
    table = paths['caver_home'] / 'bin/atom_radii.csv'
    helper = ROOT / protocol['caver']['helper_file']
    for path, expected in [
        (jar, protocol['caver']['jar_sha256']),
        (table, protocol['caver']['table_sha256']),
        (helper, protocol['caver']['helper_sha256']),
        (paths['ghecom_cmd'], protocol['ghecom']['executable_sha256']),
    ]:
        if _sha(path) != expected:
            raise ValueError(f'Original engine or helper identity changed: {path}')
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    report = {
        'schema': 'topomt.benchlab.effective-radius-observations/1',
        'case_id': protocol['case_id'],
        'owning_issue': protocol['owning_issue'],
        'scope': 'Original input-radius assignment; no new pocket/channel interpretation',
        'protocol_sha256': _sha(AUDIT / 'protocol.json'),
        'producer_commit': '6808516',
        'audit_driver_sha256': _sha(Path(__file__)),
        'producer_state': 'Declared protocol/helper commit plus this retained audit driver; pre-existing version-file edit preserved',
        'observations': [],
    }
    with tempfile.TemporaryDirectory(prefix='topomt_radius_reader_') as temporary:
        build = Path(temporary)
        command = [
            str(paths['javac_cmd']),
            '-J-Xmx128m',
            '-J-XX:ActiveProcessorCount=1',
            '-classpath',
            str(jar),
            '-d',
            str(build),
            str(helper),
        ]
        code = _launch(command, args.output, 'compile')
        if code != 0:
            raise ValueError(
                'Java audit caller compilation failed; inspect retained compile logs'
            )
        report['compile'] = {
            'command': command,
            'returncode': code,
            'compiler_sha256': _sha(paths['javac_cmd']),
        }
        for row in protocol['runs']:
            directory = args.output / row['id']
            directory.mkdir()
            output = directory / 'results'
            output.mkdir()
            source = (
                CASE / protocol['source_file']
                if row['input'] == 'original'
                else AUDIT / protocol['aligned_file']
            )
            expected_input = (
                protocol['source_sha256']
                if row['input'] == 'original'
                else protocol['aligned_sha256']
            )
            if _sha(source) != expected_input:
                raise ValueError('Declared input changed')
            submitted = directory / 'input.pdb'
            submitted.write_bytes(source.read_bytes())
            if row['method'] == 'ghecom':
                command = [
                    str(paths['ghecom_cmd']),
                    'P',
                    '-ipdb',
                    str(submitted),
                    '-opdbin',
                    str(output / 'assigned.pdb'),
                    '-opocpdb',
                    str(output / 'pockets.pdb'),
                ]
                additional = {}
            else:
                command = [
                    str(paths['java_cmd']),
                    '-Xmx128m',
                    '-XX:ActiveProcessorCount=1',
                    '-Djava.awt.headless=true',
                    '-classpath',
                    os.pathsep.join([str(build), str(jar)]),
                    'CaverRadiusAudit',
                    str(table),
                    str(submitted),
                ]
                additional = {'atom_radii.csv': table, 'CaverRadiusAudit.java': helper}
            code = _launch(command, output, 'stdout')
            expected_code = 1 if row['method'] == 'ghecom' else 0
            if code != expected_code:
                raise ValueError(
                    f'Original reader failed: {row["id"]}; inspect retained files'
                )
            radii, xyz = _read_original(row['method'], output)
            reference = np.asarray(
                puw.get_value(
                    msm.get(str(submitted), coordinates=True), to_unit='angstroms'
                )
            ).reshape(-1, 3)
            np.testing.assert_allclose(xyz, reference, rtol=0, atol=1e-12)
            metadata = {
                'operation': 'input_radius_audit',
                'execution_status': 'completed',
                'version': protocol[row['method']]['version'],
                'command': command,
                'returncode': code,
                'source_input_sha256': _sha(submitted),
                'engine_sha256': _sha(
                    jar if row['method'] == 'caver' else paths['ghecom_cmd']
                ),
                'workers': 1,
                'interpretation': report['scope'],
            }
            run = ProviderRun.capture(
                row['method'],
                'cli',
                submitted,
                output,
                metadata=metadata,
                additional_inputs=additional,
            )
            bundle = directory / 'reader.zip'
            run.save(bundle)
            edge = float(np.linalg.norm(xyz[0] - xyz[1]))
            if not np.allclose(radii, radii[0], rtol=0, atol=1e-12):
                raise ValueError(
                    'Equal-radius analytic implication requires equal assigned radii'
                )
            entry = {
                **row,
                'status': 'completed',
                'input_sha256': _sha(submitted),
                'radii': _record(radii, 'angstroms', 'atomic_radii'),
                'coordinates': _record(xyz, 'angstroms', 'coordinates'),
                'bundle': {
                    'file': str(bundle.relative_to(AUDIT))
                    if bundle.is_relative_to(AUDIT)
                    else str(bundle.relative_to(args.output)),
                    'sha256': _sha(bundle),
                    'run_id': run.run_id,
                },
                'ball_model_implication': {
                    'meaning': 'Independent equal-ball geometry, not an original detector prediction',
                    'face_clearance': _record(
                        edge / np.sqrt(3) - radii[0], 'angstroms', 'face_clearance'
                    ),
                    'residence_clearance': _record(
                        edge * np.sqrt(6) / 4 - radii[0],
                        'angstroms',
                        'residence_clearance',
                    ),
                },
            }
            report['observations'].append(entry)
            (args.output / 'report.json').write_text(
                json.dumps(report, indent=2, allow_nan=False) + '\n'
            )
            print(row['id'], 'radii (angstroms):', radii.tolist(), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
