# pyCASTA original source and installed receiving

Completed on **2026-11-06** under
[#101](https://github.com/uibcdf/topomt/issues/101), which remains open. This
checkpoint accepts one exact development wheel on Linux x86-64/Python **3.14.10**
for original pyCASTA execution, source-bound saved recovery and an explicit
prepared PharmacophoreMT composition. Native research remains paused.

## Exact candidate and dependencies

| Item | Identity |
| --- | --- |
| Producer | `02a38be58adef184e7d1331093b98e589e0b1f96` |
| Wheel | `topomt-0.5.0+371.g02a38be.dirty-py3-none-any.whl` |
| Size | 21,607,051 bytes |
| SHA-256 | `285e8d928e1ec17f3b1ad760e0cbf6553809c3c79b3a3521248911382047c4db` |
| Build checks | All 639 tracked runtime/resource paths and 643 hashed RECORD entries verified |

The independent build clone differs only in its generated version file. Filename,
metadata and embedded versions agree. The known clean-version transition in
[#78](https://github.com/uibcdf/topomt/issues/78) remains open; this is a stable
development candidate. An initial resource-inventory omission was reproduced by
the existing distribution guard and corrected before building the accepted wheel.
The principal checkout's human version-file edit remained byte-identical.

The original is the **published pyCASTA 1.0.8 wheel**, 42,814 bytes, SHA-256
`486feb6848b7a0949ad114aa675b7ec1c4186c3be06a0ea2665c56ffbaf5d487`.
Its retained source distribution is 42,207 bytes, SHA-256
`2d695be0e6c8e2d4eb0f3db35cca7e0c76fbc094e428ab955ad20d07214a82b2`.
All published Python files passed static parsing. The separate consultation
checkout at `f3418f38cd3d` has an indentation error; it was not used as the engine
or changed during this work.

The controlled profile reuses exact newly source-built MolSysMT and
PharmacophoreMT wheels from the preceding receiving work:

| Dependency | Source commit | Wheel SHA-256 |
| --- | --- | --- |
| MolSysMT `0.23.0+368.g00abb958f` | `00abb958fb93649131d5ce5fe5e12e90cf4900e9` | `60a042df84375752d37c65e961036d78fa13d5f4ea0ddb6e231a7abd447a31a1` |
| PharmacophoreMT `0.4.0+98.gb934471` | `b934471ac8ab8bdb1bd7646550ac23baeb07daa7` | `23c95687942408de58c358c7a9a0e041391ac586f8ef93d502e45e0e5c5b2dcc` |

Other recorded inputs include Biopandas **0.5.2**, Biopython **1.88**,
scikit-learn **1.9.1**, Trimesh **5.2.0**, NumPy **2.5.4**, SciPy **1.18.1**,
Pandas **3.1.1**, Cython **3.2.6** and Pytest Receptor **1.2.2**. Fourteen
hash-pinned wheels supply only previously absent distributions; existing
dependency versions were preserved. The two temporary receivers have the same
**398 Conda records** and **221/220 Python distributions**, differing only by
the deliberately absent pyCASTA distribution. Complete inputs and profiles are
archived. The separate [reconstruction inventory](evidence/pycasta_installed_handoff_20261106_environment.json)
retains acquisition URLs, artifact identities and the distinction between Conda
ownership and embedded build-wheel metadata. Working and shared development
environments were not changed.

Public MolSysMT 0.23.0 lacks the source recorder's `permute_atoms` capability,
as documented by the preceding AlphaSpace2 checkpoint. These source pins do not
establish a public-only installation or compatibility with current sibling mains.

## Executed controls

| Gate | Result |
| --- | --- |
| Controlled source selection | **219 passing tests**, including two reporting-protocol tests |
| Distribution contract | **18 passing tests**, including inventory completeness and package-discovery guards |
| Exact installed selection | **217 collected, executed and passing cases**, zero skips, xfails or deselections; 91.29 seconds |
| Direct original comparisons | Four bundled structures: **2pk4, 1stp, 2ifb and 1hew**, preserving their original submitted PDB bytes, including server job filenames |
| Independent complete flows | Two source flows and two installed flows, first `pm/fs/radians`, then `nm/ps/radians`; **five pockets and four sites per flow** |
| Independent engine-free receiving | Two saved consumers with pyCASTA uninstalled and its package/scripts blocked; **four sites each and zero import attempts** |

The source and installed selections overlap and must not be summed as distinct
coverage. Reported timings describe validation, not throughput or memory
benchmarks; representative performance measurements remain a separate requirement
before making optimization or speed claims. Controls cover route-owned arguments, legacy original syntax
forwarding, full-source/reference/frame admission, ATOM/HETATM correspondence,
original NPZ versus verified tetrahedron maps, malformed and empty saved data,
tagged undefined measurements, detachment and attributed descriptors. An explicit
test-package anchor prevents optional providers' own `tests` package from
shadowing TopoMT helpers; its initial collection failure is retained.

The prepared input is unchanged, SHA-256
`a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`:
4,047 atoms, 4,088 bonds and one reference state at zero. Public MolSysMT tools
permute the full source and declare translated, nonperiodic frame 1. The original
receives 4,003 selected protein atoms with hydrogens retained. No chemistry is
regenerated. Source labels, graph/state, full frames and original pocket records
survive persistence and agree physically under both application policies.

The analytical query explicitly selects **`pycasta:0`**, whose membership role
is **`region_tetrahedron_vertices`**. Public PharmacophoreMT recognition yields
four hydrophobic sites from full-source indices **36, 38, 1453 and 1590**. Each
uses the declared **+X projection of 0.30 nm**, **0.15 nm** radius, essentiality
`True` and weight `1`. Native query roundtrips preserve source/state/frame context.
Saved consumption reproduces the accepted query sites and metadata while keeping
source/bundle bytes and original run IDs unchanged. No feature-family fallback,
membership expansion or geometrical interpretation replaces missing recognition.

## Origins, integrity and retained failures

The detached harness contains only producer-identical tests/developer support
and separately pinned checker support. Parent-process full OriginProbe checks
pass before and after each installed gate: **2,129 → 3,984** loaded modules for
the suite, **2,017 → 3,760** for complete flows, and **2,017 → 2,985** for saved
receiving. PharmacophoreMT is absent before application policy selection.

Original detection runs in an isolated `-I -B` child. Nine retained real original
bundles have **2,117 observed child modules** and **14 loaded original source
files** each. Normal child module paths stay within the receiver, and loaded
original source bytes match the published wheel. Fileless child objects remain
raw observations, including schema-1 stringified `None` origins; complete typed
ownership of those child objects is not claimed.

Before/after file snapshots agree, external links are absent and both prefixes
pass `pip check`. Raw Conda Doctor retains **three regenerated-bytecode findings**
in the main receiver after scientific execution. The unchanged helper classifies
them only after authenticating same-package source and verifying cache headers
and isolated compiled-code equivalence. The accepted engine-free run has no raw
Doctor findings. This is not authentication of every file in either prefix.

Cloning rewrote Cython console launchers and, in the engine-free receiver, the
Trimesh launcher. Their initial RECORD failures remain archived. Reinstalling
the **same hash-qualified wheels** regenerated launchers and RECORDs legitimately;
no checker, RECORD or origin was edited to waive a failure. The failed first
engine-free acceptance stopped before science and is retained separately.

The 77 installed test warnings are declared PDB bond-inference warnings on
structural fixtures. The pre-existing `atom_label.py` invalid-escape SyntaxWarning
and optional beartype absence are also retained. Explicit value contracts ran;
broad runtime annotation checking was not qualified. Ruff, applicable local
mypy, administrative checks and headless HTML build passed; 11 existing
documentation warnings remain.

## Evidence and continuation

The [scientific archive](evidence/pycasta_installed_handoff_20261106.zip),
[inventory](evidence/pycasta_installed_handoff_20261106.json) and
[checksum](evidence/pycasta_installed_handoff_20261106.zip.sha256) retain all
successful acceptance receipts, preceding failures, inputs, original bundles,
queries, source traces, harness and receiving drivers.

- ZIP: **15,530,914 bytes**, **697 members** including its manifest.
- ZIP SHA-256: `2c65515ae6a408974429e8933f8139481c451b65244e37a3465aead665a0fc7f`.
- Manifest SHA-256: `749a950ae04774b1d6c4f43f9a4a8c9e3df77326a98669631189fb243a1442ff`.

The [durable retention receipt](evidence/pycasta_installed_handoff_20261106_retention.json)
records **24 verified primary files, 146,639,710 bytes**, plus manifests/receipts, at
`../topomt-local-backup/qualifications/pycasta-installed-20261106` relative to the
repository root. It includes actual wheels, the original source distribution,
prepared seed and scientific archive. The preflight wheel is explicitly separate
from the accepted final candidate. Durable manifest SHA-256:
`27c029f2b68999fc0ea16c83f2045c5a4457888f73f24b4ef44cd4b85220ed56`.

The [reconstruction supplement receipt](evidence/pycasta_installed_handoff_20261106_environment_retention.json)
separately verifies the environment inventory and the unchanged auxiliary
configargparser wheel: two additional files, 219,956 bytes. Its 398 observed
Conda record hashes match the accepted after-execution snapshot. The primary
manifest and scientific archive remain unchanged.

This profile does not qualify weighted CGAL triangulation, positive mesh/SASA
validation, exhaustive original fidelity, native parity, affinity, biological
relevance, exact closed regions, the full suite or the supported platform/Python
matrix. The published CGAL path is a SciPy placeholder. Rtree/PyMOL are absent;
upstream can turn conditional validation failures into negative outcomes, which
are retained without treating them as physical exclusion. Native
[#53](https://github.com/uibcdf/topomt/issues/53), fidelity
[#19](https://github.com/uibcdf/topomt/issues/19), component/full-suite
#16/#58 and release #78/#81 retain their own gates.

Continue the [provider handoff plan](../provider_handoff_plan.md) with
**CASTp/CASTpFold**, preserving all earlier candidate identities and regression
evidence. The five-provider programme #101 remains open; DFND stays paused.
