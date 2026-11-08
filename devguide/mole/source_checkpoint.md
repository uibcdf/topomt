# Original MOLE source integration checkpoint

Date: 2026-11-08; owner [#140](https://github.com/uibcdf/topomt/issues/140).
This follows the completed four-engine batch #135 as a separately requested
local provider. It does not change those historical receipts or qualify an
installed/public TopoMT package.

## Original producer and acquisition

The clean reference clone
`.cache/mole-originality-review/reference/webchemistry` is pinned to official
`sb-ncbr/webchemistry@fe0e84582a6bd42bc69224fd3a3022bf5c51cec3`.
An isolated `git archive` copy, `.cache/mole-integration/source`, was compiled;
the reference clone and the separate legacy MOLE consultation clone are unchanged.
The MIT licence and original authorship remain intact. The maintained CLI
reports **2.5.26.10.26**; its original source returns a nonzero error status.
It differs from the older .NET Framework CLI assessed in the method review.

The maintainer installed Ubuntu's .NET SDK **10.0.114** and runtime **10.0.14**
on Ubuntu 26.04.1 x86_64. Runtime C# dependencies were restored using the
original project references and NuGet requirements, into the task-owned cache.
No Python environment dependency was changed. The maintained upstream build is:

```bash
dotnet publish AppsAndServices/Tunnels/WebChemistry.Tunnels.Server/WebChemistry.Tunnels.Server.csproj \
    -c Release -o /path/to/output \
    -p:GenerateAssemblyInfo=false -p:UseSharedCompilation=false \
    -p:BuildInParallel=false -p:RestoreDisableParallel=true \
    -m:1 --disable-build-servers
```

The original executable is retained at
`.cache/mole-integration/dist/mole2`; use this explicit path in the current
workspace. Neither the executable nor its libraries are committed into TopoMT.
Recorded SHA-256 identities cover the selected executable and original companion
DLL/configuration files. The build command changes build concurrency/server
behavior only; scientific code and optimization settings are unmodified.
After building, all **260 archived original files** were verified byte-identical
to the pinned clean source. The selected apphost SHA-256 is
`fc496182be3a084ee25bbc2b3c8e4b20e0b3b6bbf8bcd15e5ddb386a841e6eef`;
`WebChemistry.Tunnels.Core.dll` is
`af23a057235e427c5cca22a1b069474031bc8d7fb5c87800c51c966e7cf0a6d9`.
These fingerprints identify this local build, not a published upstream artifact.

## Resource scope

The shared host is `ixtlilton`, 20 logical CPUs and about 62 GB physical RAM.
Before work, available RAM was about 56 GB, measured swap I/O was inactive and
memory PSI averages were zero. Slurm's local nodes were `inval` and its remote
nodes `unk*`; no job was queued. Direct fallback used one OS CPU, one numerical
worker, a 6 GiB address-space limit, a 1 GiB .NET managed heap cap and bounded
CPU/wall time. Serial build servers were disabled rather than left persistent.

Compilation completed in **32.66 s**, maximum RSS **218180 KiB**. The original
distributed 1TQN example completed in **2.18 s** and reports 14 tunnels, 9
cavities and 6 voids. Timings include the stated operation only and are not a
provider-performance benchmark. Source adapter execute/save/recover pilots
completed below 300 MiB maximum RSS; the .NET heap cap is not a total-process
memory guarantee. Resources were reviewed between execution phases.

## Frozen original controls

All files live in `tests/data/original_local/`, with SHA-256 values in
`receipt.json`. They are technical integration controls, not native DFND
characterization or BenchLab protein studies.

| Capture | Unchanged source | Explicit settings | Original output |
| --- | --- | --- | --- |
| `mole.zip` | Existing CAVER-distributed 1AKD `source.pdb` | Original defaults, automatic origins | 2 tunnels; 5 cavities; 8 voids |
| `mole-empty.zip` | Same 1AKD source | `interior_threshold=1000000` angstroms | Completed empty channels/cavity/void collections |
| `mole-1tqn.zip` | Official example `mole_1tqn.cif` | Original defaults plus automatic and merged pores | 14 tunnels, 3 pores, 4 merged pores; 9 cavities and 6 voids |

The high-threshold empty case is an operational control, not a recommended
scientific setting. Separate 1AKD pore-enabled controls produced zero pores;
those valid results were retained rather than substituted with another method.
The official example provides positive original pore/merged-pore evidence.
The 1TQN input is copied byte-for-byte from the pinned official example;
`MOLE_LICENSE.txt` retains the source licence. Earlier CAVER data provenance and
its licence remain unchanged. No service received coordinates.

## Source contract and validation

The adapter admits the reviewed exact CLI version. It requires consistent
original completion markers and successful XML/JSON outputs, preserving the
unversioned `startpoints.xml` root as actually exported. Configuration, source
mapping, stdout/stderr, original JSON/XML/CSV, executable hashes and resource
settings are retained. Saved reconstruction validates existing original-local
source context without subprocesses. No optional engine is imported or probed
when reconstructing saved files.

Parser/argument/runner/source tests are in `tests/test_mole_provider.py`.
Their analytical protocol fixtures do not claim detector evidence. Committed
original reconstruction and explicit quantity conversion under nm/ps and pm/fs
policies are guarded by
`tests/test_mole_evidence.py::test_original_mole_evidence_reconstructs_without_engine`.
The designated `tests/methods/mole/test_original_cli.py` gate uses
`TOPOMT_MOLE_CMD`; specifying an absent engine fails rather than skips. It
compares direct original execution with public adapter output, includes positive
pores and real empty output, and exercises saved reconstruction.

The combined selected source run passed **236 tests in 82.60 s**, with no skips:
43 MOLE cases plus the earlier original-provider parser/argument/workflow/
evidence/persistence/dependency controls and real pyKVFinder source gates.
One CPU and the stated limits were retained; maximum observed RSS was
**488288 KiB**. The initial MOLE-only gate passed 41 cases before adding the
explicit failed-run/CLI-status controls. Tests use the shared Python 3.14.10
environment and Pytest Receptor `--receptor=llm`; `--noconftest` avoids unrelated
suite-wide Numba warming and does not establish a full-suite result.

Ruff passes repository-wide (538 Python files formatted). Scoped mypy passes
15 source/test files with the shared interpreter as its Python 3.14 target.
Complete Sphinx HTML built in **8.00 s**, maximum RSS **275064 KiB**; its 12
warnings exactly match the preceding four-provider baseline after normalizing
task paths. No new warnings were introduced, and the rendered public MOLE guide
was checked for the version and volume-definition text. Existing documentation
warning ownership remains unchanged. Local report indexes and lifecycle guards
are checked separately before publication.

The source implementation is delivered through the principal-maintainer direct
commit/push route with `[skip ci]`. Hosted required checks and coverage were not
run for this increment; existing #58/#81 and exact-candidate recovery retain
ownership. This does not qualify an installed TopoMT distribution or a release.
The shared editable-workspace checks preserve the pre-existing human
`topomt/_version.py` edit; that file is excluded from these commits. They are
not an exact clean installed-candidate qualification.

Full suite, other Python minors/OSes, plotting/viewer behavior, hosted services,
public installation and exhaustive scientific fidelity are not certified here.
Existing #16/#19/#58/#81/#101 gates retain their own scope.
