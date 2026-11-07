# Public original-result persistence checkpoint

Owner: [TopoMT #101](https://github.com/uibcdf/topomt/issues/101).
Source producer: `49440b7e40848e96735a30cf0d117152b22105b0`.
Recorded on 2026-11-06 local / 2026-11-07 UTC. This is a source-development
increment under the [provider plan](provider_handoff_plan.md), with no new wheel,
environment installation, server submission or installed-candidate claim.

## Public workflow

```python
result.save('original.zip')
restored = topomt.load_provider_output('original.zip', molecular_system=source)
assert restored.run == result.run
```

`ProviderOutput.save` delegates to the existing evidence writer. It does not
serialize arbitrary manually constructed record fields or the full MolSysMT
object; source-bound evidence includes full-source identity and selected-frame
coordinate snapshots. Preserve the original molecular source separately.

The loader validates the complete ProviderRun bundle before selecting a registered
files reader. It accepts no replacement method, backend, selection, frame,
chemical state or execution settings. AlphaSpace2 retains its explicit binder
source requirement for bound runs. The loaded run must equal the verified run,
including original backend, metadata, ID and artifact bytes; a changed reread
cannot pass as the original acquisition.

Supported recorded routes are fpocket `cli`/`wrapper`/`files`, Pocketeer,
AlphaSpace2 and pyCASTA `library`, and source-bound CASTp `files`. Unknown routes
are rejected before provider dispatch. No original engine or server runs during
reconstruction. Existing provider-specific APIs and `output.run.save` remain
available.

Current CASTp direct-server captures still lack the full-source reconstruction
protocol. Saving retains their evidence for inspection; the new loader does not
upgrade it or silently rerun the server. An explicitly source-bound import of
the retained ZIP is a separate files run. This limitation is current, not merely
a property of historical bundles.

## fpocket source-bound acquisition

New captures with an explicit submitted atom map and reference chemical context
record protocol 1, its source-context artifact and the complete source snapshot
through the shared MolSysMT-bound provenance validators. Adapter-owned fields
cannot be overridden through extra metadata. Capturing uses owned staging,
preserves symlinks for rejection and refuses supplemental-name collisions;
original input/output files remain unchanged.

Saved reconstruction reuses the original ProviderRun rather than recapturing
it as a new files run. It validates the full selected source frame, excluded
atoms, reference chemistry, original PDB/map and pocket serial coverage. A
single-frame `structure_indices='all'` capture records frame zero explicitly.
Valid available-empty results retain zero records; absent required original
reports are rejected. Legacy raw imports with context options omitted retain
their previous behavior. Bundles without sufficient source context remain
inspectable and require explicit raw import instead of inferred binding.

## Executed source controls

| Selection | Result |
| --- | --- |
| Combined public persistence, fpocket source-bound, export and existing regression selection | **323 passed, zero skips**, 38.98 seconds; eight visible legacy PDB-inference warnings |
| New persistence admission tests | **44 passing cases**, included above |
| New fpocket saved-output tests | **49 passing cases**, included above |
| Five-reader save/load workflows | **12 passing cases**, included above: five providers, AlphaSpace2 bound and unbound, both nm/ps/radians and pm/fs/radians |
| Distribution and reporting contracts | **20 passed**, 4.94 seconds |
| Ruff | Whole repository check passed; **491 files** already formatted |
| Scoped mypy | Eight executable modules passed with imports skipped and missing optional stubs ignored |
| Documentation | Full HTML build succeeded with 12 existing warnings; final incremental build succeeded with eight |

The component counts overlap and must not be summed with the combined selection.
The 12 workflows exercise original-format analytical builders or existing committed
saved results; they are parser/reconstruction controls, not 12 new original-engine
calculations. Each verifies record order, IDs, roles, memberships, parents, fields,
quantities, geometries, source/binder snapshots, original files and repeated public
save identity. Engine imports/execution and network access are guarded during
recovery. The fpocket suite additionally exercises a fresh Python process.

The combined selection explicitly loads current TopoMT source in the existing
engine-free Python 3.14.10 receiver, with MolSysMT
`00abb958fb93649131d5ce5fe5e12e90cf4900e9`. This is a controlled development pin,
not public-only dependency delivery or qualification of the older installed
TopoMT wheel. Tests use explicit Pytest Receptor loading and `--noconftest`;
global warmup and unrelated fixtures are not claimed.

A separate broad working-environment run has **149 passes and one failure** in
the unchanged `test_chemical_context._with_states` fixture: MolSysDict 0.1 rejects
preparation history before the fpocket adapter is called. This compatibility
failure is retained for the existing full-suite/qualification backlog (#16/#58),
not waived or reported as passing. No chemistry or old fingerprint is rewritten
to hide it. A pre-existing fpocket `files.py` mypy mismatch also remains:
its frame argument admits `int | list[int]`, while `Topography` annotates `int`.
The identical baseline diagnostic is retained separately. Full type cleanliness
is not claimed.

Focused logs and failing-first controls are retained under
`.cache/provider-persistence/`, `.cache/fpocket-saved-output/evidence/` and
`.cache/saved-provider-workflows/evidence/`. The first loader admission red is
retained only in the agent terminal transcript; its final cases are in the
combined passing log. Durable guards are the committed test modules, with source
fixtures and archived-input hashes selected by those tests. No new molecular
evidence ZIP is needed for this API increment.

Task-only caches remain owned by #101; review by 2026-11-13 and remove when their
development evidence is no longer needed. Preserve the existing controlled
receiver and earlier candidate/evidence resources while their owners need them.
Installed receiving, full suite/matrix, package delivery and broader service
admission retain their separate gates. This milestone does not automatically
start another package qualification while source development continues.
