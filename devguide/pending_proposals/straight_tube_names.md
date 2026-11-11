---
summary: Give the two straight-tube inputs descriptive identities and migrate the active reader.
issue: uibcdf/topomt#182
status: active
opened: 2026-11-10
closed:
severity: low
verification: inspected
area: [dfnd, data, docs]
guard:
normative:
blocked_by: []
supersedes: []
---

# Descriptive straight-tube names

## What

The maintainer approves `straight_tube_narrow_dense` and
`straight_tube_wide_sparse`, and requests removal of former names wherever
possible. Names describe center placement, without assuming a physical channel
or a successful analysis. The generic `cylinder_tube` generator remains unchanged.

## How

Rename both catalog PDB/docs, construction registrations, resource inventory,
tests and active guidance. Migrate the narrow-tube BenchLab directory and current
reader/download; retain minimal relocation pages for already published URLs.
Keep frozen input/reference/native bytes and published old archives unchanged.
Use explicit current identity metadata around the unchanged captured model.

## Why

Both radial size and sampling differ: narrow/dense has ring radius 3.5 Å,
nominal spacing 2.5 Å and 81 atoms; wide/sparse has radius 6 Å, nominal spacing
3.5 Å and 77 atoms. Their shared nominal length is 20 Å. Their names must not
encode a probe-dependent finding or a judgment about correctness.

## What was refuted

A filename change does not require regenerating atomic coordinates or running
the full 73-system catalog. Replacing strings inside frozen quantity records,
certificates or original observations would change provenance and invalidate
checksums. Former catalog filenames need no supported aliases; historical
scientific evidence and immutable Git history retain their captured identities.

## Scope and exclusions

Naming and receiving continuity only. No scientific operator, query, attribution,
original-provider run, new wide-tube study or closure of #180/#181/#76/#16.
The original three-case notebook/artifact/archive bytes stay unchanged.

## Acceptance criteria

New registrations/files and real consumers resolve without former active catalog
aliases. Guard exact PDB identity and generator geometry, unchanged reference
replay and native supports, current notebook sources/outputs and complete
download integrity. Run appropriate bounded tests, Ruff/scoped typing, report/
finding checks, independent notebook kernels and strict documentation validation.
Reconcile maintained issue/card/method links without changing scientific finding
states. Publish [skip ci] source commits and verify public pages/download.
