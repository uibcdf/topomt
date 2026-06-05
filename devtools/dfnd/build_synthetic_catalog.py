"""Build the DFND synthetic-shape catalog: write PDBs + an auto-labelled README.

Each catalog entry is a dummy-atom shape (argon) with topography known by
construction. This script writes one PDB per entry to ``topomt/data/synthetic``
and regenerates ``README.md`` with the DFND family summary actually produced at
the documented probe radius -- so the table never drifts from the code.

The battery is meant to grow (parametric variants of a shape are first-class
entries). Add tuples to ``CATALOG`` and re-run. Design notes:
``devguide/DFND/synthetic_benchmarks.md``.
"""

import re
from collections import Counter
from pathlib import Path

from topomt.dfnd import synthetic as syn
from topomt.dfnd.graph import DelaunayFlowNetwork

OUTPUT_DIR = Path('topomt/data/synthetic')
SIGNIFICANT_RESIDENTS = 5

# (name, builder -> (coords, radii), probe_radius, expected-by-construction note)
CATALOG = [
    # --- baseline / original battery ---
    (
        'argon_cube',
        lambda: syn.argon_cube(),
        1.3,
        'simplest cell: 8 argon at cube vertices, body diagonal = 2*(r_Ar+r_probe); '
        'void at probe<1.4, marginal/empty at exactly 1.4 (threshold knife-edge)',
    ),
    (
        'tetrahedron_void',
        lambda: syn.tetrahedron(edge=6.0),
        1.4,
        'minimal 4-atom cell (sanity baseline)',
    ),
    (
        'hollow_sphere_void',
        lambda: syn.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0),
        1.4,
        'one enclosed void (0 mouths)',
    ),
    (
        'hollow_sphere_pocket',
        lambda: syn.hollow_sphere_with_opening(10.0, 3.5, 30.0, jitter=0.1, seed=0),
        1.4,
        'one polar opening -> pocket (1 mouth)',
    ),
    (
        'hollow_sphere_leaky',
        lambda: syn.hollow_sphere(12.0, 4.5, jitter=0.1, seed=0),
        1.8,
        'wall seals a 1.8 A probe, leaks a 1.0 A probe (sweep)',
    ),
    (
        'tube_channel',
        lambda: syn.cylinder_tube(20.0, 6.0, 3.5, jitter=0.1, seed=0),
        1.4,
        'open tube -> channel (>=2 mouths). Wide/sparsely-walled: the lumen channel '
        '(channel, 2 mouths) is the dominant feature, alongside several '
        'shallow side-pockets at the wall windows.',
    ),
    (
        'tube_channel_clean',
        lambda: syn.cylinder_tube(20.0, 3.5, 2.5, jitter=0.1, seed=0),
        1.4,
        'narrow, densely-walled tube -> a single clean channel (channel, '
        '2 mouths) with minimal side-pocket noise; the canonical two-mouth-channel '
        'fixture.',
    ),
    (
        'dumbbell',
        lambda: syn.dumbbell(7.0, 12.5, 3.5, jitter=0.1, seed=0),
        1.4,
        'two chambers + throat: 1 void @1.4, 2 voids @2.2 (volume != connectivity)',
    ),
    (
        'solid_ball_control',
        lambda: syn.solid_ball(8.0, 3.5, jitter=0.1, seed=0),
        1.4,
        'negative control: no cavity',
    ),
    # --- batch A: simple shapes (+ parametric variants) ---
    (
        'blind_well_d6_r6',
        lambda: syn.blind_well(6.0, 6.0, seed=0),
        1.4,
        'shallow bored well -> pocket (1 mouth)',
    ),
    (
        'blind_well_d8_r6',
        lambda: syn.blind_well(6.0, 8.0, seed=0),
        1.4,
        'deep bored well -> pocket (1 mouth)',
    ),
    (
        'blind_well_d12_r6',
        lambda: syn.blind_well(6.0, 12.0, seed=0),
        1.4,
        'very deep bored well -> pocket (depth layers)',
    ),
    (
        'slab_pore_r4_t6',
        lambda: syn.slab_with_pore(4.0, 6.0, seed=0),
        1.4,
        'pore through a slab -> channel (2 mouths)',
    ),
    (
        'two_voids_gap14',
        lambda: syn.two_voids(8.0, 3.5, 14.0, seed=0),
        1.4,
        'two disjoint hollow spheres -> two separate voids (counting)',
    ),
    (
        'surface_bowl_shallow_d2',
        lambda: syn.surface_bowl(9.0, 2.0, seed=0),
        1.4,
        'shallow dent -> open pocket + surface texture',
    ),
    (
        'surface_bowl_deep_d6',
        lambda: syn.surface_bowl(9.0, 6.0, seed=0),
        1.4,
        'deeper bowl -> dominant open pocket + surface texture',
    ),
    # --- batch B: average-complexity shapes (+ parametric variants) ---
    (
        'branched_tube_y',
        lambda: syn.branched_tube(11.0, 5.0, seed=0),
        1.4,
        'Y junction of three tubes -> channel with 3 mouths',
    ),
    (
        'nested_spheres',
        lambda: syn.nested_spheres(14.0, 7.0, seed=0),
        1.4,
        'sphere inside a sphere -> core void + shell-gap void (2 voids)',
    ),
    (
        'curved_tube_120',
        lambda: syn.curved_tube(12.0, 120.0, 5.0, seed=0),
        1.4,
        'bent tube -> channel (2 mouths), curvature-independent',
    ),
    (
        'flask_neck_narrow',
        lambda: syn.flask(neck_radius=2.5, seed=0),
        1.4,
        'narrow neck seals chamber -> void + neck pocket (throat gating)',
    ),
    (
        'flask_neck_wide',
        lambda: syn.flask(neck_radius=5.0, seed=0),
        1.4,
        'wide neck -> open pocket (throat open, no void)',
    ),
    (
        'two_openings_pinhole',
        lambda: syn.hollow_sphere_two_openings(
            opening1_half_angle_deg=35.0, opening2_half_angle_deg=10.0, seed=0
        ),
        1.4,
        'pinhole second mouth does not register -> pocket (marginal mouth)',
    ),
    (
        'two_openings_open',
        lambda: syn.hollow_sphere_two_openings(
            opening1_half_angle_deg=35.0, opening2_half_angle_deg=25.0, seed=0
        ),
        1.4,
        'both mouths register -> channel (2 mouths)',
    ),
    # --- batch C: sophisticated / anomalous shapes (+ parametric variants) ---
    (
        'asymmetric_dumbbell',
        lambda: syn.asymmetric_dumbbell(8.0, 5.0, 11.0, seed=0),
        1.4,
        'unequal chambers + offset throat: 1 void @1.4, 2 voids @2.2',
    ),
    (
        'swiss_cheese_percolating',
        lambda: syn.swiss_cheese(11.0, 4.5, 7.0, seed=0),
        1.4,
        'overlapping carved voids percolate -> one connected mega-cluster',
    ),
    (
        'swiss_cheese_sparse',
        lambda: syn.swiss_cheese(11.0, 4.0, 8.0, seed=0),
        1.4,
        'wider-spaced voids -> partially separated cavities',
    ),
    (
        'void_with_island',
        lambda: syn.void_with_island(11.0, 3.0, seed=0),
        1.4,
        'solid island inside a void -> still one void (genus not tracked)',
    ),
    (
        'helical_tube',
        lambda: syn.helical_tube(1.5, 8.0, 10.0, 4.5, seed=0),
        1.4,
        'helical channel -> 1 channel (2 mouths), complex 3D path',
    ),
    (
        'onion_shells_3',
        lambda: syn.onion_shells((18.0, 12.0, 6.0), seed=0),
        1.4,
        'three concentric shells -> three nested voids',
    ),
    # --- batch D: adversarial shapes (where other detectors can fail) ---
    # (dumbbell @ sep 12.5 above also serves the fusion/separation threshold case:
    #  1 void @1.5 -> 2 voids @1.6; orientation invariance reuses hollow_sphere_void.)
    (
        'sliver_sheet',
        lambda: syn.sliver_sheet(18.0, 3.5, seed=0),
        1.4,
        'flat sheet: no false tunnel/void (alpha-shape sliver trap)',
    ),
    (
        'pocket_intruder_open',
        lambda: syn.pocket_with_mouth_intruder(intruder=False, seed=0),
        1.4,
        '3-atom wall mouth open -> pocket',
    ),
    (
        'pocket_intruder_sealed',
        lambda: syn.pocket_with_mouth_intruder(intruder=True, seed=0),
        1.4,
        'one extra atom in the mouth seals it -> void (4th-atom intrusion)',
    ),
    (
        'flask_cryptic',
        lambda: syn.flask(neck_radius=3.0, neck_length=2.5, seed=0),
        1.4,
        'gated chamber: void @1.4 (sealed) -> pocket @1.0 (revealed by smaller probe)',
    ),
    (
        'rough_surface',
        lambda: syn.rough_surface(20.0, amplitude=1.3, seed=0),
        1.4,
        'sub-probe roughness -> spray of tiny spurious features (over-reporting study)',
    ),
    # --- batch E: interfaces (dry banks + wet gap; see interfaces.md) ---
    (
        'two_blocks_fused',
        lambda: syn.two_blocks(gap=2.0, seed=0),
        1.4,
        'narrow gap -> dry network bridges -> one body (interface fuses)',
    ),
    (
        'two_blocks_interface',
        lambda: syn.two_blocks(gap=5.0, seed=0),
        1.4,
        'solvent-wide gap -> two dry banks + a wet interface lined by both',
    ),
    (
        'two_blocks_interface_wide_gap',
        lambda: syn.two_blocks(gap=6.3, seed=0),
        1.4,
        'wide solvent gap (>=3.4 A vdW clearance) -> two dry banks + a wet interface lined by both',
    ),
    (
        'two_blocks_interface_slabs',
        lambda: syn.two_blocks_interface_slabs(gap=5.0, seed=0),
        1.4,
        'local interface fragment: only the two facing x-layers from each block',
    ),
    (
        'three_blocks_interface',
        lambda: syn.three_blocks(gap=5.0, seed=0),
        1.4,
        'three bodies in a row -> two interfaces',
    ),
    (
        'interface_pocket',
        lambda: syn.interface_pocket(gap=2.0, pocket_radius=6.0, seed=0),
        1.4,
        'cavity at the contact plane -> buried pocket lined by both bodies',
    ),
    (
        'interface_pocket_open',
        lambda: syn.interface_pocket(gap=2.0, pocket_radius=6.0, mouth=True, seed=0),
        1.4,
        'interface cavity with a mouth -> one-mouth pocket lined by both bodies',
    ),
    (
        'three_body_junction',
        lambda: syn.three_body_junction(9.0, 5.5, seed=0),
        1.4,
        'three blocks at 120 deg -> central cavity lined by three bodies',
    ),
    # --- pathological: KNOWN FAILURES (see pathological_systems.md) ---
    (
        'pathological_deep_narrow_well',
        lambda: syn.blind_well(well_radius=3.0, depth=14.0, seed=0),
        1.4,
        'FAIL: deep narrow well fragments into stacked pockets (ideal: 1 pocket)',
    ),
    (
        'pathological_long_pore',
        lambda: syn.slab_with_pore(pore_radius=3.0, thickness=14.0, seed=0),
        1.4,
        'FAIL: long pore loses through-connectivity (ideal: 1 channel)',
    ),
    (
        'pathological_flat_slab',
        lambda: syn.flat_slab(20.0, 4.0, 4.0, seed=0),
        1.4,
        'FAIL: flat convex slab emits spurious voids (ideal: 0 cavities)',
    ),
    (
        'pathological_perfect_cube',
        lambda: syn.hollow_cube(8.0, 3.5, jitter=0.0, seed=0),
        1.4,
        'FAIL: perfect lattice (jitter=0) is degenerate/unstable (WP4)',
    ),
    (
        'pathological_jittered_cube',
        lambda: syn.hollow_cube(8.0, 3.5, jitter=0.1, seed=0),
        1.4,
        'reference: same cube with 0.1 A jitter gives a different answer',
    ),
    (
        'pathological_two_balls',
        lambda: syn.two_balls(6.0, 8.0, seed=0),
        1.4,
        'FAIL: two convex bodies make a phantom inter-body pocket (ideal: 0)',
    ),
    (
        'pathological_parallel_plates',
        lambda: syn.parallel_plates(separation=3.0, seed=0),
        1.4,
        'FAIL: thin gap between plates fragments into spurious voids (ideal: 0)',
    ),
    (
        'pathological_undersampled_sphere',
        lambda: syn.hollow_sphere(10.0, 4.6, jitter=0.1, seed=0),
        1.4,
        'FAIL: same R=10 cavity reads as channel when wall is sparsely sampled (sampling sensitivity)',
    ),
    # thin-tube radius family: same shape, behaviour changes with the radius
    (
        'pathological_thin_tube_r20',
        lambda: syn.cylinder_tube(16.0, 2.0, 3.0, jitter=0.1, seed=0),
        1.4,
        'FAIL: very thin tube -> no significant feature (ideal: 1 channel)',
    ),
    (
        'pathological_thin_tube_r25',
        lambda: syn.cylinder_tube(16.0, 2.5, 3.0, jitter=0.1, seed=0),
        1.4,
        'FAIL: thin tube fragments into pockets (ideal: 1 channel)',
    ),
    (
        'pathological_thin_tube_r30',
        lambda: syn.cylinder_tube(16.0, 3.0, 3.0, jitter=0.1, seed=0),
        1.4,
        'FAIL: thin tube produces a spurious void (ideal: 1 channel)',
    ),
    (
        'thin_tube_r35',
        lambda: syn.cylinder_tube(16.0, 3.5, 3.0, jitter=0.1, seed=0),
        1.4,
        'reference: at r=3.5 the tube is finally recognised as a channel',
    ),
    (
        'pathological_patchy_sphere',
        lambda: syn.hollow_sphere_patchy(10.0, 3.0, 0.6, seed=0),
        1.4,
        'FAIL: closed sphere with a sparsely-sampled hemisphere reads as open (ideal: void)',
    ),
    (
        'pathological_mixed_radii_shell',
        lambda: syn.mixed_radii_shell(10.0, 4.3, seed=0),
        1.4,
        'FAIL: noble-gas mixed-radii wall reclassifies vs uniform argon (radius model; He/Ne/Ar/Kr/Xe)',
    ),
    # second sweep: systematic mechanism coverage
    (
        'pathological_marginal_gate_sphere',
        lambda: syn.hollow_sphere(11.0, 4.2, jitter=0.2, seed=0),
        1.4,
        'FAIL: wall gate at the probe threshold -> void/pocket/channel flickers with the seed',
    ),
    (
        'pathological_oblate_void',
        lambda: syn.oblate_void(7.0, 2.0, seed=0),
        1.4,
        'FAIL: thin slit-shaped void fragments into two voids (ideal: 1)',
    ),
    (
        'pathological_conical_channel',
        lambda: syn.conical_channel(6.0, 1.5, 16.0, seed=0),
        1.4,
        'FAIL: tapering channel fragments into pockets, no channel (ideal: 1 channel)',
    ),
    (
        'pathological_star_void',
        lambda: syn.star_void(seed=0),
        1.4,
        'FAIL: star/branched void fragments; core void not even dominant (ideal: 1 void)',
    ),
    (
        'pathological_toroidal_void',
        lambda: syn.toroidal_void(seed=0),
        1.4,
        'FAIL: genus-1 donut void splits into two voids (ideal: 1)',
    ),
    (
        'pathological_pocket_in_pocket',
        lambda: syn.pocket_in_pocket(seed=0),
        1.4,
        'FAIL: nested pocket+sub-pocket over-segments, no hierarchy (ideal: ~2 nested)',
    ),
    (
        'pathological_u_channel',
        lambda: syn.u_channel(seed=0),
        1.4,
        'FAIL: U-tunnel not connected as a channel + spurious void (ideal: 1 channel)',
    ),
    (
        'pathological_edge_cavity',
        lambda: syn.edge_cavity(seed=0),
        1.4,
        'FAIL: cavity at the block corner fragments into pockets (ideal: 1)',
    ),
    (
        'pathological_packed_blob_loose',
        lambda: syn.packed_blob(12.0, 3.8, seed=0),
        1.4,
        'FAIL: loosely packed solid blob sprays phantom voids (ideal: 0)',
    ),
    (
        'packed_blob_dense',
        lambda: syn.packed_blob(12.0, 3.0, seed=0),
        1.4,
        'reference: at vdW contact the same blob has zero phantom features (clean)',
    ),
    (
        'two_chambers_septum',
        lambda: syn.two_chambers_septum(4.5, 1.0, seed=0),
        1.4,
        'reference: a 1 A septum correctly keeps two chambers as two voids',
    ),
]


def _family_summary(coords, radii, probe_radius):
    network = DelaunayFlowNetwork.from_arrays(coords, radii, epsilon=1e-7)
    topo = network.get_topography(probe_radius=probe_radius, min_size=0)
    domains = topo['raw']['wet_components']
    significant = Counter(
        d['family'].replace('_domain', '')
        for d in domains
        if d['n_resident_nodes'] >= SIGNIFICANT_RESIDENTS
    )
    parts = [f'{count}x {name}' for name, count in sorted(significant.items())] or [
        '(none significant)'
    ]
    n_dry = sum(1 for c in topo['dry']['components'] if c['size'] >= 50)
    if n_dry >= 2:  # interface systems: report dry banks
        parts.append(f'{n_dry} dry bodies')
    return ', '.join(parts)


_DOC_AUTO_OPEN = '<!-- AUTO:build_synthetic_catalog -->'
_DOC_AUTO_CLOSE = '<!-- /AUTO -->'
_DOC_AUTO_RE = re.compile(
    re.escape(_DOC_AUTO_OPEN) + r'.*?' + re.escape(_DOC_AUTO_CLOSE),
    flags=re.DOTALL,
)


def _auto_block(name, n_atoms, probe, note, families):
    """The machine-maintained data header of a per-system doc (between AUTO markers)."""
    return (
        f'{_DOC_AUTO_OPEN}\n'
        f'- **PDB:** `{name}.pdb`\n'
        f'- **Atoms:** {n_atoms} · **Probe:** {probe} Å\n'
        f'- **Expected by construction:** {note}\n'
        f'- **DFND families (significant):** {families}\n'
        f'{_DOC_AUTO_CLOSE}'
    )


def _write_system_doc(output_dir, name, n_atoms, probe, note, families):
    """Per-system markdown (`<name>.md`): what to observe, why, DFND verdict.

    The data header (between the AUTO markers) is regenerated every build; the prose
    below it is authored by hand and **never overwritten**. A missing doc is created
    as a skeleton with TODO prose so coverage stays complete without clobbering.
    """
    path = output_dir / f'{name}.md'
    block = _auto_block(name, n_atoms, probe, note, families)
    if path.exists():
        text = path.read_text()
        if _DOC_AUTO_RE.search(text):
            path.write_text(_DOC_AUTO_RE.sub(lambda _m: block, text, count=1))
        return  # has prose already; only the header was refreshed
    skeleton = (
        f'# {name}\n\n'
        f'{block}\n\n'
        '## What to observe\n\n_TODO_\n\n'
        '## Why\n\n_TODO_\n\n'
        '## DFND verdict\n\n_TODO (does it get this right, or is there an inconsistency?)_\n'
    )
    path.write_text(skeleton)


def build(output_dir=OUTPUT_DIR):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, builder, probe, note in CATALOG:
        built = builder()
        elements = None
        if len(built) == 3:  # (coords, radii, element_symbols)
            coords, radii, elements = built
        else:
            coords, radii = built
        syn.to_pdb(coords, radii, output_dir / f'{name}.pdb', elements=elements)
        families = _family_summary(coords, radii, probe)
        _write_system_doc(output_dir, name, len(coords), probe, note, families)
        rows.append((name, len(coords), probe, note, families))

    lines = [
        '# DFND Synthetic Benchmark Structures',
        '',
        'Dummy **argon** atoms (vdW radius 1.88 A) in simple geometries whose topography',
        'is known by construction (mixed-radii systems use other noble gases He/Ne/Kr/Xe',
        'so the per-atom radius is encoded by the element). Generated by',
        '`topomt.dfnd.synthetic`; regenerate this',
        'directory and table with `python devtools/dfnd/build_synthetic_catalog.py`.',
        'Design and the probe-tight wall-spacing rule:',
        '`devguide/DFND/synthetic_benchmarks.md`.',
        '',
        'DFND tests build with the explicit argon radius (1.88 A) via',
        '`DelaunayFlowNetwork.from_arrays`; these PDBs are for sharing and cross-algorithm',
        'comparison (CASTp/fpocket re-derive radii from the element). The last column is',
        f'the DFND family summary at the listed probe (significant = >= {SIGNIFICANT_RESIDENTS} resident nodes).',
        '',
        '| File | Atoms | Probe (A) | Expected by construction | DFND families (significant) |',
        '|---|---:|---:|---|---|',
    ]
    for name, n, probe, note, families in rows:
        lines.append(f'| `{name}.pdb` | {n} | {probe} | {note} | {families} |')
    (output_dir / 'README.md').write_text('\n'.join(lines) + '\n')
    return rows


if __name__ == '__main__':
    built = build()
    print(f'Wrote {len(built)} PDBs + README to {OUTPUT_DIR}')
    for name, n, probe, note, families in built:
        print(f'  {name:28s} N={n:4d} probe={probe} -> {families}')
