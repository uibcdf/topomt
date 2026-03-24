from .BaseFeature import BaseFeature
import copy

class Feature2D(BaseFeature):

    def __init__(self, feature_id=None, feature_type='feature_2d', atom_indices=None,
                 atom_labels=None, atom_label_format=None, topography=None, source=None, source_id=None,
                 boundaries=None, points=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        self.boundaries = set() if boundaries is None else set(boundaries)
        self.points = set() if points is None else set(points)

        self.solvent_accessible_area = None
        self.solvent_accessible_volume = None
        self.molecular_surface_area = None
        self.molecular_surface_volume = None
        self.length = None
        self.corner_points_count = None

        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Feature2D':
        """Return a copy of the Topography object.

        Parameters
        ----------
        deep : bool, optional
            If True (default), perform a deep copy of all internal
            data structures. If False, only a shallow copy is made.
        """
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __copy__(self):

        new_feature = super().__copy__()
        new_feature.boundaries = copy.copy(self.boundaries)
        new_feature.points = copy.copy(self.points)
        new_feature.solvent_accessible_area = copy.copy(self.solvent_accessible_area)
        new_feature.solvent_accessible_volume = copy.copy(self.solvent_accessible_volume)
        new_feature.molecular_surface_area = copy.copy(self.molecular_surface_area)
        new_feature.molecular_surface_volume = copy.copy(self.molecular_surface_volume)
        new_feature.length = copy.copy(self.length)
        new_feature.corner_points_count = copy.copy(self.corner_points_count)
        return new_feature

    def __deepcopy__(self, memo):

        new_feature = super().__deepcopy__(memo)
        new_feature.boundaries = copy.deepcopy(self.boundaries, memo)
        new_feature.points = copy.deepcopy(self.points, memo)
        new_feature.solvent_accessible_area = copy.deepcopy(self.solvent_accessible_area, memo)
        new_feature.solvent_accessible_volume = copy.deepcopy(self.solvent_accessible_volume, memo)
        new_feature.molecular_surface_area = copy.deepcopy(self.molecular_surface_area, memo)
        new_feature.molecular_surface_volume = copy.deepcopy(self.molecular_surface_volume, memo)
        new_feature.length = copy.deepcopy(self.length, memo)
        new_feature.corner_points_count = copy.deepcopy(self.corner_points_count, memo)
        return new_feature

    def add_connected_boundary(self, feature_or_id: 'BaseFeature | str'):

        if self._topography is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected boundary.')

        self._topography.connect_features(feature_or_id, self.feature_id)

    def add_connected_point(self, feature_or_id: 'BaseFeature | str'):

        if self._topography is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected boundary.')

        self._topography.connect_features(feature_or_id, self.feature_id)

    def _add_boundary_id(self, boundary_id: str):

        self.boundaries.add(boundary_id)

    def _add_point_id(self, point_id: str):

        self.points.add(point_id)
