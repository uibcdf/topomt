# Moving TopoMT development to another machine

This handoff preserves the local development branch, human work and committed
scientific evidence. It also identifies what must be reconstructed and qualified
on the receiving machine. Read [onboarding](onboarding.md),
[status](status.md) and [the environment guide](packaging_and_environments.md)
alongside these transfer steps.

## Source baseline and local work

The reviewed scientific baseline on 2026-11-06 is
`87fd192b03f36b0e24a279450fab3c60620244bd`, branch
`work/fpocket-handoff-101`. It is 35 commits ahead of local `main` and
`origin/main` at `0f82d5adfae73ae24846f713ab5bf62782a4f1ad`.
The branch has no tracking upstream. An `origin` remote exists for the public
TopoMT repository; the working branch is not present in the published branch
snapshot recorded by [status](status.md). A fresh clone of published `main`
therefore omits this local development history.

The human modification to `topomt/_version.py` is deliberately separate from
committed work. Its SHA-256 is
`91af00335ecf06be1573c95e22dbba13bfaa0a9e472ffa3de802cee87dc38baf`.
Do not replace it with the committed file or regenerate it during environment
setup without preserving the edit. The filename is generated during packaging,
but its current content is still human work.

Commit the reviewed documentation changes before producing the transfer bundle.
The exported HEAD will then be later than the scientific baseline above; record
that actual HEAD rather than hardcoding the baseline as the final transfer
identity. A Git bundle contains committed objects and refs, not uncommitted
changes or untracked files. Review `git status` and preserve any additional
uncommitted work separately before using this recipe.

## Export committed history and the human version patch

Run these steps at the chosen transfer moment. Choose a new directory on
**durable storage outside the repository**. Do not use `/tmp` or `/dev/shm` as
the sole transfer location.

From the source repository root, after checking that the reviewed documentation
is committed and the remaining local change is the preserved version edit:

```bash
set -eu
topomt_transfer_dir=/absolute/path/on/durable/storage/topomt-transfer
mkdir -p "$topomt_transfer_dir"
test ! -e "$topomt_transfer_dir/topomt.bundle"
test ! -e "$topomt_transfer_dir/human-version.patch"
git status --short --branch
git rev-parse HEAD > "$topomt_transfer_dir/source-head.txt"
git diff --binary HEAD -- topomt/_version.py > "$topomt_transfer_dir/human-version.patch"
sha256sum topomt/_version.py > "$topomt_transfer_dir/human-version.sha256"
git bundle create "$topomt_transfer_dir/topomt.bundle" --all
git bundle verify "$topomt_transfer_dir/topomt.bundle"
```

Review the patch and compare the version-file digest with the preserved digest
above. Then generate transport checksums with relative filenames:

```bash
cd "$topomt_transfer_dir"
sha256sum topomt.bundle human-version.patch human-version.sha256 source-head.txt > SHA256SUMS
```

Keep `SHA256SUMS`, the bundle and the separate patch together. The bundle also
contains the committed evidence ZIPs. It does not contain local Conda/virtual
environments, caches, credentials or external source trees. No remote write is
needed to produce this local transfer.

## Receive and verify the checkout

Use a destination where `topomt/` does not already exist. From its parent:

```bash
set -eu
topomt_transfer_dir=/absolute/path/to/received/topomt-transfer
(cd "$topomt_transfer_dir" && sha256sum -c SHA256SUMS)
git clone --branch work/fpocket-handoff-101 "$topomt_transfer_dir/topomt.bundle" topomt
cd topomt
test "$(git rev-parse HEAD)" = "$(cat "$topomt_transfer_dir/source-head.txt")"
git bundle verify "$topomt_transfer_dir/topomt.bundle"
git apply --check "$topomt_transfer_dir/human-version.patch"
git apply "$topomt_transfer_dir/human-version.patch"
sha256sum -c "$topomt_transfer_dir/human-version.sha256"
git status --short --branch
```

A bundle clone initially points `origin` at the bundle file. Restore the intended
repository transport explicitly, for example:

```bash
git remote set-url origin https://github.com/uibcdf/topomt.git
git fetch origin
git branch -vv
```

Fetching updates remote observations without merging or resetting the received
working branch. A clone can create an upstream pointing at a branch from the
bundle; remove that inherited tracking relationship if it does not correspond
to a real reviewed remote branch. The original working branch had no upstream.
Set a new upstream only when the intended published working branch is chosen;
`origin/main` is not a substitute for preserving the 35 local commits.
Remote configuration does not authorize pushing, merging or releasing.

## Evidence that survives the transfer

The committed `devguide/` inventory contains **18 evidence ZIPs**, totaling
**30,332,025 compressed bytes**. The migration audit verified CRC, safe member
paths and **971 payload hashes/sizes** against their manifests, with no errors.
Archives use different historical manifest/sidecar schemas: `bytes` and `size`
can describe sizes, and `members` can be either a count or a hash mapping. Read
the actual schema rather than treating all sidecars as one interchange format.

| Committed artifact | Available scientific material |
| --- | --- |
| [AlphaSpace2 prepared consumer](alphaspace2/evidence/alphaspace2_prepared_consumer_20261106.zip) and [sidecar](alphaspace2/evidence/alphaspace2_prepared_consumer_20261106.json) | Verified prepared seed, full sources, original bundles, public native query JSON, explicit recipes, two unit-policy flows and source test evidence. Archive SHA-256 `e5ed2e08b84d46995fb2159f86e7815676004ac7d7ccaf28cc7a490c6712d790`. |
| [Pocketeer installed receiving](pocketeer/evidence/pocketeer_installed_handoff_20261106.zip) and [sidecar](pocketeer/evidence/pocketeer_installed_handoff_20261106.json) | Prepared seed, sources/bundles/models, executed installed receipts, dependency identities and selected dependency wheels. Archive SHA-256 `3b1aac470c4c6e49e76350f69967b8662fe7c9e0aeee0d1c2e23b8013381ed37`. |
| [fpocket fresh-package receiving](fpocket4/evidence/fresh_package_receiving_20261105.zip) and [sidecar](fpocket4/evidence/fresh_package_receiving_20261105.json) | Prepared seed, both declared source/consumer profiles, original bundles and model JSON, build/install evidence and source pins. Archive SHA-256 `4e00e49aa4dc63776e8e6c0252a494b9cc258c9fa993c9e58064948ea37040ed`. |
| [AlphaSpace2 saved-output evidence](alphaspace2/evidence/alphaspace2_saved_output_20261106.zip) and [sidecar](alphaspace2/evidence/alphaspace2_saved_output_20261106.json) | Bound/unbound structural sources, original bundles, independent pre-refactor witnesses and engine-free recovery evidence. |

Older fpocket and Pocketeer archives retain additional sources and queries.
Follow their overview/checkpoint links from the [reference catalogue](reference_catalog.md).
Historical absolute paths inside logs and drivers identify where those results
ran. They are not requirements for the directory layout of the new machine.
Preserve archived bytes; adapt a copied recorder's input/output paths when
performing a new execution and retain that execution's separate receipt.

### Recover the prepared receptor safely

The historical prepared seed is available inside the AlphaSpace2 prepared archive
as `inputs/prepared.h5msm`, with SHA-256
`a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a`.
The following standard-library operation reads only that named member, verifies
its checksum and creates a new output file without overwriting one. Run it from
the received repository root after replacing the destination path:

```bash
python - /absolute/path/on/durable/storage/prepared.h5msm <<'PY'
import hashlib
from pathlib import Path
import sys
from zipfile import ZipFile

archive = Path('devguide/alphaspace2/evidence/alphaspace2_prepared_consumer_20261106.zip')
with ZipFile(archive) as handle:
    data = handle.read('inputs/prepared.h5msm')
expected = 'a42ef9868578ba16c62d52a1267d24160b973dca0d50dbc804ca46b6b2fe316a'
if hashlib.sha256(data).hexdigest() != expected:
    raise ValueError('Prepared receptor checksum mismatch')
with Path(sys.argv[1]).open('xb') as handle:
    handle.write(data)
PY
```

The destination parent must already exist. This extracts supplied chemistry;
it does not regenerate preparation or admit another chemical state. The same
seed is also preserved in the fpocket fresh-package archive, Pocketeer installed
archive and fpocket original-handoff archive.

### Artifacts that are no longer available

The former `/dev/shm` workspace is empty at this handoff. The exact TopoMT wheels
mentioned as temporarily retained by historical checkpoints are **not inside
the committed archives**. Their receipts and digests survive; their bytes do not.
For example, the recorded Pocketeer candidate is
`topomt-0.5.0+355.gbb34e67.dirty-py3-none-any.whl`, 21,585,201 bytes, SHA-256
`4c6484fbc09a2b320de7ac7d576a661bb1616894ece379488aea48bc5df3578d`.
That digest identifies a historical file; it cannot recreate it. The fpocket
TopoMT wheels and the complete installed dependency prefixes also remain
unavailable. A fresh build is a new candidate and requires its own qualification.

The later AlphaSpace2 installed attempt after baseline `87fd192` has no committed
installed checkpoint or retained candidate in this checkout. Conversation-only
outcomes are not acceptance evidence. Its updated exact installed qualification
remains pending, even though the preceding source control is durably archived.

The [historical CASTp1 build recipe](castp/castp1_original_build.md) also depends
on an external, modified Alphashape source tree and its local build helper.
Those `/home/diego/.../Alphashape` paths are historical dependencies outside
TopoMT. Obtain and identify the intended source/patch before rebuilding that
oracle; transferring TopoMT alone does not recreate it.

## Acceptance on the new machine

1. Verify the received HEAD, branch, separate version patch, evidence ZIP hashes
   and complete documentation before installing or rebuilding packages.
2. Use the current registered development profile and Python 3.14 through
   [packaging and environments](packaging_and_environments.md). Historical
   source pins describe historical experiments, not an automatic upgrade plan
   or the new machine's environment lock.
3. Verify actual editable imports from outside the checkout and execute
   `python -m pip check`. Review original-engine capabilities separately from
   their adapters and saved-result readers.
4. Follow [validation and tests](validation_and_tests.md), using a published
   Pytest Receptor. Check report indexes and run the initial reporting/argument
   selection; record the new host's failures, skips and actual origins.
5. Select the next scientific task from [status](status.md) and
   [the provider plan](provider_handoff_plan.md). For updated installed
   qualification, retain the actual candidate wheels on durable storage together
   with hashes, dependency closure and before/after import/file checks.

New-host development readiness establishes only the operations actually tested.
It does not establish the full source suite, installed matrix, another platform,
current sibling compatibility or public delivery. Those gates retain their
owning issues and executed evidence.
