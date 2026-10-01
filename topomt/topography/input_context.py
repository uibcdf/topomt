"""Recoverable selected molecular input without a second topology model."""

from typing import Any, Optional
from uuid import uuid4

import molsysmt as msm
import numpy as np
from molsysmt.native import MolSys

from topomt import pyunitwizard as puw
from topomt.tools.geometry.arrays import _GeometrySnapshot, immutable_array


class InputContext(_GeometrySnapshot):
    """Retain one selected input occurrence and its original atom mapping.

    Parameters
    ----------
    coordinates, radii : PyUnitWizard quantity
        Selected coordinates (N, 3) and radii (N,). Stored in nm.
    atom_indices : numpy.ndarray
        Unique non-negative source atom indices in selected local order.
    selection : str or tuple of int
        Requested selection before engine-specific hydrogen filtering.
    structure_index : int or None
        Original frame index; None for explicit array inputs.
    selection_syntax : str
        Syntax of the requested selection.
    hydrogen_policy, radii_model : str
        Policies used to prepare the geometry input.
    molecular_system : molsysmt.MolSys, optional
        Already selected, single-frame MolSys in the same local atom order.
        An independent copy is retained; omit for topology-free array input.

    Returns
    -------
    InputContext
        Protected numerical evidence and recoverable selected molecular input.

    Raises
    ------
    ValueError
        If units, shapes, atom mapping or molecular snapshot are inconsistent.

    Notes
    -----
    The opaque source_id identifies this captured occurrence. It does not prove
    molecular identity or correspondence with another independently built input.
    Coordinates use nonperiodic Cartesian geometry without an applied transform.
    Molecular topology and structural metadata remain owned by MolSysMT.

    Examples
    --------
    >>> saved = InputContext(
    ...     coordinates=puw.quantity([[0., 0., 0.]], 'nm'),
    ...     radii=puw.quantity([0.17], 'nm'), atom_indices=np.array([8]),
    ...     selection='array', structure_index=None,
    ...     selection_syntax='explicit_indices', hydrogen_policy='provided_atoms',
    ...     radii_model='provided')
    >>> saved.local_atom_indices([8], source_id=saved.source_id)
    [0]
    """

    def __init__(
        self,
        *,
        coordinates: Any,
        radii: Any,
        atom_indices: np.ndarray,
        selection: str | tuple[int, ...],
        structure_index: Optional[int],
        selection_syntax: str,
        hydrogen_policy: str,
        radii_model: str,
        molecular_system: Optional[MolSys] = None,
    ) -> None:
        if not puw.is_quantity(coordinates) or not puw.is_quantity(radii):
            raise ValueError('InputContext coordinates and radii require length units.')
        self._coordinates = immutable_array(
            np.asarray(puw.get_value(coordinates, to_unit='nm'), dtype=float)
        )
        self._radii = immutable_array(
            np.asarray(puw.get_value(radii, to_unit='nm'), dtype=float)
        )
        indices = np.asarray(atom_indices)
        if (
            indices.ndim != 1
            or indices.dtype.kind not in 'iu'
            or np.any(indices < 0)
            or len(np.unique(indices)) != len(indices)
        ):
            raise ValueError(
                'Source atom indices must be unique non-negative integers.'
            )
        self.atom_indices = immutable_array(indices.astype(int, copy=False))
        n_atoms = len(indices)
        if self._coordinates.shape != (n_atoms, 3) or self._radii.shape != (n_atoms,):
            raise ValueError('Selected coordinates, radii and atom mapping disagree.')
        if (
            not np.all(np.isfinite(self._coordinates))
            or not np.all(np.isfinite(self._radii))
            or np.any(self._radii <= 0)
        ):
            raise ValueError(
                'Coordinates must be finite and radii finite and positive.'
            )
        self.source_id = f'input-{uuid4().hex}'
        self.selection = selection if isinstance(selection, str) else tuple(selection)
        self.selection_syntax = selection_syntax
        if structure_index is not None and (
            isinstance(structure_index, bool)
            or not isinstance(structure_index, int | np.integer)
            or structure_index < 0
        ):
            raise ValueError('The source frame index must be a non-negative integer.')
        self.structure_index = None if structure_index is None else int(structure_index)
        self.coordinate_unit = 'nm'
        self.radii_unit = 'nm'
        self.coordinate_convention = 'nonperiodic_cartesian'
        self.coordinate_transform = 'identity'
        self.hydrogen_policy = hydrogen_policy
        self.radii_model = radii_model
        self._molecular_snapshot = None
        if molecular_system is not None:
            if structure_index is None:
                raise ValueError('Molecular snapshot requires its source frame index.')
            if msm.get(molecular_system, n_atoms=True, n_structures=True) != [
                n_atoms,
                1,
            ]:
                raise ValueError(
                    'Molecular snapshot must contain selected atoms and one frame.'
                )
            captured_coords = puw.get_value(
                msm.get(molecular_system, coordinates=True), to_unit='nm'
            )[0]
            if not np.array_equal(captured_coords, self._coordinates):
                raise ValueError(
                    'Molecular snapshot coordinates disagree with geometry.'
                )
            self._molecular_snapshot = msm.copy(molecular_system)
            # Supported native property; share owned bytes rather than retaining a
            # second coordinate buffer alongside the native geometry snapshot.
            self._molecular_snapshot.structures.coordinates = puw.quantity(
                self._coordinates[None], 'nm'
            )
        self._freeze_arrays()

    @property
    def coordinates(self) -> Any:
        """Return selected coordinates with protected numeric storage.

        Returns
        -------
        PyUnitWizard quantity
            (N, 3) selected coordinates in nm, with independent array metadata.
        """
        return puw.quantity(self._coordinates, 'nm')

    @property
    def radii(self) -> Any:
        """Return selected atomic radii with protected numeric storage.

        Returns
        -------
        PyUnitWizard quantity
            (N,) atomic radii in nm, with independent array metadata.
        """
        return puw.quantity(self._radii, 'nm')

    def recover_molecular_system(self) -> MolSys:
        """Return an independent selected MolSys containing the saved frame.

        Returns
        -------
        molsysmt.MolSys
            Editable copy with local atom indices 0..N-1. Use atom_indices to
            translate them to original source indices. Its frame index is 0.

        Raises
        ------
        ValueError
            If the input supplied arrays without molecular topology.

        Examples
        --------
        >>> from topomt.dfnd import synthetic, DelaunayFlowNetwork
        >>> network = DelaunayFlowNetwork(synthetic.tetrahedron().to_molsysmt())
        >>> restored = network.input_context.recover_molecular_system()
        >>> msm.get(restored, n_atoms=True, n_structures=True)
        [4, 1]
        """
        if self._molecular_snapshot is None:
            raise ValueError('This array input has no retained molecular topology.')
        return msm.copy(self._molecular_snapshot)

    def local_atom_indices(
        self, source_atom_indices: list[int], *, source_id: str
    ) -> list[int]:
        """Map source indices after verifying occurrence and selected membership.

        Parameters
        ----------
        source_atom_indices : list of int
            Original source atom indices, in requested order.
        source_id : str
            Input occurrence namespace for those indices.

        Returns
        -------
        list of int
            Corresponding local selected atom indices, preserving order.

        Raises
        ------
        ValueError
            If the namespace differs, an index is unselected, or indices are
            not a one-dimensional integer collection.

        Examples
        --------
        See the class example for explicit source-to-local translation.
        """
        if source_id != self.source_id:
            raise ValueError(
                'Atom mapping requires the same captured source occurrence.'
            )
        requested = np.asarray(source_atom_indices)
        if requested.ndim != 1 or (requested.size and requested.dtype.kind not in 'iu'):
            raise ValueError(
                'Source atom indices must be a one-dimensional integer collection.'
            )
        positions = {
            int(source): local for local, source in enumerate(self.atom_indices)
        }
        if any(int(index) not in positions for index in requested):
            raise ValueError('A source atom is outside the selected input.')
        return [positions[int(index)] for index in requested]
