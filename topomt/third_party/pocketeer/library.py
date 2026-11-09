import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from depdigest import dep_digest

from topomt import Topography
from topomt import pyunitwizard as puw
from topomt._ackredit import attributed, scientific_call
from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.pocketeer_arguments import OPTIONS, RADIUS_PIPELINES
from topomt.provider_output import ProviderRun
from topomt.third_party._common import (
    import_upstream_module,
    installed_provider_version,
    prepare_wrapper_input_pdb,
    validate_single_frame_pdb,
)
from topomt.third_party.pdb_context import (
    reference_chemical_context,
    source_input_context,
)

from .parser import _output_protocol
from .records import pockets_to_topography


def _json_ready(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value


def _normalize_upstream_pocketeer_kwargs(kwargs):
    normalized = dict(kwargs)

    distance_keys = ('r_min', 'r_max', 'polar_probe_radius', 'merge_distance')
    for key in distance_keys:
        value = normalized.get(key, None)
        if value is not None and puw.is_quantity(value):
            normalized[key] = float(puw.get_value(value, to_unit='angstroms'))

    sasa_threshold = normalized.get('sasa_threshold', None)
    if sasa_threshold is not None and puw.is_quantity(sasa_threshold):
        normalized['sasa_threshold'] = float(
            puw.get_value(sasa_threshold, to_unit='angstroms**2')
        )

    min_spheres = normalized.get('min_spheres', None)
    if min_spheres is not None:
        normalized['min_spheres'] = int(min_spheres)

    return normalized


@attributed('pocketeer', route='original')
@arg_digest(**OPTIONS, map=RADIUS_PIPELINES)
@dep_digest('pocketeer', when={'upstream_root': None})
@dep_digest('biotite')
def get_topography(
    molecular_system: Any,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    chemical_state: str | int = 'reference',
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    skip_digestion: bool = False,
    **kwargs: Any,
) -> Topography:
    """Run the original Pocketeer library on one submitted coordinate frame.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Source atom inventory and coordinates.
    selection : str or sequence of int, default='all'
        Nonempty source selection. Submitted rows use source atom order.
    structure_indices : int or sequence of int, default=0
        One source frame. None or 'all' must resolve to one exported frame.
    chemical_state : str or int, default='reference'
        Unambiguous reference state or its index. MolSysMT owns the state and
        PDB export. No protonation, charge or bond preparation is performed.
    syntax : str, default='MolSysMT'
        Source selection syntax.
    upstream_root : str or Path, optional
        Source-import fallback when the original package is unavailable.
    skip_digestion : bool, default=False
        Internal bypass for already admitted arguments.
    **kwargs
        Original r_min, r_max, polar_probe_radius, sasa_threshold,
        merge_distance, min_spheres and the three ignore_* flags.
        Bare distances/areas use angstroms/angstroms squared; compatible
        scalar quantities are converted to those protocol units.
        Original defaults remain owned by Pocketeer for omitted options.

    Returns
    -------
    Topography
        Original pockets, source mappings and captured execution evidence.

    Raises
    ------
    ArgumentError
        If options, finite scalars, radius range or index axes are invalid.
    ValueError
        If the exported frame or atom mapping is incompatible.
    LibraryNotFoundError
        If an original-route dependency is unavailable.

    Examples
    --------
    >>> result = get_topography('protein.pdb', min_spheres=40)  # doctest: +SKIP
    """

    chemical_context = reference_chemical_context(
        molecular_system, chemical_state, provider='Pocketeer'
    )
    with tempfile.TemporaryDirectory(prefix='topomt_pocketeer_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)

        input_pdb, selected_atom_indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )
        validate_single_frame_pdb(input_pdb, provider='Pocketeer')
        source_context = source_input_context(molecular_system, structure_indices)

        upstream = import_upstream_module('pocketeer', upstream_root=upstream_root)
        atomarray = scientific_call('biotite', upstream.load_structure, str(input_pdb))
        if len(atomarray) != len(selected_atom_indices):
            raise ValueError(
                'Pocketeer input atom count differs from the selected molecular system; '
                'atom identities cannot be mapped safely.'
            )
        normalized_kwargs = _normalize_upstream_pocketeer_kwargs(kwargs)
        pockets = upstream.find_pockets(atomarray, **normalized_kwargs)

        import biotite.structure as struc

        filtered_atom_indices: np.ndarray = np.arange(len(atomarray), dtype=int)
        if normalized_kwargs.get('ignore_hydrogens', True):
            filtered_atom_indices = filtered_atom_indices[
                atomarray.element[filtered_atom_indices] != 'H'
            ]
        if normalized_kwargs.get('ignore_water', True):
            filtered_atom_indices = filtered_atom_indices[
                ~struc.filter_solvent(atomarray[filtered_atom_indices])
            ]
        if normalized_kwargs.get('ignore_hetero', True):
            filtered_atom_indices = filtered_atom_indices[
                ~atomarray.hetero[filtered_atom_indices]
            ]

        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        (output_dir / 'topomt_source_context.json').write_text(
            json.dumps(source_context, sort_keys=True, allow_nan=False)
        )
        upstream.write_pockets_json(str(output_dir / 'pocketeer_pockets.json'), pockets)
        (output_dir / 'topomt_masks.json').write_text(
            json.dumps(
                {
                    'schema_version': 1,
                    'pockets': [
                        {
                            'pocket_id': pocket.pocket_id,
                            'mask': np.asarray(pocket.mask, dtype=bool).tolist(),
                        }
                        for pocket in pockets
                    ],
                },
                sort_keys=True,
            )
        )
        api_file = Path(upstream.find_pockets.__code__.co_filename)
        with api_file.open('rb') as file_handle:
            api_sha256 = hashlib.file_digest(file_handle, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'pocketeer',
            'library',
            input_pdb,
            output_dir,
            metadata={
                'version': upstream.__version__,
                'distribution_version': installed_provider_version(upstream),
                'api_sha256': api_sha256,
                'parameters': _json_ready(normalized_kwargs),
                'output_protocol': _output_protocol(),
                'selection': _json_ready(selection),
                'structure_indices': _json_ready(structure_indices),
                'chemical_state_context': chemical_context,
                'syntax': syntax,
                'selected_atom_indices': selected_atom_indices.tolist(),
                'filtered_input_atom_indices': filtered_atom_indices.tolist(),
            },
        )

        return pockets_to_topography(
            molecular_system,
            pockets,
            selected_atom_indices,
            filtered_atom_indices,
            run,
            selection=selection,
            structure_indices=structure_indices,
        )
