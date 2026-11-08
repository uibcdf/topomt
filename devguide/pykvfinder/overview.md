# pyKVFinder original-provider overview

The tetrahedron [zero-cutoff diagnostic](zero_cutoff_diagnostic.md) records a
suspected original-export limitation and a separately declared one-voxel control.
Its results do not change the scientific kernels or the molecular source pilot.

Upstream collaboration: with explicit maintainer authorization, the packaging-only
compatibility proposal and bounded evidence were published as
[LBC-LNBio/pyKVFinder#222](https://github.com/LBC-LNBio/pyKVFinder/issues/222).
This is a proposal for upstream review, not an accepted change or upstream release.

Review: 2026-11-07. Implemented source boundary; runtime evidence retains its
recorded inputs and limits. Full installed/platform qualification is separate.

[Official source](https://github.com/LBC-LNBio/pyKVFinder) · [Resource conversation](https://github.com/uibcdf/topomt/discussions/107) · [Implementation issue](https://github.com/uibcdf/topomt/issues/136)

## Scientific and access contract

Original 0.9.6 and explicitly selected compatibility source; dual-probe cavities, grid points and TOML descriptors.
Access/licence: GPL-3.0-or-later. This is a no-payment local route.
Provider labels do not admit native DFND classification or establish biological
binding relevance, continuous-region geometry or comparative accuracy.

## Public route

Use `topomt.get_provider_output(source, method='pykvfinder')` or
`topomt.third_party.pykvfinder.get_output(source, ...)`. Follow the
[complete option, acquisition and recovery guide](../../docs/content/user/original_local_providers.md).
Source ownership, selections, one frame and reference chemistry use MolSysMT's
existing public operations. Availability is lazy and route-specific. Explicit
commands are checked and executed through the same resolved path.

Save original evidence with `output.save(path)`; use `load_provider_output`
with the original full source for engine-independent reconstruction. Original
artifacts, typed measurements, declared geometries, selection/frame/chemistry
and resource settings remain attributed to the same run. Missing atom maps
remain `None`; original labels are not guessed into source indices.

## Evidence and next gates

The compiled `0.9.6+uibcdf.2` compatibility source passes 266 upstream/compatibility
unit cases on Python 3.14.10/NumPy 2.5.4. The tomlkit>=0.14 route has floor
0.14.0 and current 0.15.2 controls. A direct-original TopoMT pilot reports 12
cavities on the retained 1AKD input; the designated source gate checks original
volumes/areas/residues and successful nonempty/empty saved reconstruction.
The upstream checkout remains clean and unmodified; the fork's C/algorithm
files and scientific defaults remain identical to upstream v0.9.6.

The shared [implementation plan](../external_provider_expansion_plan.md)
and [expansion checkpoint](../original_provider_expansion_checkpoint.md)
distinguish protocol tests, actual upstream execution, source recovery and
pending installed/package qualification. Tests use
`tests/test_new_provider_parsers.py`, `tests/test_new_provider_arguments.py`
and `tests/test_new_provider_workflows.py`; analytical fixtures in those files
are not detector-execution evidence.

Keep new versions and scientific definitions explicit. Broader descriptor
fidelity belongs to #19; release and interpreter/platform evidence belongs to
#16/#58/#81. Do not silently switch to another provider or a native reproduction.
