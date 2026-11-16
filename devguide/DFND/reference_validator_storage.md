# Reference-validator checkpoint storage

Owner [#76](https://github.com/uibcdf/topomt/issues/76), S2/S6 reliability
follow-up after S7. Persistence changes; geometry, topology, integration,
requested precision and native DFND policy are unchanged.

## One reader envelope

All subdivision, serial/parallel power-cell, region-volume, analytic-task and
generic progress bundles now apply one **16 MiB encoded-byte ceiling per JSON
record**, including manifests. JSON escaping, indentation and the final newline
count. No rounding, truncation or omitted constraints make a record fit.

Every data record and manifest is encoded and checked before creating the
exclusive destination. Oversize/non-JSON rejection leaves no new directory;
earlier checkpoints are never overwritten. After writing starts an interruption
can still leave a torn directory, which readers reject. Flush/fsync and publishing
the manifest last do not guarantee durability against every storage failure.

The incremental encoder avoids building the entire output text first. Existing
input objects, individual string chunks and multiple preflighted payloads still
consume memory beyond a single record ceiling. External process/group memory,
CPU and elapsed-time limits remain required; no RAM is reserved by these calls.

## Corrected source scope

At `0ecfd7a`, only the **parallel** power writer allowed 128 MiB while its reader
allowed 16 MiB; earlier plural wording was too broad. Serial power and region
writers already capped data but could create a directory before finding oversize.
Subdivision had no paired size check. Generic S7 progress bounded data but not
its schema-bearing manifest. All these routes now share the bounded encoder;
both power writers delegate to the common manifest-last writer.

Schemas and data encoding remain compatible; manifests can change harmless
formatting. Source-bound work still requires its recorded source/runtime: do not
rewrite kernel identities to resume old checkpoints with new code. The old
source capsules and portable mathematical proofs are preserved unchanged.

An oversized record is an operational limit, never evidence of empty space,
complete topology, reached precision or a finished calculation. Preserve the
last valid checkpoint. Chunked storage or a larger limit would require another
explicit protocol; neither is selected here.

## Receiving and remaining gates

The [versioned record](../evidence/reference_validator_storage_v1/README.md)
retains failing baseline reproductions, actual 16 MiB/one-byte-excess controls,
scaled byte-boundary controls through six routes and fresh independent readers
with producers/scientific packages blocked. The capsule freezes source, exact
Model and bundles for the six small controls.

This is no new nineteen-profile scientific run, four-worker qualification,
S8 completion, native #181/#180/#184/#188 fix or public admission. Earlier
scientific precision and S6/S7 timing records retain their source scope.
Remaining S1/S3/S5 and broader S8/P6/P7 stay under #76; canonical native
receiving remains #76/#60 and installed/platform/full-suite qualification #16.
