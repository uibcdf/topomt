from __future__ import annotations

import copy
from collections.abc import Iterator, Mapping
from typing import Any

import molsysmt as msm

from topomt.features import _FEATURE_PREFIXES, _FEATURE_TYPE_REGISTRY

from ..features.BaseFeature import (
    BaseFeature,
    FeatureID,
    FeatureType,
    ShapeType,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class Topography(Mapping[str, BaseFeature]):
    """
    Central registry of all features.

    Public API uses *feature_id*.
    Internal storage and relations use *feature_index* for efficiency.
    """

    def __init__(
        self,
        molecular_system: Any | None = None,
        selection: Any = 'all',
        structure_indices: int = 0,
        features: list[BaseFeature] | None = None,
    ) -> None:
        # main store: id → feature
        self._features: dict[FeatureID, BaseFeature] = {}

        # derived indexes
        self._by_dimensionality: dict[int, set[FeatureID]] = {
            0: set(),
            1: set(),
            2: set(),
        }
        self._by_shape: dict[ShapeType, set[FeatureID]] = {
            'concavity': set(),
            'convexity': set(),
            'mixed': set(),
            'boundary': set(),
            'point': set(),
        }
        self._by_type: dict[FeatureType, set[FeatureID]] = {}

        # parent/child relations (by id)
        self._children_of: dict[FeatureID, set[FeatureID]] = {}
        self._parents_of: dict[FeatureID, set[FeatureID]] = {}

        # molecular system references
        self._molecular_system: Any | None = None
        self._molsys: Any | None = None
        self.selection = selection
        self.structure_indices = structure_indices

        if molecular_system is not None:
            self._molecular_system = molecular_system
            self._molsys = msm.convert(
                molecular_system,
                selection=selection,
                structure_indices=structure_indices,
                to_form='molsysmt.MolSys',
            )

        if features is not None:
            for feature in features:
                self.add_feature(feature)

    # -----------------
    # Mapping interface
    # -----------------

    def __repr__(self) -> str:
        parts = ', '.join(f'{ftype}={len(ids)}' for ftype, ids in self._by_type.items())
        return f'<TopoMT Topography total={len(self)} {parts}>'

    def __getitem__(self, feature_id: FeatureID) -> BaseFeature:
        """Allow: topo["Pock001"] → feature with feature_id == "Pock001"."""
        return self._features[feature_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._features)

    def __len__(self) -> int:
        return len(self._features)

    def copy(self, deep: bool = True) -> Topography:
        """Return a semantic copy preserving all analysis state."""
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __copy__(self):
        new_topography = type(self).__new__(type(self))
        for name, value in self.__dict__.items():
            if name == '_features':
                continue
            setattr(new_topography, name, copy.copy(value))
        new_topography._features = {}
        for feature_id, feature in self._features.items():
            new_feature = feature.copy(deep=False)
            new_feature._topography = new_topography
            new_topography._features[feature_id] = new_feature
        return new_topography

    def __deepcopy__(self, memo):
        new_topography = type(self).__new__(type(self))
        memo[id(self)] = new_topography
        for name, value in self.__dict__.items():
            setattr(new_topography, name, copy.deepcopy(value, memo))
        for feature in new_topography._features.values():
            feature._topography = new_topography
        return new_topography

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # internal helpers
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @property
    def features(self) -> dict[FeatureID, BaseFeature]:
        return self._features

    @property
    def molecular_system(self) -> Any | None:
        return self._molecular_system

    @molecular_system.setter
    def molecular_system(self, value: Any | None) -> None:
        if value is None:
            self._molecular_system = None
            self._molsys = None
        else:
            self._molecular_system = value
            self._molsys = msm.convert(value, to_form='molsysmt.MolSys')

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: add_feature and add_new_feature
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    @staticmethod
    def _validate_feature_id(feature_id: FeatureID) -> None:
        if not isinstance(feature_id, str):
            raise TypeError('feature_id must be a string')
        if not feature_id:
            raise ValueError('feature_id must not be empty')

    def _validate_new_feature(
        self, feature: BaseFeature, *, allowed_id: FeatureID | None = None
    ) -> None:
        if not isinstance(feature, BaseFeature):
            raise TypeError('feature must be a BaseFeature')
        if feature._topography is not None and feature._topography is not self:
            raise ValueError('Feature belongs to a different Topography.')
        if feature.feature_id is not None:
            self._validate_feature_id(feature.feature_id)
            if (
                feature.feature_id in self._features
                and feature.feature_id != allowed_id
            ):
                raise ValueError(
                    f"Feature ID '{feature.feature_id}' is already registered."
                )
        if feature.feature_type is None:
            raise ValueError('feature_type must be defined')

    def _add_to_indexes(self, feature: BaseFeature) -> None:
        self._by_dimensionality.setdefault(feature.dimensionality, set()).add(
            feature.feature_id
        )
        self._by_shape.setdefault(feature.shape_type, set()).add(feature.feature_id)
        self._by_type.setdefault(feature.feature_type, set()).add(feature.feature_id)

    def _remove_from_indexes(self, feature: BaseFeature) -> None:
        self._by_dimensionality.get(feature.dimensionality, set()).discard(
            feature.feature_id
        )
        self._by_shape.get(feature.shape_type, set()).discard(feature.feature_id)
        self._by_type.get(feature.feature_type, set()).discard(feature.feature_id)

    def add_feature(self, feature: BaseFeature) -> FeatureID | None:
        """Atomically add a feature and update all derived indexes."""
        if (
            isinstance(feature, BaseFeature)
            and feature.feature_id in self._features
            and self._features[feature.feature_id] is feature
        ):
            return None
        self._validate_new_feature(feature)
        generated_id = feature.feature_id is None
        feature_id = (
            self._make_next_feature_id(feature.feature_type)
            if generated_id
            else feature.feature_id
        )
        self._validate_feature_id(feature_id)
        if feature_id in self._features:
            raise ValueError(f"Feature ID '{feature_id}' is already registered.")

        atom_indices = feature.atom_indices
        if (
            self._molsys is not None
            and feature.atom_labels is not None
            and atom_indices is None
        ):
            previous_topography = feature._topography
            feature._topography = self
            try:
                atom_indices = feature._get_atom_indices_from_atom_labels()
            finally:
                feature._topography = previous_topography

        feature._set_registered_feature_id(feature_id)
        feature.atom_indices = atom_indices
        feature._topography = self
        self._features[feature_id] = feature
        self._add_to_indexes(feature)
        self._children_of[feature_id] = set()
        self._parents_of[feature_id] = set()
        return feature_id if generated_id else None

    def replace_feature(
        self, feature_id: FeatureID, feature: BaseFeature
    ) -> BaseFeature:
        """Atomically replace a feature while preserving compatible relations."""
        self._validate_feature_id(feature_id)
        if feature_id not in self._features:
            raise KeyError(feature_id)
        self._validate_new_feature(feature, allowed_id=feature_id)
        if feature.feature_id != feature_id:
            raise ValueError('Replacement feature_id must match the registered ID.')
        previous = self._features[feature_id]
        if feature is previous:
            return previous
        for child_id in self._children_of[feature_id]:
            _validate_child_parent_compat(self._features[child_id], feature)
        for parent_id in self._parents_of[feature_id]:
            _validate_child_parent_compat(feature, self._features[parent_id])
        self._remove_from_indexes(previous)
        self._features[feature_id] = feature
        feature._topography = self
        self._add_to_indexes(feature)
        previous._topography = None
        self._sync_feature_relation_sets()
        return previous

    def rename_feature(self, feature_id: FeatureID, new_feature_id: FeatureID) -> None:
        """Atomically rename a feature and all registry-owned relations."""
        self._validate_feature_id(feature_id)
        self._validate_feature_id(new_feature_id)
        if feature_id not in self._features:
            raise KeyError(feature_id)
        if new_feature_id in self._features:
            raise ValueError(f"Feature ID '{new_feature_id}' is already registered.")
        if feature_id == new_feature_id:
            return
        feature = self._features[feature_id]
        self._features = {
            (new_feature_id if key == feature_id else key): value
            for key, value in self._features.items()
        }
        for ids in (
            *self._by_dimensionality.values(),
            *self._by_shape.values(),
            *self._by_type.values(),
        ):
            if feature_id in ids:
                ids.remove(feature_id)
                ids.add(new_feature_id)
        self._children_of = self._renamed_relation_map(
            self._children_of, feature_id, new_feature_id
        )
        self._parents_of = self._renamed_relation_map(
            self._parents_of, feature_id, new_feature_id
        )
        feature._set_registered_feature_id(new_feature_id)
        self._sync_feature_relation_sets()

    def remove_feature(self, feature_id: FeatureID) -> BaseFeature:
        """Atomically remove a feature and all registry-owned relations."""
        self._validate_feature_id(feature_id)
        if feature_id not in self._features:
            raise KeyError(feature_id)
        feature = self._features.pop(feature_id)
        self._remove_from_indexes(feature)
        self._children_of.pop(feature_id, None)
        self._parents_of.pop(feature_id, None)
        for ids in self._children_of.values():
            ids.discard(feature_id)
        for ids in self._parents_of.values():
            ids.discard(feature_id)
        feature._topography = None
        self._sync_feature_relation_sets()
        return feature

    @staticmethod
    def _renamed_relation_map(relations, old_id, new_id):
        return {
            (new_id if key == old_id else key): {
                new_id if value == old_id else value for value in values
            }
            for key, values in relations.items()
        }

    def _sync_feature_relation_sets(self) -> None:
        for feature in self._features.values():
            if hasattr(feature, 'surfaces'):
                feature.surfaces = set()
            if hasattr(feature, 'boundaries'):
                feature.boundaries = set()
            if hasattr(feature, 'points'):
                feature.points = set()
        for parent_id, child_ids in self._children_of.items():
            parent = self._features[parent_id]
            for child_id in child_ids:
                child = self._features[child_id]
                child._add_surface_id(parent_id)
                if child.dimensionality == 0:
                    parent._add_point_id(child_id)
                elif child.dimensionality == 1:
                    parent._add_boundary_id(child_id)

    def add_new_feature(
        self,
        feature_type: str,
        feature_id: FeatureID | None = None,
        atom_indices: list[int] | None = None,
        atom_labels: list[str] | None = None,
        atom_label_format: str | None = None,
        **kwargs,
    ) -> FeatureType | None:
        """Create a feature of the given type and add it to the topography.

        Parameters
        ----------
        feature_type : str
            Name of the feature type, e.g. "Pocket", "Void", "Mouth".
        atom_indices : list[int], optional
            Atom indices associated to this feature, if relevant.
        **kwargs
            Extra arguments specific to the concrete feature class.

        Returns
        -------
        BaseFeature
            The created feature instance.
        """
        feature_class = _FEATURE_TYPE_REGISTRY.get(feature_type.lower())
        if feature_class is None:
            raise ValueError(f'Unknown feature_type {feature_type!r}')

        new_feature_id = False
        if feature_id is None:
            feature_id = self._make_next_feature_id(feature_type)
            new_feature_id = True

        new_feature = feature_class(
            feature_id=feature_id,
            atom_indices=atom_indices,
            atom_labels=atom_labels,
            atom_label_format=atom_label_format,
            **kwargs,
        )

        self.add_feature(new_feature)

        if new_feature_id:
            return feature_id
        else:
            return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: connect_features
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def connect_features(
        self,
        child_feature_or_id: FeatureID | BaseFeature,
        parent_feature_or_id: FeatureID | BaseFeature,
    ) -> None:
        """Atomically connect a child feature to a parent feature."""
        if not isinstance(child_feature_or_id, (str, BaseFeature)):
            raise TypeError('child_feature_or_id must be a feature ID or BaseFeature')
        if not isinstance(parent_feature_or_id, (str, BaseFeature)):
            raise TypeError('parent_feature_or_id must be a feature ID or BaseFeature')

        child, child_needs_add = self._resolve_feature_for_connection(
            child_feature_or_id, 'Child'
        )
        parent, parent_needs_add = self._resolve_feature_for_connection(
            parent_feature_or_id, 'Parent'
        )
        _validate_child_parent_compat(child, parent)

        added_ids = []
        try:
            if child_needs_add:
                self.add_feature(child)
                added_ids.append(child.feature_id)
            if parent_needs_add:
                self.add_feature(parent)
                added_ids.append(parent.feature_id)
        except Exception:
            for added_id in reversed(added_ids):
                self.remove_feature(added_id)
            raise

        child_id = child.feature_id
        parent_id = parent.feature_id
        self._children_of[parent_id].add(child_id)
        self._parents_of[child_id].add(parent_id)
        self._sync_feature_relation_sets()

    def _resolve_feature_for_connection(self, value, role):
        if isinstance(value, str):
            if value not in self._features:
                raise ValueError(
                    f"{role} feature with id '{value}' is not in the topography."
                )
            return self._features[value], False
        self._validate_new_feature(
            value,
            allowed_id=value.feature_id if value.feature_id in self._features else None,
        )
        if value.feature_id in self._features:
            if self._features[value.feature_id] is not value:
                raise ValueError(
                    f"Feature ID '{value.feature_id}' is already registered."
                )
            return value, False
        return value, True

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: lookups
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def get_features(
        self,
        *,
        by: str | None = None,
        value: str | int | list | tuple | set | None = None,
        grouped_by: str | None = None,
        as_feature_ids: bool = False,
    ):
        """Devuelve features filtradas y opcionalmente agrupadas.

        Parameters
        ----------
        by : {"id", "type", "shape", "dimensionality", None}
            Criterio de filtrado. Si es None, se consideran todas.
        value : any
            Valor del criterio. Para "id" puede ser str o iterable de str.
        grouped_by : {"type", "shape", "dimensionality", None}
            Si se indica, la salida es un dict agrupado por ese criterio.
        as_feature_ids : bool
            Si True, se devuelven ids; si False, objetos.
        """
        # 1) obtener el conjunto inicial de ids
        if by is None:
            feature_ids = set(self._features.keys())

        elif by == 'type':
            feature_ids = set(self._by_type.get(value, ()))

        elif by == 'shape':
            feature_ids = set(self._by_shape.get(value, ()))

        elif by == 'dimensionality':
            feature_ids = set(self._by_dimensionality.get(value, ()))

        elif by == 'id':
            # value puede ser un id o un iterable de ids
            feature_ids = set()
            if isinstance(value, str):
                if value in self._features:
                    feature_ids.add(value)
            elif isinstance(value, (list, tuple, set)):
                for fid in value:
                    if fid in self._features:
                        feature_ids.add(fid)
            else:
                # nada válido
                feature_ids = set()
        else:
            raise ValueError(f"Unknown 'by' criterion: {by!r}")

        # 2) si no hay agrupamiento, devolvemos lista plana
        if grouped_by is None:
            if as_feature_ids:
                return feature_ids
            else:
                return set([self._features[fid] for fid in feature_ids])

        # 3) salida agrupada
        out: dict[str | int, list] = {}
        for fid in feature_ids:
            feat = self._features[fid]
            if grouped_by == 'type':
                key = feat.feature_type
            elif grouped_by == 'shape':
                key = feat.shape_type
            elif grouped_by == 'dimensionality':
                key = feat.dimensionality
            else:
                raise ValueError(f"Unknown 'grouped_by' criterion: {grouped_by!r}")

            out.setdefault(key, set())
            out[key].add(fid if as_feature_ids else feat)

        return out

    def get_feature_by_id(self, feature_id: FeatureID) -> BaseFeature:
        if feature_id not in self._features:
            raise ValueError(
                f"Feature with id '{feature_id}' is not in the topography."
            )
        else:
            return self._features[feature_id]

    def children_of(
        self, feature_id: FeatureID, as_feature_ids=False
    ) -> set[BaseFeature] | set[FeatureID]:
        if as_feature_ids:
            return self._children_of[feature_id]
        else:
            return set([self._features[fid] for fid in self._children_of[feature_id]])

    def parents_of(
        self, feature_id: FeatureID, as_feature_ids=False
    ) -> set[BaseFeature] | set[FeatureID]:
        if as_feature_ids:
            return self._parents_of[feature_id]
        else:
            return set([self._features[fid] for fid in self._parents_of[feature_id]])

    def info(self) -> dict[str, dict[str, int]]:
        return {
            'by_type': {ftype: len(ids) for ftype, ids in self._by_type.items()},
            'by_shape': {shape: len(ids) for shape, ids in self._by_shape.items()},
            'by_dimensionality': {
                dim: len(ids) for dim, ids in self._by_dimensionality.items()
            },
            'total': len(self._features),
        }

    def to_records(self) -> list[dict[str, object]]:
        records = []
        for fid, feat in self._features.items():
            records.append(
                {
                    'id': fid,
                    'type': feat.feature_type,
                    'shape': feat.shape_type,
                    'dim': feat.dimensionality,
                }
            )
        return records

    def show(self, **kwargs):
        """
        Visualize the topography using molsysmt.view.
        """
        from molsysmt import view as msm_view

        view = msm_view(self._molecular_system, standard=True, **kwargs)

        for fid, feature in self._features.items():
            if feature.feature_type == 'pocket':
                if feature.atom_indices is not None:
                    sel = '@' + ','.join(map(str, feature.atom_indices))
                    # Assign a color per pocket or a default one
                    view.add_surface(sel, opacity='0.3', color='red')

        return view

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # auxiliary functions
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def _make_next_feature_id(self, feature_type: FeatureType) -> FeatureID:
        """
        Generate the next default feature id for a given feature type.
        E.g., for feature_type 'pocket', returns 'POC-1', 'VOI-20', etc.
        """

        prefix = _FEATURE_PREFIXES.get(feature_type, feature_type[:3].upper())
        index = 1
        while f'{prefix}-{index}' in self._features:
            index += 1
        return f'{prefix}-{index}'


def _validate_child_parent_compat(child: BaseFeature, parent: BaseFeature) -> None:

    if parent.dimensionality != 2:
        raise ValueError('Parent must be 2D (Feature2D)')

    if child.dimensionality not in (0, 1):
        raise ValueError('Child must be 0D or 1D')

    if child.feature_type == 'mouth' and parent.shape_type != 'concavity':
        raise ValueError('Mouth must attach to a concavity feature')

    if child.feature_type == 'base_rim' and parent.shape_type != 'convexity':
        raise ValueError('BaseRim must attach to a convexity')
