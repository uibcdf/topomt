"""Reusable source profile and comparison tools for original-provider controls.

These operations orchestrate public MolSysMT tools. They perform no molecular
recognition, chemical preparation, atom matching or pharmacophore modeling.
"""

from dataclasses import asdict
from itertools import zip_longest
from math import isfinite, isnan
from typing import Any

import molsysmt as msm
import numpy as np

from topomt import pyunitwizard as puw
from topomt.third_party.output import ProviderOutput


def chemical_state_context(source: Any) -> dict[str, int | None]:
    """Return the declared state count/reference without inferring chemistry.

    Parameters
    ----------
    source : molsysmt.MolSys
        Native molecular source supplied by MolSysMT.

    Returns
    -------
    dict
        Count and reference index. Absent states have count None; a present
        empty inventory has count zero. An ambiguous reference remains None.

    Raises
    ------
    AttributeError
        If source does not expose the native public chemical_states domain.
    """
    states = source.chemical_states
    return {
        'count': None if states is None else states.n_chemical_states,
        'reference_index': None
        if states is None
        else states.reference_chemical_state_index,
    }


def prepare_reference_source(molecular_system: Any) -> tuple[Any, list[int]]:
    """Declare a nonconsecutive selection and a translated second frame.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Single-frame source with protein and auxiliary atoms,
        exactly one declared chemical state and reference index zero. Chemistry
        must already be prepared for any subsequent recognition.

    Returns
    -------
    molecular_system
        Copied/permuted full source with frame 1 translated by (0.3,-0.2,0.1) nm.
        All selections, permutation and coordinate operations belong to MolSysMT.
    list of int
        Nonconsecutive source indices of protein/peptide atoms.

    Raises
    ------
    ValueError
        If the source does not meet this explicit analytical control profile.
        No missing chemistry is inferred or repaired.

    Examples
    --------
    >>> source, selection = prepare_reference_source(Path('prepared.h5msm'))  # doctest: +SKIP
    """
    source = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    if msm.get(source, n_structures=True) != 1:
        raise ValueError('The pilot seed requires exactly one coordinate frame.')
    if chemical_state_context(source) != {'count': 1, 'reference_index': 0}:
        raise ValueError(
            'Pilot requires one explicit reference chemical state at index 0.'
        )
    protein = msm.select(source, selection="molecule_type in ['protein', 'peptide']")
    auxiliary = sorted(set(range(msm.get(source, n_atoms=True))) - set(protein))
    order = [
        int(index)
        for pair in zip_longest(protein, auxiliary)
        for index in pair
        if index is not None
    ]
    source = msm.permute_atoms(source, order)
    selection = [
        int(index)
        for index in msm.select(
            source, selection="molecule_type in ['protein', 'peptide']"
        )
    ]
    if not np.any(np.diff(np.asarray(selection, dtype=int)) > 1):
        raise ValueError(
            'Pilot requires nonconsecutive protein atoms and auxiliary atoms.'
        )
    second = msm.structure.translate(
        source, translation=puw.quantity([[[0.3, -0.2, 0.1]]], 'nm')
    )
    # Historical interaction analyses do not describe the newly declared frame.
    # Append only Structures; the sole state supplies its implicit association.
    msm.append_structures(source, msm.convert(second, to_form='molsysmt.Structures'))
    return source, selection


def _original_value(value: Any) -> Any:
    """Compare undefined original measurements without admitting NaN geometry."""
    if isinstance(value, list):
        return [_original_value(item) for item in value]
    if isinstance(value, float) and not isfinite(value):
        return ('nonfinite', 'nan' if isnan(value) else 'inf' if value > 0 else '-inf')
    return value


def pocket_signature(output: ProviderOutput) -> list[dict[str, Any]]:
    """Snapshot ordered consumer fields without recaptured-run identity.

    Parameters
    ----------
    output : ProviderOutput
        Detached original provider output.

    Returns
    -------
    list of dict
        IDs, source membership/role, explicit nm geometry and original attributed
        measurement fields. Execution IDs and converted measurement values are
        excluded so legacy fpocket files recapture can compare its original
        scientific fields. Undefined measurement values use comparable markers;
        finite values and geometry remain unchanged. This is not an exhaustive
        comparison of extra fields.

    Raises
    ------
    AttributeError
        If the object does not follow the ProviderOutput contract.
    """
    return [
        {
            'source_id': pocket.source_id,
            'atom_indices': pocket.atom_indices,
            'atom_role': pocket.atom_role,
            'geometries': {
                name: asdict(geometry) for name, geometry in pocket.geometries.items()
            },
            'measurements': {
                name: {
                    key: _original_value(value) if key == 'original_value' else value
                    for key, value in asdict(measurement).items()
                    if key not in {'run_id', 'value'}
                }
                for name, measurement in pocket.measurements.items()
            },
        }
        for pocket in output.pockets
    ]


def pocket_outputs_agree(left: ProviderOutput, right: ProviderOutput) -> bool:
    """Compare consumer signatures with 1e-12 nm tolerance only on geometry.

    Parameters
    ----------
    left, right : ProviderOutput
        Original and recovered provider results in the same source namespace.

    Returns
    -------
    bool
        Exact identity, membership, definitions and original measurements agree;
        geometry agrees with zero relative and 1e-12 nm absolute tolerance.

    Raises
    ------
    AttributeError
        If an object does not follow the ProviderOutput contract.
    """
    first, second = pocket_signature(left), pocket_signature(right)
    if len(first) != len(second):
        return False
    for a, b in zip(first, second):
        if a['geometries'].keys() != b['geometries'].keys():
            return False
        for kind in a['geometries']:
            for name in ('points_nm', 'radii_nm'):
                x = a['geometries'][kind].pop(name)
                y = b['geometries'][kind].pop(name)
                if x is None or y is None:
                    if x != y:
                        return False
                elif np.shape(x) != np.shape(y) or not np.allclose(
                    x, y, rtol=0.0, atol=1e-12
                ):
                    return False
    return first == second
