# Paired-size checkpoint receiving

Owner [TopoMT #76](https://github.com/uibcdf/topomt/issues/76), S2/S6 reliability
follow-up. [Contract and corrected source scope](../../DFND/reference_validator_storage.md).
Baseline: `0ecfd7a268d1d1c0b53e185615ede8f95b5e5f2c`.

`before.json`/`before.log` retain two failing pre-fix reproductions: the parallel
writer accepts data beyond its reader's ceiling, and a generic manifest can
exceed that ceiling. The serial power/region writers already limited data to
16 MiB; the earlier plural 128 MiB description was too broad. Their preflight
order and subdivision/manifest limits are corrected in this delivery.

All six routes now bound every JSON data/manifest record at 16 MiB before
creating a new exclusive directory. Tests include actual 16 MiB acceptance,
one-byte-excess rejection, JSON escapes/formatting/newline accounting, scaled
exact/excess thresholds through every scientific loader, and preservation of
the previous checkpoint. No rounding or geometric constraint is changed.

The two disjoint regression groups pass **257 tests (179 + 78)**. Two capsule
guards complete **259 distinct selected tests**. The 21 new storage tests include
six fresh scientific-reader subprocesses with site packages disabled and
producers/scientific libraries blocked. `receiving.zip` additionally freezes the
51 source modules, six control bundles/Models and the reader script, then replays
all six from an extracted capsule. `fresh_readers.json` records that execution;
`capsule_manifest.json` binds all members. Raw is a storage-only control; other
routes use the existing exact one-ball Model. No nineteen-profile scientific
run is implied. Source-bound records require the recorded source/runtime.

Runs are sequential on one allowed logical CPU with a 2 GiB address-space
ceiling, finite CPU/elapsed limits and conservative host-reserve monitoring.
`*_execution.json` records parent and waited-child resource scopes; aggregate
child CPU can exceed a per-process CPU ceiling. Five-second group RSS samples
can miss peaks or double-count shared pages. No parallel benchmark or speedup
is claimed. Ruff, the 51-module local mypy route, report-index/offline comparative
checks and strict local single-CPU Sphinx pass; this is not hosted deployment.

`source_qualification.json` and `MANIFEST.json` record source/test/evidence
identity and preservation checks. The original 355 frozen files and prior
capsules are unchanged. Exact drivers are retained before temporary cleanup.
The paired-size defect is resolved at this source scope, not left as a current
pending limitation. Chunked/larger-record storage is not selected. S1/S3/S5,
broader S8/P6/P7, the full parallel panel/four workers, native
#181/#180/#184/#188, canonical #76/#60 and installed/platform/full-suite #16
retain their separate gates. The issue remains partial/open.
