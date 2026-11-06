"""Source provenance and mappings at MolSysMT's reference-state PDB boundary."""

import hashlib
import json
from numbers import Integral
from typing import Any

import molsysmt as msm


def reference_chemical_context(
    molecular_system: Any,
    chemical_state: str | int = 'reference',
    *,
    provider: str,
) -> dict[str, Any]:
    """Record the unambiguous reference used by MolSysMT's PDB exporter.

    Other state selection is rejected rather than changing a molecular reference
    or using private provider contexts. A digest binds the provider's formal
    charges (integer elementary-charge units), bond table and completeness. It
    is integrity evidence, not authentication or a chemical-readiness assessment.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source inventory; the digest covers its reference state.
    chemical_state : str or int, default='reference'
        Unambiguous reference or its nonnegative integer index.
    provider : str
        Adapter name used in diagnostics.

    Returns
    -------
    dict
        Reference index, state count and ID, and SHA-256 of charges, bonds and
        connectivity completeness. No state is inferred or modified.

    Raises
    ------
    ValueError
        If the state is absent, empty, ambiguous or not the current reference.

    Examples
    --------
    >>> context = reference_chemical_context(source, provider='Pocketeer')  # doctest: +SKIP
    """
    if not (
        isinstance(chemical_state, str)
        and chemical_state == 'reference'
        or isinstance(chemical_state, Integral)
        and not isinstance(chemical_state, bool)
        and int(chemical_state) >= 0
    ):
        raise ValueError('chemical_state must be reference or its integer index.')
    source = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    states = source.chemical_states
    if states is None:
        raise ValueError(f'{provider} chemical-state context is absent.')
    count = states.n_chemical_states
    if count == 0:
        raise ValueError(f'{provider} input has zero chemical states.')
    reference = states.reference_chemical_state_index
    if reference is None:
        raise ValueError(f'{provider} chemical-state reference is ambiguous.')
    if chemical_state != 'reference' and int(chemical_state) != reference:
        raise ValueError(
            f'{provider} nonreference chemical-state export is unsupported by the '
            'qualified MolSysMT PDB conversion; no reference is changed.'
        )
    ids = msm.get(source, chemical_state_id=True)
    charges = msm.get(
        source, element='atom', formal_charge=True, chemical_state=reference
    )
    encoded_charges = None
    if charges is not None:
        encoded_charges = [
            int(value) if isinstance(value, Integral) else None for value in charges
        ]
    chemistry = {
        'formal_charges': {'value': encoded_charges, 'unit': 'e'},
        'bonds': states.get_bonds(chemical_state=reference).to_json(orient='split'),
        'connectivity_completeness': msm.get(
            source, connectivity_completeness=True, chemical_state=reference
        ),
    }
    digest = hashlib.sha256(
        json.dumps(chemistry, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()
    return {
        'index': int(reference),
        'reference_index': int(reference),
        'state_count': int(count),
        'state_id': ids[reference],
        'pdb_chemistry_sha256': digest,
    }


_ATOM_ATTRIBUTES = (
    'atom_id',
    'atom_name',
    'atom_type',
    'group_id',
    'group_name',
    'chain_id',
)


def validate_reference_chemical_context(
    molecular_system: Any, context: Any, *, provider: str
) -> None:
    """Require the exact saved reference schema and public source chemistry.

    Integer fields reject booleans/floats before comparing the source. This
    prevents Python's numerically equal values from disguising malformed JSON.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source whose existing reference state is compared.
    context : dict
        Exact recorded index/reference/count/ID and chemistry digest schema.
    provider : str
        Provider name used in disagreement diagnostics.

    Returns
    -------
    None
        Saved typed values and public source facts agree.

    Raises
    ------
    ValueError
        If the saved schema, selector or source chemistry disagrees. No state
        is prepared, inferred or changed to obtain agreement.
    """
    keys = {
        'index',
        'reference_index',
        'state_count',
        'state_id',
        'pdb_chemistry_sha256',
    }
    if (
        not isinstance(context, dict)
        or set(context) != keys
        or any(
            type(context[k]) is not int
            for k in ('index', 'reference_index', 'state_count')
        )
        or not 0
        <= context['index']
        == context['reference_index']
        < context['state_count']
    ):
        raise ValueError(f'Invalid {provider} saved chemical-state context.')
    actual = reference_chemical_context(
        molecular_system, context['index'], provider=provider
    )
    if json.dumps(context, sort_keys=True) != json.dumps(actual, sort_keys=True):
        raise ValueError(
            f'Source chemical-state context disagrees with the saved {provider} run.'
        )


def source_input_context(
    molecular_system: Any, structure_indices: Any
) -> dict[str, Any]:
    """Snapshot public source identities and one full coordinate frame.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source, including atoms omitted from provider submission.
    structure_indices : int or sequence of int
        Exactly one source frame.

    Returns
    -------
    dict
        Schema 1 atom attributes, atom count and full coordinates with an
        explicit nanometer unit. This is adapter provenance, not an atom matcher.

    Raises
    ------
    ValueError
        If coordinates are nonfinite or do not describe exactly one frame.
    """
    import numpy as np

    from topomt import pyunitwizard as puw

    attributes = msm.get(
        molecular_system,
        element='atom',
        output_type='dictionary',
        get_missing_bonds=False,
        **{name: True for name in _ATOM_ATTRIBUTES},
    )
    n_atoms = int(msm.get(molecular_system, n_atoms=True))
    coordinates = np.asarray(
        puw.get_value(
            msm.get(
                molecular_system, structure_indices=structure_indices, coordinates=True
            ),
            to_unit='nm',
        )
    )
    if coordinates.shape != (1, n_atoms, 3) or not np.isfinite(coordinates).all():
        raise ValueError('Source context requires one finite full coordinate frame.')
    encoded = {}
    for name, values in attributes.items():
        encoded[name] = (
            None
            if values is None
            else [
                value.item() if isinstance(value, np.generic) else value
                for value in values
            ]
        )
    return {
        'schema_version': 1,
        'n_atoms': n_atoms,
        'atom_attributes': encoded,
        'coordinates': {'value': coordinates[0].tolist(), 'unit': 'nm'},
    }


def validate_source_input_context(
    molecular_system: Any, context: dict[str, Any], structure_indices: Any
) -> None:
    """Require agreement with a captured full-source identity and frame.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Full source supplied during saved-result recovery.
    context : dict
        Schema 1 record from source_input_context, with explicit nm units.
    structure_indices : int or sequence of int
        Saved source frame selector.

    Returns
    -------
    None
        Source identities and coordinates agree without changing the source.

    Raises
    ------
    ValueError
        If schema, identities or coordinates disagree. Absolute coordinate
        tolerance is 1e-12 nm; no alignment or correspondence is inferred.
    """
    import numpy as np

    actual = source_input_context(molecular_system, structure_indices)
    try:
        if (
            set(context) != set(actual)
            or type(context['schema_version']) is not int
            or context['schema_version'] != 1
            or type(context['n_atoms']) is not int
            or context['n_atoms'] != actual['n_atoms']
            or json.dumps(context['atom_attributes'], sort_keys=True)
            != json.dumps(actual['atom_attributes'], sort_keys=True)
            or set(context['coordinates']) != {'value', 'unit'}
            or context['coordinates']['unit'] != 'nm'
        ):
            raise ValueError('Source atom context disagrees with the saved run.')
        values = context['coordinates']['value']
        if not isinstance(values, list) or any(
            not isinstance(row, list)
            or len(row) != 3
            or any(type(value) not in (int, float) for value in row)
            for row in values
        ):
            raise ValueError('Invalid saved source context coordinate types.')
        saved: np.ndarray = np.asarray(values, dtype=float)
        current = np.asarray(actual['coordinates']['value'], dtype=float)
        if (
            saved.shape != current.shape
            or not np.isfinite(saved).all()
            or not np.allclose(saved, current, rtol=0, atol=1e-12)
        ):
            raise ValueError('Source coordinates disagree with the saved context.')
    except (KeyError, TypeError, OverflowError) as error:
        raise ValueError('Invalid saved source context.') from error


def validate_submitted_pdb(
    molecular_system: Any,
    pdb_file: Any,
    atom_indices: Any,
    *,
    selection: Any,
    structure_indices: Any,
    syntax: str,
) -> dict[int, int]:
    """Validate a submitted PDB row map against public MolSysMT selections.

    Parameters
    ----------
    molecular_system : MolSysMT-compatible input
        Source inventory and coordinates.
    pdb_file : pathlib.Path
        Actual submitted PDB; one frame is admitted separately.
    atom_indices : sequence of int
        Source index for each submitted ATOM/HETATM row.
    selection : str or sequence of int
        Source selection that the unique row map must cover.
    structure_indices : int or sequence of int
        One source frame.
    syntax : str
        MolSysMT selection syntax.

    Returns
    -------
    dict
        Unique submitted serial to source index map.

    Raises
    ------
    ValueError
        If coverage, serials or coordinates conflict. Coordinate tolerance is
        0.00051 angstroms for the submitted PDB's three-decimal representation.
    """
    import numpy as np

    from topomt import pyunitwizard as puw

    indices = np.asarray(atom_indices)
    lines = [
        line
        for line in pdb_file.read_text().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    selected = msm.select(molecular_system, selection=selection, syntax=syntax)
    if (
        indices.ndim != 1
        or indices.dtype.kind not in 'iu'
        or len(indices) != len(lines)
        or len(np.unique(indices)) != len(indices)
        or set(indices) != set(selected)
    ):
        raise ValueError('The submitted atom map must uniquely cover the selection.')
    serials = [int(line[6:11]) for line in lines]
    if len(set(serials)) != len(serials):
        raise ValueError('Submitted PDB atom serials must be unique.')
    coordinates = puw.get_value(
        msm.get(
            molecular_system,
            selection=indices,
            structure_indices=structure_indices,
            coordinates=True,
        ),
        to_unit='angstroms',
    )
    submitted = np.asarray(
        [[float(line[start : start + 8]) for start in (30, 38, 46)] for line in lines]
    )
    if coordinates.shape != (1, len(indices), 3) or not np.allclose(
        coordinates[0], submitted, rtol=0, atol=0.00051
    ):
        raise ValueError('Submitted PDB coordinates disagree with the source frame.')
    return {serial: int(index) for serial, index in zip(serials, indices)}
