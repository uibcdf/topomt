# Effective atomic radii: original-reader follow-up

The [comparison notebook](comparisons.ipynb) left two assignments explicitly
unknown at its checkpoint. This follow-up, owned by
[TopoMT #143](https://github.com/uibcdf/topomt/issues/143), resolves the radii
actually assigned by the retained GHECOM and CAVER input readers. Earlier inputs,
notebooks, observations and figures remain byte-for-byte unchanged.

## What the original readers assign

The control uses the frozen four-atom `ATOM`/`DUM` export. A separate variant
changes only atom-name columns 13–16 from `C   ` to ` C  `, preserving all
coordinates, ordering, element fields and other bytes. The four-row
[protocol](artifacts/radius_audit_v1/protocol.json) was committed at `6808516`
before execution. The paired result is:

| Original reader | Original atom name `C   ` | Aligned atom name ` C  ` | Direct evidence |
| --- | --- | --- | --- |
| GHECOM 2026/08/17 | 1.87 Å for all four atoms | 1.87 Å for all four atoms | Original `-opdbin` export explicitly writes assigned atomic radii to occupancy. |
| CAVER 3.02 | 1.70 Å for all four atoms | 1.70 Å for all four atoms | Original public `PdbFileFactory`, `PeriodicTable` and `Atom.getRadius` operations, using the default CLI reader route. |

Alignment does **not** change the numerical radius in either tested route. That
observation is specific to this input, table and version; it does not establish
that atom naming never matters.

GHECOM illustrates why comments are insufficient evidence: an explanatory
comment in `Radius.c` shows an older generic fallback of 1.50 Å, whereas the
actual included `defradius_Chothia1976.h` ends in `xxxx xxx 1.87`. Its carbon
pattern also assigns 1.87 Å. The original executable confirms the current table's
value. Selected source files were checked against the retained author's archive
byte-for-byte; no scientific source was edited.

CAVER's actual default reader constructs `PdbFileFactory(PeriodicTable)` and
uses `removeAltConf=true`. Inspection of the original bytecode identifies that
route; the Java caller invokes those public operations directly and implements
no radius rules. The periodic element table's carbon radius is used. The
residue-specific `AtomRadii` constructor is a different route and is not silently
selected for this audit. No tunnel calculation is run by that caller.

## Why this matters at our three probes

For the **rounded PDB** coordinates, applying the independently justified regular
tetrahedron formulas to these equal-ball assignments gives:

| Input ball model | Face clearance | Central residence clearance | At 1.2 Å | At 1.4 Å |
| --- | --- | --- | --- | --- |
| GHECOM-assigned radii, 1.87 Å | 1.190229 Å | 1.375863 Å | Room inside, faces sealed. | No room inside the finite cell. |
| CAVER-assigned radii, 1.70 Å | 1.360229 Å | 1.545863 Å | Room inside and through faces. | Room inside, faces sealed. |

Both equal-ball models have no room in the finite cell for a 1.7 Å probe.
The [native full-precision reference](system.ipynb) instead uses explicit 1.70 Å
balls and edge 5.3 Å: face clearance 1.359956 Å, residence clearance 1.545574 Å.
The small CAVER-model difference above is the disclosed PDB rounding effect.

These are **independent ball-model implications**, not new predictions or accepted
topography outputs from either detector. They explain why GHECOM's empty 1.4 Å
control cannot fairly be scored against DFND's sealed 1.4 Å reference as though
the atomic geometry were identical. At 1.2 Å the implied face-transit regime also
differs before considering the methods' different geometric operators.

Matching CAVER's atom radii to the reference does not remove its previously
recorded origin/shell failure or establish a continuous tunnel. Original radius
assignment, molecular approximations, probes, region operators and public labels
remain distinct. No native kernel or upstream scientific code is changed, and
no superiority, count-accuracy or solvent-volume claim follows.

## Original evidence and reproducibility

The [quantity-aware report](artifacts/radius_audit_v1/report.json) stores four
assigned-radius arrays, coordinates, original capsule identities and independent
clearances. The [receipt](artifacts/radius_audit_v1/receipt.json) covers original
files, protocol and exact executed driver. Reading these records requires no
original engine. Each capsule is input-reader evidence for `ProviderRun.load`,
not a source-bound accepted pocket/channel result for `load_provider_output`.

| Audit row | Original capsule |
| --- | --- |
| GHECOM, original name | [Reader and original files](artifacts/radius_audit_v1/original_readers/ghecom-original/reader.zip) |
| GHECOM, aligned name | [Reader and original files](artifacts/radius_audit_v1/original_readers/ghecom-aligned/reader.zip) |
| CAVER, original name | [Reader and original files](artifacts/radius_audit_v1/original_readers/caver-original/reader.zip) |
| CAVER, aligned name | [Reader and original files](artifacts/radius_audit_v1/original_readers/caver-aligned/reader.zip) |

The [separate aligned PDB](artifacts/radius_audit_v1/input_aligned.pdb) and protocol
preserve the exact perturbation. GHECOM's normal tiny P-mode invocation also
performs its default calculation; those files are retained but only its exported
input radii are interpreted here. This is not another comparative probe sweep.

An [initial receiver attempt](artifacts/radius_audit_v1/initial_reader_attempt/ghecom_input_model.zip)
and its [failure record](artifacts/radius_audit_v1/initial_reader_attempt/attempt_record.json)
remain explicit. GHECOM successfully wrote its original radius export, but its
nonnumeric `REMARK` metadata caused general MolSysMT PDB reading to fail. The
compatibility/diagnostic question is handed off in
[MolSysMT #654](https://github.com/uibcdf/molsysmt/issues/654). The corrected audit
reuses TopoMT's existing original-provider point reader for that geometric export;
MolSysMT still reads the actual standard input coordinates for verification.
No output metadata is removed or rewritten to hide the initial failure.

To deliberately repeat the original-reader audit, review shared resources and
use the same pinned original tools. From the repository root:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  taskset -c 0 prlimit --as=4294967296 --cpu=60 -- \
  python devtools/benchlab/audit_tetrahedron_radii.py \
  --tools tools.json --output /tmp/tetrahedron-radius-repeat
```

The JSON admits only location keys `ghecom_cmd`, `caver_home`, `java_cmd` and
`javac_cmd`. The original jar, atom table, GHECOM executable and Java caller must
match the protocol hashes. Existing output directories and hidden scientific
overrides are refused. Java uses one processor and a 128 MiB heap; commands have
20-second timeouts. The observed complete paired run took 3.74 seconds, with
maximum observed process RSS about 151 MiB. These are operational receipts,
not cross-method performance measurements or reserved machine resources.

This bounded input audit resolves the two previously unknown assignments. Native
volume precision #75, the independent reference panel #76, complete synthetic
characterization and later protein studies retain their own gates. The certified
closed shell remains the next native reference, followed by a separately justified
opening in that same frozen wall.
