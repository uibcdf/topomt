---
summary: Shallow Topography copies share nested registry indexes and relation sets.
issue: uibcdf/topomt#74
status: resolved
opened: 2026-10-01
closed: 2026-10-01
severity: high
verification: measured
area: [topography, registry]
guard: tests/test_topography_registry.py::test_shallow_copy_registry_mutations_are_independent
normative:
blocked_by: []
supersedes: []
---

# Topography shallow-copy registry ownership

## What

`Topography.__copy__` copies index/relation dictionaries without copying their
nested sets. Registry mutation through the copy corrupts the original indexes.

## How

Reproduced at `7bd47faba6179a6e02444331e442acd251572564` on Python 3.13.14:

```python
from topomt import Topography
from topomt.features import Pocket

original = Topography(features=[Pocket(feature_id='POC-1')])
copied = original.copy(deep=False)
copied.remove_feature('POC-1')
# list(original) remains ['POC-1']; its pocket type index becomes empty.
```

On a fresh pair, rename in the copy to `POC-renamed`; original type lookup then
raises `KeyError('POC-renamed')`. Copy each registry-owned nested set explicitly;
the DFND `Components.copy(deep=False)` path provides an existing local pattern.

## Why

This breaks independent registry mutation and threatens future participant and
relation ownership under #60/#61. Passing deep-copy tests do not guard this path.

## What was refuted

The failure does not require DFND, a provider, MolSysViewer or a molecular input.
Deep copy is not the failing operation. An unconditional deep copy would change
the intentional sharing contract of scientific payloads.

## Scope and exclusions

Fix shallow registry/index/relation ownership and owner rebinding. Do not redesign
Topography or make arbitrary scientific arrays immutable in this bounded issue.
Native snapshot/cache ownership is separately tracked in #60.

## Acceptance criteria

Add failing pytest regressions first. Add/remove/rename/replace/connect through
either copy preserve the other's Mapping, filters, relations and owners. Retain
deep-copy coverage and explicitly document allowed shallow payload sharing.

## Resolution (2026-10-01)

`Topography.__copy__` now copies every nested membership/adjacency set in the
five registry-owned index and relation maps. Copied feature objects retain
independent owners and relation fields. Other analysis attributes still use
their existing shallow-copy behavior; this correction does not recursively
duplicate scientific payloads.

Before the implementation change, the guard failed in all ten combinations
of add/remove/rename/replace/connect and mutation through original/copy.
After the correction, the registry module passes **23 tests**. The guard
checks the untouched Mapping, all three filter indexes, parent/child views,
feature relation fields and owner references. Separate tests retain deep-copy
coverage and demonstrate nested analysis-payload sharing in shallow mode.

The copy docstring describes this ownership boundary. Direct mutable views,
native array/cache snapshots and public support/context adoption remain #60;
this resolution does not close that broader contract.
