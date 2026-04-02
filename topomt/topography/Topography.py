from __future__ import annotations

import copy
from collections.abc import Mapping, Iterator
from typing import Any

import molsysmt as msm

from topomt.features import _FEATURE_TYPE_REGISTRY, _FEATURE_PREFIXES
from ..features.BaseFeature import BaseFeature, FeatureID, FeatureIndex, FeatureType, ShapeType, Dimensionality


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main class
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Topography(Mapping[str, BaseFeature]):
    """
    Central registry of all features.

    Public API uses *feature_id*.
    Internal storage and relations use *feature_index* for efficiency.
    """

    def __init__(self, molecular_system: Any | None = None, selection: Any = 'all', structure_indices: int = 0,
                 features: list[BaseFeature] | None = None) -> None:
        # main store: id → feature
        self._features: dict[FeatureID, BaseFeature] = {}

        # derived indexes
        self._by_dimensionality: dict[int, set[FeatureID]] = {0: set(), 1: set(), 2: set()}
        self._by_shape: dict[ShapeType, set[FeatureID]] = {
            "concavity": set(),
            "convexity": set(),
            "mixed": set(),
            "boundary": set(),
            "point": set(),
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
            self._molsys = msm.convert(molecular_system, selection=selection, structure_indices=structure_indices,
                                       to_form='molsysmt.MolSys')

        if features is not None:
            for feature in features:
                self.add_feature(feature)

    # -----------------
    # Mapping interface
    # -----------------

    def __repr__(self) -> str:
        parts = ", ".join(f"{ftype}={len(ids)}" for ftype, ids in self._by_type.items())
        return f"<TopoMT Topography total={len(self)} {parts}>"

    def __getitem__(self, feature_id: FeatureID) -> BaseFeature:
        """Allow: topo["Pock001"] → feature with feature_id == "Pock001"."""
        return self._features[feature_id]

    def __iter__(self) -> Iterator[str]:
        return iter(self._features)

    def __len__(self) -> int:
        return len(self._features)

    def copy(self, deep: bool = True) -> Topography:
        """Return a copy of the Topography object.

        Parameters
        ----------
        deep : bool, optional
            If True (default), perform a deep copy of all internal
            data structures. If False, only a shallow copy is made.
        """
        return copy.deepcopy(self) if deep else copy.copy(self)

    def __copy__(self):
        new_topo = Topography(molecular_system=self._molsys)
        new_topo._molecular_system = self._molecular_system
        for feature_id, feature in self._features.items():
            new_feature = feature.copy(deep=False)
            new_feature._topography = new_topo
            new_topo.add_feature(new_feature)
        for parent_id, chidren_id in self._children_of.items():
            for child_id in chidren_id:
                new_topo.connect_features(child_id, parent_id)
        return new_topo

    def __deepcopy__(self, memo):
        new_topo = Topography(molecular_system=copy.deepcopy(self._molsys, memo))
        new_topo._molecular_system = copy.deepcopy(self._molecular_system, memo)
        for feature_id, feature in self._features.items():
            new_feature = feature.copy(deep=True)
            new_feature._topography = new_topo
            new_topo.add_feature(new_feature)
        for parent_id, chidren_id in self._children_of.items():
            for child_id in chidren_id:
                new_topo.connect_features(child_id, parent_id)
        return new_topo

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

    def add_feature(self, feature: BaseFeature) -> FeatureID | None:
        """
        Add a feature to the topography.
        - automatically updates dimensional, shape, and type registries
        """

        new_feature_id = False
        if feature.feature_id is None:
            feature_id = self._make_next_feature_id(feature.feature_type)
            feature.feature_id = feature_id
            new_feature_id = True
        else:
            feature_id = feature.feature_id
            if feature_id in self._features:
                Warning(f"Feature with id '{feature_id}' is already in the topography. Skipping addition.")

        # store
        self._features[feature_id] = feature

        # ensure features share the topography references
        if feature._topography is not None:
            if id(feature._topography) != id(self):
                raise ValueError("Feature is already assigned to a different Topography.")
        else:
            feature._topography = self

        # derived index by dimension
        self._by_dimensionality.setdefault(feature.dimensionality, set()).add(feature_id)
        # derived index by shape
        self._by_shape.setdefault(feature.shape_type, set()).add(feature_id)
        # derived index by type
        self._by_type.setdefault(feature.feature_type, set()).add(feature_id)

        # init empty relations
        self._children_of.setdefault(feature_id, set())
        self._parents_of.setdefault(feature_id, set())

        # ensure atom_indices are set if atom_labels and molecular_system are provided
        if self._molsys is not None:
            if (feature.atom_labels is not None) and (feature.atom_indices is None):
                feature.atom_indices = feature._get_atom_indices_from_atom_labels()

        if new_feature_id:
            return feature_id
        else:
            return None


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
            raise ValueError(f"Unknown feature_type {feature_type!r}")

        new_feature_id = False
        if feature_id is None:
            feature_id = self._make_next_feature_id(feature_type)
            new_feature_id = True

        new_feature = feature_class(feature_id=feature_id, atom_indices=atom_indices, atom_labels=atom_labels,
                                    atom_label_format=atom_label_format, **kwargs)

        self.add_feature(new_feature)

        if new_feature_id:
            return feature_id
        else:
            return None

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # public: connect_features
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def connect_features(self, child_feature_or_id: FeatureID | BaseFeature, parent_feature_or_id: FeatureID | BaseFeature) -> None:
        """
        """

        child_id= None
        parent_id= None

        if isinstance(child_feature_or_id, BaseFeature):
            if child_feature_or_id.feature_id not in self._features:
                self.add_feature(child_feature_or_id)
            child_id = child_feature_or_id.feature_id
        elif isinstance(child_feature_or_id, str):
            child_id = child_feature_or_id
            if child_id not in self._features:
                raise ValueError(f"Child feature with id '{child_id}' is not in the topography.")

        if isinstance(parent_feature_or_id, BaseFeature):
            if parent_feature_or_id.feature_id not in self._features:
                self.add_feature(parent_feature_or_id)
            parent_id = parent_feature_or_id.feature_id
        elif isinstance(parent_feature_or_id, str):
            parent_id = parent_feature_or_id
            if parent_id not in self._features:
                raise ValueError(f"Parent feature with id '{parent_id}' is not in the topography.")

        child = self._features[child_id]
        parent = self._features[parent_id]

        # external validators
        _validate_child_parent_compat(child, parent)

        # register relations
        self._children_of[parent.feature_id].add(child_id)
        self._parents_of[child.feature_id].add(parent_id)

        # sync connections in feature objects
        if parent.dimensionality == 2:
            child._add_surface_id(parent_id)
            if child.dimensionality == 0:
                parent._add_point_id(child_id)
            elif child.dimensionality == 1:
                parent._add_boundary_id(child_id)
        else:
            raise ValueError('Parent feature must be 2D (Feature2D)')

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

        elif by == "type":
            feature_ids = set(self._by_type.get(value, ()))

        elif by == "shape":
            feature_ids = set(self._by_shape.get(value, ()))

        elif by == "dimensionality":
            feature_ids = set(self._by_dimensionality.get(value, ()))

        elif by == "id":
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
            if grouped_by == "type":
                key = feat.feature_type
            elif grouped_by == "shape":
                key = feat.shape_type
            elif grouped_by == "dimensionality":
                key = feat.dimensionality
            else:
                raise ValueError(f"Unknown 'grouped_by' criterion: {grouped_by!r}")

            out.setdefault(key, set())
            out[key].add(fid if as_feature_ids else feat)

        return out

    def get_feature_by_id(self, feature_id: FeatureID) -> BaseFeature:
        if feature_id not in self._features:
            raise ValueError(f"Feature with id '{feature_id}' is not in the topography.")
        else:
            return self._features[feature_id]

    def children_of(self, feature_id: FeatureID, as_feature_ids=False) -> set[BaseFeature] | set[FeatureID]:
        if as_feature_ids:
            return self._children_of[feature_id]
        else:
            return set([self._features[fid] for fid in self._children_of[feature_id]])

    def parents_of(self, feature_id: FeatureID, as_feature_ids=False) -> set[BaseFeature] | set[FeatureID]:
        if as_feature_ids:
            return self._parents_of[feature_id]
        else:
            return set([self._features[fid] for fid in self._parents_of[feature_id]])

    def info(self) -> dict[str, dict[str, int]]:
        return {
            "by_type": {ftype: len(ids) for ftype, ids in self._by_type.items()},
            "by_shape": {shape: len(ids) for shape, ids in self._by_shape.items()},
            "by_dimensionality": {dim: len(ids) for dim, ids in self._by_dimensionality.items()},
            "total": len(self._features),
        }


    def to_records(self) -> list[dict[str, object]]:
        records = []
        for fid, feat in self._features.items():
            records.append({
                "id": fid,
                "type": feat.feature_type,
                "shape": feat.shape_type,
                "dim": feat.dimensionality,
            })
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

        index = len(self._by_type.get(feature_type, []))+1
        prefix = _FEATURE_PREFIXES.get(feature_type, feature_type[:3].upper())
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
