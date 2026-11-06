# Moving TopoMT development to another machine

This handoff preserves published development history, committed scientific
evidence and a separate local-file backup. Read [onboarding](onboarding.md),
[status](status.md) and [the environment guide](packaging_and_environments.md)
alongside these steps. Publication is source delivery, not scientific or
installed-package qualification.

## Published source and local backup

The scientific review baseline is `87fd192b03f36b0e24a279450fab3c60620244bd`;
the documentation review is `f3ffa90acbcfced831e397e0a75e510924ca9204`.
Before publication the development branch was ahead of remote `main` and had no
upstream. The subsequent user-authorized publication fast-forwards `main` and
publishes `work/fpocket-handoff-101`, preserving all development commits and their
original identities. The old unpublished-branch snapshot in the review history
is not the receiving procedure after that publication.

The final source SHA and remote checks are retained in `PUBLICATION_RECEIPT.json`
inside the separate `topomt-local-files.zip`. Check that receipt and current
remote state when receiving the work. The working clone finishes on `main`,
tracking `origin/main`; the development branch also has its remote counterpart.
No release tag or package qualification follows from publishing these refs.

The only local tracked modification before cleanup was the generated
`topomt/_version.py`, SHA-256
`91af00335ecf06be1573c95e22dbba13bfaa0a9e472ffa3de802cee87dc38baf`.
Its exact bytes and patch were preserved in the verified ZIP before restoring
the tracked file. The ZIP also retains all 543 ignored generated files and the
recent documentation-validation outputs. The checkout's current version file
is the tracked one; the archived local edit is an optional historical state.

## Clone on the receiving machine

Use a destination where `topomt/` does not already exist:

```bash
git clone https://github.com/uibcdf/topomt.git topomt
cd topomt
git switch main
git log -1 --oneline
git status --short --branch
git branch -vv
```

Confirm that the received history contains the published SHA recorded by the
backup receipt. If remote `main` has subsequently advanced, inspect its ancestry
rather than assuming a different HEAD means the earlier work was lost. Select
the recorded commit explicitly when reproducing that exact snapshot.

## Transfer and verify the local-file ZIP

Copy `topomt-local-files.zip` and its `.sha256` sidecar from the durable sibling
backup directory to durable storage on the receiving machine. Keep the archive
outside the source checkout. The root `RESTORE_INSTRUCTIONS.md` explains every
payload directory and its placement; `MANIFEST.json` records SHA-256 and size
for each payload. A compact verification from any directory is:

```bash
python - /PATH/TO/topomt-local-files.zip <<'PYVERIFY'
import hashlib
import json
from pathlib import Path
import sys
from zipfile import ZipFile

archive = Path(sys.argv[1])
with ZipFile(archive) as saved:
    if saved.testzip() is not None:
        raise ValueError('ZIP integrity check failed')
    manifest = json.loads(saved.read('MANIFEST.json'))['files']
    if set(saved.namelist()) != set(manifest) | {'MANIFEST.json'}:
        raise ValueError('Unexpected ZIP member inventory')
    for name, item in manifest.items():
        data = saved.read(name)
        if len(data) != item['bytes'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError(f'Backup checksum mismatch: {name}')
print('All backup payloads verified')
PYVERIFY
```

Extract the verified archive to a separate directory. Keep validation JSON,
logs, JUnit XML and events as evidence; `validation_20261106/html-final/index.html`
is the archived public-docs build. Recreate SDKs and environments through the
environment guide. The old temporary SDK clones were excluded because their
Git alternates refer to the old host. Archived reporter/docs overlays are
verification inputs, not replacements for a fresh installation.

Leave `repository_ignored/` in the backup: bytecode, Numba/cache files and
`topomt.egg-info` are generated and can depend on the old interpreter or host.
The saved `repository_state/topomt/_version.py` and `human-version.patch` can
restore the historical local edit if explicitly needed. Applying them makes
the new clone dirty; a normal continuation uses the tracked version file and
lets the build backend generate versions in an appropriate isolated checkout.

## Optional offline source copy

A bundle is an alternative when the receiving host cannot access GitHub.
Create it from the final committed source into a new directory on durable
storage outside the repository:

```bash
set -eu
topomt_transfer_dir=/absolute/path/on/durable/storage/topomt-transfer
mkdir -p "$topomt_transfer_dir"
test ! -e "$topomt_transfer_dir/topomt.bundle"
git rev-parse HEAD > "$topomt_transfer_dir/source-head.txt"
git bundle create "$topomt_transfer_dir/topomt.bundle" --all
git bundle verify "$topomt_transfer_dir/topomt.bundle"
```

Transfer the bundle, recorded HEAD and the local-file ZIP separately. A bundle
contains Git objects and refs, not uncommitted edits, ignored files or runtime
environments. A bundle clone initially points `origin` at a local file; restore
the intended GitHub URL before fetching or publishing. The public-clone route
above already configures the ordinary remote correctly.

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

1. Verify the received published history, branch, local-file backup and evidence
   ZIP hashes before installing or rebuilding packages.
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
