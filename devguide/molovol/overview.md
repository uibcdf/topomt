# Original local MoloVol

Implementation owner: [#190](https://github.com/uibcdf/topomt/issues/190).
Original source: [molovol/MoloVol](https://github.com/molovol/MoloVol), MIT.
The [user guide](../../docs/content/user/molovol.md) defines the public contract.
Broader POVME/PyVOL assessment remains [#159](https://github.com/uibcdf/topomt/issues/159).
This provider work does not advance the independent native review under #187.

## Scientific and API boundary

`get_provider_output(..., method='molovol')` returns `MoloVolOutput` with
original internal rows, total measures, decoded report fields and complete
report text. One-probe Outside remains in the original data; it does not become
an internal cavity or a finite exterior volume. Accessible probe-core and
probe-occupied volumes are distinct. The two Molecular volume rows have
separate keys. Optional surfaces remain absent when not requested.

Two-probe Isolated/Pocket/Tunnel rows retain original labels in the shared
`cavities` collection. A large-probe-defined exterior is not DFND's hull.
Centers are midpoints of original region bounds, not closed supports or proven
clearance witnesses. No native Topography admission or atom-map inference is
made. The initial isolated route admits neutral explicit PDB element fields;
periodic/ionic routes and full OpenDX interpretation are outside this delivery.
Exhaustive scientific/model fidelity remains under #19, and installed/public
qualification under #101/#16. Exclusions are not promises of new capabilities.

## Source and build receipt — 2026-11-11

Consultation checkout: `~/repos@others/MoloVol`, detached and clean at
**`76693ae9c2b44270ae0875cefd96f8c0e9c61246`**. No scientific source was
patched. The initially inspected master and v1.2.0.2 commit
`7b2e508a2b1e06e0b06d56f89fc24e8f849db38c` adds unconditional Windows-console
calls in `src/base_init.cpp`; it was inspected, not claimed to build on Linux.
The selected preceding revision retains wxWidgets compatibility changes and
reports **1.2.0**. Git identity, tag and printed version are separate facts.
Inspect exact revision/dirty state again before any reference update.

The maintainer installed CMake 4.4.5, wxWidgets 3.3.4 and Xvfb in
`molsyssuite@uibcdf_3.14`. The C++ compiler was GCC 15.2. Original CMake's
renderer-off configuration avoids VTK. Its CLI still initializes wxWidgets.
The opt-in tools are declared in `devtools/conda-envs/original_local_env.yaml`,
not mandatory package dependencies.

Reproduce with one build worker, substituting actual checkout/prefix paths:

```bash
cmake -S "$MOLOVOL_SOURCE" -B .cache/molovol/build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DMOLOVOL_RENDERER=OFF -DMOLOVOL_BUILD_TESTING=OFF \
  '-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=-O2 -g0 -DNDEBUG -Wno-error=sign-compare' \
  -DCMAKE_BUILD_RPATH="$CONDA_PREFIX/lib"
cmake --build .cache/molovol/build --target molovol --parallel 1
```

The first bounded compile stopped at `src/atomtree.cpp:148` because GCC 15
promoted a signed-comparison warning to an error. The explicit build flag above
allows that warning without altering scientific source. RelWithDebInfo avoids
the project's automatic Release LTO. The successful original default build
took **76.967 s**, peak child RSS **444604 KiB**, one worker, 6 GiB address-space
and 300-second CPU/wall ceilings. Its unrelated icon target reported missing
ImageMagick `convert`; the CLI built and executed successfully. GUI packaging,
installer/icon production and VTK rendering are not qualified here.

The selected executable is `.cache/molovol/build/molovol`. Default element
resources are resolved beside it at `inputfile/elements.txt`, or selected
explicitly. Both selected executable and original/effective resource hashes
are saved. Private Xvfb uses `-displayfd`, TCP disabled and child-only DISPLAY;
it terminates only its own process in a finally block. The environment's
process isolation blocks Unix socket creation, so actual display tests were
authorized outside that isolation with the same resource limits. Startup is
bounded at 10 seconds and cleanup at 5 seconds before a last own-child kill.

## Frozen original execution evidence

`tests/data/original_local/molovol/input.pdb` contains four carbon dummy atoms,
exact submitted decimal coordinates ±1.874 Å. Its SHA-256 is
`481c34c20a847f91190bf94b94ab9cd25dddda577afefb3d0c4f919c7d6b409c`.
It is not the full-precision BenchLab JSON model. The original resource
`elements.txt` has SHA-256
`92a7e3b352cdece923c054fc07026c5ec74135b8bd8ce071af62741529f0fa8f`;
its carbon radius is 1.77 Å. Explicit C=1.7 Å overrides use a private effective
table; no inherited DFND radius is assumed.

| Saved control | Probe / grid / depth | Original outcome |
| --- | --- | --- |
| `isolated.zip` | 1.4 Å / 0.1 Å / 4, C=1.7 Å, surfaces | Outside plus one Isolated region; occupied 12.036 Å³, accessible core 0.076 Å³. |
| `empty.zip` | 6 Å / 0.3 Å / 4, C=1.7 Å | Completed report with zero internal regions. |
| `two_probe.zip` | 1.4 and 4 Å / 0.2 Å / 4, C=1.7 Å | Five original internal region rows; retain their own types. |
| `table_radii.zip` | 1.4 Å / 0.2 Å / 4, original C=1.77 Å | One internal region; original resource/radii attribution path. |

The initial independent direct pilot took 4.863 s and 41284 KiB peak child RSS.
The four-case designated gate then passed in **26.04 s** (27.728 s including
runner setup; 290004 KiB parent peak RSS). Each case ran through the public API,
then directly through the same original executable with exact captured PDB,
effective table and arguments. Every decoded field matched. Save/load retained
source context and attribution without starting another process.
The input protocol, original report and MIT licence are retained alongside
the bundles. Earlier failures in the test's capture-object inspection were
corrected before reporting a passing gate; they were not scientific failures.

These are adapter/execution controls, not an accuracy benchmark, a DFND
comparison or a claim of synthetic percolation detection. BenchLab inputs,
notebooks, archives and pending scientific questions remain untouched.

## Attribution and recovery guards

The MoloVol paper is DOI `10.1107/S1600576722004988` (Maglic and Lavendomme,
2022). Original element-resource references were inspected in its own header:
Alvarez neutral radii `10.1039/C3DT50599E`, Shannon ionic radii
`10.1107/S0567739476001551`, and Meija et al. atomic weights
`10.1515/pac-2015-0305`. Titles/authors/publication details were checked against
primary records; the weights author list also against the original author
archive. Offline declarations live in `_bibliography.py`.

The neutral-only route credits actually selected non-overridden Alvarez radii
from the recognized table and referenced natural-element atomic weights used.
No Shannon citation is earned without an ionic route. Artificial-element
weights marked unreferenced by the table do not acquire an IUPAC citation.
Unknown custom tables preserve bytes/fingerprints without invented references.
Selected input-data references have `input_data_reference` roles. Completed
empty results are credited, failed calculations are not. Files reading bypasses
new tracking and retains the producer's version and detached bibliography.

`tests/test_molovol_provider.py` guards units, option groups, query/resource
consistency, bounded preflight rejection, own-display cleanup, empty versus
failed outcomes, optional recorder failure/absence and a fresh reader with the
runner/recorder blocked. `tests/methods/molovol/test_original_cli.py` is an
explicit `TOPOMT_MOLOVOL_CMD` gate; a selected absent binary fails rather than
silently skipping. It uses real Ackredit with selected/unselected data citations
and an enclosing capture. Protocol replays are labelled separately from genuine
original execution. Source qualification is not an installed support matrix.

The final selected run passed **294 tests in 60.36 s**, including the four
original gates and earlier providers' parser/argument/recovery/evidence/
persistence/attribution/reporting regressions. Runner-inclusive wall time was
62.173 s, parent peak RSS **340564 KiB**, one CPU/numerical thread, 6 GiB AS and
120 CPU-second limits. The editable shared workspace preserves its pre-existing
human version edit. Ruff passes and all 620 Python files are formatted; scoped
mypy passes 13 affected source files for 3.11 and 3.14 static targets. These
checks do not execute every supported minor. Full suite/coverage/hosted CI and
installed matrices remain under #16/#58/#81/#101; this increment uses `[skip ci]`.

Clean committed-source documentation at
`05910720ee95e9e9bd14a2421bb7c17bcae08a5f` passes strict Sphinx with zero
warnings: **109 pages and 10561 local links**, 21.913 seconds, peak RSS
310552 KiB, one worker. The clean archive imports the committed version, not the
human workspace edit. The [receipt](../evidence/molovol_documentation_2026_11_11.json)
and [archived completion record](../archive/integrate_molovol.md) retain exact
scope. This is not a deployed-site or installed-distribution certificate.
