# Reference-state admission for original fpocket

Date: 2026-11-05. Owners:
[#101](https://github.com/uibcdf/topomt/issues/101) (original-provider handoff) and
[#100](https://github.com/uibcdf/topomt/issues/100) (ChemicalStates receiving).
The user authorized consolidation and this bounded state-control segment.

## Supported boundary

The qualified MolSysMT source `00abb958fb93649131d5ce5fe5e12e90cf4900e9`
exports PDB chemical fields from the reference state. Its public converter has
no independent nonreference export selector. TopoMT therefore accepts
`chemical_state='reference'` or the matching integer reference index. A
reference at index 1 is supported; TopoMT never changes the source reference.
Selecting another state, using the unsupported `structure` selector, an ambiguous
reference, an absent chemical domain or a zero-state inventory fails before the
original executable is invoked. Invalid boolean/noninteger selectors reject.
This limitation is specific to the recorded source profile, not a claim about
every future MolSysMT converter or a new published dependency minimum.

`run.metadata['chemical_state_context']` records the chosen/reference index,
inventory count, provider state-ID label and `pdb_chemistry_sha256`. The digest
uses the provider's formal charges in elementary-charge units, bond table and
selected-state connectivity completeness. It binds the original full source
chemistry; it neither reconstructs chemistry nor authenticates its correctness.
Unknown connectivity and a declared complete graph with zero bonds stay
distinct. They remain usable spatial inputs without becoming chemically ready
for native pharmacophore recognition.

Files recovery can receive this exact entry as `chemical_state_context`; its
source identity and digest must match before records are attached. A changed
charge assignment is rejected even if coordinates agree. The chosen state,
original artifacts and detached output survive H5MSM/ZIP recovery and later
source edits. Historical files calls without chemical options retain their
legacy behavior and make no new state-qualification claim. Both qualification
recorders now pass a saved context when it exists, while still reading old runs.

The chemical-domain fixtures use public `ChemicalStatesDict` conversion and
controlled domain assignment. They declare analytical state labels and charge
controls, not biological protomers. No private state context, reference mutation,
alternate chemical store or molecular compatibility facade was introduced.

## Executed evidence

Test-first failures established the previously missing chemical-state keywords
and malformed-context handling. The first fixture attempt incorrectly edited
typed-leaf registrations inside a whole-system transport; it was replaced by
the owning ChemicalStates codec and public validated assignment. The absent
domain fixture uses the supported optional-domain MolSysDict reader.

`tests/methods/fpocket4/test_chemical_context.py` passes **11 cases**:

- nonreference, ambiguous, absent, zero-state and unsupported-selector rejection
  before the engine (a forbidden-call guard proves the ordering);
- reference index 1 writes the declared `1+` PDB charge fields without altering
  the reference or the other state's missing charges;
- unknown versus known-empty connectivity has distinct retained context;
- files recovery retains state labels/indices and rejects later source chemistry
  changes or malformed saved context;
- the original fpocket binary executes a two-state 3PTB control with reference 1;
  saved source plus original files recover the same ordered records, membership,
  geometry and attributed measurements after CLI temporary directories disappear.

The final selected input-context, registry, provider, fpocket, dependency and
governance battery passes **153 tests, five deselected, zero executed skips**
in 121.64 s. All new chemical controls, original fpocket execution, source
recovery and the prepared PharmacophoreMT consumer execute. The five exclusions
retain the unrelated installed-library/subprocess selectors from the prior
checkpoint; this is not a complete-suite or hosted qualification claim.
The 14 legacy input/map controls also pass against the unchanged host MolSysMT
checkout without the source override. Complete Ruff lint/format passes across
417 files. Scoped mypy 2.3.1 passes the five affected executable modules with
imported bodies skipped. Temporary type tooling was removed after the check.
`make -C docs html` completes with the same 12 warnings outside the edited user
page, including the missing PlantUML executable; no new page diagnostic appears.
Required full-suite/hosted recovery remains [#58](https://github.com/uibcdf/topomt/issues/58),
and source/public Python delivery remains [#16](https://github.com/uibcdf/topomt/issues/16).

The [new archive](evidence/reference_context_20261105.zip) contains the original
run and two-state source; its [summary and member digests](evidence/reference_context_20261105.json)
record exact sources, tested worktree hashes and actual state context. The saved
execution reports 10 pockets; counts belong to that run, not all future runs.
Its chemical reference is `analytical-state-1`, index 1 of two states. This
analytical control does not admit a new biological state.

The [earlier handoff and consumer archive](evidence/original_handoff_20261105.zip)
now preserves the original 3PTB/ERalpha sources, bundles, two native queries and
receipts outside temporary storage. Its
[manifest](evidence/original_handoff_20261105.json) was reverified before removing
temporary duplicates. Historical receipts and original producer identities were
preserved. Existing sources/artifacts remain those in the
[initial source checkpoint](handoff_checkpoint.md) and
[prepared consumer checkpoint](pharmacophore_handoff_checkpoint.md).

TopoMT consolidation is in local commits `cc4f976`, `d406caf`, `4bd7450`; this
state segment follows that base. The pre-existing generated-version edit is
excluded. The principal MolSysMT checkout remains at `71fbe4f46d3c...`; the probe
imports the pinned independent source and its previously recorded unchanged
native artifact. PharmacophoreMT's current clean head is `b934471ac8ab...`; its
package bytes are unchanged from the earlier `869cf967cba0...` consumer source.
No sibling code or shared environment was modified.

## Reproduce and remaining scope

```bash
TOPOMT_FPOCKET_CMD="$PILOT_FPOCKET" PYTHONPATH="$PILOT_MOLSYSMT" \
  python -m pytest --noconftest --receptor=llm \
  tests/methods/fpocket4/test_chemical_context.py
```

The exact pinned source is required for the declared codec controls. Set the
executable variable explicitly to execute the designated real-engine case;
ordinary absence skips do not qualify that case. The archived original run
can be recovered through the files route without installing fpocket.

Independent nonreference export requires an owning MolSysMT operation before
TopoMT can qualify it. This work does not deliver arbitrary-state export,
structure-associated state inference, general preparation, all engine receiving,
clean installed/public qualification, a release, affinity or biological validation.
The PharmacophoreMT recorder remains its fixed single-reference hydrophobic
control. #97 copy ownership and the remaining #100/#101 acceptance keep their
independent scope; no issue is automatically closed by these local checks.
