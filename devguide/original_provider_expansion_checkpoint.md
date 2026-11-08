# Original local provider source checkpoint

Date: 2026-11-07. Work owner [#135](https://github.com/uibcdf/topomt/issues/135).
This is a development-source checkpoint, not installed/public qualification,
native DFND protein characterization or a BenchLab comparison.

## Implemented boundaries

Four new adapters use the original engine/files interface: pyKVFinder, GHECOM,
CAVER and P2Rank. Existing pocket access is preserved; cavity, channel and site
records have their own accessors. Geometry has an explicitly named nm storage
contract and returns physical quantities. Original descriptor units/definitions,
unavailable mappings and provider identities remain explicit.

Source ownership, selection, frame/reference chemistry, PDB export and source
verification reuse MolSysMT and the existing TopoMT provenance tools. ArgDigest
owns closed options and physical/resource admission; DepDigest owns selected
optional Python/executable availability; SMonitor owns diagnostics; PyUnitWizard
owns explicit unit conversions. New saved readers import no optional engine.

The Java runners select/check/execute the same command. P2Rank uses its original
main class directly to preserve the caller's heap limit. GHECOM accepts its
unusual successful return code only under the observed revision and complete
postconditions. Execution failures retain bounded partial original evidence on
the exception; saved failed runs cannot become successful output.

## Actual original execution

All four original pilots used the unchanged 1AKD structure from the official CAVER
distribution. The complete captured runs, original source and checksum receipt
are committed under [tests/data/original_local](../tests/data/original_local).
The independent CSV/grid assertions in
`tests/test_new_provider_evidence.py` compare exposed results to original bytes,
under nm/ps and pm/fs policies, with subprocess execution prohibited on recovery.

| Original engine | Observed output | Complete source execute/save/recover | Maximum observed process RSS |
| --- | --- | --- | --- |
| CAVER 3.02, OpenJDK 21.0.10-internal | 47 retained tunnel profiles | 15.11 s; 1 GiB heap, one processor | 727 MiB |
| P2Rank 2.5.1, same Java | 5 predicted sites | 14.45 s; 1 GiB heap, one worker/processor | 577 MiB |
| GHECOM 2026/08/17 | 41 P-mode morphological pockets | 4.62 s; serial, 1 Å grid, original 1.87/6 Å probes | 285 MiB |
| pyKVFinder 0.9.6+uibcdf.2, NumPy 2.5.4 | 12 grid cavities | 4.42 s; serial, 1 Å grid, original remaining defaults | 283 MiB |

Timings include source conversion and reconstruction in each retained pilot,
not just engine calculation. RSS comes from the enclosing timed process tree's
observed maximum and is not an additive total or a reservation. They are
technical smoke measurements on one input, not speed/accuracy rankings.
Different output counts compare different scientific objects.

Acquired original archives:

| Distribution | SHA-256 |
| --- | --- |
| CAVER 3.02 official ZIP | `2d819541c7e3d3b223de18ba9a5bf2fbfaf92cced380d29e86cd749f7070ee1e` |
| P2Rank 2.5.1 official release | `d243f2d9036ac053fefb9407b5fe1c85f4fe077c519fd975ac585e995feab274` |
| GHECOM 2026-08-17 author's archive | `38cd23271c50b5af079c53c6511248f0b08c82df51128041e37815fc1eb4a10e` |

GHECOM's historical 2021 archive URL returned a missing-file message. The
author's public source at `e1950a405323d069673fe2df445ecd3f41e8651e`
was reviewed instead. Current GCC's default C standard rejected its old-style
prototypes. Unmodified source built with `-std=gnu99 -O2 -g -Wall`, one build
worker, 1 GiB virtual-memory limit and 120 CPU seconds: 12.94 s elapsed,
62 MiB maximum RSS. Its `main` unconditionally returns 1 and its current CLI
uses positional P / cluspock. Its output identifies clusters by MODEL;
the residue number in grid rows is the voxel value 64, not the cluster.
These are source-observed protocol facts, not reasons to discard failures.

## pyKVFinder compatibility fork

The clean consultation checkout is `~/repos@others/pyKVFinder`, upstream
`20add3537319ffd11e5e660a9181dd986651e928` (v0.9.6).
The maintainer requested a compatibility fork:
[uibcdf/pyKVFinder, uibcdf-compat](https://github.com/uibcdf/pyKVFinder/tree/uibcdf-compat),
initial commit `6e192135e887d450b8776a479e8fbc850c6fc211`.
The qualified continuation is `e0f0fa6d32109ebd02d951ef4d7f84f3e1a88fb9`.
Original `main` and scientific kernels are unchanged.
Its clean compatibility checkout is `~/repos@others/pyKVFinder-uibcdf`, tracking
the fork's `uibcdf-compat` branch. Both checkouts share Git objects and preserve
the upstream `origin` plus the separate `uibcdf` remote.

The fork identifies itself as `0.9.6+uibcdf.2`, admits NumPy 2.5, puts already
lazy plotting libraries in an extra and removes unused Cython from build inputs.
After the maintainer installed SWIG 4.5.1/tomlkit 0.15.2, its native build passed
on Python 3.14.10/NumPy 2.5.4. Both upstream unit modules plus our metadata/TOML
controls passed **266 cases**, 35.17 s, about 161 MiB maximum RSS. The same C,
algorithm modules and data remain unchanged in the final source; both locally
built compatibility versions produced an identical native-extension SHA-256
`2c98ef8a500effb64ece4a182d691df6d89e8e603635e25781c6c9f5ff09d0c2`.
All 12 cavity descriptors agree between these builds on the retained input.

The final development wheel built from source `6986f6787fe460afcc2834a600b9085b305b3d95`
has SHA-256 `75ca16857992cb7b9f45572336b6a97d028889b0e0729482d34d837310a01e7f`.
It is not a published distribution. Its qualified extension was also placed in
the compatibility checkout (ignored by Git) so source-root development works
without installing pyKVFinder into the shared environment. Rebuild after native
C/SWIG changes. The optional separate-interpreter route remains available.

The maintainer additionally requested removing the unproven tomlkit <0.16 cap.
The fork now requires `tomlkit>=0.14.0`. A separately downloaded 0.14.0 wheel,
isolated from the shared environment, passed **68** box/hydropathy/export and
metadata/TOML controls in 0.39 s. The shared 0.15.2 passed the full selected
upstream unit modules and direct workflow. Official latest release was observed
as 0.15.2; no future 0.16 runtime compatibility is claimed. This is an explicit
dependency-policy decision backed by actual public load/dump API use, rather
than a claim to have tested unreleased versions.

The designated `tests/methods/pykvfinder/test_original_library.py` source gate
was run with `TOPOMT_PYKVFINDER_ROOT` pointing to the compiled checkout. Both
the direct-original comparison (volumes, areas, interface residues and identity)
and valid-empty source/save/recovery passed. A specified missing/shadowed source
fails the gate; ordinary absent-engine skips do not substitute for this receipt.

## Validation and deferred scope

The selected local checks cover all five older saved-provider families,
new protocols/arguments, source selection/frame/chemistry, alternate units,
engine-free recovery, original CLI bytes, explicit command identity and failed
receipt retention. Three older source-root bypass tests were stale: their
sentinel stopped at PDB export even though reference chemistry now precedes
export. The corrected sentinels stop at the first source boundary without
weakening molecular admission or requiring an installed source-root engine.

The task-owned logs and exact original distribution receipts are retained in
`.cache/third-party-expansion/` for review and subsequent installed qualification.
Final local outcomes: **193 passed** in 50.44 s, including all four original
evidence readers, both actual pyKVFinder source gates and reporting-protocol
checks; about 452 MiB maximum observed RSS. Selected source tests ran with
one CPU, a 6 GiB address-space cap, 120 CPU seconds and one thread per numeric
runtime. The suite-wide conftest warmup and automatic plugin loading were
excluded explicitly; this is the named selection, not the full suite.
The final focused recheck passed another 25 selected cases after explicit
three-coordinate typing and source-origin admission, without rerunning engines
outside the named source gate. Ruff lint and format checks pass repository-wide
(530 Python files formatted),
and the bounded mypy check includes the shared geometry model plus 33 affected
source/test files against the shared Python 3.14 runtime. Fork scientific/TOML
tests are recorded separately; the overlapping 266/68 counts are not additive
and are not included in the 193.

The complete Sphinx build succeeded with one worker, 7.25 s elapsed and about
267 MiB maximum RSS. Its 12 warnings match the previous tetrahedron-study
baseline exactly after path normalization; the new guide and all four method
sections are present in the rendered HTML. Existing documentation/PlantUML
warnings remain #64/#9. No new docs warnings were introduced.

Slurm was inspected before execution; the local node reported inval and the
other nodes unknown, and two immediate bounded allocation attempts failed.
The measured local fallback used OS CPU/address-space/time limits. Available
RAM stayed above 54 GiB with no observed memory pressure or active swap traffic.
The limits applied to these development checks do not reserve resources for
future calls. Full CI/support-matrix recovery remains #16/#58/#81.
No new remote coordinate submission, installed artifact, complete suite, support
matrix, native reproduction or exhaustive descriptor-fidelity claim is made.
Those remain #16/#19/#58/#81 and the existing #101 handoff route.
