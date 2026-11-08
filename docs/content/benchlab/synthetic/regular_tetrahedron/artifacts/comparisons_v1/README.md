# Original comparison evidence, version 1

This is the evidence for the [comparison notebook](../../comparisons.ipynb),
owned by [TopoMT #141](https://github.com/uibcdf/topomt/issues/141).

- `protocol.json`: fourteen rows committed at `59bc96c` before new original
  topography execution. Frozen coordinates/radii and all previous case artifacts
  retain their hashes. This PDB export does not encode the native atomic radii.
- `model_audit.json`: original pyKVFinder read_pdb radius 1.66 Å and maintained
  MOLE source default 1.61 Å versus native 1.7 Å; GHECOM/CAVER effective DUM
  assignments remain unverified. Exact revisions and source links are included.
- `initial_attempt/`: unchanged first attempt. The study driver incorrectly
  stopped remaining pyKVFinder controls after one control failed. Its rejected
  files also exposed TopoMT #142's completed-metadata receipt defect. Retain this
  directory for historical inspection; do not use those failed receipts as
  successful output. The corrected planned set is `original_observations/`.
- `original_observations/`: all fourteen planned rows, with ten actual executions
  and four correctly skipped controls following failed CAVER/MOLE standards.
  Successful empty collections have zero accepted records. Failed/invalid/skipped
  rows have no inferred counts. Each actual submitted PDB and original bundle is
  retained, including stdout/stderr and available parameter files.
- `positive_cutoff_protocol.json`: post-observation hypothesis, committed at
  `a8065a7` before executing this diagnostic. It changes only pyKVFinder's zero
  cutoff to one voxel, (0.2 Å)³. `positive_cutoff_observations/` retains all three
  results separately; none replaces a failed predeclared control.
- `evidence_receipt.json`: hashes of protocols and original artifacts, source
  producer, resource limits and measurements. Drivers briefly overlapped on the
  same single CPU. These wall times are receipts, not a performance benchmark.
- `comparison_report.json`, `atomic_models.png`, `original_grid_regions.png`:
  executed notebook report and exact displayed figures. Rerunning the notebook
  displays fresh verified observations without replacing any artifact.

## Download the original files

Read the [planned observations](original_observations/observations.json),
[separate diagnostic observations](positive_cutoff_observations/observations.json)
and [initial attempt history](initial_attempt/observations.json). Each ZIP below
contains the exact submitted input, original available result/diagnostic files
and a checksum manifest. A failed ZIP is for inspection, without accepted output.
The four skipped controls have no invented bundle. Physical-value records retain
their units in the same object.

| Current planned execution | Original capture |
| --- | --- |
| pyKVFinder standard | [Completed empty](original_observations/pykvfinder-standard/original.zip) |
| pyKVFinder zero cutoff, small probe 1.2 Å | [Rejected results](original_observations/pykvfinder-probe-1p2/failed.zip) |
| pyKVFinder zero cutoff, small probe 1.4 Å | [Rejected results](original_observations/pykvfinder-probe-1p4/failed.zip) |
| pyKVFinder zero cutoff, small probe 1.7 Å | [Rejected results](original_observations/pykvfinder-probe-1p7/failed.zip) |
| GHECOM standard | [Completed empty](original_observations/ghecom-standard/original.zip) |
| GHECOM small probe 1.2 Å | [Completed region](original_observations/ghecom-probe-1p2/original.zip) |
| GHECOM small probe 1.4 Å | [Completed empty](original_observations/ghecom-probe-1p4/original.zip) |
| GHECOM small probe 1.7 Å | [Completed empty](original_observations/ghecom-probe-1p7/original.zip) |
| CAVER standard | [Failed origin/shell calculation](original_observations/caver-standard/failed.zip) |
| MOLE standard | [Failed four-atom calculation](original_observations/mole-standard/failed.zip) |

| Post-observation diagnostic | Original capture |
| --- | --- |
| pyKVFinder one-voxel cutoff, small probe 1.2 Å | [Completed region](positive_cutoff_observations/pykvfinder-one-voxel-1p2/original.zip) |
| pyKVFinder one-voxel cutoff, small probe 1.4 Å | [Completed region](positive_cutoff_observations/pykvfinder-one-voxel-1p4/original.zip) |
| pyKVFinder one-voxel cutoff, small probe 1.7 Å | [Completed region](positive_cutoff_observations/pykvfinder-one-voxel-1p7/original.zip) |

The initial attempt is retained for audit rather than mixed with the corrected
planned set: [pyKVFinder standard](initial_attempt/pykvfinder-standard/original.zip),
[rejected pyKVFinder 1.2 Å](initial_attempt/pykvfinder-probe-1p2/failed.zip),
[GHECOM standard](initial_attempt/ghecom-standard/original.zip),
[GHECOM 1.2 Å](initial_attempt/ghecom-probe-1p2/original.zip),
[GHECOM 1.4 Å](initial_attempt/ghecom-probe-1p4/original.zip),
[GHECOM 1.7 Å](initial_attempt/ghecom-probe-1p7/original.zip),
[CAVER failure](initial_attempt/caver-standard/failed.zip) and
[MOLE failure](initial_attempt/mole-standard/failed.zip).

Standalone figures: [atomic-model implications](atomic_models.png) and
[original grid regions](original_grid_regions.png). The case index links the
reviewed quantity-aware comparison report.

## Deliberately repeat original execution

The ordinary notebook requires no original engine. To run engines, first inspect
shared resources, then provide a JSON file with local location options only:

```json
{
  "pykvfinder": {"upstream_root": "/path/to/reviewed/pyKVFinder"},
  "ghecom": {"ghecom_cmd": "/path/to/ghecom"},
  "caver": {"caver_home": "/path/to/caver", "java_cmd": "/path/to/java"},
  "mole": {"mole_cmd": "/path/to/mole2"}
}
```

pyKVFinder optionally accepts `python_cmd` for its interpreter. No scientific
parameter overrides are accepted in this location file. Keep one numerical
thread, one OS CPU and a conservative process memory/time limit, as declared in
the protocol. From the repository root:

```bash
python devtools/benchlab/run_regular_tetrahedron_comparisons.py \
  --tools tools.json --output /tmp/tetrahedron-original-repeat
python devtools/benchlab/run_regular_tetrahedron_comparisons.py \
  --tools tools.json --positive-cutoff-diagnostic \
  --output /tmp/tetrahedron-positive-cutoff-repeat
```

Existing output directories are refused. This case-specific driver is an
experiment orchestrator, not a new scientific method or benchmark framework.
It uses TopoMT's public original-provider APIs. Record unavailable engines as
unavailable; do not install a substitute algorithm to manufacture a result.
No service submission, polling, full synthetic panel or protein study is part
of these commands. The historical six-provider report remains separate.

## Original implementations and licences

The reviewed executions use pyKVFinder `0.9.6+uibcdf.2` (packaging fork, original
kernels/data unchanged), GHECOM `2026/08/17`, CAVER `3.02` with Java 21 and
WebChemistry Tunnels/MOLE `2.5.26.10.26` with .NET 10. The saved engine receipts
identify executable/module/dictionary bytes when the process completed; the
failed MOLE bundle retains its original version header in stdout.

Original source qualification and licence references remain in the repository:
`devguide/original_provider_expansion_checkpoint.md`, `devguide/mole/source_checkpoint.md`
and `tests/data/original_local/README.md`. Original pyKVFinder, CAVER and MOLE
licence texts are retained with those molecular controls. GHECOM's LGPL-3.0
licence and exact source identity are recorded in `devguide/ghecom/overview.md`
and `tests/data/original_local/README.md`.
No executable, Java runtime, .NET runtime or full source tree is redistributed
here. Original input/output and diagnostic bytes retain their identity. Presence
in this unit does not qualify an installed TopoMT package or all tool versions.
