"""Prototype: derive interface features from raw DFND topography records.

An *interface* is a wet region whose lining is contributed by atoms from two or
more bodies (see ``devguide/DFND/interfaces.md``). This module post-processes the
output of ``DelaunayFlowNetwork.get_topography`` -- it does not touch the
geometric substrate (``R_residence`` / ``R_gate``).

Bodies can be supplied two ways (interfaces.md section 4):

- **explicit per-atom labels** (e.g. chain identity) -- the robust route, and the
  only one that works for tightly packed interfaces whose dry interiors fuse;
- **derived from the dry network** (``body_labels_from_dry_components``) -- the
  native, label-free route, valid only when a probe-resident wet layer separates
  the banks.
"""

from collections import Counter

import numpy as np

_INTERFACE_FAMILY_BY_FAMILY = {
    'void': 'interface_void',
    'pocket': 'interface_pocket',
    'multi_external_link': 'interface_channelway',
    'surface_concavity': 'bare_interface',
}


def body_labels_from_dry_components(topography, n_atoms, min_component_size=1):
    """Assign each atom a body id from the dry component that contains it.

    Components are ranked by size (largest first) so the dominant bank wins atoms
    shared on a boundary. Atoms in no qualifying component get ``-1``.
    """
    labels = np.full(int(n_atoms), -1, dtype=int)
    components = sorted(
        (c for c in topography['dry']['components'] if c['size'] >= min_component_size),
        key=lambda c: c['size'],
        reverse=True,
    )
    for body_id, component in enumerate(components):
        for atom in component['atom_indices']:
            if labels[atom] == -1:
                labels[atom] = body_id
    return labels


def classify_interface_components(wet_components, body_labels,
                               min_body_atoms=3, min_minority_fraction=0.15):
    """Tag each wet domain with its lining-body composition and interface status.

    A domain is an interface region when >=2 distinct bodies each contribute at
    least ``min_body_atoms`` lining atoms and the minority body holds at least
    ``min_minority_fraction`` of the multi-body lining (so single-body surface
    texture with a few stray neighbours is not mislabelled).
    """
    body_labels = np.asarray(body_labels)
    records = []
    for domain in wet_components:
        labels = body_labels[domain['atom_indices']]
        counts = {int(body): int(n) for body, n in Counter(labels.tolist()).items()
                  if body >= 0 and n >= min_body_atoms}
        total = sum(counts.values())
        n_bodies = len(counts)
        minority = (min(counts.values()) / total) if n_bodies >= 2 else 0.0
        is_interface = n_bodies >= 2 and minority >= min_minority_fraction
        family = domain['family']
        records.append({
            'component_id': domain['id'],
            'family': family,
            'n_resident_nodes': domain['n_resident_nodes'],
            'n_lining_bodies': n_bodies,
            'lining_body_split': counts,
            'minority_fraction': minority,
            'is_interface': is_interface,
            'interface_family': _INTERFACE_FAMILY_BY_FAMILY.get(family) if is_interface else None,
        })
    return records


def annotate_interfaces(topography, n_atoms, body_labels=None, **kwargs):
    """Convenience wrapper: classify all wet domains and return only interfaces.

    With ``body_labels=None`` the bodies are derived from the dry network (native
    route). Returns the list of interface records (``is_interface`` is True).
    """
    if body_labels is None:
        body_labels = body_labels_from_dry_components(topography, n_atoms)
    classified = classify_interface_components(
        topography['raw']['wet_components'], body_labels, **kwargs
    )
    return [record for record in classified if record['is_interface']]
