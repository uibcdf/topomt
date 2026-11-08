# CAVER original-provider overview

Review: 2026-11-07. Implemented source boundary; runtime evidence retains its
recorded inputs and limits. Full installed/platform qualification is separate.

[Official source](https://www.caver.cz/index.php?sid=199) · [Resource conversation](https://github.com/uibcdf/topomt/discussions/104) · [Implementation issue](https://github.com/uibcdf/topomt/issues/138)

## Scientific and access contract

CAVER 3.02 command-line distribution; ordered original tunnel centerlines and local free radii.
Access/licence: GPLv3 CLI; distinct from Analyst. This is a no-payment local route.
Provider labels do not admit native DFND classification or establish biological
binding relevance, continuous-region geometry or comparative accuracy.

## Public route

Use `topomt.get_provider_output(source, method='caver')` or
`topomt.third_party.caver.get_output(source, ...)`. Follow the
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
