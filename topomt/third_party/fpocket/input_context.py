"""Admission of chemical context supported by the original fpocket PDB route."""

import hashlib
import json
from numbers import Integral
from typing import Any

import molsysmt as msm


def _chemical_context(
    molecular_system: Any, chemical_state: str | int = 'reference'
) -> dict[str, Any]:
    """Record the unambiguous reference used by MolSysMT's PDB exporter.

    Other state selection is rejected rather than changing a molecular reference
    or using private provider contexts. A digest binds the provider's formal
    charges (integer elementary-charge units), bond table and completeness. It
    is integrity evidence, not authentication or a chemical-readiness assessment.
    """
    if not (
        isinstance(chemical_state, str)
        and chemical_state == 'reference'
        or isinstance(chemical_state, Integral)
        and not isinstance(chemical_state, bool)
    ):
        raise ValueError('chemical_state must be reference or its integer index.')
    source = msm.convert(molecular_system, to_form='molsysmt.MolSys')
    states = source.chemical_states
    if states is None:
        raise ValueError('fpocket chemical-state context is absent.')
    count = states.n_chemical_states
    if count == 0:
        raise ValueError('fpocket input has zero chemical states.')
    reference = states.reference_chemical_state_index
    if reference is None:
        raise ValueError('fpocket chemical-state reference is ambiguous.')
    if chemical_state != 'reference' and int(chemical_state) != reference:
        raise ValueError(
            'fpocket nonreference chemical-state export is unsupported by the '
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
