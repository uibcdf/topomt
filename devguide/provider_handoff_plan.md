# Reproducible original-provider handoff plan

Accepted technical direction: 2026-11-06. The earlier automated development goal
was paused and cleared during migration. The user subsequently selected the
AlphaSpace2 and pyCASTA receiving continuations, now completed within their bounded
[AlphaSpace2](alphaspace2/installed_receiving_checkpoint.md) and
[pyCASTA](pycasta/installed_receiving_checkpoint.md) installed checkpoints. This plan
preserves the full five-provider scientific scope and its remaining gates.
Owner for the first consumer pilots: [#101](https://github.com/uibcdf/topomt/issues/101).
Provider fidelity remains [#19](https://github.com/uibcdf/topomt/issues/19);
component qualification and full-suite backlog remain #16/#58. This plan is
outside the issue-report queues and does not change their lifecycle or scope.

## Outcome and ownership

Enable a reproducible path from a receptor prepared in MolSysMT, through an
explicit original pocket provider, to attributed pocket records and declared
PharmacophoreMT hypotheses. Integrate all currently registered external methods:
fpocket, Pocketeer, AlphaSpace2, pyCASTA and CASTp/CASTpFold. Native reproductions
retain their independent scientific contracts and are not prerequisites for
original-provider handoff.

MolSysMT owns loading, representation, selections, atom correspondence,
coordinates, chemistry and preparation. TopoMT owns external topography adapters,
their original evidence, source index maps and pocket representations.
PharmacophoreMT owns recognition, feature complementation, projections, matching
tolerances, essentiality, weights and native pharmacophore persistence. ArgDigest,
DepDigest, SMonitor and PyUnitWizard retain their registered responsibilities.
Missing provider capabilities are reported to their owner instead of copied
into TopoMT. Use public tools; respect the sibling contribution route before
changing another component.

## Evidence required for completion

1. Each supported original route has appropriate ArgDigest value/name contracts,
   optional dependency guards and explicit operational errors. Missing engines
   never select a different method silently.
2. Real original execution and persisted recovery agree on pocket order/IDs,
   membership roles, source indices, available geometry, original fields and
   attributed units/definitions. Keep source selection, frame, chemical state,
   versions/options and original bytes; distinguish unknown, empty and invalid.
3. Saved results remain independent of temporary files and later source changes.
   Recovery verifies compatible source evidence and works without the original
   engine. Physical quantities agree under alternate application unit policies.
4. Prepared real receptors pass source persistence, original detection, saved
   recovery and public PharmacophoreMT consumption. Explicit scientific choices
   stay in the consumer; preserve site-to-source context through model roundtrip.
   No affinity, binding-site relevance or exact closed region is inferred from
   provider rank, masks or alpha spheres.
5. Exact installed candidates and dependency origins are verified in clean
   environments. Retain actual wheels/digests, executed guards, skips and limits.
   Current support/matrix/full-suite obligations retain their owning records;
   source checks and old installed wheels cannot qualify changed candidates.

## Current sequence and gaps

| Provider | Current bounded evidence | Next required work |
| --- | --- | --- |
| fpocket | Original CLI/files, reference chemistry, prepared hydrophobic consumer and bounded installed receipts under `fpocket4/`; the current Pocketeer candidate repeats these controls. | Preserve regression coverage; broader fidelity and component gates retain their owners. |
| Pocketeer | Public 0.4.0 original, argument/state and saved-reader controls; prepared public PharmacophoreMT receiving under both unit policies. Exact producer `bb34e67` also passes 311 installed cases without skips and two independent prepared flows in a new prefix. | Preserve the qualified candidate and regression evidence; general fidelity and component gates remain separate. |
| AlphaSpace2 | Historical source receiving at `ce4708a` retains its 523 distinct affected cases. Exact producer `5ae5c46` now has 256 passing installed cases, two complete 13-pocket/two-site flows under alternate units and independent engine-free recovery. See the [installed checkpoint](alphaspace2/installed_receiving_checkpoint.md). | Preserve the candidate and regressions; broader fidelity and component gates retain their owners. |
| pyCASTA | Original 1.0.8 argument/source contracts, schema-1 saved recovery and prepared public consumption. Exact producer `02a38be` passes 217 installed cases, two complete five-pocket/four-site unit-policy flows and independent engine-free receiving. See its [installed checkpoint](pycasta/installed_receiving_checkpoint.md). | Preserve the candidate and regressions; native #53, exhaustive fidelity and general component gates remain separate. |
| CASTp/CASTpFold | Existing server/files adapters and retained archive evidence. | Verify current route/context fidelity and qualify an explicit consumer profile. |

The AlphaSpace2 installed checkpoint records Linux/Python 3.14.10 receiving with
new wheels from MolSysMT `00abb958f` and PharmacophoreMT `b934471`. Its source pins,
candidate and executed controls retain their own identities. Public-only
dependency acquisition and compatibility with current sibling mains remain
separate from this result.

Continue the technical sequence with CASTp/CASTpFold's original route/source
contracts, saved recovery and explicit prepared consumer. Preserve the fpocket,
Pocketeer, AlphaSpace2 and pyCASTA regressions through the existing developer recorders and public
PharmacophoreMT tools. Issue #101 remains open: completion requires all five
providers and the evidence above, while exhaustive fidelity and general
component qualification retain their separate gates.
