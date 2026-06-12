from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Literal

from topomt._private.atom_label import parse_list_of_atom_labels
from topomt.config import atom_label_format as default_atom_label_format

from ._feature_constants import (
    _DIMENSIONALITY_BY_FEATURE_TYPE,
    _FEATURE_TYPE_TO_CLASS_NAME,
    _SHAPE_TYPE_BY_FEATURE_TYPE,
)

FeatureID = str
FeatureIndex = int
FeatureType = str
ShapeType = Literal['concavity', 'convexity', 'mixed', 'boundary', 'point']
Dimensionality = Literal[0, 1, 2, None]

if TYPE_CHECKING:
    from topomt.topography import Topography


class BaseFeature:
    def __init__(
        self,
        feature_id=None,
        feature_type=None,
        atom_indices=None,
        atom_labels=None,
        atom_label_format=None,
        feature_label=None,
        source=None,
        source_id=None,
        topography=None,
    ):
        """
        atom_indices : sequence of int, optional
        For topographic features, these indices are expected to identify the
        atoms that geometrically delimit the feature, i.e. lining or
        tangential/osculating atoms of the receptor.

        atom_label_format : str, optional
        Format string for atom labels, e.g. `"{atom_name}-{atom_id}"`.
        """

        if atom_label_format is None:
            atom_label_format = default_atom_label_format

        self._feature_id = feature_id
        self.feature_type = feature_type
        self.feature_label = feature_label
        self.source = source
        self.source_id = source_id
        self.atom_indices = atom_indices
        self.atom_labels = atom_labels
        self.atom_label_format = atom_label_format
        self.shape_type = None
        self.dimensionality = None
        self._topography = None

        if self.feature_type is not None:
            self._set_shape_type()
            self._set_dimensionality()

        if topography is not None:
            self._topography = topography
            feature_id = self._topography.add_feature(self)

        if source is None:
            self.source = 'TopoMT'
            self.source_id = self.feature_id

        if (
            (self.atom_indices is None)
            and (self.atom_labels is not None)
            and (self._topography is not None)
        ):
            self.atom_indices = self._get_atom_indices_from_atom_labels()

    def __repr__(self):
        class_name = _FEATURE_TYPE_TO_CLASS_NAME.get(self.feature_type)
        return f'<TopoMT {class_name} with feature_id={self.feature_id}>'

    def copy(self, deep: bool = True) -> BaseFeature:
        """Return a copy of the Topography object.

        Parameters
        ----------
        deep : bool, optional
            If True (default), perform a deep copy of all internal
            data structures. If False, only a shallow copy is made.
        """
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __copy__(self):

        new_feature = self.__class__.__new__(self.__class__)
        for k, v in self.__dict__.items():
            if k == '_topography':
                new_feature._topography = None
            else:
                setattr(new_feature, k, copy.copy(v))
        return new_feature

    def __deepcopy__(self, memo):

        new_feature = self.__class__.__new__(self.__class__)
        memo[id(self)] = new_feature
        for k, v in self.__dict__.items():
            if k == '_topography':
                new_feature._topography = None
            else:
                setattr(new_feature, k, copy.deepcopy(v, memo))
        return new_feature

    def info(self):
        return {
            'feature_id': self.feature_id,
            'feature_type': self.feature_type,
            'shape_type': self.shape_type,
        }

    @property
    def feature_id(self):
        return self._feature_id

    @feature_id.setter
    def feature_id(self, value):
        if self._topography is not None and value != self._feature_id:
            raise AttributeError(
                'feature_id is immutable while registered; use Topography.rename_feature().'
            )
        self._feature_id = value

    def _set_registered_feature_id(self, value: str) -> None:
        self._feature_id = value

    @property
    def id(self):
        return self.feature_id

    @id.setter
    def id(self, value):
        self.feature_id = value

    @property
    def topography(self) -> Topography | None:
        return self._topography

    @property
    def molecular_system(self) -> Any | None:
        if self._topography is None:
            return None
        return self._topography.molecular_system

    def _set_dimensionality(self):

        if self.feature_type is None:
            self.dimensionality = None
            return

        self.dimensionality = _DIMENSIONALITY_BY_FEATURE_TYPE[self.feature_type]

    def _set_shape_type(self):

        if self.feature_type is None:
            self.shape_type = None
            return

        self.shape_type = _SHAPE_TYPE_BY_FEATURE_TYPE[self.feature_type]

    def _get_atom_indices_from_atom_labels(self):

        if self._topography is None:
            raise ValueError('Topography is not set for this feature.')

        dict_of_lists = parse_list_of_atom_labels(
            self.atom_labels, self.atom_label_format, output_type='dict of lists'
        )
        if 'atom_id' in dict_of_lists:
            dict_of_lists['atom_id'] = [int(x) for x in dict_of_lists['atom_id']]
        if 'group_id' in dict_of_lists:
            dict_of_lists['group_id'] = [int(x) for x in dict_of_lists['group_id']]
        atom_indices = self._topography._molsys.topology.get_atom_indices(
            **dict_of_lists
        )

        return atom_indices
