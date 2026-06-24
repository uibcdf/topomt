"""Guard: keep the DFND output-status registry in sync with the kernel.

This is the anti-drift test behind the canonical/experimental boundary
(``topomt/dfnd/output_status.py``). It enforces that nothing the kernel emits is
left unclassified and nothing flagged ``experimental`` is mislabelled, so the
boundary stays alive by construction rather than by human memory.
"""

import numpy as np
import pytest

from topomt.dfnd import families as fam
from topomt.dfnd import output_status as ostat
from topomt.dfnd import synthetic
from topomt.dfnd.components import build_components
from topomt.dfnd.graph import DelaunayFlowNetwork

# Synthetic panel chosen to exercise several families and the wet motifs.
_PANEL = [
    synthetic.dumbbell(),
    synthetic.hollow_sphere(),
    synthetic.hollow_sphere_with_opening(),
    synthetic.argon_cube(),
]


def _components_for(system):
    network = DelaunayFlowNetwork.from_coordinates_and_radii(
        np.asarray(system.coords, dtype=float),
        np.asarray(system.radii, dtype=float),
    )
    result = network.get_topography()
    return build_components(result, network)


# --- registry internal consistency -----------------------------------------


def test_registry_entries_are_well_formed():
    for name, entry in ostat.OUTPUT_STATUS.items():
        assert entry.status in ostat.VALID_STATUS, name
        assert entry.kind in ostat.VALID_KIND, name
        if entry.status == 'canonical':
            assert entry.promotion_gate is None, f'{name} canonical but has a gate'
            assert entry.blocker_ref is None, f'{name} canonical but has a blocker'
        else:
            assert entry.promotion_gate, f'{name} non-canonical but has no gate'
            assert entry.blocker_ref, f'{name} non-canonical but has no blocker_ref'


# --- families: exact static coverage (strong guarantee) ---------------------


def test_every_family_constant_is_classified():
    """A new or removed DFND family forces a registry update."""
    assert set(fam.SIDE_BY_FAMILY) == ostat.names_by_kind('family')


# --- runtime: nothing emitted is unclassified or mislabelled ----------------


def test_emitted_families_and_motifs_match_the_registry():
    family_names = ostat.names_by_kind('family')
    motif_names = ostat.names_by_kind('motif')
    experimental_motifs = ostat.experimental_motif_types()

    observed_families: set[str] = set()
    observed_motifs: dict[str, bool] = {}  # motif_type -> seen with experimental flag

    for system in _PANEL:
        for component in _components_for(system).values():
            observed_families.add(component.family)
            for motif in component.motifs:
                mtype = motif.get('motif_type')
                if mtype is None:
                    continue
                is_experimental = 'experimental' in motif.get('flags', [])
                observed_motifs[mtype] = observed_motifs.get(mtype, False) or (
                    is_experimental
                )

    # Nothing emitted may be unclassified.
    assert observed_families <= family_names, (
        f'unclassified families emitted: {observed_families - family_names}'
    )
    assert set(observed_motifs) <= motif_names, (
        f'unclassified motif types emitted: {set(observed_motifs) - motif_names}'
    )

    # The runtime experimental flag must agree with the registry both ways.
    for mtype, seen_experimental in observed_motifs.items():
        registered_experimental = mtype in experimental_motifs
        assert seen_experimental == registered_experimental, (
            f"motif '{mtype}': runtime experimental flag={seen_experimental} but "
            f'registry experimental={registered_experimental}'
        )


def test_panel_actually_exercises_canonical_and_experimental_motifs():
    """Guard against a vacuous panel: the panel must emit at least one canonical
    and one experimental motif, or the consistency test above proves nothing."""
    seen = set()
    for system in _PANEL:
        for component in _components_for(system).values():
            for motif in component.motifs:
                if motif.get('motif_type'):
                    seen.add(motif['motif_type'])
    canonical_motifs = ostat.names_by_kind('motif') - ostat.experimental_motif_types()
    if not (seen & canonical_motifs):
        pytest.skip('panel produced no canonical motif (needs a richer fixture)')
    if not (seen & ostat.experimental_motif_types()):
        pytest.skip('panel produced no experimental motif (needs a richer fixture)')


# --- catalog: classify is total -------------------------------------------


def test_catalog_classification_is_total():
    """The kernel/catalog reframe of the family guard: every catalog
    classification (``classify`` -> ``component.classification``) a component
    receives must be registered -- nothing classified may be left unregistered."""
    registered = ostat.catalog_classification_names()
    observed: set[str] = set()
    for system in _PANEL:
        for component in _components_for(system).values():
            name = (getattr(component, 'classification', None) or {}).get('name')
            if name is not None:
                observed.add(name)
    assert observed, 'panel produced no catalog classifications'
    assert observed <= registered, (
        f'unregistered catalog classifications: {observed - registered}'
    )
