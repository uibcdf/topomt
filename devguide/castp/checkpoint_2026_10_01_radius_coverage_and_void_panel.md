# CASTp radius coverage and expanded closed-void checkpoint

Date: 2026-10-01. Bounded outcome under
[#82](https://github.com/uibcdf/topomt/issues/82), extending the
[four-system radius-profile study](checkpoint_2026_10_01_castp3_radius_profile.md).

## Scope and reproducible evidence

The offline radius audit accounts for all **89 bundled CASTpFold archives**
and **59,080 printed bulbs**, evaluating `protor` and `castp3_protor` separately.
The [compact radius artifact](artifacts/radius_audit_2026_10_01.json) preserves
archive/PDB/bulb SHA-256 identities, per-case status counts, atom-label coverage
and new conditional candidates. The [closed-void artifact](artifacts/void_audit_2026_10_01.json)
contains twenty systems, exact memberships and each independently compared
SA/MS quantity with units, error and rounding allowance.

The audit reuses existing provider-specific radius assignment operations.
It searches all supported protein heavy-atom labels rather than filtering for
ASP/GLU. Source PDB coordinates are treated as the exact archived input; printed
bulb centers/radii have rounding half-width 0.00005 Å. The base-radius interval
is derived from `sqrt(distance**2 - bulb_radius**2) - probe_radius`, including
coordinate/radius rounding bounds. Probe 1.4 Å is the explicit archived-panel
assumption, not a new live-server observation.

Four noncoplanar equal-power contacts and no interior supported atom establish
conditional compatibility. Three unchanged contacts allow a unique fourth
candidate within a 0.25 Å search window; this window is not a passing tolerance.
Multiple candidates remain ambiguous. Simultaneous unknown changes, omitted
atom types, variants absent from the corpus and server preprocessing are not
certified. Raw alternate locations are retained in the radius audit; conflicts
can therefore describe input-inclusion differences rather than wrong radii.
Bulb files do not identify their supporting atoms. The algorithm distinguishes
compatible evidence from recovered server atom identity.

Reproduce the full radius report and compact summary:

```bash
python -m devtools.castp.audit_castp3_radii \
  --output /tmp/castp_radius_full.json --summary-output /tmp/castp_radius_summary.json
```

## Corpus result and other oxygen controls

| Profile | Compatible bulbs | Unique one-change candidates | Ambiguous | Conflicts | Unresolved |
|---|---:|---:|---:|---:|---:|
| `protor` | 47,718 | 9,177 | 16 | 411 | 1,758 |
| `castp3_protor` | 58,696 | 3 | 18 | 363 | 0 |

The existing four carboxylate overrides remove most incompatibilities. Seventy
of the 89 archives have every bulb compatible under `castp3_protor`; this does
not certify their component decomposition or all atom assignments.

Observed counts below are unique atom serials per archive, counted only when
they contact compatible bulbs. Presence is tracked separately in the artifact.
Homologous structures are not independent chemical families.

| Atom label | Present atoms | Observed compatible atoms under `castp3_protor` |
|---|---:|---:|
| ASN OD1 | 1,418 | 341 |
| GLN OE1 | 1,047 | 280 |
| SER OG | 2,140 | 634 |
| THR OG1 | 1,774 | 515 |
| TYR OH | 1,039 | 383 |

All twenty standard amino-acid backbone O labels have positive observations.
ASP OD1/OD2 and GLU OE1/OE2 have respectively 448, 433, 431 and 464 observed
atoms under the empirical profile. These controls support the current amide,
hydroxyl and backbone assignments in observed geometry; they do not exclude
differences in unobserved labels, protonation states or later server versions.

## Terminal oxygen is a separate unresolved policy

Three unique conditional candidates support OXT near 1.50 Å instead of local
O2H1 / 1.46 Å: 1A4J feature 3 bulbs 116 and 159 (zero-based bulb indices),
GLY L217 serial 1668; and 1CDO feature 39 bulb 2, LEU B374 serial 5607.
The artifact preserves their conservative radius intervals. An independent
linear equal-power solve checks the hypothesized four supports against all
four printed center/radius values; this is a conditional reconstruction,
not proof of the server's inclusion policy.

No OXT label has positive compatible contact evidence under the current
1.46 Å assignment. Other archives contain extra interior OXT atoms even with
four compatible anchors: 1BID, 1BLH, 1BMQ, 1YPI, 2YPI, 5CNA and 7CPA.
Increasing their radius worsens that contradiction. Inclusion, typing and
archive/job version must be established together under
[#84](https://github.com/uibcdf/topomt/issues/84). No OXT override is adopted.

## Expanded analytical closed-void panel

The exact archived PDB, protein/peptide selection, 1.4 Å probe, explicit
`castp3_protor` and base alpha rank are fixed. Membership is matched by verified
original atom serial sets; measures are compared only for uniquely matched
components. Duplicate membership multiplicity is retained and ambiguous scalar
association cannot pass. Areas use Å², volumes Å³. Absolute allowance is
0.00050001 with zero relative tolerance, reflecting three-decimal output.

| PDB | Server voids | Native voids | Exact memberships | Passing SA/MS measures | Outcome |
|---|---:|---:|---:|---:|---|
| 1a6w | 12 | 12 | 12 | 48 | pass |
| 1bmq | 15 | 15 | 15 | 60 | pass |
| 1cge | 7 | 4 | 4 | 16 | three missing voids |
| 1crn | 1 | 1 | 1 | 4 | pass |
| 1hel | 4 | 4 | 4 | 16 | pass |
| 1hew | 3 | 3 | 3 | 12 | pass |
| 1ifb | 4 | 4 | 4 | 16 | pass |
| 1rob | 2 | 2 | 2 | 8 | pass |
| 1snc | 8 | 8 | 8 | 32 | pass |
| 1srf | 12 | 12 | 12 | 48 | pass |
| 1stn | 7 | 7 | 7 | 28 | pass |
| 1stp | 3 | 3 | 3 | 12 | pass |
| 2ctv | 14 | 14 | 14 | 56 | pass |
| 2ifb | 6 | 6 | 6 | 24 | pass |
| 2lyz | 6 | 6 | 6 | 24 | pass |
| 2pk4 | 4 | 4 | 4 | 16 | pass |
| 2tga | 16 | 16 | 16 | 64 | pass |
| 3phv | 2 | 2 | 2 | 8 | pass |
| 3ptb | 14 | 14 | 14 | 56 | pass |
| 5dfr | 3 | 3 | 3 | 12 | pass |

Nineteen systems reproduce **136 voids and all 544 SA/MS measures**. Including
1CGE's four reproduced cavities yields **140 exact memberships and 560 passing
measures out of 143 server voids**; twelve quantities for the three missing
components are unmeasured, not counted as passing or measured residuals.
All 231 archived 1CGE bulbs are compatible with the radius audit, which still
does not establish closed-component topology. Investigation remains under
[#85](https://github.com/uibcdf/topomt/issues/85).

Run the complete molecular panel explicitly; it returns nonzero for 1CGE:

```bash
python -m devtools.castp.audit_castp3_void_measurements \
  --ids 1a6w 1bmq 1cge 1crn 1hel 1hew 1ifb 1rob 1snc 1srf \
        1stn 1stp 2ctv 2ifb 2lyz 2pk4 2tga 3phv 3ptb 5dfr \
  --output /tmp/castp_void_panel.json
```

## Corrected oracle identity and historical limits

The first eight-system run misreported 1ROB because the old harness indexed raw
PDB rows after MolSysMT had removed alternate locations. The exact PDB has
1077 atom rows but 1073 retained atoms; 1007 mapped positions were wrong.
The shared operation now obtains retained MolSysMT IDs and verifies their
coordinates/serials against the source, rejecting inconsistencies. The rerun
has two exact voids and eight matching measures. The pinned artifact contains
the corrected result; the failing-first regression owns
[#83](https://github.com/uibcdf/topomt/issues/83).

The [historical 38-system membership checkpoint](checkpoint_2026_04_29_castp3_38_system_oracle_parity.md)
has not been rerun. Its alternate-location counts must not be treated as
verified current evidence. Its old cavity mismatches for 5DFR, 1A6W, 1BMQ,
1STN, 2IFB and 1SNC are superseded only for the present fixed-profile closed-void
contract. Open pocket/mouth membership was not measured in this new panel.

## Verification and next work

The permanent molecular regression panel covers all nineteen passing systems;
a separate diagnostic test preserves 1CGE's missing cavities in the denominator.
Independent sphere tests cover unfamiliar labels, rounded output, interior
atoms, coplanarity and ambiguous/multiple changed supports. The compact corpus
artifact is guarded against changes in any of the 89 archive hashes.

Verification with pytest-receptor: the expanded CASTp selector passed 616
tests in 740 seconds; the subsequent twenty-test audit selector also passed,
including the independently reconstructed OXT bulbs, corpus hashes and 1CGE
failure accounting added after the larger run's collection. The reporting
protocol's two tests pass and generated queue/archive indexes are current.
Ruff lint and formatting pass across the repository; bounded mypy checks pass
for both new offline audit modules with imported bodies skipped and absent
third-party stubs ignored. The HTML documentation build succeeds with eight
existing heading/toctree diagnostics; it is not a warning-free gate (#64).
The local quantity layer is PyUnitWizard source `23554a7`, matching the
controlled previous CASTp validation setup. This selector does not certify the
entire library or the cross-platform release matrix under #16.

```bash
python -m pytest --receptor=llm \
  tests/methods/castp/test_castp_radius_audit.py \
  tests/methods/castp/test_castp_void_measurement_audit.py \
  tests/methods/castp/test_castp3_oracle_comparison.py \
  tests/methods/castp/test_castp_modern_void_measurements.py
```

Next work is the OXT inclusion/radius policy (#84), 1CGE closed connectivity
(#85), then open-pocket and mouth definitions under #41–#52. None of these
results establish full CASTp3 equivalence or change DFND or public Topography
semantics. Original external-tool integrations remain separate.
