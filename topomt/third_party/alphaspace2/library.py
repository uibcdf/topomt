import hashlib
import inspect
import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from depdigest import dep_digest

from topomt import Topography
from topomt._ackredit import attributed, scientific_call
from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.alphaspace2_arguments import (
    LIBRARY_PIPELINES,
    OPTIONS,
)
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
    validate_submitted_pdb,
)

from .output import _output_protocol
from .records import snapshot_to_topography


def _snapshot_json_value(value):
    if isinstance(value, np.ndarray):
        return _snapshot_json_value(value.tolist())
    if isinstance(value, np.generic):
        return _snapshot_json_value(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return {'nonfinite': str(value)}
    if isinstance(value, (list, tuple)):
        return [_snapshot_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _snapshot_json_value(item) for key, item in value.items()}
    return value


def _patch_alphaspace2_mdtraj_sasa(upstream):
    import inspect

    from mdtraj.geometry import _geometry

    try:
        sasa_signature = inspect.signature(_geometry._sasa)
    except (TypeError, ValueError):
        return

    if len(sasa_signature.parameters) != 6:
        return

    functions_module = import_upstream_module(
        'alphaspace2.functions',
        upstream_root=None,
    )

    def get_sasa_compat(protein_snapshot, cover_atom_coords=None):
        probe_radius = 0.14
        n_sphere_points = 960

        if cover_atom_coords is None:
            xyz = np.array(protein_snapshot.xyz, dtype=np.float32)
            atom_radii = [
                functions_module._ATOMIC_RADII[atom.element.symbol]
                for atom in protein_snapshot.topology.atoms
            ]
        else:
            xyz = np.array(
                np.expand_dims(
                    np.concatenate(
                        (protein_snapshot.xyz[0], cover_atom_coords), axis=0
                    ),
                    axis=0,
                ),
                dtype=np.float32,
            )
            atom_radii = [
                functions_module._ATOMIC_RADII[atom.element.symbol]
                for atom in protein_snapshot.topology.atoms
            ] + [0.17 for _ in range(xyz.shape[1] - protein_snapshot.xyz.shape[1])]

        radii = np.array(atom_radii, np.float32) + probe_radius
        atom_mapping = np.arange(xyz.shape[1], dtype=np.int32)
        atom_selection_mask = np.ones(xyz.shape[1], dtype=np.int32)
        out = np.zeros((1, xyz.shape[1]), dtype=np.float32)
        scientific_call(
            'mdtraj_sasa',
            _geometry._sasa,
            xyz,
            radii,
            int(n_sphere_points),
            atom_mapping,
            atom_selection_mask,
            out,
        )
        return out[:, : protein_snapshot.xyz.shape[1]][0]

    functions_module.getSASA = get_sasa_compat


def _patch_alphaspace2_numpy_compatibility():
    if not hasattr(np, 'float'):
        setattr(np, 'float', float)


def _initialize_unbound_contacts(snapshot) -> bool:
    """Supply the upstream source fix missing from the PyPI 0.1.2 release."""
    if snapshot._alpha_contact is not None:
        return False
    snapshot._alpha_contact = np.zeros(len(snapshot._alpha_xyz), dtype=bool)
    snapshot._beta_contact = np.zeros(len(snapshot._beta_alpha_index_list), dtype=bool)
    snapshot._pocket_contact = np.zeros(
        len(snapshot._pocket_alpha_index_list), dtype=bool
    )
    return True


def _validate_loaded_coordinates(
    trajectory: Any, indices: np.ndarray, context: dict[str, Any], role: str
) -> None:
    """Bind MDTraj's ordered nm rows to the admitted source frame.

    No atom matching or alignment is inferred. The absolute tolerance covers
    PDB's three-decimal angstrom rounding (0.000051 nm), and the relative
    tolerance covers four float32 epsilons in MDTraj's coordinate conversion.
    """
    xyz = np.asarray(trajectory.xyz)
    if xyz.shape != (1, len(indices), 3):
        raise ValueError(
            f'AlphaSpace2 {role} must contain a single frame and the submitted atom count.'
        )
    if not np.isfinite(xyz).all():
        raise ValueError(f'AlphaSpace2 {role} coordinates must be finite.')
    expected = np.asarray(context['coordinates']['value'], dtype=float)[indices]
    if not np.allclose(
        xyz[0], expected, rtol=4 * np.finfo(np.float32).eps, atol=0.000051
    ):
        raise ValueError(
            f'AlphaSpace2 {role} loaded coordinates disagree with the source rows.'
        )


@attributed('alphaspace2', route='original')
@arg_digest(**OPTIONS, map=LIBRARY_PIPELINES)
@dep_digest('alphaspace2', when={'upstream_root': None})
@dep_digest('mdtraj')
def get_topography(
    molecular_system: Any,
    *,
    selection: str = 'all',
    structure_indices: int | list[int] = 0,
    chemical_state: str | int = 'reference',
    syntax: str = 'MolSysMT',
    upstream_root: str | Path | None = None,
    min_vertices: int = 20,
    binder: Any | None = None,
    binder_selection: str = 'all',
    binder_structure_indices: int | list[int] = 0,
    binder_chemical_state: str | int = 'reference',
    binder_syntax: str = 'MolSysMT',
    skip_digestion: bool = False,
) -> Topography:
    """Run the original AlphaSpace2 engine on a receptor and optional binder.

    Parameters
    ----------
    molecular_system : molecular system
        Receptor in a form supported by MolSysMT.
    selection : str, default='all'
        Receptor atom selection in ``syntax``.
    structure_indices : int or list of int, default=0
        Receptor frame selection. The submitted structure must have one frame.
    chemical_state : str or int, default='reference'
        Existing unambiguous receptor reference state or its index. No reference
        is changed and no chemistry is prepared or inferred here.
    syntax : str, default='MolSysMT'
        Receptor selection syntax.
    upstream_root : str or Path, optional
        Source checkout import root when the optional package is unavailable.
    min_vertices : int, default=20
        Minimum alpha-site count for returning a pocket. Original outputs retain
        every pocket regardless of this filter.
    binder : molecular system, optional
        Ligand in the same coordinate frame as the receptor. No alignment is
        performed. May be the same complex with a separate atom selection.
    binder_selection : str, default='all'
        Binder atom selection in ``binder_syntax``.
    binder_structure_indices : int or list of int, default=0
        Binder frame selection. The submitted structure must have one frame.
    binder_chemical_state : str or int, default='reference'
        Existing unambiguous binder reference state or its index, independently
        of the receptor. An explicit index requires a binder.
    binder_syntax : str, default='MolSysMT'
        Binder selection syntax.
    skip_digestion : bool, default=False
        Internal bypass for already admitted argument values.

    Returns
    -------
    Topography
        Original pocket measurements, contact state and portable input/output.
        A binder activates contacts and occupancy, but not Vina receptor typing.

    Raises
    ------
    ArgumentError
        If an index axis, selection, route option or positive count is invalid.
        Argument admission precedes dependency loading and molecular conversion.
    ValueError
        If a reference state is absent, empty, ambiguous or conflicts with an
        explicit index; or if a submitted frame, row map or loaded coordinate
        axis disagrees with its source. Nonreference export is not substituted.
    TypeError
        If unsupported engine options are supplied.
    LibraryNotFoundError
        If a required optional library is absent.

    Examples
    --------
    >>> topography = get_topography('receptor.pdb', binder='ligand.pdb')
    """
    chemical_context = reference_chemical_context(
        molecular_system, chemical_state, provider='AlphaSpace2 receptor'
    )
    binder_chemical_context = (
        None
        if binder is None
        else reference_chemical_context(
            binder, binder_chemical_state, provider='AlphaSpace2 binder'
        )
    )
    source_context = source_input_context(molecular_system, structure_indices)
    binder_source_context = (
        None
        if binder is None
        else source_input_context(binder, binder_structure_indices)
    )
    with tempfile.TemporaryDirectory(prefix='topomt_alphaspace2_') as tmpdir_name:
        tmpdir = Path(tmpdir_name)
        input_pdb, selected_atom_indices = prepare_wrapper_input_pdb(
            molecular_system,
            tmpdir=tmpdir,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        validate_single_frame_pdb(input_pdb, provider='AlphaSpace2 receptor')
        serial_map = validate_submitted_pdb(
            molecular_system,
            input_pdb,
            selected_atom_indices,
            selection=selection,
            structure_indices=structure_indices,
            syntax=syntax,
        )

        binder_trajectory = None
        binder_metadata = None
        additional_inputs: dict[str, str | Path] = {}
        if binder is not None:
            binder_dir = tmpdir / 'binder'
            binder_dir.mkdir()
            binder_pdb, binder_atom_indices = prepare_wrapper_input_pdb(
                binder,
                tmpdir=binder_dir,
                selection=binder_selection,
                structure_indices=binder_structure_indices,
                syntax=binder_syntax,
            )
            validate_single_frame_pdb(binder_pdb, provider='AlphaSpace2 binder')
            binder_serial_map = validate_submitted_pdb(
                binder,
                binder_pdb,
                binder_atom_indices,
                selection=binder_selection,
                structure_indices=binder_structure_indices,
                syntax=binder_syntax,
            )
            binder_input_name = f'binder/{binder_pdb.name}'
            additional_inputs[binder_input_name] = binder_pdb
            binder_metadata = {
                'input_artifact': f'input/{binder_input_name}',
                'selection': _snapshot_json_value(binder_selection),
                'structure_indices': _snapshot_json_value(binder_structure_indices),
                'syntax': binder_syntax,
                'selected_atom_indices': binder_atom_indices.tolist(),
                'atom_serial_to_index': {
                    str(serial): index for serial, index in binder_serial_map.items()
                },
                'chemical_state_context': binder_chemical_context,
                'source_context_artifact': 'output/topomt_binder_context.json',
            }

        import mdtraj as md

        receptor = scientific_call('mdtraj', md.load, str(input_pdb))
        _validate_loaded_coordinates(
            receptor, selected_atom_indices, source_context, 'receptor'
        )
        if binder_source_context is not None:
            binder_trajectory = scientific_call('mdtraj', md.load, str(binder_pdb))
            _validate_loaded_coordinates(
                binder_trajectory, binder_atom_indices, binder_source_context, 'binder'
            )
        upstream = import_upstream_module('alphaspace2', upstream_root=upstream_root)
        _patch_alphaspace2_numpy_compatibility()
        _patch_alphaspace2_mdtraj_sasa(upstream)
        snapshot = upstream.Snapshot()
        snapshot.run(receptor, binder=binder_trajectory)
        unbound_contacts_initialized = _initialize_unbound_contacts(snapshot)

        output_dir = tmpdir / 'results'
        output_dir.mkdir()
        (output_dir / 'topomt_source_context.json').write_text(
            json.dumps(source_context, sort_keys=True, allow_nan=False)
        )
        if binder_source_context is not None:
            (output_dir / 'topomt_binder_context.json').write_text(
                json.dumps(binder_source_context, sort_keys=True, allow_nan=False)
            )
        snapshot.save(
            output_dir=str(output_dir),
            receptor=receptor,
            binder=binder_trajectory,
            chimera_scripts=False,
            contact_only=False,
        )
        state = {
            'schema_version': 1,
            **{
                name: _snapshot_json_value(value)
                for name, value in snapshot.__dict__.items()
            },
            'pocket_properties': [
                {
                    'index': pocket.index,
                    'alpha_indices': _snapshot_json_value(pocket.alpha_index),
                    'beta_indices': _snapshot_json_value(
                        snapshot._pocket_beta_index_list[pocket.index]
                    ),
                    'space': _snapshot_json_value(pocket.space),
                    'nonpolar_space': _snapshot_json_value(pocket.nonpolar_space),
                    'score': _snapshot_json_value(pocket.score),
                    'occupied_space': _snapshot_json_value(pocket.occupiedSpace),
                    'occupied_nonpolar_space': _snapshot_json_value(
                        pocket.occupiedNonpolarSpace
                    ),
                    'occupancy': _snapshot_json_value(pocket.occupancy),
                    'occupancy_nonpolar': _snapshot_json_value(
                        pocket.occupancy_nonpolar
                    ),
                    'is_contact': bool(pocket.isContact),
                }
                for pocket in snapshot.pockets
            ],
            'beta_properties': [
                {
                    'index': beta.index,
                    'alpha_indices': _snapshot_json_value(
                        snapshot._beta_alpha_index_list[beta.index]
                    ),
                    'space': _snapshot_json_value(beta.space),
                    'nonpolar_space': _snapshot_json_value(beta.nonpolar_space),
                    'scores': _snapshot_json_value(beta.scores),
                    'score': _snapshot_json_value(beta.score),
                    'best_probe_type': beta.best_probe_type,
                    'occupied_space': _snapshot_json_value(beta.occupiedSpace),
                    'occupied_nonpolar_space': _snapshot_json_value(
                        beta.occupiedNonpolarSpace
                    ),
                    'occupancy': _snapshot_json_value(beta.occupancy),
                    'occupancy_nonpolar': _snapshot_json_value(beta.occupancy_nonpolar),
                    'is_contact': bool(beta.isContact),
                }
                for beta in snapshot.betas
            ],
        }
        (output_dir / 'topomt_snapshot.json').write_text(
            json.dumps(state, sort_keys=True, allow_nan=False)
        )
        source_file = Path(inspect.getfile(upstream.Snapshot))
        with source_file.open('rb') as file_handle:
            source_sha256 = hashlib.file_digest(file_handle, 'sha256').hexdigest()
        run = ProviderRun.capture(
            'alphaspace2',
            'library',
            input_pdb,
            output_dir,
            additional_inputs=additional_inputs,
            metadata={
                'snapshot_source_sha256': source_sha256,
                'distribution_version': installed_provider_version(upstream),
                'output_protocol': _output_protocol(),
                'source_context_artifact': 'output/topomt_source_context.json',
                'chemical_state_context': chemical_context,
                'atom_serial_to_index': {
                    str(serial): index for serial, index in serial_map.items()
                },
                'unbound_contacts_initialized': unbound_contacts_initialized,
                'receptor_input_artifact': f'input/{input_pdb.name}',
                'binder': binder_metadata,
                'selection': _snapshot_json_value(selection),
                'structure_indices': _snapshot_json_value(structure_indices),
                'syntax': syntax,
                'min_vertices': min_vertices,
                'selected_atom_indices': selected_atom_indices.tolist(),
                'snapshot_settings': {
                    name: _snapshot_json_value(getattr(snapshot, name))
                    for name in (
                        'min_r',
                        'max_r',
                        'beta_cluster_dist',
                        'pocket_cluster_dist',
                        'contact_cutoff',
                    )
                },
            },
        )

        return snapshot_to_topography(
            molecular_system,
            state,
            selected_atom_indices,
            run,
            selection=selection,
            structure_indices=structure_indices,
            min_vertices=min_vertices,
        )


get_topography_with_alphaspace2 = get_topography
