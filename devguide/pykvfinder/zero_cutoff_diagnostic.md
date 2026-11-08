# Zero-cutoff diagnostic and proposed upstream report

Date: 2026-11-08. Observed during [TopoMT #141](https://github.com/uibcdf/topomt/issues/141).
This records a suspected upstream limitation, not a scientific-kernel fix.
The earlier explicit external publication authorization covered the separate
[packaging issue #222](https://github.com/LBC-LNBio/pyKVFinder/issues/222).
Publication of the report below requires its own maintainer authorization.
No external scientific issue or comment has been sent at this checkpoint.

The [comparison notebook](../../docs/content/benchlab/synthetic/regular_tetrahedron/comparisons.ipynb)
and `artifacts/comparisons_v1/` retain exact original input/output, the frozen
initial protocol, separately declared positive-cutoff diagnostic and checksums.
The fork remains clean at `e0f0fa6d32109ebd02d951ef4d7f84f3e1a88fb9`; its scientific
C, algorithm modules and data are unchanged from upstream 0.9.6. TopoMT refuses
the inconsistent original exports; #142 fixes only the failed-receipt status.

## Proposed issue title

Zero volume cutoff on a four-atom input produces zero-volume labels and inconsistent exports

## Proposed issue body

While studying a tiny geometric control, we observed inconsistent exported cavity
labels when `volume_cutoff=0`. Is zero a supported cutoff for this input, or should
the public API require a strictly positive value?

We used the explicitly identified `0.9.6+uibcdf.2` packaging fork from issue #222,
on Linux with Python 3.14.10, NumPy 2.5.4 and tomlkit 0.15.2. Scientific C/Python
algorithm files and the radius dictionary are unchanged from upstream 0.9.6
(`20add3537319ffd11e5e660a9181dd986651e928`). We have not independently reproduced
this in an unmodified supported upstream environment, so the scope remains this
exact compatibility build/input.

Input `input.pdb` contains the following exact four dummy carbon rows:

```text
ATOM      1 C    DUM A   1       1.874   1.874   1.874  1.00  0.00           C
ATOM      2 C    DUM A   2       1.874  -1.874  -1.874  1.00  0.00           C
ATOM      3 C    DUM A   3      -1.874   1.874  -1.874  1.00  0.00           C
ATOM      4 C    DUM A   4      -1.874  -1.874   1.874  1.00  0.00           C
END
```

The original reader warns that DUM is unknown and assigns the GEN carbon radius
1.66 Å to all atoms. Original public workflow:

```python
import pyKVFinder

result = pyKVFinder.run_workflow(
    'input.pdb', step=0.2, probe_in=1.2, probe_out=4.0,
    removal_distance=0.0, volume_cutoff=0.0, nthreads=1,
)
result.export('cavities.pdb', nthreads=1)
result.write('results.toml', 'cavities.pdb')
```

Observed: a warning reports 6112 cavities exceeding the maximum supported 1352
and warns that labels may not be unique. The TOML VOLUME table contains 1352
entries: 1351 zero-volume entries and one `Kgx` entry with volume 79.47 Å³.
The exported PDB contains 9934 grid points, all labelled `Kgx`. Thus PDB and
descriptor label sets disagree. Small-probe values 1.4 and 1.7 also produce
inconsistent exports under the same zero-cutoff protocol.

In a separately declared diagnostic, changing only `volume_cutoff` to
`0.2**3` (one voxel, 0.008 Å³) gives one consistent `KAA` label at each probe.
At probe 1.2, the positive-cutoff descriptor volume is again 79.47 Å³. We do not
interpret these regions as a biological binding site or use a different method's
cavity count as ground truth.

Source inspection suggests a possible boundary interaction: `DFS` returns
immediately at grid boundaries, whereas `_cluster` increments `tag` before DFS
and keeps a zero-volume label when the cutoff is zero. This is a hypothesis,
not a proposed scientific change. Would you prefer rejecting zero explicitly,
or treating boundary-only/zero-volume labels differently?

The controlled input, original receipts and diagnosis are available in TopoMT's
`docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/comparisons_v1/`,
with the rejected zero-cutoff observations and the positive-cutoff diagnostic
kept separate. No scientific kernel was modified to obtain the diagnostic.
