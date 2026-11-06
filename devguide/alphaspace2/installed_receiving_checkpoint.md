# AlphaSpace2 exact installed receiving on the new host

Completed on **2026-11-06** under the original-provider programme
[#101](https://github.com/uibcdf/topomt/issues/101), which remains open. This
checkpoint accepts one exact installed development candidate on Linux x86-64
with Python **3.14.10** and the dependency profile below. It follows the
[prepared source checkpoint](handoff_checkpoint.md), preserving its chemical
input, scientific calls, policies and numerical comparisons.

## Candidate and acquisition

Producer: `5ae5c46d94e425eab24b2aeb8420a4f3b697eebe`.

| Artifact | Identity |
| --- | --- |
| TopoMT wheel | `topomt-0.5.0+367.g5ae5c46.dirty-py3-none-any.whl` |
| Size | 21,597,426 bytes |
| SHA-256 | `de94e54776bd2222ab6444f7a29aab9f43aa05a77755282c1203191873abb277` |
| Content checks | 636 hashed wheel RECORD entries; 632 source/resource paths checked |

The wheel was built in an independent clone. Its filename, distribution
metadata and embedded version agree. The initial clean-version transition
reproduced the known generated-file problem in
[#78](https://github.com/uibcdf/topomt/issues/78); that failed preflight is
retained. This stable development candidate does not resolve the release
version gate. The human edit to the working clone's `topomt/_version.py` was
preserved byte for byte.

The public MolSysMT **0.23.0** profile stopped before original-engine execution:
it does not expose `permute_atoms`, which the prepared source recorder uses.
The accepted profile therefore uses newly built, installed wheels from the
recorded source commits:

| Dependency | Source commit | Installed version | Wheel SHA-256 |
| --- | --- | --- | --- |
| MolSysMT | `00abb958fb93649131d5ce5fe5e12e90cf4900e9` | `0.23.0+368.g00abb958f` | `60a042df84375752d37c65e961036d78fa13d5f4ea0ddb6e231a7abd447a31a1` |
| PharmacophoreMT | `b934471ac8ab8bdb1bd7646550ac23baeb07daa7` | `0.4.0+98.gb934471` | `23c95687942408de58c358c7a9a0e041391ac586f8ef93d502e45e0e5c5b2dcc` |

Both wheels passed payload/RECORD checks. MolSysMT was rebuilt with Rust
**1.99.1**, independently of the historical toolchain; these are new wheel
bytes, not reproductions of lost historical wheels. Sibling checkouts and
their compiled extensions were preserved. Public PharmacophoreMT 0.4.0 also
uses a different MolSysMT hydrogen-bond API from the pinned consumer. No
public-only or current-sibling compatibility claim follows from this profile.

The original engine was **AlphaSpace2 0.1.2**, installed from the retained
locally built original-engine wheel, SHA-256
`82933999551c2ef67b7c24fbf7214c3e775a55b37a297f418cff73e383a69eff`.
All 19 package files, including 12 Python files, match the retained public
source distribution byte for byte. This is not a claim that the wheel itself
was published upstream. The profile also uses MDTraj **1.11.1**, Cython
**3.2.6**, configargparser **0.0.2**, ArgDigest **0.17.1**, DepDigest **0.15.2**,
PyUnitWizard **0.29.1**, SMonitor **0.22.1**, NumPy **2.5.4**, SciPy **1.18.1**,
Pandas **3.1.1**, RDKit **2026.9.2** and Pytest Receptor **1.2.2**. Exact
artifacts, acquisition receipts and complete inventories are in the evidence.
Optional beartype is absent; explicit argument contracts ran, but broad runtime
annotation checking was not qualified.

## Executed acceptance

The controlled source run passed before installed receiving. Fresh installed
processes then ran from an isolated harness copied from the producer's Git
blobs, with no TopoMT source tree or editable distribution available to them.

| Gate | Executed result |
| --- | --- |
| Installed adapter and shared contracts | **256 collected, executed and passing cases**, zero skips, xfails, failures or deselections; 82.97 seconds |
| Independent complete original-to-consumer flows | Two flows, first `pm/fs/radians`, then `nm/ps/radians`; **13 pockets and two donor query sites each** |
| Independent saved-result receiving | Two complete saved consumers with AlphaSpace2 and MDTraj distributions absent and their imports blocked; **zero engine import attempts**, two sites each |
| Dependency consistency | `pip check` passed for both receiving prefixes after acceptance |

The installed test selection includes all four AlphaSpace2 argument,
input-context, saved-output and PharmacophoreMT-handoff modules, the shared
dispatch/output/handoff tools, and eight direct-original comparisons. It does
not select the full scientific suite or native parity battery. The 59 warnings
are retained: 49 declared PDB bond-inference warnings from structural fixtures
and 10 original AlphaSpace2 undefined-occupancy divide warnings. The 256 cases
overlap earlier source batteries and must not be added to historical counts as
distinct coverage.

Both complete flows use the exact prepared seed, SHA-256
`a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`.
Its full source has 4,047 atoms and 4,088 bonds; the original engine receives
4,003 protein atoms with hydrogens retained. The recorder preserves reference
state 0 and constructs the declared translated, nonperiodic frame 1. It does
not repeat chemical preparation. Source correspondence, chemistry, physical
coordinates and original snapshots agree under both unit policies.

The selected pocket is `alphaspace2:20`. Recognized acceptors at source atom
indices **1674** and **1707** produce two ligand-donor query sites through the
same explicit **+X, 0.30 nm** projection, **0.15 nm** radius and **−X** donor
orientation. The same lining membership has no hydrophobic features, and this
negative control remains empty. No atoms, radii or tolerances were broadened.
Saved recovery preserves original run identifiers and source/bundle bytes,
including the native-query serialization roundtrip.

## Import and file integrity

Each acceptance process verifies the installed candidate hash and import
origins before and after its scientific work. The recorded loaded-module
counts are **2,125 → 4,078** for the suite, **2,013 → 3,856** for the complete
flows, and **2,013 → 2,991** for saved receiving. PharmacophoreMT is not loaded
before application policy is set. Explicit generated-module attestations are
bound to installed owning bytes; origins and module registries are not
rewritten. The first installed attempt stopped before science because an
attestation owner was not yet loaded. Its receipt and the narrowly revised
owner configuration are retained separately.

Before/after integrity checks combine native Conda Doctor, pip-owned RECORD
entries, launchers and link snapshots. Snapshots agree and contain no external
links. **Raw Conda Doctor still reports regenerated bytecode**: four files in
the main prefix and one in the engine-free prefix. These are classified only
after authenticating their same-package source, checking bytecode headers and
comparing their code to an isolated compilation without execution. This is
neither a raw-Doctor-clean result nor authentication of every file in a prefix.
The engine-free prefix matches the main Conda closure and pip distributions
except for the two deliberately absent original engines; its initial missing
RDKit closure and exact repair inputs are also retained.

## Evidence and retention

The [scientific ZIP](evidence/alphaspace2_installed_handoff_20261106.zip),
[inventory](evidence/alphaspace2_installed_handoff_20261106.json) and
[checksum](evidence/alphaspace2_installed_handoff_20261106.zip.sha256) retain
the sources, original bundles, queries, harness, drivers, frozen acceptance
wrapper, inventories, successful receipts and preceding failed attempts.

- ZIP: **10,575,173 bytes**, **279 members** including its manifest.
- ZIP SHA-256: `b77ffe51b3a2a54e8f78e6e5ff0eb4bbfb71d815979a74b34f1082de76099a19`.
- Manifest SHA-256: `8211d8fe999c418abc8f3f9180e5c95b289e1f9dab9801a2dd4bda742cb319e8`.

The actual seven wheels, two source distributions, prepared seed and scientific
archive/sidecars are also retained outside the temporary prefixes at
`../topomt-local-backup/qualifications/alphaspace2-installed-20261106`, relative
to the repository root. The [retention receipt](evidence/alphaspace2_installed_handoff_20261106_retention.json)
records **13 verified files, 113,815,343 bytes**, plus the durable manifest and
receipts. Durable manifest SHA-256:
`5bf7c8782aa0c2d4808361c291f0b6cea1934a6dadfac389461d39eef1c0fd22`.
These new retained candidates do not restore missing historical wheel bytes.

Documentation closeout passed dependency-route, broadcast and report-index
checks, both reporting-protocol tests, and the HTML build with headless Java.
The build retains 11 existing documentation warnings; these checks do not
replace the scientific acceptance above or clear the documentation backlog.

## Remaining scope

This one prepared receptor and explicit analytical query do not establish
affinity, biological relevance, an exact closed pocket region, exhaustive
provider fidelity, a full source suite, public release qualification, or the
supported operating-system/Python matrix. Issues
[#16](https://github.com/uibcdf/topomt/issues/16),
[#58](https://github.com/uibcdf/topomt/issues/58),
[#78](https://github.com/uibcdf/topomt/issues/78),
[#81](https://github.com/uibcdf/topomt/issues/81) and general original fidelity
[#19](https://github.com/uibcdf/topomt/issues/19) retain their own gates.

Continue the [provider handoff plan](../provider_handoff_plan.md) with pyCASTA,
then CASTp/CASTpFold. DFND and native-method research remain paused.
