from .Feature2D import Feature2D
import copy

class Groove(Feature2D):
    """An elongated open concavity with a defined long axis -- a surface furrow. The
    first refined leaf of ``open_concavity`` (occlusion <= 1), assigned when the shape
    elongation clears a PROVISIONAL threshold (the elongation debt, decision S12;
    validate on real PDBs before treating it as canonical). See feature_catalog.md.
    """

    def __init__(self, feature_id=None, atom_indices=None, atom_labels=None, atom_label_format=None, source=None,
                 source_id=None, topography=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type='groove', atom_indices=atom_indices,
                         atom_labels=atom_labels, atom_label_format=atom_label_format, source=source, source_id=source_id,
                         topography=topography)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Groove':
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
