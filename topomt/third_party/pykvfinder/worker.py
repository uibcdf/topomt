"""Isolated original pyKVFinder worker; no execution on import."""

import hashlib
import json
import platform
import shutil
import sys
from pathlib import Path


def _identity(path: Path) -> dict:
    with path.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    return {'path': str(path.resolve()), 'sha256': digest, 'size': path.stat().st_size}


def main(request_file: str) -> None:
    """Use only public upstream operations and explicit worker counts."""
    request = json.loads(Path(request_file).read_text())
    root = request['upstream_root']
    if root is not None:
        sys.path.insert(0, root)
    import pyKVFinder

    module_path = Path(pyKVFinder.__file__).resolve()
    if root is not None and not module_path.is_relative_to(Path(root).resolve()):
        raise ValueError('Requested pyKVFinder source root was shadowed')
    if pyKVFinder.__version__ not in {'0.9.6', '0.9.6+uibcdf.1'}:
        raise ValueError('This adapter requires the reviewed pyKVFinder 0.9.6 protocol')
    output = Path(request['output'])
    dictionary = output.parent / 'vdw.dat'
    shutil.copyfile(module_path.parent / 'data/vdw.dat', dictionary)
    parameters = request['parameters']
    result = pyKVFinder.run_workflow(
        request['input'], vdw=str(dictionary), nthreads=request['workers'], **parameters
    )
    if result is None:
        pyKVFinder.write_results(
            str(output / 'results.toml'),
            request['input'],
            None,
            str(output / 'cavities.pdb'),
            volume={},
            area={},
            step=parameters['step'],
        )
        (output / 'cavities.pdb').write_text(
            'REMARK Original pyKVFinder returned no cavities\n'
        )
    else:
        result.export(str(output / 'cavities.pdb'), nthreads=request['workers'])
        result.write(str(output / 'results.toml'), str(output / 'cavities.pdb'))
    import numpy
    import pyKVFinder._pyKVFinder as extension

    receipt = {
        'version': pyKVFinder.__version__,
        'python_version': platform.python_version(),
        'numpy_version': numpy.__version__,
        'module': _identity(module_path),
        'native_extension': _identity(Path(extension.__file__)),
        'interpreter': _identity(Path(sys.executable)),
        'dictionary': _identity(dictionary),
        'original_empty': result is None,
    }
    (output / 'engine_identity.json').write_text(json.dumps(receipt, allow_nan=False))


if __name__ == '__main__':
    main(sys.argv[1])
