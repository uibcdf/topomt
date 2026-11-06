# Original-provider dispatch through ArgDigest

Date: 2026-11-05. Owner: [#101](https://github.com/uibcdf/topomt/issues/101).
The user prioritized secure argument digestion and authorized this first stage.
The implementation is local commit `f7f4947` (use the full producer identity in
the [artifact sidecar](evidence/argdigest_dispatch_20261105.json)).

## Boundary implemented

`topomt.get_provider_output` now has an auditable ArgDigest plan. Ordered
pipelines call TopoMT's owning `method` and `backend` digesters with the dispatch
caller identity. Method digestion precedes the method-dependent backend check.
Invalid types, unsupported methods and incompatible original routes fail before
the selected provider is imported. The diagnostic inherits TopoMT's catalogued
`ArgumentError` and retains `ValueError` compatibility.

Method aliases, case-insensitive names, default backends and CASTp file imports
without an explicit molecular source remain supported. Provider molecular
objects, array selections and keyword names/values are forwarded unchanged.
The dispatcher disables generic name rewriting and argument-centric digestion
for this stage; its two explicit ArgDigest pipelines own routing validation.
This uses the provider's supported pipeline-only mode, not a local decorator or
compatibility implementation. No direct beartype decoration was added.

The function contract explicitly delegates additional keywords. Optional-library
adapters can expose dynamic upstream options that this dispatcher cannot enumerate
without resolving their provider. This stage therefore does not claim that all
provider keyword/value contracts are digested. Direct fpocket API/CLI/files
entry points and their specific inputs remain the next bounded migration; source
frame, atom correspondence and chemical-state admission remain with their owners.

## Provider requirement and packaging

The qualified minimum is ArgDigest >=0.17.0. The old scientific pin
`c604ce387fe60558ceb51a3016892e7a10686504` lacks explicit `argument_digestion`
selection. Both scientific source inputs now use the exact 0.17.0 commit
`c7128f09b2fe064b6c5603d1077dbd2cec52223d`. Its `argdigest` runtime tree is
identical to the previously tested `cd9c4f3...` source:
`5d0ac16a88baf0690a0da3384cc61471d9742965`. This is the qualified consumer floor,
not a claim that every routing primitive first appeared in 0.17.0.

Metadata, recipe, ordinary generated environments and the specialized base test
environment are aligned. The shared generator reports no remaining changes.
The source-input hashes are updated; all other source pins are preserved.
Declared preflight passes for 19 routes, 12 source records and seven contexts.
Actual hosted execution of those source contexts remains separate evidence.
Suite dependency-graph receiving remains coordinated under the existing
[#78](https://github.com/uibcdf/topomt/issues/78) distribution follow-up; no
sibling governance inventory was edited here.

The runtime resource inventory now covers 613 files: the three new dispatch
modules and the earlier fpocket `input_context.py` omission are included. The
earlier wheel already contained that context module; its mandatory resource
inventory was incomplete. No earlier artifact or receipt is relabeled.

## Validation and exact new artifacts

Test-first execution reproduced 19 failures and 11 passing compatibility cases.
The final dispatch module has 33 passing cases, covering rejection before provider
import, validation order, every default backend, aliases, optional source input,
array identity, delegated keyword names and an inspectable contract. The new
dependency-floor test also failed before the metadata change.

The wider source/context/provider selection passed 185 cases with five deliberate
exclusions. Its single additional failure was the reporting subprocess under
`PYTHONSAFEPATH`; both reporting checks passed separately in the ordinary command
environment. Final dispatch/reporting checks pass 35 cases. The final dependency,
reporting and full distribution-control selection passes 26 cases. These records
do not turn the original 186-case invocation into an entirely green invocation.

Complete Ruff lint and format checks pass across 421 files. Mypy 2.3.1 passes five
affected modules with imported bodies skipped. Full Sphinx generation succeeds
with 12 existing warnings; the incremental update after the minimum-version edit
succeeds with eight warnings. The edited engine guide has no diagnostic.

A new TopoMT wheel was built from the exact implementation commit in an independent
clean Git snapshot, preserving the user's generated-version edit. Its observed
development version is `0.5.0+340.gf7f4947.dirty`; the existing generated-version
build-hook caveat remains under #78. A separate exact ArgDigest 0.17.0 wheel was
built. Both filenames, sizes and SHA256 values remain in the sidecar. The original
suite wheels are unchanged and retained separately.

Against these two new installed wheels in the independent package environment,
**65 tests pass, zero skips/failures, in 39.96 s**: the 33 routing cases plus all
32 original-engine/scientific handoff cases. Both persisted consumer policies
retain 15 hydrophobic sites. All 613 required resources occur in the wheel.
Before/after checks cover 26,213 RECORD hashes across all 138 distributions and
all loaded runtime file/package origins. `pip check` reports no broken requirements.
The same 36 declared-edge PDB inference warnings and the pre-existing invalid-escape
SyntaxWarning remain documented; no chemistry was fabricated to remove them.

The [evidence archive](evidence/argdigest_dispatch_20261105.zip) contains declarations,
copied tests/helpers, scientific outputs, XML results, logs, provenance receipts,
task scripts and member hashes. Original new wheels remain at
`/dev/shm/topomt-installed-101.bch3yxd8/dispatch/wheels`, temporary local retention.
No full-suite/hosted, other-minor/platform, Conda/public-package or complete
ArgDigest migration claim follows. Recovery owners remain
[#58](https://github.com/uibcdf/topomt/issues/58) and
[#16](https://github.com/uibcdf/topomt/issues/16). No remote branch or issue changed.

The subsequent [specific argument stage](argument_contracts_checkpoint.md) adds
the original fpocket API/CLI/files contracts and 115 installed passing cases in
a new candidate. This dispatch-stage artifact and its earlier scope remain intact.
