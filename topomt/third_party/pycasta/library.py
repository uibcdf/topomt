import hashlib
import json
import subprocess
import sys
import tempfile
from importlib.util import find_spec
from pathlib import Path
from typing import Any

import numpy as np
from depdigest import dep_digest
from scipy.spatial import Delaunay

from topomt import Topography
from topomt._ackredit import attributed, scientific_call
from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.pycasta_arguments import OPTIONS
from topomt._private.smonitor import LibraryNotFoundError, signal
from topomt.provider_output import ProviderRun
from topomt.third_party._common import (
    prepare_wrapper_input_pdb,
    validate_single_frame_pdb,
)
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
    validate_submitted_pdb,
)

from .parser import output_protocol, parse_result
from .parser import protein_atom_indices_from_pdb as _protein_atom_indices_from_pdb
from .records import result_to_topography

_PYCASTA_WORKER = """
import json
import hashlib
from importlib.metadata import PackageNotFoundError, distribution
from pathlib import Path
import sys

sys.path.insert(0, sys.argv[1])
import config
import run_analysis

result = run_analysis.process_pdb(sys.argv[2])
Path(sys.argv[3]).write_text(json.dumps(result, sort_keys=True, allow_nan=True))
try:
    installed_distribution = distribution('pycasta')
    installed_entry = Path(installed_distribution.locate_file('pycasta/run_analysis.py')).resolve()
    distribution_version = (
        installed_distribution.version
        if Path(run_analysis.__file__).resolve() == installed_entry else None
    )
    distribution_identity = {
        'name': installed_distribution.metadata['Name'],
        'version': installed_distribution.version,
        'root': str(installed_distribution.locate_file('')),
        'selected_run_analysis_matches': distribution_version is not None,
    }
except PackageNotFoundError:
    distribution_version = None
    distribution_identity = None
Path(sys.argv[4]).write_text(json.dumps({
    'use_cgal': bool(config.USE_CGAL),
    'filter_alpha_by_sasa': bool(config.FILTER_ALPHA_BY_SASA),
    'save_alpha': bool(config.SAVE_ALPHA),
    'validation_method': config.VALIDATION_METHOD,
    'use_existing_results': bool(config.USE_EXISTING_RESULTS),
    'manual_alpha': config.MANUAL_ALPHA,
    'version_tag': run_analysis.VERSION_TAG,
    'distribution_version': distribution_version,
}, sort_keys=True))
root = Path(sys.argv[1]).resolve()
output = Path(sys.argv[3]).parent
modules, sources = {}, {}
for name, module in sorted(sys.modules.copy().items()):
    if module is None:
        continue
    filename = getattr(module, '__file__', None)
    spec = getattr(module, '__spec__', None)
    modules[name] = {
        'file': str(filename) if filename is not None else None,
        'spec_origin': str(spec.origin) if spec is not None else None,
    }
    if filename is None:
        continue
    path = Path(filename).resolve()
    if path.is_file() and path.is_relative_to(root):
        relative = path.relative_to(root)
        target = output / 'topomt_worker_sources' / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        data = path.read_bytes()
        target.write_bytes(data)
        sources['output/topomt_worker_sources/' + relative.as_posix()] = {
            'path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
        }
(output / 'topomt_worker_origins.json').write_text(json.dumps({
    'schema_version': 1, 'source_root': str(root),
    'executable': sys.executable, 'python': sys.version,
    'distribution_version': distribution_version,
    'observed_distribution': distribution_identity,
    'sys_path': list(sys.path), 'modules': modules, 'source_files': sources,
}, sort_keys=True, allow_nan=False))
"""


def _get_source_root(upstream_root: str | Path | None) -> Path:
    """Locate scripts without importing pyCASTA's global config in this process."""
    candidates: tuple[Path, ...]
    if upstream_root is not None:
        root = Path(upstream_root).expanduser().resolve()
        if root.is_file():
            root = root.parent
        candidates = (root, root / 'pycasta', root / 'src' / 'pycasta')
    else:
        spec = find_spec('pycasta')
        if spec is None:
            raise LibraryNotFoundError(library='pycasta')
        candidates = tuple(Path(path) for path in spec.submodule_search_locations or ())
    for candidate in candidates:
        if (candidate / 'run_analysis.py').is_file():
            return candidate
    raise ValueError('pyCASTA installation or upstream_root has no run_analysis.py')


def _json_safe(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return _json_safe(value.tolist())
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return {'nonfinite': str(value)}
    return value


@attributed('pycasta', route='original')
@signal(tags=['provider', 'pycasta', 'library'])
@arg_digest(**OPTIONS)
@dep_digest('pycasta', when={'upstream_root': None})
def get_topography(
    molecular_system: Any,
    *,
    selection: Any = 'all',
    structure_indices: int | list[int] = 0,
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    chemical_state: str | int = 'reference',
    skip_digestion: bool = False,
) -> Topography:
    """Run original pyCASTA with an exact source-bound recoverable snapshot.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source molecular system; no chemical preparation is performed.
    selection : str or sequence of int, default='all'
        Atoms submitted in source order. Original pyCASTA separates ATOM rows.
    structure_indices : int or sequence of int, default=0
        Exactly one frame; no alignment is performed.
    syntax : str, default='MolSysMT'
        Molecular selection syntax.
    upstream_root : str or pathlib.Path, optional
        Explicit original source directory, otherwise the installed package.
    chemical_state : str or int, default='reference'
        Existing, unambiguous reference state or its index.
    skip_digestion : bool, default=False
        Internal bypass for arguments already admitted by this adapter.

    Returns
    -------
    Topography
        Original pocket fields, source mappings and retained output bytes.

    Raises
    ------
    ArgumentError
        If argument types, frame, paths or option names are invalid.
    ValueError
        If source/reference, submitted rows, original arrays or maps disagree.
    LibraryNotFoundError
        If the selected original installation is unavailable.

    Examples
    --------
    >>> result = get_topography('source.h5msm')  # doctest: +SKIP
    """
    chemical_context = reference_chemical_context(
        molecular_system, chemical_state, provider='pyCASTA'
    )
    source_context = source_input_context(molecular_system, structure_indices)
    with tempfile.TemporaryDirectory(prefix='topomt_pycasta_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, selected = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )
        validate_single_frame_pdb(input_pdb, provider='pyCASTA')
        validate_submitted_pdb(
            molecular_system,
            input_pdb,
            selected,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )
        source_root = _get_source_root(upstream_root)
        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        result_path = output_dir / 'topomt_returned_result.json'
        configuration_path = output_dir / 'topomt_execution_configuration.json'
        execution = subprocess.run(
            [
                sys.executable,
                '-I',
                '-B',
                '-c',
                _PYCASTA_WORKER,
                str(source_root),
                str(input_pdb),
                str(result_path),
                str(configuration_path),
            ],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            check=True,
        )
        (output_dir / 'topomt_stdout.txt').write_text(execution.stdout)
        (output_dir / 'topomt_stderr.txt').write_text(execution.stderr)
        result = _json_safe(json.loads(result_path.read_text()))
        result_path.write_text(json.dumps(result, sort_keys=True, allow_nan=False))
        configuration = json.loads(configuration_path.read_text())
        version_tag = configuration['version_tag']
        if (
            not isinstance(version_tag, str)
            or not version_tag
            or version_tag in ('.', '..')
            or '/' in version_tag
            or '\\' in version_tag
        ):
            raise ValueError('Invalid pyCASTA original version-tag directory.')
        protein_coords = np.asarray(result['protein_coords'], dtype=float)
        if (
            protein_coords.ndim != 2
            or protein_coords.shape[1] != 3
            or not np.isfinite(protein_coords).all()
        ):
            raise ValueError('Invalid pyCASTA original protein coordinate array.')
        protein_indices = _protein_atom_indices_from_pdb(
            input_pdb, selected, protein_coords
        )
        # The existing live-route proof is retained. Recovery consumes this exact
        # verified map and never repeats SciPy's tetrahedralization.
        simplices = scientific_call('qhull', Delaunay, protein_coords).simplices
        index_path = output_dir / 'topomt_tetrahedron_indices.json'
        index_path.write_text(
            json.dumps(
                {'schema_version': 1, 'simplices': simplices.tolist()}, sort_keys=True
            )
        )
        alpha_file = output_dir / version_tag / f'{input_pdb.stem}.alpha.npz'
        if not alpha_file.is_file():
            raise ValueError(
                'pyCASTA did not export the original alpha array; atom mapping cannot be verified.'
            )
        protocol = output_protocol()
        state = parse_result(
            result_path.read_bytes(),
            alpha_file.read_bytes(),
            index_path.read_bytes(),
            protocol,
        )
        (output_dir / 'topomt_source_context.json').write_text(
            json.dumps(source_context, sort_keys=True, allow_nan=False)
        )
        with (source_root / 'run_analysis.py').open('rb') as stream:
            source_sha256 = hashlib.file_digest(stream, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'pycasta',
            'library',
            input_pdb,
            output_dir,
            metadata={
                'source_sha256': source_sha256,
                'version_tag': version_tag,
                'configuration': configuration,
                'distribution_version': configuration.get('distribution_version'),
                'output_protocol': protocol,
                'selection': _json_safe(selection),
                'structure_indices': _json_safe(structure_indices),
                'syntax': syntax,
                'chemical_state_context': chemical_context,
                'source_context_artifact': 'output/topomt_source_context.json',
                'selected_atom_indices': selected.tolist(),
                'protein_atom_indices': protein_indices.tolist(),
                'alpha_artifact': 'output/'
                + alpha_file.relative_to(output_dir).as_posix(),
                'worker_origin_artifact': 'output/topomt_worker_origins.json',
            },
        )
        return result_to_topography(
            molecular_system,
            state,
            protein_indices,
            run,
            selection=selection,
            structure_indices=structure_indices,
        )
