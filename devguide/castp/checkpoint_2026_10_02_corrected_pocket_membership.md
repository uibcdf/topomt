# Corrected CASTp3 pocket and mouth membership comparison

Completed: 2026-10-02. Owning audit: [#87](https://github.com/uibcdf/topomt/issues/87).

## Contract and panel

The comparison recalculates the historical thirty-eight systems plus 1A4J
and 1CDO, the two additional inputs in the twenty-two-system analytical
closed-void panel. These are forty pinned CASTpFold archives from the broader
eighty-nine-archive radius corpus. The other forty-nine archives are outside
this native feature-comparison panel; radius compatibility does not certify
their pocket decomposition.

Each calculation uses the exact PDB bundled with its archive, protein/peptide
selection, explicit `castp3_protor`, a 1.4 angstrom probe and full depth.
Peripheral atom expansion, length epsilon and face-rank epsilon are zero.
Original atom serials are verified against the retained MolSysMT atom IDs and
coordinates. The implicit-H correction and observed terminal policy are
described in the [preceding checkpoint](checkpoint_2026_10_01_hydrogen_and_terminal_policy.md).
The scientific backend is unchanged from source `387f9b4`.

The audit compares **exact atom-set multisets**, including duplicate
multiplicity. Equal counts alone do not pass. Missing and extra memberships
are retained separately for every feature class. No approximate match, oracle
atom expansion or molecule-specific numerical adjustment is used.

`pocket` is the single-mouth class in the existing server taxonomy; channels
and branched channels are reported separately. A mouth row is the **aggregated
exported atom record for a parent open feature**. Matching that record does not
prove equal individual topological mouths or boundary triangles.

## Recalculated historical cohort

The thirty-eight historical inputs now give:

| Feature class | Server | Native | Exact atom sets |
|---|---:|---:|---:|
| Pockets | 443 | 457 | 386 |
| Closed voids | 306 | 306 | 306 |
| Channels | 46 | 46 | 40 |
| Branched channels | 10 | 10 | 7 |
| Aggregate mouth records | 499 | 513 | 435 |

The old sweep recorded 363 matching pockets and 407 matching mouth records.
Those old counts precede the corrected source mapping and preparation policy;
the affected alternate-location counts were not valid current evidence.
The current calculation replaces that evidence, without identifying any one
change as the sole cause of each improvement.

All 306 closed-void memberships match. This extends atom-set/count evidence;
independent SA/MS agreement remains the separately tested twenty-two-system,
225-void, 900-measure panel. It does not add analytical metric comparisons for
the other closed voids.

Seven historical inputs match all compared classes: 1CRN, 1HEW, 1IFB, 1ROP,
1SRF, 2PK4 and 3PHV. 1CRN has no open pockets and is an evaluated-empty open
case; six of these seven demonstrate nonempty open-feature agreement.
Ten historical systems match all pockets, including the empty 1CRN case.

Observed examples separate agreement from residuals:

- 1A6U: all 21 pockets match, while 23 of 24 mouth records match.
- 1SRF: all pockets, channels, branched channels, voids and mouth records match.
- 1CGE: all seven voids and three channels match; eight of eleven server
  pockets match, with twelve native pockets and eleven of fourteen matching
  mouth records.
- 1STP: four of five pockets match although all six exported mouth records do.
- 3PTB: pocket and void counts now agree, but one pocket and one mouth atom set
  differ. The historical count discrepancy is not a current failure claim.
- 1BMQ: all fifteen voids and both channels match, but four additional native
  pockets remain; fourteen of twenty server pockets match exactly.

The historical micro-pocket 27 in 3PTB and micro-pocket 34 in 1BMQ both now
match their archived pocket and aggregate mouth atom sets. Independent molecular
guards recalculate these exact source records. Their old classifications are
no longer current impossibility counterexamples; exact mouth triangles and
SA/MS quantities are not certified by this result.

These patterns do not identify a unique algorithmic cause. Lining/rim atom
reporting, component construction and filtering require independent diagnosis.
The older micro-mouth reproducibility conclusions must be re-examined with
the corrected inputs rather than used as current impossibility evidence.

## Full forty-system result

All forty calculations completed without calculation errors:

| Feature class | Server | Native | Exact atom sets |
|---|---:|---:|---:|
| Pockets | 534 | 551 | 468 |
| Closed voids | 388 | 388 | 388 |
| Channels | 52 | 53 | 45 |
| Branched channels | 17 | 17 | 8 |
| Aggregate mouth records | 603 | 621 | 520 |

Pocket agreement is **468/534 (87.6%)**. There are 66 unmatched server pocket
sets and 83 unmatched native pocket sets. These include different lining sets
and component/count differences; they are not automatically 83 extra physical
pockets. The net pocket-count excess is seventeen.

All 388 closed-void memberships match. The newly added proteins have distinct
open-feature results: 1A4J matches 49 of 55 pockets (58 native), while 1CDO
matches 33 of 36 (36 native). Their exact voids and analytical measures do not
establish open-pocket parity.

Ten cases have complete pocket agreement, including the empty 1CRN case:
1A6U, 1CRN, 1HEW, 1IFB, 1RBP, 1ROP, 1SNC, 1SRF, 2PK4 and 3PHV. Thus nine
of thirty-nine nonempty pocket cases are fully exact. Seven cases match every
compared class, as listed above. Eight match all exported mouth records,
including the empty case; this is seven of thirty-nine nonempty mouth cases.

The [per-PDB table](artifacts/membership_audit_2026_10_02_by_pdb.md) retains all
forty cases. The [complete JSON artifact](artifacts/membership_audit_2026_10_02_corrected_inputs.json)
retains exact archive/PDB hashes, calculation policies, full missing/extra sets,
per-case duration, cohort and aggregate counts, the scientific source revision
and exact source hashes. It preserves evaluated-empty cases and duplicate
multiset semantics. No discrepant case is omitted from the denominator.

Residual diagnosis is tracked under [#88](https://github.com/uibcdf/topomt/issues/88).
Start with the single lining atom missing in 1STP (serial 592), the lining/rim
atom missing in 3PTB (1054), and the extra mouth atom in 1A6U (733). Then
investigate count/component differences in 1BMQ, 1CGE and 1A4J, and the branched
channel mismatches. These are observations, not established root causes.

## Reproduction

```bash
python -m devtools.castp.compare_castp3_oracles \
  --ids 1crn 1rop 2pk4 3phv 8rat 1stp 1rob 2lyz 1ifb 2ifb \
        1hew 1stn 1hel 1snc 5dfr 1hfc 1brq 1rbp 1hsi 1hiv \
        1ida 3ptb 3ptn 4phv 2tga 1cge 1a6u 1srf 1mtw 2ctv \
        1esa 1a6w 1inc 1bmq 1ahc 4ca2 3tms 1djb 1a4j 1cdo \
  --radii-model castp3_protor --workers 3 \
  --output-json /tmp/castp_membership_40.json \
  --output-md /tmp/castp_membership_40.md
```

The JSON retains requested cases, completion state, exact input hashes,
per-case policies, counts and complete missing/extra atom sets. It is updated
after each calculation, allowing incomplete runs to be identified. Calculation
errors remain explicit case records and produce exit 1. A completed discrepant
comparison exits 0 because the computation completed; inspect `passed` to assess
parity. Markdown counts alone do not replace the full record.

## Verification and limits

Audit-contract tests protect duplicate multiplicity, equal-count mismatches,
source identity and explicit unit-bearing policy. Six molecular controls
recalculate complete feature memberships against their original archives.
The published artifact is guarded against incomplete/missing cases, altered
input hashes and inconsistent missing/extra counts.

Verification with pytest-receptor: 20 audit/control tests pass in 111 seconds;
the two additional historical micro-pocket tests pass in 142 seconds; the
complete-artifact guard passes separately. These are 23 distinct tests.
Ruff and bounded mypy pass. Local numerical validation uses the controlled
PyUnitWizard source `23554a7`, consistent with preceding CASTp checkpoints.
This is not installed-package or full OS/Python support certification under #16.

The completed preceding-source CI run `36942562766` fails all six cells.
Native failed-log inspection reveals per-atom connectivity errors affecting
CASTp on Python 3.11/3.12. MolSysMT fixed the empty-array dimensionality issue
under its #283 in `91f157eeb`, while TopoMT CI remains pinned to the older
`3bcfaf4`. Source adoption and matrix revalidation remain consumer work under
TopoMT #16. Python 3.13 has separate local numerical evidence; neither these
comparisons nor its CI passing subsets certify the other cells. No scientific
backend or dependency/CI configuration was changed in this audit.

HTML builds with the same eight existing heading/toctree warnings tracked
under #64. Reporting-protocol tests and generated indexes pass.

This comparison does not measure open-feature SA/MS quantities, exact surface
patches, individual mouth topology or general CASTp3/server equivalence. DFND
and public Topography semantics are unchanged. No server request or original
CASTp executable is required for the calculations. This developer audit adds
no optional engine dependency or new attribution boundary.
