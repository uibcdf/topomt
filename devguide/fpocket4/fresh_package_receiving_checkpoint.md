# Fresh-package fpocket receiving control

Date: 2026-11-05. Owner: [#101](https://github.com/uibcdf/topomt/issues/101).
Distribution follow-up: [#78](https://github.com/uibcdf/topomt/issues/78),
[#16](https://github.com/uibcdf/topomt/issues/16) and
[#58](https://github.com/uibcdf/topomt/issues/58).

## Outcome and unchanged candidate

The same **32 tests pass in each of two environment profiles**, with zero skips
or failures: 38.04 s with declared dependencies alone, then 39.06 s after enabling
the optional type-checking dependency. These are two executions of the same
32 tests, not 64 distinct tests. Original fpocket, persisted H5MSM/ZIP recovery,
reference-state controls and the prepared PharmacophoreMT consumer all execute.
Both unit policies retain 15 hydrophobic sites with the declared analytical
0.30 nm projection and 0.15 nm radius.

The original nine suite/support wheels from the
[earlier installed control](installed_receiving_checkpoint.md) were reused byte
for byte. No candidate was rebuilt, relabeled or replaced. The original TopoMT
producer remains `edb43579b2a937e1ac5faa7f89876c7ff3c81e5c`; all installation
receipts match the [original wheel manifest](evidence/installed_receiving_20261105.json).

## Isolated package closure

A new virtual environment disables system and user site-packages. It reuses
Python 3.14.7 and its standard library, but has no path to the shared external
site-packages and no editable hooks. The detached test support is unchanged;
its fixture-data link addresses the newly installed TopoMT resources.

Resolution selected 137 distributions, including the nine local wheels. Every
input is retained as an exact URL and SHA256 in `resolved-inputs.txt`; installation
used `--no-deps --require-hashes` against that frozen resolution. Selected external
versions include NumPy 2.5.4, SciPy 1.18.1, pandas 3.1.1, Pint 0.26.2,
RDKit 2026.9.1, mmcif 1.2.1 and pytest 9.2.0. This measures compatibility with
those actual packages; it establishes no new minimum supported versions.

The wheel-only resolution could not obtain nglview. Allowing source distributions
for nglview and mmcif completed resolution. Their exact public source archives
were built locally; mmcif required CMake 3.31.6, Flex 2.6.4 and Bison 3.8.2 in
separate temporary build-tool directories. The original failures and successful
build logs are retained. These tools were not installed into the runtime prefix
or the principal development environment. The two resulting external wheels
retain their own hashes and original local bytes.

`pip check` reports **No broken requirements found** before and after science.
The earlier seven Amber-related conflicts do not occur in this package closure.
Before and after the first execution, 25,784 RECORD hashes match across all 137
distributions. Every loaded file-backed runtime module and package search path
is checked against the new prefix or the explicitly allowed standard-library
and detached support locations. The prior, separately documented PyUnitWizard
compatibility-alias check remains in place without altering the shared checker.

The metadata-only profile has no beartype: ArgDigest reports its optional runtime
type checking as disabled. Its scientific control still passes. A second
sequential profile adds beartype 0.22.9 from PyPI, retains the first profile's
receipt, and repeats the same tests. Its 138 distributions and 26,210 RECORD
hashes match before and after; beartype loads from the new prefix, and the
disabled-type-check diagnostics disappear. Beartype remains optional support
inside ArgDigest, not a replacement argument-validation layer in TopoMT.

Both executions report 36 `PDBBondInferenceWarning` instances because an optional
legacy inference engine is absent: only declared edges are retained. The prepared
H5MSM positive control and the incomplete-PDB negative control both pass. No
connectivity completeness or chemistry is fabricated to suppress these warnings.
The pre-existing invalid-escape SyntaxWarning in `atom_label.py` also remains.

## ArgDigest priority and observed gap

The user clarified that secure digestion through ArgDigest is the priority.
A read-only audit of the original installed candidate finds no `digestion_plan`
on `topomt.get_provider_output`, `fpocket.api.get_output`,
`fpocket.cli.get_topography` or `fpocket.files.load_topography`. The provider
modules also report no decorated functions through ArgDigest's own audit tool.
Calling the dispatcher with an integer `method` or `backend` raises `AttributeError`
from `.lower()`, before reaching an engine, rather than an ArgDigest diagnostic.

This is a concrete integration/diagnostic gap, not evidence of an exploit or
silent scientific corruption. Existing local admission guards protect the
tested selections, frames and chemical-state cases; the passing battery does
not certify complete ArgDigest coverage.

The next code change should declare function/keyword contracts and per-argument
digestion at these boundaries, following the
[canonical guide](../../ARGDIGEST_GUIDE.md). Preserve optional/default and legacy
files semantics, provider ownership of source-dependent checks, supported array
inputs and early rejection before original-engine execution. Add failing cases
first, retain the 32-case scientific control, and use ArgDigest's optional type
checking rather than decorating these APIs directly with beartype. Review the
actual consumed provider capabilities before changing any dependency floor.

## Evidence and limits

The [archive](evidence/fresh_package_receiving_20261105.zip) and
[sidecar](evidence/fresh_package_receiving_20261105.json) preserve both scientific
executions, before/after provenance, acquisition/build/install logs, exact task
scripts, copied support, prepared seed, ArgDigest audit and member digests.
Original suite wheels remain at the earlier task artifact path; the two built
external wheels remain under that task's `clean/external-wheels` directory.
These are temporary local artifact locations, not durable public hosting.

This closes the shared-Python-package limitation for this bounded Linux x86_64 /
Python 3.14 receiving control. It does not establish a public source-free
acquisition route for the local suite wheels, an independently provisioned
interpreter/OS, a Conda candidate, full scientific or hosted gates, other Python
minors, macOS arm64, or complete argument-contract coverage. The human version
edit, principal environments, sibling worktrees and project dependencies remain
unchanged. No remote publication, issue closure or support claim follows.

The subsequent [ArgDigest dispatch stage](argdigest_dispatch_checkpoint.md)
implements method/backend admission in a new candidate and records 65 installed
passing cases. The earlier artifacts and audit above retain their original
identities; the direct-provider boundary migration remains incomplete.
