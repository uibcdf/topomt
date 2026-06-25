from .Feature2D import Feature2D
import copy

class Cleft(Feature2D):
    """A deep open canyon -- the active-site cleft between two lobes. A leaf of
    ``open_concavity`` (occlusion <= 1), assigned when the depth (``buriedness``)
    clears a PROVISIONAL threshold; DFND sees the inter-lobe context only as depth,
    so a cleft is a deep open concavity (checked before the elongated ``groove``).
    Validate the threshold on real PDBs before treating it as canonical (S12). See
    feature_catalog.md.
    """

    def __init__(self, feature_id=None, atom_indices=None, atom_labels=None, atom_label_format=None, source=None,
                 source_id=None, topography=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type='cleft', atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Cleft':
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
