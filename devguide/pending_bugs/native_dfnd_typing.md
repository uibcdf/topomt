---
summary: Qualify native DFND component, data, base-feature and mesh annotations.
issue: uibcdf/topomt#189
status: open
opened: 2026-11-11
closed:
severity: low
verification: reproduced
area: [dfnd, typing]
guard:
normative:
blocked_by: []
supersedes: []
---

# Native internal typing follow-up

## What

The later comments on #77 collected native typing debt beyond that issue's
original public `Topography` acceptance. This record retains that independent
work when the bounded public-registry correction closes. No numerical defect is
inferred from static diagnostics.

## How

Python 3.14.10, mypy 2.4.1, active MolSysSuite scientific interpreter, with the
checker in `topomt-dev`. From the repository root:

```bash
python -m mypy --config-file devtools/mypy_topography.ini \
  --python-executable /path/to/scientific/python \
  topomt/features/BaseFeature.py topomt/delaunay_mesh.py \
  topomt/dfnd/components.py topomt/dfnd/data.py
```

The 2026-11-11 current check reports **56 diagnostics in four unchanged files**:
BaseFeature 1, mesh 3, components 51, data 1. Two are unresolved SciPy stubs;
the rest are local annotations. MolSysMT is explicitly excepted by the bounded
configuration, with imports followed silently. Selection, dependency policy and
checker revision differ from the earlier 8/19/55-diagnostic invocations; these
counts must not be conflated. Earlier exact-source shadow comparisons remain
in #77's comments and the input-context/physical-boundary checkpoints.

The public-registry selection's success does not claim these imported bodies
are clean. Local diagnostic output is
`.cache/api-maintenance-171-174-77/native_typing_handoff.log`; its summary and
source hashes are retained in `../evidence/api_maintenance_2026_11_11.json`.

## Why

Wet/dry component fields, optional support keys, loop-variable narrowing and
mesh face/tuple types should be truthful without changing runtime structures or
the scientific result. BaseFeature's TYPE_CHECKING import currently treats the
Topography module as a type.

## Policy and priority clarification — 2026-11-11

The [MolSysSuite quality-tooling policy](https://github.com/uibcdf/molsyssuite/blob/main/devguide/python_tooling_policy.md#type-checking-and-runtime-validation)
leaves static checking to each member. Its
[ecosystem policy](https://github.com/uibcdf/molsyssuite/blob/main/devguide/python_ecosystem_policy.md#applicability-and-behavior)
assigns nontrivial public argument validation/normalization to ArgDigest.
Neither requires blanket internal annotations or a clean whole-package mypy
gate. TopoMT's [local instructions](../../AGENTS.md) require public annotations
and applicable local type checks; they do not impose complete private coverage.

ArgDigest validates executed boundary calls. Static checking helps developers
inspect declared types and their use inside implementations. These roles can
complement each other; neither replaces scientific tests or independent
geometric evidence. The 56 recorded diagnostics therefore do not establish
56 runtime/scientific defects, an ArgDigest failure or suite noncompliance.

This issue retains local annotation-maintenance work for deliberate selection,
not a prerequisite for BenchLab or the native scientific sequence. Prefer
focused corrections that clarify the actual object model or prevent a concrete
error. Do not turn this handoff into universal annotation coverage, duplicate
runtime type validation or decorating every internal helper with ArgDigest.

## What was refuted

These are not new diagnostics caused by a scientific-kernel change in the public
typing batch. The four files remain byte-identical to its initial source.
Changing returned data, suppressing all errors or replacing types with `Any`
would not establish meaningful typing.

## Scope and exclusions

Only this native internal selection and its explicit dependency typing policy.
#86 retains CASTp geometry; #16/#58 retain full scientific, installed and CI
qualification. The scientific sequence remains with #187 and its existing
boundary/precision owners.

## Acceptance criteria

Add typed public/internal consumers and any necessary runtime regressions first;
correct local hints/narrowing while preserving shapes, units, index/support
maps, subclasses and scientific definitions. Qualify this bounded selection
without broad ignores and retain the public-registry gate and frozen evidence.
