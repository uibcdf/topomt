"""Admission of chemical context supported by the original fpocket PDB route."""

from typing import Any

from topomt.third_party.pdb_context import reference_chemical_context


def _chemical_context(
    molecular_system: Any, chemical_state: str | int = 'reference'
) -> dict[str, Any]:
    return reference_chemical_context(
        molecular_system, chemical_state, provider='fpocket'
    )
