# MOLE original-provider overview

Review: 2026-11-08. Implementation owner [#140](https://github.com/uibcdf/topomt/issues/140).
Use [the source checkpoint](source_checkpoint.md) for exact execution evidence;
installed/public TopoMT qualification remains separate.

[Maintained source](https://github.com/sb-ncbr/webchemistry) · [Legacy standalone tree](https://github.com/sb-ncbr/MOLE) · [Resource conversation #105](https://github.com/uibcdf/topomt/discussions/105)

## Scientific and access contract

The MIT-licensed maintained source at
`fe0e84582a6bd42bc69224fd3a3022bf5c51cec3` produces MOLE
`2.5.26.10.26`. It builds with .NET SDK 10 and is distinct from the older
standalone tree, the Python MOLEonline API server and the live hosted service.
This integration executes the original local engine; no scientific C# code or
defaults are patched. See [the method comparison](../DFND/mole_comparison_2026_11_07.md)
for the antecedent analysis and its separate evidence scope.

MOLE decomposes Delaunay space and reports channel profiles, cavity facets,
tetrahedral volumes, origins, layers, lining labels and chemical descriptors.
Original `Cavity` and `Void` labels remain labels from this method. Its cavity
volume sums tetrahedron volumes, not solvent-excluded free space. Profiles and
meshes do not independently establish native DFND objects or biological function.

## Public route

Use `topomt.get_provider_output(source, method='mole', mole_cmd='/path/to/mole2')`
or `topomt.third_party.mole.get_output`. The
[public guide](../../docs/content/user/original_local_providers.md#mole)
defines the closed option set, physical units, resource controls and limitations.
MolSysMT owns source representation, selection, frame, chemistry and PDB export.
The selected executable is checked and run through the same resolved path.
The .NET processor count and managed heap cap default to 1 and 1024 MiB;
these are not a total-process memory limit or resource reservation.

`MoleOutput.channels` retains Tunnels/Pores/MergedPores/Paths collection identity;
`cavities` retains both original Cavities and Voids. Each feature keeps detached
original fields, quantity-aware geometry and attributed supported measurements.
`original_data` exposes the complete detached JSON, including the global surface,
origins, configuration and descriptors. Do not interpret the source's `Auto`
field as a replacement for the submitted `origin_policy` and original origins.
Atom mappings remain unavailable rather than inferred from residue strings.

Save original evidence with `output.save(path)` and reconstruct with
`topomt.load_provider_output(path, molecular_system=source)`. Recovery validates
the full original source, chemistry, frame and submitted PDB mapping without
requiring MOLE, .NET or network access. Failure receipts retain inspectable bytes
and are not recoverable as completed output.

## Attribution and remaining gates

Original algorithm: Sehnal et al., *MOLE 2.0: Advanced approach for analysis of
biomacromolecular channels* (2013), DOI
[10.1186/1758-2946-5-39](https://doi.org/10.1186/1758-2946-5-39).
Use the original provider/version when citing an execution; the 2025 online
interface publication is a separate resource. This adapter preserves original
artifacts and offline citation guidance. It introduces no optional Ackredit
session/tracking boundary or import-time registration.

Hosted automation, membrane orientation, user exit/query/path controls,
exhaustive descriptor normalization and native reproduction are outside this
source milestone. #19 owns broader fidelity, #101/#16 installed/public evidence,
and #58/#81 full-suite/matrix/coverage recovery. Technical molecular smoke inputs
do not start native DFND protein characterization or a molecular BenchLab study.
