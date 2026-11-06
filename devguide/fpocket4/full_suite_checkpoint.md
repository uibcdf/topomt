# Complete source-suite checkpoint

Date: 2026-11-05. Handoff owner: [#101](https://github.com/uibcdf/topomt/issues/101).
Full qualification remains under [#16](https://github.com/uibcdf/topomt/issues/16)
and [#58](https://github.com/uibcdf/topomt/issues/58).
Tested source: `ca8ad21f726b19cb32644fbc611ff5f48c043f8f`, with the existing
user edit to `topomt/_version.py` preserved byte for byte.

## Complete execution

The entire `tests/` selection collected and executed **2,245 cases** with normal
conftest loading, no deselection and four xdist workers grouped by module.
Python 3.14.7 on Linux x86_64 used source TopoMT and an independent package
prefix containing 141 distributions. Original fpocket execution and the
prepared receptor were available. This is source-suite evidence, separate from
the earlier [144-case installed-wheel control](public_gateways_checkpoint.md).

The complete run finished in **1,078.31 s**, exit 1:

| Outcome | Cases |
| --- | ---: |
| Passed | 2,156 |
| Failed | 8 |
| Skipped | 76 |
| Expected failures | 5 |
| Setup/teardown errors | 0 |

All **144 ArgDigest/original-handoff cases** and all **952 modern CASTp void
measurement cases** passed. The JSONL stream is complete, integrity-valid and
untruncated. JUnit reports 81 skipped cases because it includes the five expected
failures. The 76 ordinary omissions retain their individual reasons, including
absent optional engines/mirrors, CASTp 1.0 oracles, BCIF fixtures and explicitly
deferred analyses. They do not qualify those routes.

## Failure classification

All eight failing selectors were repeated sequentially against pre-ArgDigest
source `edb43579b2a937e1ac5faa7f89876c7ff3c81e5c`, using the same installed
dependencies. Source origins and identical test-file bytes were verified.
All eight fail there with **identical exception messages**:

- Four DFND raw-record characterization hashes differ from their stored
  expectations. Their existing scientific investigation remains under #16;
  no expected hash, tolerance or scientific result was changed here.
- Two addon selection tests reach `MolSysViewer.active_selection.set`, which
  tries to convert an unavailable parent index with `int(None)`.
- Two invalid-input tool tests encounter absent optional `scikit-learn` and
  `scikit-image` distributions before reaching the expected value rejection.

Installing only the declared optional tools and their missing dependencies
added nine distributions, changing none of the original 141 versions.
Both affected modules then passed **20 cases, zero skips/failures**, in 0.15 s;
`pip check` passed. This separate 150-distribution control resolves those two
environment failures; it does not replace the original full-suite outcome.
The six DFND/viewer failures remain unresolved baseline findings.

A standalone public MolSysViewer workflow also reproduces the selection error:
load its bundled pentalanine, then set atom selection `[0, 1, 2]`.
The corresponding `chain_index` values are unavailable. The
[provider issue draft](viewer_selection_issue_draft.md) is prepared for human
review; no new issue was published. Missing indices must not be invented to
make the selection succeed.

## Retained evidence and limits

The [archive](evidence/full_suite_20261105.zip) and
[sidecar](evidence/full_suite_20261105.json) retain commands, package identities,
test-file digests, full and baseline JSONL/XML/logs, skip reasons, optional-tools
receipts and the standalone viewer reproduction. Original wheel bytes remain
in the task-owned temporary namespace; earlier artifact identities are unchanged.

The first attempt lacked OpenMM and was interrupted after 1,092 cases. The
CASTp preparation error also reproduced against the baseline; installing
OpenMM 8.6.1 made both isolated controls pass. A second attempt left no final
XML after a conversation interruption. Neither is counted as a complete run.
The final attempt used pytest-receptor's existing incremental event facility.
Its header labels the explicit `-p xdist.plugin` route as `serial`; the original
argv and `gw0`–`gw3` phase identities retain the actual distributed execution.
Original evidence bytes were not edited to correct that metadata discrepancy.

This checkpoint identifies no failing regression attributable to the ArgDigest
changes. It does not establish a green full suite, hosted CI, another Python
minor/platform, or new installed/public-package qualification. Coverage #81 is
unchanged. The next bounded original-provider receiving work is Pocketeer,
followed by AlphaSpace2 and pyCASTA, retaining argument, source, unit and chemical
context checks for each provider.
