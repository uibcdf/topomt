# Public fpocket gateway contracts

Date: 2026-11-05. Owner: [#101](https://github.com/uibcdf/topomt/issues/101).
Producer: `4a55982f9eb8d7b4cfa70104dd7d71a5314c72d6`.

`get_topography` and `get_pockets` now have auditable ArgDigest routing plans.
They preserve case-insensitive `cli`, `wrapper`, `native`, `topomt` and the default
CLI route. Invalid types/routes raise a catalogued argument error, also catchable
as `ValueError`, before delegation. Files recovery remains a separate route.
The public file wrapper admits the owning loader's option names and leaves
value digestion to that loader. Native/variant options remain explicitly
delegated; their value contracts and algorithmic parity are not qualified here.

Internal calls pass an already admitted route without repeating its digestion.
A test-first follow-up caught a duplicated bypass keyword: `get_output` now
consumes that control explicitly and rejects nonboolean values before delegation.
Original CLI/files input values still reach their owning argument contracts.

The initial test run reproduced 16 failures and eight passing compatibility cases.
The final new module has 29 cases covering route/alias preservation, early
rejection, option identity, the file-name domain, inspectable plans and bypass
handling. Both bypass follow-up cases failed before correction.

The wider source battery passed 269 cases, five deliberate exclusions and zero
executed skips before the final bypass correction. Final contract checks pass
112 cases. These are separate scopes, not one claimed 271-case source run.
Ruff lint/format passes across 427 files; scoped mypy passes six modules with
imported bodies skipped; Sphinx succeeds with eight existing warnings.
Resource and dependency-route declarations are unchanged from the
[previous stage](argument_contracts_checkpoint.md).

The exact new wheel passes **144 installed cases, zero failures/skips, in 40.30 s**:
29 new gateway cases, 83 existing argument/dispatch cases and all 32 original-engine
and scientific handoff cases. Its independent package environment passes all
required-resource, before/after RECORD and loaded-origin checks across 138
distributions. `pip check` reports no broken requirements. Existing PDB inference
and invalid-escape diagnostics remain; no chemistry or native parity is inferred.

The [archive](evidence/public_gateways_20261105.zip) and
[sidecar](evidence/public_gateways_20261105.json) retain wheel identity, copied
tests/helpers, science outputs, logs, XML, task scripts and member digests.
The observed development wheel is `0.5.0+344.g4a55982.dirty`; its version build-hook
caveat remains under [#78](https://github.com/uibcdf/topomt/issues/78). Original
bytes remain at `/dev/shm/topomt-installed-101.bch3yxd8/gateways/wheels`, temporary
local retention. Earlier artifacts and the user's version edit remain intact.

The initial host test process stalled on dependency disk I/O and was stopped
after matching its command. Executed evidence uses the independent package
environment. This is bounded Linux x86_64/Python 3.14 receiving; full hosted,
Conda/public, other-minor/platform and native-value/parity qualification remain
separate under [#58](https://github.com/uibcdf/topomt/issues/58) and
[#16](https://github.com/uibcdf/topomt/issues/16). No remote issue or branch changed.
