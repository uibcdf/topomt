# Bounded installed fpocket receiving control

Date: 2026-11-05. Scientific owner: [#101](https://github.com/uibcdf/topomt/issues/101).
Distribution follow-up: [#78](https://github.com/uibcdf/topomt/issues/78);
Python/public delivery: [#16](https://github.com/uibcdf/topomt/issues/16).

## Executed result

**32 tests passed, zero skips, zero failures, in 43.79 s** against locally built,
noneditable wheels on Linux x86_64 / Python 3.14.7. The tests ran from a detached
support directory outside every source checkout. They exercised:

- exact atom selection, submitted-to-source mapping and single-frame admission;
- unsupported/missing chemical-state rejection before engine execution,
  reference index 1, chemistry-digest validation and detached source recovery;
- real fpocket execution followed by original ZIP/H5MSM recovery;
- prepared ERalpha/EST pocket membership consumed by PharmacophoreMT's public
  recognition and projection operations, persisted as native JSON under both
  nm/ps and pm/fs unit policies;
- independent site-coordinate/radius assertions, incompatible consumer context
  rejection, source checksum rejection and the incomplete-chemistry negative control.

The prepared execution returned 14 pockets. Its first pocket produced 15
hydrophobic sites under each unit policy, using the already declared analytical
projection of 0.30 nm along +x and radius 0.15 nm. This continues the
[prepared-source control](pharmacophore_handoff_checkpoint.md); it adds installed
receiving evidence without admitting a biological binding model. The separate
3PTB run returned nine pockets; observed counts identify individual executions.

## Original producer and installed files

The original TopoMT producer is `edb43579b2a937e1ac5faa7f89876c7ff3c81e5c`.
Dependencies retain the previously studied MolSysMT
`00abb958fb93649131d5ce5fe5e12e90cf4900e9` and PharmacophoreMT
`b934471ac8ab8bdb1bd7646550ac23baeb07daa7` sources. Independent full Git snapshots
were clean before building. New sibling work was observed and excluded; no
principal sibling checkout or shared installation was edited.

| Local wheel | SHA256 |
| --- | --- |
| `topomt-0.5.0+337.gedb4357.dirty-py3-none-any.whl` | `d767c86274e5cd3b5e055642ff2440433fd01ab15903e505f98bc8c816cbc92b` |
| `molsysmt-0.23.0+368.g00abb958f-cp311-abi3-linux_x86_64.whl` | `29ee31477065db70f0d58085c4598a6b8d66495a06c98e0f23c894bdd9c0c1d9` |
| `pharmacophoremt-0.4.0+98.gb934471-py3-none-any.whl` | `9a18a044fd4c63827619b52af3be9c37112fa397fb8b0ac655729920b5517b45` |

Build isolation used each source's declared requirements, including
`versioningit~=2.0` for TopoMT/PharmacophoreMT. The retained cache inventory records
downloaded tool identities; it does not substitute for a complete per-hook build
environment capture. TopoMT's build changed only its generated version file and
produced the recorded `.dirty` development version. Preserve that observation
and original artifact; investigate build-hook version handling under #78 before
selecting a release candidate. The user's live version-file edit was untouched.

MolSysMT's Rust extension was compiled anew with Rust/Cargo 1.98.1, rather than
reusing the source pilot's host extension. The installed 5,184,304-byte extension
has SHA256 `737086505b2bd3efd982216bcb90d8c8ce45e4ca65dd8a69fdb00baf0b7c6308`.
The original fpocket executable remains the previously recorded 4.2.3 package
binary, SHA256 `18a3a5e78481e572018703fd7e463969dd1cc598464efde18acf30284f5941eb`.

Nine wheels, including the suite support libraries and pytest receptor, were
installed with dependency resolution disabled into an exclusive temporary
prefix. Ordinary external packages came from the existing Conda site-packages
through a plain path entry; their editable hooks were not executed. All required
TopoMT resources (609) occur in its wheel, and no unexpected package root occurs.
Before and after science, 5,117 installed RECORD hashes matched across the nine
distributions, and wheel digests matched installation receipts. Loaded suite
modules resolved inside the new installed prefix; no editable finder was loaded.

The shared import checker at MolSysSuite
`b9852d973e96613a68cab7278491ff647bfd0b7d` checked the other suite roots unchanged.
It initially rejected the fileless `pyunitwizard.main` compatibility alias.
The task recorder therefore checks every loaded PyUnitWizard file origin and
the alias's two generator-function code origins separately, against its installed
`__init__.py`. No module, alias or shared checker was rewritten. This bounded
adaptation is retained explicitly; it does not claim the unmodified generic
checker accepts that provider alias. A reusable checker improvement belongs in
MolSysSuite, with this case as consumer evidence.

## Retained evidence and remaining gates

The [archive](evidence/installed_receiving_20261105.zip) retains scientific output,
the exact detached test support and task scripts, build/install/test logs,
before/after import and file checks, source pins, tool-cache identities and a
member-digest manifest. Its [sidecar](evidence/installed_receiving_20261105.json)
binds the original producer and wheel digests. The copied scientific helpers keep
their historical source-profile names and limits; the enclosing installed
receipt supplies this execution's additional provenance.

Original wheel bytes remain in
`/dev/shm/topomt-installed-101.bch3yxd8/wheels`. That is temporary local retention,
not a durable artifact service or public package route. The evidence archive
contains their identities, not the wheels themselves. Retain those exact bytes
before any further qualification; a future rebuild is a different candidate.

The declared dependency-route preflight passes with the accepted SDK
`8f00e6d9de943b6e4710ea62936e2ebea00fad24`. It covers the maintained declarations,
not a newly admitted acquisition route for these scientific source pins. All 50
active direct requirements across the installed wheels satisfy their metadata
constraints. `pip check` still reports the same seven inherited Amber-related
missing/conflicting requirements from the shared external package set. The
pre-existing invalid-escape SyntaxWarning in `topomt/_private/atom_label.py`
also remains observable.

This is a bounded installed receiving control with shared external dependencies.
A clean source-free dependency closure, full scientific suite, declared Conda
artifact, hosted gates, macOS arm64 and Python 3.11–3.13 remain unqualified here.
No dependency floor, release plan, public version/support claim or issue closure
was introduced. Full-suite/hosted recovery remains under
[#58](https://github.com/uibcdf/topomt/issues/58). The upstream
[negative-charge parser report](https://github.com/Discngine/fpocket/issues/188)
remains separate from installed receiving success.
