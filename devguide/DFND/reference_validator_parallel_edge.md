# Parallel execution of certified analytic integration

Owner [#76](https://github.com/uibcdf/topomt/issues/76), performance stage S7.
This is the execution continuation of the
[analytic edge derivation](reference_validator_edge_integration.md), using the
[bounded local executor](reference_validator_parallel_resume.md). It changes
neither the atom-ball model nor the independent complete topology construction,
region assignment, sphere cuts, numerical scheme or volume request. It is a
developer checker route, not an exported public TopoMT detector/backend.

## Complete geometry before parallel arithmetic

`EdgeVerificationSession` admits the entire untrusted `power_edge_volume`
certificate. It checks schema/arithmetic/Model binding, exact units, scheme,
dyadic bits and original request, then independently verifies complete topology.
The same serial `assigned_faces` reconstructs every oriented triangle and its
proved global region. All atomic constraints participate in that construction;
one owner ball suffices locally only because its complete power ordering has
already been verified.

A task is **one oriented triangular face piece**, evaluated analytically along
its edges by the existing `triangle_flux`. It is not a spatial sample or a new
subdivision. The complete frontier is fixed, canonical and bounded by the
existing 4096-piece envelope. Its digest binds all exact centers, expanded
radii, triangles, region IDs and nm units. Task IDs bind Model, full certificate
(including precision request/bits), executable/runtime, frontier and piece index.
Changing probe/frame/domain, arithmetic or assignment rejects work reuse.

The default executes directly on one CPU without a pool. An explicit
`LocalPolicy(workers=2)` uses the existing bounded spawned executor. Every worker
receives the complete immutable Model and a canonical numerical task. It runs
the same exact/outward interval checker; no producer-selected numerical bound
or region label is accepted from the input certificate.

## Signed accounting and completion

For each piece k the checker obtains a signed interval I_k. It retains negative
contributions and every outward rounding error. The total uses each I_k once;
region j uses exactly the pieces whose checked region is j. The original exact
interval reduction, physical-domain clipping and absolute AND relative tests
apply to the total and every region. No per-task relative tolerance replaces
the global request, and no small positive component is dropped.

Completion order does not change the canonical reduction. Missing, repeated,
foreign or malformed task replies fail; a failed task is never an empty piece.
No sum over unfinished work is returned as a whole-domain enclosure. S7 starts
with complete topology, unlike unfinished S6 source construction, but incomplete
integration still cannot supply a volume or a satisfied-precision flag.

Only independently justified empty and whole-free shortcuts avoid arithmetic;
exact rational zero-radius flux retains its original behavior. Valid enclosure,
complete integration and attained numerical precision remain separate outcomes.
A complete positive integral with a literal-zero request can remain unresolved.
The scheme is fixed-frontier integration, not a new adaptive parallel partition.

## Trust boundary, saving and recovery

The worker is part of the independent checker, with the same trusted rational
interval implementation as direct serial execution. The coordinator reconstructs
geometry and assignments; workers execute only selected analytic arithmetic.
Normal process execution/transport is part of this trusted software base, not
a cryptographic proof of remote computation or a fault-tolerant hardware claim.
The executor is not an extensible source of user-supplied scientific results.

An owned session keeps exact immutable computed intervals internally and rejects
PID changes, executable changes and serialization. A snapshot is **untrusted
proof data** when passed to another process. It binds each signed bound to an
explicit `nm**3` unit. Generic bounded storage writes the data exclusively,
flushes/fsyncs it and publishes its checksum manifest last. Existing directories
are never overwritten; torn, changed and duplicate-key records are rejected.
The manifest is storage integrity, not mathematical acceptance or full storage-
hardware crash durability.

`from_bundle` reads exactly the hashed bytes, reconstructs the original full
geometry/frontier, and **recomputes every saved interval** before reusing it.
Even a correctly rehashed but numerically forged bound is rejected. A cached
accepted flag or digest cannot create a trusted context. The pure
`verify.edge_progress.check_progress` needs no pool/producer imports and reports
an inventory without pretending that a partial sum encloses the whole volume.

Prepared plans, low-level reductions and the provenance-header builder are
internal implementation helpers. Admission and completeness belong to the raw
verification/session entry points; calling a helper with arbitrary claimed
bounds is not a certification route. A provenance header alone proves nothing.

The completed `finish()` receipt records actual checker source identities and
the same mathematical fields as the ordinary serial reader. The original
symbolic certificate remains portable and unchanged. An independent fresh
serial read reconstructs and integrates it without task caches, a process pool,
producer or scientific floating-point packages. Receiving compares these full
mathematical outputs, not merely overlapping intervals or component counts.

## Developer workflow and resources

The caller owns the exact Model and symbolic certificate, finite external CPU/
wall/address-space limits, explicit affinity and a shared-host reserve. No free
resource observation reserves a machine. The following is a developer example;
it does not impose operating-system limits itself.

```python
from pathlib import Path
from devtools.reference_validator.edge_tasks import EdgeVerificationSession
from devtools.reference_validator.parallel import LocalPolicy

session = EdgeVerificationSession(model, certificate)
session.advance(piece_budget=2)  # Direct serial execution is the default.
session.save(Path('new_partial_work'))

# In a later process with the same Model and exact executable/runtime:
resumed = EdgeVerificationSession.from_bundle(model, Path('new_partial_work'))
while resumed.snapshot['stop_reason'] != 'pieces_complete':
    progress = resumed.advance(
        piece_budget=512, policy=LocalPolicy(workers=2),
    )
    resumed.save(Path('new_checkpoints') / f"pieces_{len(progress['items']):04d}")
result = resumed.finish()
```

The existing pool enforces bounded workers/queues, child memory/CPU ceilings,
no nested pools and host reserve checks. A pool CPU allowance covers its whole
lifetime, not each task. Use finite piece budgets and save between steps. On
cooperative stop or failure, completed work remains available for an explicit
checkpoint; an external hard stop can lose work since the last saved state.
Signal-aware launchers must stop their owned process groups, including children,
and mark interruption even if a child exits cleanly. Launch each longer analysis
within its own finite execution window and exclusive output directory.

## Receiving and remaining gates

The [versioned receiving](../evidence/reference_validator_parallel_edge_v1/README.md)
freezes 51 source modules and the same original Models/certificates/requests.
It receives sixteen boundary precision controls and nine region controls in
serial/two-worker modes, including tiny eight-region and asymmetric three-region
cases. The three original 1.4 Å Models are tetrahedron, closed shell and dumbbell,
with a bounded pause, fresh-process recovery and a further independent serial
read. Unit controls additionally cover signed owner faces, exact shortcuts,
zero-error requests, false saved arithmetic, changed bindings, missing/duplicate
work, child failure, cancellation and producer-free partial reading.

Separate numerical-task time from topology/frontier reconstruction, storage,
recovery and the subsequent serial check. Pool startup can dominate a small
system. A faster arithmetic phase does not establish an equal full-workflow
speedup, and a spawned one-worker workflow is a different baseline from the
new direct serial default. Report the actual source and all timing scopes.

Four workers, the full parallel nineteen-profile panel, broader S8/P6/P7 and
remaining S1/S3/S5 work retain their gates. Original S6 receiving and the earlier
nineteen-profile serial precision retain their own source snapshots; old source-
bound checkpoints require their recorded source/runtime. Native #181/#180/#184/
#188, canonical native receiving #76/#60 and installed/public/platform #16 are
unchanged. No new geometry family, protein or original-provider phase is selected.
