"""Isolated adapter around public POVME APIs; no scientific algorithm copy."""

import hashlib
import io
import json
import platform
import sys
from importlib.metadata import version
from pathlib import Path


def identity(path: Path) -> dict:
    return {
        'path': str(path.resolve()),
        'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'size': path.stat().st_size,
    }


def main(request_file: str) -> int:
    request = json.loads(Path(request_file).read_text())
    output = Path(request['output'])
    for name in ['pymolecule_root', 'upstream_root']:
        if request[name] is not None:
            sys.path.insert(0, request[name])
    try:
        import loguru
        import numpy as np
        import povme
        import pydantic
        import pymolecule
        import scipy
        from povme.config import PocketVolumeConfig
        from povme.pocket.volume import PocketVolume
    except ModuleNotFoundError as cause:
        if cause.name not in {
            'povme',
            'pymolecule',
            'pydantic',
            'loguru',
            'numpy',
            'scipy',
            'yaml',
        }:
            raise
        (output / 'missing_dependency.json').write_text(
            json.dumps({'module': cause.name})
        )
        return 66
    for module, key in [(povme, 'upstream_root'), (pymolecule, 'pymolecule_root')]:
        if request[key] is not None and not Path(
            module.__file__
        ).resolve().is_relative_to(Path(request[key]).resolve()):
            raise ValueError('Requested original Python source was shadowed')
    if povme.__version__ not in {'2.2.2', '2.2.2+uibcdf.1'}:
        raise ValueError(
            'Unsupported POVME protocol; the modern 2.2.2 source is required'
        )
    config_data = json.loads(Path(request['configuration']).read_text())
    config = PocketVolumeConfig(**config_data)
    if config.use_ray or config.n_cores != 1:
        raise ValueError('Only serial original POVME execution is admitted')
    modules = {'povme': povme, 'pymolecule': pymolecule}
    source_files = {
        name + '/' + str(path.relative_to(Path(module.__file__).parent)): identity(path)
        for name, module in modules.items()
        for path in sorted(Path(module.__file__).parent.rglob('*.py'))
    }
    runtime = {
        'version': povme.__version__,
        'software_variant': 'uibcdf_compatibility_fork'
        if '+uibcdf.' in povme.__version__
        else 'upstream',
        'python_version': platform.python_version(),
        'numpy_version': np.__version__,
        'scipy_version': scipy.__version__,
        'pydantic_version': pydantic.__version__,
        'loguru_version': version('loguru'),
        'package_source': source_files,
        'interpreter': identity(Path(sys.executable)),
        'pymolecule_version': pymolecule.__version__,
    }
    (output / 'engine_identity.json').write_text(
        json.dumps(
            {'schema': 'topomt.povme-worker@1', 'status': 'started', **runtime},
            allow_nan=False,
        )
    )
    # The original worker catches some frame errors and returns zero/omitted
    # entries. Preserve diagnostics and reject error-level fallbacks explicitly.
    errors = []
    povme.enable_logging(30)
    sink = loguru.logger.add(lambda message: errors.append(str(message)), level='ERROR')
    pdb = pymolecule.Molecule()
    pdb.io.load_pdb_into_using_file_object(
        io.StringIO(Path(request['input']).read_text()), False, False, False
    )
    submitted_count = sum(
        line.startswith(('ATOM  ', 'HETATM'))
        for line in Path(request['input']).read_text().splitlines()
    )
    if len(pdb.information.atom_information) != submitted_count:
        raise ValueError('Original pymolecule did not retain every submitted atom')
    result = PocketVolume(config).run(request['input'], str(output) + '/', chunk_size=1)
    loguru.logger.remove(sink)
    (output / 'diagnostics.json').write_text(json.dumps({'errors': errors}))
    if errors or set(result) != {1} or not np.isfinite(result[1]) or result[1] < 0:
        raise ValueError('Original POVME frame failed or returned incomplete results')
    initial = np.load(output / 'point_field.pdb.npy', allow_pickle=False)
    if initial.ndim != 2 or initial.shape[1] != 3 or not np.isfinite(initial).all():
        raise ValueError('Original POVME input point field is malformed')
    receipt = {
        'schema': 'topomt.povme-worker@1',
        'status': 'completed',
        **runtime,
        'configuration': config.model_dump(),
        'initial_point_count': len(initial),
        'point_support_status': 'reported'
        if (output / 'frame_1.pdb').is_file()
        else 'not_written_by_original',
        'protocol_units': {'length': 'angstroms', 'volume': 'angstroms**3'},
        'original_result': {'1': float(result[1])},
    }
    (output / 'engine_identity.json').write_text(json.dumps(receipt, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
