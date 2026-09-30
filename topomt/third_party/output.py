"""Provisional provider outputs with permanent access to reported pockets.

These records preserve provider definitions. They do not assert canonical DFND
classification or volumetric support. The private legacy bridge can be replaced
when adapters produce these records directly.
"""

import copy
from dataclasses import dataclass, field
from typing import Any, ClassVar, TypeVar

import numpy as np

from topomt._pyunitwizard import pyunitwizard as puw
from topomt.provider_output import ExternalMeasurement, ProviderRun


@dataclass(frozen=True)
class PocketGeometry:
    """An explicitly defined point or sphere representation in nanometers.

    Parameters
    ----------
    kind : str
        Representation name, such as ``alpha_spheres`` or ``lining_atoms``.
    points_nm : tuple of tuples of float
        Ordered point coordinates in nanometers.
    definition : str
        Provider-specific meaning of the points.
    radii_nm : tuple of float, optional
        Sphere radii in nanometers, in the same order as the points.

    Raises
    ------
    ValueError
        If geometry is nonfinite, has inconsistent shapes, or negative radii.

    Examples
    --------
    >>> geometry = PocketGeometry('sites', ((0., 0., 0.),), 'Reported site')
    >>> geometry.coordinates.shape
    (1, 3)
    """

    kind: str
    points_nm: tuple[tuple[float, float, float], ...]
    definition: str
    radii_nm: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        points = np.asarray(self.points_nm, dtype=float)
        if points.size == 0:
            points = points.reshape(0, 3)
        if not self.kind or not self.definition:
            raise ValueError('Geometry kind and definition are required')
        if points.ndim != 2 or points.shape[1] != 3 or not np.isfinite(points).all():
            raise ValueError('Geometry points must be finite with shape (N, 3)')
        object.__setattr__(self, 'points_nm', tuple(tuple(row) for row in points))
        if self.radii_nm is not None:
            radii = np.asarray(self.radii_nm, dtype=float)
            if (
                radii.shape != (len(points),)
                or not np.isfinite(radii).all()
                or np.any(radii < 0)
            ):
                raise ValueError(
                    'Geometry radii must be finite, nonnegative and match points'
                )
            object.__setattr__(self, 'radii_nm', tuple(radii))

    @property
    def coordinates(self) -> Any:
        """Return a separate length quantity with shape (N, 3)."""
        return puw.quantity(
            np.asarray(self.points_nm, dtype=float).reshape(-1, 3), 'nm'
        )

    @property
    def radii(self) -> Any | None:
        """Return separate sphere-radius quantities, or None for point geometry."""
        return (
            None
            if self.radii_nm is None
            else puw.quantity(np.asarray(self.radii_nm), 'nm')
        )


@dataclass(frozen=True)
class ProviderRecord:
    """Detached pocket or auxiliary record linked to an original provider run.

    Parameters
    ----------
    source_id : str
        Original source identifier; not a Topography registry identifier.
    record_kind : str
        ``pocket`` or ``mouth_aggregate`` for the initial adapters.
    run : ProviderRun
        Recoverable original inputs, outputs and execution metadata.
    atom_indices : tuple of int, optional
        Source molecular-system indices, or None if mapping is unavailable.
    atom_labels : tuple of str, optional
        Original atom labels when supplied by the provider.
    atom_role : str
        Meaning of membership: lining, residue membership or region vertices.
    parent_source_ids : tuple of str, optional
        Source-record parents, including CASTp aggregate-to-pocket links.
    _fields : dict, optional
        Provider-specific parsed fields, copied on construction and access.
    _geometries : tuple of PocketGeometry, optional
        Available representations. Absence does not mean computed empty geometry.

    Raises
    ------
    ValueError
        If source identity, geometry keys or measurement provenance conflict.

    Examples
    --------
    A consumer uses ``record.geometries['alpha_spheres'].coordinates`` and checks
    available keys before requesting a representation.
    """

    source_id: str
    record_kind: str
    run: ProviderRun
    atom_indices: tuple[int, ...] | None = None
    atom_labels: tuple[str, ...] | None = None
    atom_role: str = 'provider_membership'
    parent_source_ids: tuple[str, ...] = ()
    _fields: dict[str, Any] = field(default_factory=dict, repr=False)
    _geometries: tuple[PocketGeometry, ...] = field(default_factory=tuple, repr=False)

    def __post_init__(self) -> None:
        if (
            not self.source_id
            or not self.atom_role
            or self.record_kind not in {'pocket', 'mouth_aggregate'}
        ):
            raise ValueError(
                'Provider record requires source identity and a supported kind'
            )
        if len({geometry.kind for geometry in self._geometries}) != len(
            self._geometries
        ):
            raise ValueError('Duplicate geometry kind')
        fields = copy.deepcopy(self._fields)
        for measurement in fields.get('external_measurements', {}).values():
            if measurement.run_id != self.run.run_id:
                raise ValueError('Measurement belongs to a different provider run')
        object.__setattr__(self, '_fields', fields)
        object.__setattr__(self, '_geometries', tuple(self._geometries))
        object.__setattr__(self, 'parent_source_ids', tuple(self.parent_source_ids))
        if self.atom_indices is not None:
            indices = tuple(int(index) for index in self.atom_indices)
            if any(index < 0 for index in indices):
                raise ValueError('Source atom indices must be nonnegative')
            object.__setattr__(self, 'atom_indices', indices)
        if self.atom_labels is not None:
            object.__setattr__(self, 'atom_labels', tuple(self.atom_labels))

    @property
    def run_id(self) -> str:
        """Return the recoverable source-run identity."""
        return self.run.run_id

    @property
    def fields(self) -> dict[str, Any]:
        """Return independent copies of all parsed provider-specific fields."""
        return copy.deepcopy(self._fields)

    @property
    def measurements(self) -> dict[str, ExternalMeasurement]:
        """Return attributed measurements, retaining each original definition."""
        return copy.deepcopy(self._fields.get('external_measurements', {}))

    @property
    def geometries(self) -> dict[str, PocketGeometry]:
        """Return available representations, without inventing a closed region."""
        return {geometry.kind: geometry for geometry in self._geometries}


@dataclass(frozen=True)
class ProviderOutput:
    """Provider-specific result independent of a live Topography registry.

    Parameters
    ----------
    run : ProviderRun
        Immutable original evidence, including selection/frame metadata.
    records : tuple of ProviderRecord
        Ordered pocket and auxiliary records.
    input_points_nm : tuple of tuples of float, optional
        Snapshot of source-system coordinates at the selected frame. Exact
        submitted PDB bytes remain separately available in ``run``.

    Raises
    ------
    ValueError
        If records conflict with the provider/run or have dangling source links.

    Examples
    --------
    ``output.pockets`` is the shared consumer access. Save original evidence with
    ``output.run.save('original.zip')``; it is not a serialization of this output.
    """

    run: ProviderRun
    records: tuple[ProviderRecord, ...]
    input_points_nm: tuple[tuple[float, float, float], ...] | None = field(
        default=None, repr=False
    )
    provider: ClassVar[str] = ''
    schema_version: ClassVar[int] = 1

    def __post_init__(self) -> None:
        records = tuple(self.records)
        if self.run.provider != self.provider:
            raise ValueError('Provider output and original run disagree')
        identifiers = {record.source_id for record in records}
        if len(identifiers) != len(records):
            raise ValueError('Duplicate provider source identifier')
        for record in records:
            if record.run != self.run:
                raise ValueError('Record belongs to another provider run')
            if not set(record.parent_source_ids) <= identifiers:
                raise ValueError('Dangling source-record parent')
        object.__setattr__(self, 'records', records)
        if self.input_points_nm is not None:
            geometry = PocketGeometry(
                'source_atoms', self.input_points_nm, 'Source-frame snapshot'
            )
            object.__setattr__(self, 'input_points_nm', geometry.points_nm)

    @property
    def pockets(self) -> tuple[ProviderRecord, ...]:
        """Return every provider-reported pocket, including CASTp closed cavities."""
        return tuple(
            record for record in self.records if record.record_kind == 'pocket'
        )

    @property
    def input_coordinates(self) -> Any | None:
        """Return a separate source-frame length quantity, or unavailable None."""
        if self.input_points_nm is None:
            return None
        return puw.quantity(np.asarray(self.input_points_nm).reshape(-1, 3), 'nm')


def _length_values(value: Any, *, bare_unit: str | None = None) -> np.ndarray:
    if puw.is_quantity(value):
        return np.asarray(puw.get_value(value, to_unit='nm'), dtype=float)
    if bare_unit is None:
        raise ValueError('Provider geometry requires an explicit length unit')
    return np.asarray(
        puw.get_value(puw.quantity(value, bare_unit), to_unit='nm'), dtype=float
    )


_Output = TypeVar('_Output', bound=ProviderOutput)


def _from_topography(
    topography: Any,
    output_type: type[_Output],
    *,
    source_molecular_system: Any = None,
    source_structure_indices: int | list[int] = 0,
    atom_index_map: tuple[int, ...] | None = None,
) -> _Output:
    """Detach existing adapter fields without treating legacy types as evidence."""
    runs = tuple(topography.provider_runs.values())
    if len(runs) != 1:
        raise ValueError(
            'Provider output requires exactly one recoverable original run'
        )
    run = runs[0]
    source_coordinates = None
    source = (
        topography.molecular_system
        if source_molecular_system is None
        else source_molecular_system
    )
    frames = (
        topography.structure_indices
        if source_molecular_system is None
        else source_structure_indices
    )
    if source is not None:
        import molsysmt as msm

        coordinates = msm.get(
            source,
            coordinates=True,
            structure_indices=frames,
        )
        coordinates = _length_values(coordinates)
        if coordinates.ndim != 3 or coordinates.shape[0] != 1:
            raise ValueError('Provider output requires one source coordinate frame')
        source_coordinates = coordinates[0]
    records = []
    for feature in topography.values():
        if getattr(feature, 'provider_run_id', None) != run.run_id:
            raise ValueError('Feature has no matching recoverable provider run')
        record_kind = 'mouth_aggregate' if feature.feature_type == 'mouth' else 'pocket'
        fields = {
            name: value
            for name, value in vars(feature).items()
            if not name.startswith('_')
        }
        fields['legacy_feature_type'] = feature.feature_type
        indices = None if feature.atom_indices is None else tuple(feature.atom_indices)
        if indices is not None and atom_index_map is not None:
            if any(index < 0 or index >= len(atom_index_map) for index in indices):
                raise ValueError(
                    'Provider atom mapping falls outside the submitted selection'
                )
            fields['submitted_atom_indices'] = indices
            indices = tuple(atom_index_map[index] for index in indices)
        atom_role = {
            'pocketeer': 'pocket_residue_atoms',
            'pycasta': 'region_tetrahedron_vertices',
        }.get(run.provider, 'provider_lining_atoms')
        geometries = []
        if source_coordinates is not None and indices is not None:
            if any(index < 0 or index >= len(source_coordinates) for index in indices):
                raise ValueError('Provider atom mapping falls outside the source frame')
            points = source_coordinates[np.asarray(indices, dtype=int)]
            geometries.append(
                PocketGeometry(
                    'member_atoms',
                    tuple(map(tuple, points)),
                    f'{atom_role} mapped on source-frame coordinates',
                )
            )
            if (
                run.provider == 'pocketeer'
                and 'alpha_sphere_defining_atom_indices' in fields
            ):
                defining = np.unique(
                    np.asarray(
                        fields['alpha_sphere_defining_atom_indices'], dtype=int
                    ).reshape(-1)
                )
                if np.any(defining < 0) or np.any(defining >= len(source_coordinates)):
                    raise ValueError(
                        'Sphere-defining atom mapping falls outside the source frame'
                    )
                geometries.append(
                    PocketGeometry(
                        'lining_atoms',
                        tuple(map(tuple, source_coordinates[defining])),
                        'Union of Pocketeer sphere-defining atoms on source-frame coordinates',
                    )
                )
        for kind, center_field, radius_field, definition in (
            (
                'alpha_spheres',
                'alpha_sphere_centers',
                'alpha_sphere_radii',
                'Provider alpha sites/spheres; not a closed region or occupied volume',
            ),
            ('beta_sites', 'beta_centers', None, 'AlphaSpace2 beta-site positions'),
        ):
            centers = fields.get(center_field)
            if centers is None:
                continue
            bare_unit = 'angstroms' if run.provider == 'fpocket' else None
            points = _length_values(centers, bare_unit=bare_unit)
            if points.size == 0:
                points = points.reshape(0, 3)
            radii = fields.get(radius_field) if radius_field is not None else None
            radii_nm = (
                None
                if radii is None
                else tuple(_length_values(radii, bare_unit=bare_unit))
            )
            geometries.append(
                PocketGeometry(kind, tuple(map(tuple, points)), definition, radii_nm)
            )
        parents = tuple(
            sorted(
                parent.source_id for parent in topography.parents_of(feature.feature_id)
            )
        )
        records.append(
            ProviderRecord(
                source_id=feature.source_id,
                record_kind=record_kind,
                run=run,
                atom_indices=indices,
                atom_labels=None
                if feature.atom_labels is None
                else tuple(feature.atom_labels),
                atom_role=atom_role,
                parent_source_ids=parents,
                _fields=fields,
                _geometries=tuple(geometries),
            )
        )
    points_nm = (
        None if source_coordinates is None else tuple(map(tuple, source_coordinates))
    )
    return output_type(run=run, records=tuple(records), input_points_nm=points_nm)
