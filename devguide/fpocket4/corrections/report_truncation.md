# Report draft: temporary qvoronoi output read before flush/close

Suggested upstream title:

`load_vvertices()` reads the temporary qvoronoi output before the write stream
is synchronized

## Summary

During the audit of the native reimplementation of `fpocket4` in TopoMT, we
found evidence that upstream `fpocket` may read the temporary `qvoronoi`
output before the file stream has been flushed or closed.

This can truncate the data seen by `fill_vvertices()` even though the
underlying `qvoronoi` computation itself produced the complete output.

## Upstream location

Relevant file in the upstream codebase:

- `src/voronoi.c`

Relevant function:

- `load_vvertices()`

Observed sequence:

1. `run_qvoronoi(fvoro, ftmp);`
2. `fill_vvertices(..., tmpn2, ...)`
3. `fclose(ftmp);`

The diagnostic concern is that `fill_vvertices()` consumes `tmpn2` before
`ftmp` has been explicitly synchronized.

More precisely, in `load_vvertices()` the temporary output stream `ftmp` is
still open for writing when `fill_vvertices()` reopens the corresponding file
path and parses it.

## Why this matters

This can make the vertex-loading stage depend on buffered I/O behavior instead
of on the actual complete `qvoronoi` result. Even if this does not break on
every platform, it is fragile and makes geometry debugging significantly harder.

## Diagnostic context

This issue appeared while comparing:

- the raw tetrahedral/vertex geometry produced by the native TopoMT path,
- the raw geometry exported by an instrumented copy of upstream `fpocket`,
- and direct calls to the `qvoronoi` logic bundled with `fpocket`.

At first, the mismatch looked like a backend geometry difference between:

- SciPy/Qhull in TopoMT,
- and the embedded Qhull path inside `fpocket`.

After deeper inspection, this hypothesis became much weaker.

The decisive step was to separate:

- the true output of the embedded `run_qvoronoi()` path,
- from the later output actually consumed by `fill_vvertices()`.

## Evidence collected

### 1. The embedded Qhull output itself is complete

A minimal diagnostic runner using the same embedded `run_qvoronoi()` logic
produced output identical to the temporary file preserved from the instrumented
`fpocket` run.

This showed that the underlying Qhull stage was not the source of the missing
vertices.

### 2. The preserved temporary output and the recorded raw vertices disagreed

In the instrumented upstream copy, we preserved:

- the raw temporary `qvoronoi` output,
- and the later `raw.txt` / accepted-vertex diagnostic exports.

Parsing the preserved temporary output independently reproduced the complete
expected count of raw vertices.

However, the `raw.txt` export obtained from the original execution path showed
smaller counts in several systems.

This strongly suggests that the file was read before the stream had been fully
flushed to disk.

### 3. The discrepancy was reproducible on several real systems

In the audited `fpocket` diagnostic copy, the non-synchronized path produced
smaller raw-vertex counts than the complete `qvoronoi` output for systems such
as:

- `1GG0`
- `1N57`
- `3LKF`
- `E15ALA`

This was not a one-off observation tied to a single PDB.

### 4. Adding `fflush(ftmp)` fixed the discrepancy

In a temporary diagnostic copy of `fpocket`, adding an explicit:

```c
fflush(ftmp);
```

immediately after:

```c
run_qvoronoi(fvoro, ftmp);
```

made the raw-vertex counts match the native/SciPy reconstruction exactly in
the audited systems.

Observed consequence after the temporary flush patch:

- `1GG0`: raw parity recovered
- `1N57`: raw parity recovered
- `3LKF`: raw parity recovered
- `E15ALA`: raw parity recovered

In our diagnostic environment, after that explicit synchronization step, the
raw tetrahedral geometry exported by upstream matched the native
SciPy/DelaunayMesh reconstruction exactly in the audited systems.

## Minimal reasoning behind the diagnosis

The key logic is:

1. The standalone embedded `run_qvoronoi()` result is complete.
2. The later file consumed by `fill_vvertices()` may be shorter when read
   through the unsynchronized path.
3. Explicitly synchronizing the write stream removes that discrepancy.

That is exactly the pattern expected from reading a temporary file before the
producer stream has been flushed or closed.

## Reproduction strategy

The most reliable reproduction path is not a black-box user workflow, but a
small diagnostic instrumentation of `fpocket`:

1. Instrument `load_vvertices()` so that the temporary `qvoronoi` output file
   is preserved instead of removed.
2. Export the raw vertices later consumed by `fill_vvertices()`.
3. Run upstream `fpocket` on one or more systems such as:
   - `1GG0`
   - `1N57`
   - `3LKF`
   - `E15ALA`
4. Compare:
   - the preserved temporary `qvoronoi` output,
   - the vertices actually loaded by `fill_vvertices()`,
   - and the same run after adding `fflush(ftmp)`.

Expected diagnostic result:

- without explicit synchronization, the loaded/raw vertex count may be smaller
  than what is present in the temporary `qvoronoi` output,
- with `fflush(ftmp)`, that discrepancy disappears.

## Observed behavior vs expected behavior

Observed:

- `fill_vvertices()` can read a temporary output file while its writer stream
  is still open and unsynchronized.
- In practice, this can lead to incomplete raw-vertex intake.

Expected:

- the temporary `qvoronoi` output should be fully written before it is read
  back by `fill_vvertices()`.

## Interpretation

Our current interpretation is:

- the upstream Qhull geometry was not the main source of the previously
  observed large raw mismatch,
- the mismatch was largely caused by consuming the temporary output before
  explicit synchronization of the output stream.

This does **not** prove that every platform or standard-library combination
will always expose the same truncation behavior, but it is strong evidence that
the current code relies on fragile I/O ordering.

## Practical consequences

### For upstream fpocket

- raw vertex diagnostics may be incomplete,
- downstream behavior may depend on timing or buffering details,
- and debugging geometric discrepancies becomes much harder.

### For TopoMT parity work

- this issue initially looked like a deep backend-geometry disagreement,
- but after controlling for it, raw tetrahedral geometry matched exactly in the
  audited systems,
- so the remaining parity problems moved downstream to acceptance/filter logic.

## Suggested upstream action

Possible corrective action in `fpocket`:

1. Explicitly flush or close the temporary stream before calling
   `fill_vvertices()` on the corresponding file path.
2. Optionally add a regression test or diagnostic harness confirming that the
   temporary `qvoronoi` output is consumed completely.

Minimal candidate fix:

```c
run_qvoronoi(fvoro, ftmp);
fflush(ftmp);
```

before the call that reopens/reads the temporary file.

An even stronger version would be:

```c
run_qvoronoi(fvoro, ftmp);
fclose(ftmp);

if (j == 0) {
    fill_vvertices(..., tmpn2, ...);
} else {
    add_missing_vvertices(..., tmpn2, ...);
}
```

That would avoid relying on a still-open writer altogether.

## Proposed code change

Minimal PR candidate:

```c
run_qvoronoi(fvoro, ftmp);
fflush(ftmp);
```

More conservative PR candidate:

1. write temporary output,
2. close `ftmp`,
3. read `tmpn2`,
4. reopen a fresh stream in the next replica if needed.

## Suggested regression test idea

If upstream wants a regression guard, a small internal diagnostic or test could:

1. run `load_vvertices()` on a known system,
2. preserve the temporary `qvoronoi` output,
3. count raw vertices from both paths,
4. assert that both counts match.

## Status

This note is a draft for either:

- an upstream bug report,
- or a small pull request against `fpocket`,

but it should **not** be silently absorbed into TopoMT as if the original
behavior were correct.
