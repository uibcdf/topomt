---
summary: Attribute all reached TopoMT scientific methods and third-party routes through Ackredit.
issue: uibcdf/topomt#157
status: resolved
opened: 2026-11-08
closed: 2026-11-08
severity: high
verification: measured
area: [third-party, attribution]
guard: tests/test_scientific_attribution.py::test_real_provider_repeated_results_and_enclosing_workflow
normative: ACKREDIT_GUIDE.md
blocked_by: []
supersedes: []
---

# Ackredit attribution for all scientific methods and third-party use

## What

At intake, TopoMT had no Ackredit registration/tracking boundary for fpocket or
other providers. The legacy unused citation helper still referred to Flowcite.
Guide synchronization alone had not established runtime adoption.

## How

The maintainer expanded the scope on 2026-11-08 to all supported third parties
and every citable method/algorithm used by TopoMT. Inventory original/native/
corrected routes, DFND, tessellation and scientific numerical backends. Apply the
registered Ackredit optional-client contract; fpocket is an end-to-end control,
not the completion boundary. The source integration now declares bibliography offline, tracks reached
method/software branches in the application session, and retains detached result
bibliography/producer versions. The current route inventory and contributor
procedure are in [attribution.md](../attribution.md). Distinguish original executable, native reproduction and corrected
TopoMT variant. No implicit import hooks or import-time scientific credit.

## Why

Users need an attributed report of the methods their workflow actually used.
A shell executable cannot be inferred from Python import discovery alone.

## What was refuted

This is missing TopoMT consumer integration, not an observed Ackredit defect.
ACKREDIT_GUIDE publication under #91/#94 does not establish runtime use.
An isolated citation helper or mocked installed flag would not prove integration.

## Scope and exclusions

Complete inventory-driven adoption, with separately owned blockers if needed. Keep
Ackredit optional and preserve science when it is absent/broken. No provider
implementation, dependency-floor/public-extra or installed-matrix claim here.
The consulted Ackredit source is clean at 4beb850c8ba814e6103b4d303128a1a36eb57610.

## Acceptance criteria

Real-provider tests show applicable references after reached successful/empty
calculations, no unrelated credit, reused references across results and enclosing
sessions, absence/provider-failure diagnostics, lazy import, detached ownership
and persisted reading without another calculation credit. Verify bibliographic
records, actual original/software semantics and source/public qualification.
Document the user workflow and complete every admitted inventory boundary;
link remaining provider/method tasks without silently dropping parent scope.
A fpocket-only delivery cannot close this issue. #56/#16
retain their wider ownership.


## Delivered source behavior

- All original/native/corrected providers in the maintained inventory, including
  the selected CASTp3 versus CASTpFold service, DFND, tessellation and directly
  reached numerical/geometry/scoring/path/centrality methods participate.
- Fpocket detector and druggability criteria have separate references; only the
  reached native score or accepted original score report earns the latter.
- `topomt.get_attribution` inspects host declarations without the optional
  provider; `topomt.cite` delegates rendering without another calculation credit.
- Main result containers retain detached references/status, including cached
  geometry reuse and evaluated-empty results. Native adaptation does not claim
  execution of the original software. DFND receives no fabricated article.
- An optional provider failure is diagnosed without replacing completed science,
  including strict warning filters. Scientific failures propagate and completed
  child work remains credited.
- Attributed provider bundles use an explicit version-2 envelope around the
  original version-1 scientific manifest; original run IDs and bytes remain.
  New readers accept both formats. Legacy readers cannot read the new envelope;
  historical attribution absence stays unrecorded.
- The obsolete Flowcite shim is retired. Root AGENTS and developer/user guides
  explain how additions must maintain this coverage. The development tooling
  group includes optional Ackredit for real-provider tests; no public extra or
  required runtime dependency is introduced.

## Verification and limits

Test-first source adoption uses real editable Ackredit
`0.12.1+10.g4beb850` at clean source
`4beb850c8ba814e6103b4d303128a1a36eb57610`, Python 3.14.10.
The portable API minimum documented by the provider remains 0.9.0; this source
selection does not qualify all older releases or all supported interpreter
minors. Real native calls, analytical original-format adapter controls, genuinely
unimportable recording, strict warnings, reused/nested captures, detached
ownership and fresh saved readers have separate controls.
The final selected test/diagnostic results and deferred qualification are
recorded in [the source checkpoint](../attribution_checkpoint.md).

Protocol fixtures do not establish original-detector scientific accuracy.
No new server submission, third-party installation, scientific benchmark
comparison, rebuilt TopoMT package or public release is claimed. Broader source/
installed/public and full-matrix qualification remains in #16, and wider suite
adoption in #56. The independently discovered stale inventory was repaired
under #169, without changing existing scientific assets or tool inputs.
