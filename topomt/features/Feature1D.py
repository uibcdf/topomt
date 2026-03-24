from .BaseFeature import BaseFeature
import copy

class Feature1D(BaseFeature):

    def __init__(self, feature_id=None, feature_type='feature1D', atom_indices=None,
                 atom_labels=None, atom_label_format=None, source=None, source_id=None, topography=None,
                 surfaces=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        self.surfaces = set() if surfaces is None else set(surfaces)

        self.solvent_accessible_area = None
        self.solvent_accessible_length = None
        self.molecular_surface_area = None
        self.molecular_surface_length = None
        self.n_triangles = None

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Feature1D':
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
        new_feature.surfaces = copy.copy(self.surfaces)
        new_feature.solvent_accessible_area = copy.copy(self.solvent_accessible_area)
        new_feature.solvent_accessible_length = copy.copy(self.solvent_accessible_length)
        new_feature.molecular_surface_area = copy.copy(self.molecular_surface_area)
        new_feature.molecular_surface_length = copy.copy(self.molecular_surface_length)
        new_feature.n_triangles = copy.copy(self.n_triangles)
        return new_feature

    def __deepcopy__(self, memo):

        new_feature = super().__deepcopy__(memo)
        new_feature.surfaces = copy.deepcopy(self.surfaces, memo)
        new_feature.solvent_accessible_area = copy.deepcopy(self.solvent_accessible_area, memo)
        new_feature.solvent_accessible_length = copy.deepcopy(self.solvent_accessible_length, memo)
        new_feature.molecular_surface_area = copy.deepcopy(self.molecular_surface_area, memo)
        new_feature.molecular_surface_length = copy.deepcopy(self.molecular_surface_length, memo)
        new_feature.n_triangles = copy.deepcopy(self.n_triangles, memo)
        return new_feature

    def add_connected_surface(self, feature_or_id: 'BaseFeature | str'):

        if self._topography is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected surface.')

        self._topography.connect_features(self.feature_id, feature_or_id)

    def _add_surface_id(self, surface_id: str):

        self.surfaces.add(surface_id)
