from .Feature2D import Feature2D
import copy

class OpenConcavity(Feature2D):
    """The generic 1-mouth open concavity (occlusion <= 1): an open surface concavity
    the catalog cannot yet refine to a leaf (groove / dish / funnel) for want of the
    shape metric. The community name ``pocket`` is reserved for the occluded case
    (occlusion > 1). See devguide/DFND/feature_catalog.md.
    """

    def __init__(self, feature_id=None, atom_indices=None, atom_labels=None, atom_label_format=None, source=None,
                 source_id=None, topography=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type='open_concavity', atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'OpenConcavity':
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
        return new_feature

    def __deepcopy__(self, memo):

        new_feature = super().__deepcopy__(memo)
        return new_feature
