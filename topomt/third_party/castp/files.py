"""Import original CASTp files and recover explicitly source-bound evidence."""

from pathlib import Path
from typing import Any

from topomt._private.arg_digestion import arg_digest
from topomt._private.arg_digestion.castp_arguments import OPTIONS
from topomt._private.smonitor import signal
from topomt.io.load_CASTp import load_CASTp
from topomt.provider_output import ProviderRun

from .output import CASTpOutput


def load_topography(*, zip_file=None, dir_path=None, molecular_system=None, **kwargs):
    """Load CASTp-family results from files or archives."""

    return load_CASTp(
        zip_file=zip_file,
        dir_path=dir_path,
        molecular_system=molecular_system,
        **kwargs,
    )


@signal(tags=['provider', 'castp', 'files'])
@arg_digest(**OPTIONS)
def load_output(
    molecular_system: Any = None,
    *,
    source_atom_indices: Any = None,
    selection: Any = 'all',
    structure_indices: Any = 0,
    syntax: str = 'MolSysMT',
    chemical_state: str | int = 'reference',
    skip_digestion: bool = False,
    **kwargs: Any,
) -> CASTpOutput:
    """Import original files, optionally binding a declared source correspondence.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input, optional
        Full existing source; requires an explicit source_atom_indices map.
        Without it, original files supply their own PDB or unknown membership.
    source_atom_indices : sequence of int, optional
        Full-source index for each original result-PDB atom row, in row order.
        Correspondence is declared by the caller, never inferred or sorted.
    selection : str or sequence of int, default='all'
        Source selection covered exactly once by the map.
    structure_indices : int or one-element sequence of int, default=0
        Source coordinate frame corresponding to the original PDB.
    syntax : str, default='MolSysMT'
        MolSysMT selection syntax.
    chemical_state : str or int, default='reference'
        Existing, unambiguous reference state. No chemistry is prepared.
    skip_digestion : bool, default=False
        Internal bypass for already admitted arguments.
    **kwargs
        Legacy original ZIP, directory or individual-file import arguments.

    Returns
    -------
    CASTpOutput
        Detached records and exact evidence. Bound results retain full source
        frame, atom identities, reference chemistry and source correspondence.

    Raises
    ------
    ArgumentError
        If argument values or the selected route's option names are invalid.
    ValueError
        If source/map pairing, PDB identities, coordinates or chemistry disagree.
    OSError
        If an input cannot be read.

    Examples
    --------
    >>> result = load_output(zip_file='original.zip')  # doctest: +SKIP
    """
    from topomt.third_party.output import _from_topography

    from ._source import FILE_ARGUMENTS, _bind

    if (molecular_system is None) != (source_atom_indices is None):
        raise ValueError(
            'CASTp source binding requires both a full source and source_atom_indices.'
        )
    if molecular_system is None:
        if (
            not isinstance(selection, str)
            or selection != 'all'
            or type(structure_indices) is not int
            or structure_indices != 0
            or syntax != 'MolSysMT'
            or chemical_state != 'reference'
        ):
            raise ValueError(
                'CASTp source selectors require a full source and explicit atom map.'
            )
        topography = load_topography(**kwargs)
        return _from_topography(topography, CASTpOutput)
    topography = load_topography(_load_molecular_system=False, **kwargs)
    run = next(iter(topography.provider_runs.values()))
    explicit = None
    if kwargs.get('zip_file') is None and kwargs.get('dir_path') is None:
        explicit = {
            key: 'output/' + Path(kwargs[arg]).name
            for key, arg in FILE_ARGUMENTS.items()
            if kwargs.get(arg) is not None
        }
    return _bind(
        run,
        molecular_system,
        source_atom_indices,
        selection=selection,
        structure_indices=structure_indices,
        syntax=syntax,
        chemical_state=chemical_state,
        result_artifacts=explicit,
    )


@signal(tags=['provider', 'castp', 'files', 'recovery'])
@arg_digest(**OPTIONS)
def recover_output(
    molecular_system: Any,
    *,
    bundle_file: str | Path,
    provider_server: str | None = None,
    skip_digestion: bool = False,
) -> CASTpOutput:
    """Recover source-bound original evidence without contacting a server.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source with the saved inventory, frame and reference chemistry.
    bundle_file : str or pathlib.Path
        Bundle from ProviderRun.save after an explicitly source-bound import.
    provider_server : str, optional
        Assert agreement with the server identity recorded in that import.
    skip_digestion : bool, default=False
        Internal bypass for already admitted arguments.

    Returns
    -------
    CASTpOutput
        Reconstructed records retaining the same run ID, metadata and artifacts.

    Raises
    ------
    ArgumentError
        If arguments are invalid or saved selectors are overridden.
    ValueError
        If integrity, source context, reference state, maps or artifacts differ.
        Historical unbound runs are not upgraded by inference.
    OSError
        If the bundle cannot be read.

    Examples
    --------
    >>> result = recover_output('source.h5msm', bundle_file='bound.zip')  # doctest: +SKIP
    """
    from ._source import _recover

    return _recover(ProviderRun.load(bundle_file), molecular_system, provider_server)
