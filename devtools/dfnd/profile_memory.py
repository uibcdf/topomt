"""Measure native array storage and retained query allocations on small fixtures.

Run from the repository root. Array storage counts unique backing allocations
referenced by the network and its Delaunay mesh. Tracemalloc values are Python
and NumPy traced allocations, not process RSS or a worst-case scaling bound.
The two query results remain live during measurement.

Extracted PDB input lives in owned scratch and is removed after its last use,
including failures. The requested report remains caller-owned. Measurements
release only tracing they started and preserve a caller's active tracing session.
"""

import argparse
import gc
import json
import sys
import tracemalloc
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np

from topomt import pyunitwizard as puw
from topomt.dfnd import synthetic
from topomt.dfnd.data import DFNDData
from topomt.dfnd.graph import DelaunayFlowNetwork


def _array_bytes(network):
    buffers = {}
    for owner in (network, network.mesh):
        for array in vars(owner).values():
            if not isinstance(array, np.ndarray):
                continue
            base = array
            while isinstance(base, np.ndarray) and base.base is not None:
                base = base.base
            buffers[id(base)] = (
                base.nbytes if isinstance(base, np.ndarray) else len(base)
            )
    return sum(buffers.values())


def _measure(name, build):
    gc.collect()
    owns_tracing = not tracemalloc.is_tracing()
    if owns_tracing:
        tracemalloc.start()
    try:
        start = perf_counter()
        network = build()
        build_seconds = perf_counter() - start
        build_live, build_peak = tracemalloc.get_traced_memory()
        start = perf_counter()
        data = DFNDData(network, network.get_topography())
        first_live, _ = tracemalloc.get_traced_memory()
        reprobed = data.at_probe(puw.quantity(2.2, 'angstroms'))
        query_seconds = perf_counter() - start
        second_live, total_peak = tracemalloc.get_traced_memory()
    finally:
        if owns_tracing:
            tracemalloc.stop()
    assert reprobed.network is network
    assert reprobed.mesh.delaunay is network.mesh
    assert np.shares_memory(data.mesh.atoms.coords, reprobed.mesh.atoms.coords)
    return {
        'name': name,
        'atoms': len(network.atom_radii),
        'tetrahedra': network.n_tetrahedra,
        'input_array_bytes': sum(
            array.nbytes
            for array in (
                network.atom_coords,
                network.atom_radii,
                network.atom_indices_map,
            )
        ),
        'network_and_mesh_unique_array_bytes': _array_bytes(network),
        'build_traced_live_bytes': build_live,
        'build_traced_peak_bytes': build_peak,
        'first_query_added_traced_bytes': first_live - build_live,
        'second_query_added_traced_bytes': second_live - first_live,
        'total_traced_peak_bytes': total_peak,
        'build_seconds': round(build_seconds, 4),
        'two_queries_seconds': round(query_seconds, 4),
        'probe_queries_share_geometry': True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = []
    for name, system in (
        ('tetrahedron', synthetic.tetrahedron(edge=5.3, atom_radius=1.7)),
        ('hollow_sphere', synthetic.hollow_sphere(10.0, 3.5, jitter=0.1, seed=0)),
        ('helical_tube', synthetic.helical_tube()),
    ):
        results.append(
            _measure(
                name,
                lambda: DelaunayFlowNetwork.from_coordinates_and_radii(
                    puw.quantity(system.coords, 'angstroms'),
                    puw.quantity(system.radii, 'angstroms'),
                ),
            )
        )
    with TemporaryDirectory(prefix='topomt-memory-profile-') as directory:
        pdb_path = Path(directory) / '1crn.pdb'
        with ZipFile('topomt/data/CASTpFold_server/1crn.zip') as archive:
            name = sorted(n for n in archive.namelist() if n.lower().endswith('.pdb'))[
                0
            ]
            pdb_path.write_bytes(archive.read(name))
        results.append(_measure('1crn', lambda: DelaunayFlowNetwork(str(pdb_path))))
    args.output.write_text(
        json.dumps({'python': sys.version.split()[0], 'cases': results}, indent=2)
        + '\n'
    )
    for result in results:
        print(
            f'{result["name"]}: {result["atoms"]} atoms, '
            f'input={result["input_array_bytes"]} B, '
            f'native arrays={result["network_and_mesh_unique_array_bytes"]} B, '
            f'reprobe added={result["second_query_added_traced_bytes"]} B'
        )


if __name__ == '__main__':
    main()
