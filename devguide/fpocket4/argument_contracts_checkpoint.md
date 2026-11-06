# Original fpocket argument contracts

Date: 2026-11-05. Owner: [#101](https://github.com/uibcdf/topomt/issues/101).
Implementation: `75eb36bbd8d93d4059b6ce673a7e73adc6785da5`.

## Implemented boundary

The original `fpocket.api.get_output`, `cli.get_topography` and
`files.load_topography` now have auditable ArgDigest plans. The API's named domain
reads the CLI/files signatures lazily and admits their union of option names.
Each closed route then enforces its own signature. Unknown names, including
misspellings, raise ArgDigest's `UnknownArgumentError` before input work.

The API checks routing and names; each leaf digests values once through an
explicit argument registry. This preserves argument ownership without globally
changing the legacy TopoMT digesters. No local digestion engine, scientific
algorithm, optional dependency or direct beartype decoration was introduced.
The qualified ArgDigest >=0.17.0 requirement and exact provider wheel from the
[dispatch stage](argdigest_dispatch_checkpoint.md) remain unchanged.

Value contracts cover selection and frame shapes, syntax, executable name,
additional argument strings, file paths, metadata, submitted atom indices and
saved chemical context. Boolean, fractional, negative, nested/ragged or duplicate
index inputs are rejected as applicable. Explicit frame axes contain one index;
legacy `None`/`all` frame selectors still require source-dependent admission.
Paths and argument strings reject empty or embedded-NUL values where applicable.
Only the reference selector or a nonnegative integer chemical-state index is
admitted; the actual reference remains a source-dependent check.

Files recovery preserves omitted chemical options. Saved context must have the
declared keys, integer reference/count relationship and SHA256 shape before
parsing. Source identity, chemistry and coordinates are still checked by the
existing molecular/provider code. Selection arrays retain their identity/order;
submitted maps normalize to integer lists without mutating their input arrays.
Additional CLI options remain subject to the original engine's option semantics.

Test-first review also reproduced that metadata could reach parsing with reserved
source-context keys. `provider_metadata` can no longer replace selection, frame,
syntax, serial/submitted maps or chemical-context fields through the public files
loader. Additional annotation fields remain supported. The CLI constructs its own
metadata and passes literal `skip_digestion=True` only on its internal recovery
call, after validating or constructing those values. Physical source-agreement
checks remain active; no new source reference or connectivity is invented.

## Executed validation

The first test-first run had 45 failures and one passing compatibility case.
The metadata guard separately reproduced two failures before its fix. The final
module passes **50 cases**, including rejection before source work/parsing,
unknown-keyword diagnostics, direct-route plans, legacy omission, array ownership,
canonical syntax/argument sequences and the internal bypass.

The complete selected source/context/provider/dependency/governance battery passes
**242 tests, five deliberate exclusions, zero executed skips**, in 95.97 s.
The separate full distribution/reporting controls pass 20 cases. Complete Ruff
lint/format passes across 426 files; scoped mypy 2.3.1 passes six affected modules
with imported bodies skipped. Sphinx generation succeeds with eight existing
warnings and no diagnostic for the edited engine guide. The runtime inventory
and wheel include all 617 required resources.

A new wheel was built from an independent clean snapshot of the exact producer,
then installed only into the task's independent package environment. Its observed
development version is `0.5.0+342.g75eb36b.dirty`, retaining the existing generated
version build-hook caveat under [#78](https://github.com/uibcdf/topomt/issues/78).
The user's live generated-version edit remains unchanged.

The installed candidate passes **115 tests, zero skips/failures, in 38.14 s**:
50 specific argument cases, 33 dispatcher cases and the 32 original-engine and
scientific handoff cases. All 26,217 RECORD hashes across 138 distributions and
loaded module/package origins match before and after execution. `pip check`
reports no broken requirements. Original fpocket, reference-index-1 recovery,
prepared-source recognition and both persisted unit policies execute. The 30
declared-edge PDB inference warnings and the existing invalid-escape SyntaxWarning
remain visible; they do not become chemical-readiness or biological claims.

The [evidence archive](evidence/fpocket_arguments_20261105.zip) and
[sidecar](evidence/fpocket_arguments_20261105.json) retain exact wheel identity,
declarations, copied tests/helpers, scientific outputs, XML results, logs, task
scripts, before/after checks and member digests. Original wheel bytes remain in
`/dev/shm/topomt-installed-101.bch3yxd8/fpocket-arguments/wheels`, temporary local
retention. Earlier candidates and evidence have not been relabeled or replaced.

## Remaining scope

This qualifies the original published execution/recovery boundaries above, not
every helper or legacy native gateway. Native/TopoMT variants, direct parsed-result
assembly, other providers' argument contracts and exhaustive original fidelity
remain separate. Molecule interpretation and source-dependent agreement continue
to belong to their established owners. No full hosted suite, other Python minor,
macOS arm64, Conda/public acquisition, release or complete-library ArgDigest claim
follows. Recovery remains tracked in [#58](https://github.com/uibcdf/topomt/issues/58)
and [#16](https://github.com/uibcdf/topomt/issues/16). No remote issue or branch changed.
