---
summary: Give the two straight-tube inputs descriptive identities and migrate the active reader.
issue: uibcdf/topomt#182
status: resolved
opened: 2026-11-10
closed: 2026-11-10
severity: low
verification: measured
area: [dfnd, data, docs]
guard: devtools/tests/test_dfnd_synthetic_catalog.py::test_straight_tube_names_preserve_exact_input_and_generator
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

## Verification checkpoint

The two exact PDB digests and generator coordinates/radii pass the catalog
guards. All 304 frozen study/previous-case/archive files retain their bytes
after relocation. The generic scientific DFND modules (24 files) are unchanged.
Complete canonical raw hashes on four controls match a clean pre-migration
87af3c8 source export exactly; the four old golden expectations were already
stale and remain owned under #16. They are not updated by this delivery.

The focused 70-item selector gives 67 passes and three existing strict pending
tube targets (#180 twice, #181 once); seven affected viewer tests pass. A larger
149-item run and one 58-item viewer batch hit the selected 120 CPU-second
ceiling, so their incomplete progress does not qualify those whole selections.
Further GUI/full-suite and installed/platform qualification stays under #16.
No parallel workers were used; numerical work was limited to one CPU/thread
with 6 GiB address-space ceilings.

Both current notebooks execute independently inside the source tree and from
the exact 368-file current ZIP in /tmp using clean source 107c291. Their HTML
reference/native tables agree. Original input hash and independent certificates
are unchanged; their current names are supplied by identity.json and a new
reader protocol. Ruff and scoped helper typing pass; current issue/card/method
links are reconciled without changing finding lifecycle states.

## Resolution — 2026-11-10

Current catalog/data names, resource inventory and active consumers now use the
two descriptive identifiers, with no former catalog aliases. The narrow/dense
BenchLab directory, reader protocol, download, maintained method/case links and
issue/finding summaries use its current identity. Four small relocation pages
preserve previously published generic study URLs.

Old literal names remain only in immutable historical input/archives and Git
history. The frozen input.json contains the captured original catalog identity;
rewriting it would change its SHA-256 and every reference/observation binding.
The current identity.json supplies the maintained descriptive name instead.
Original archives and all 304 frozen evidence files are unchanged.

Strict clean-source Sphinx succeeds without warnings: 100 pages and 9,185 local
links checked. Exact portable, preservation, raw-before/after, checks and live
finding readback receipts are in devguide/evidence/straight_tube_*_v1.json.
This closes the naming migration, not physical/all-atom or full-suite work;
#180/#181 and wider #76/#16 retain their current owners and dispositions.

## Public closeout

Pages run 42963825201 succeeds at source 99e5b80. Actual current case pages
and the new download verify; its SHA-256 matches the exact 368-file ZIP tested
outside the checkout. Four published prior URLs expose current relocation links.
See devguide/evidence/straight_tube_names_public_v1.json. Issue #182 is closed;
#180/#181 and the broader #76/#16 scopes remain open.
