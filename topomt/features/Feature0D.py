from .BaseFeature import BaseFeature
import copy

class Feature0D(BaseFeature):

    def __init__(self, feature_id=None, feature_type='feature_0d', atom_indices=None,
                 atom_labels=None, atom_label_format=None, source=None, source_id=None, topography=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type=feature_type, atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        self.surfaces = set()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Feature0D':
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
        return new_feature

    def __deepcopy__(self, memo):

        new_feature = super().__deepcopy__(memo)
        new_feature.surfaces = copy.deepcopy(self.surfaces, memo)
        return new_feature

    def add_connected_surface(self, feature_or_id: 'BaseFeature | str'):

        if self._topography is None:
            raise ValueError('Topography is not set for this feature. Cannot add connected surface.')

        self._topography.connect_features(self.feature_id, feature_or_id)

    def _add_surface_id(self, surface_id: str):

        self.surfaces.add(surface_id)
