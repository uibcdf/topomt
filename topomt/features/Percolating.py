from .Feature2D import Feature2D
import copy


class Percolating(Feature2D):
    """A fully solvent-permeable (wall-less) resident region: shape_type ``neutral``.

    Neither concave nor convex nor mixed -- a porous/exposed wet region whose
    boundary has zero walls (every boundary face permeable). See
    ``devguide/DFND/object_model.md`` and ``feature_definitions.md``.
    """

    def __init__(self, feature_id=None, atom_indices=None, boundaries=None, points=None,
                 atom_labels=None, atom_label_format=None, source=None, source_id=None, topography=None, **kwargs):
        super().__init__(feature_id=feature_id, feature_type='percolating', atom_indices=atom_indices,
                         boundaries=boundaries, points=points, atom_labels=atom_labels,
                         atom_label_format=atom_label_format, source=source, source_id=source_id, topography=topography)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def copy(self, deep: bool = True) -> 'Percolating':
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __copy__(self):
        return super().__copy__()

    def __deepcopy__(self, memo):
        return super().__deepcopy__(memo)
