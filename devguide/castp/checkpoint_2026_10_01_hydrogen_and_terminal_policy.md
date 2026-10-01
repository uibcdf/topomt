# CASTp3 hydrogen preparation and bounded terminal policy

Date: 2026-10-01. This extends the
[radius-coverage and twenty-system audit](checkpoint_2026_10_01_radius_coverage_and_void_panel.md).
The completed hydrogen correction belongs to
[#85](https://github.com/uibcdf/topomt/issues/85); terminal-policy coverage
remains partial under [#84](https://github.com/uibcdf/topomt/issues/84).

## Explicit hydrogen caused the missing 1CGE cavities

The archived PDB contains 273 explicit protein hydrogen atoms. The old ProtOr
preparation admitted them as separate spheres with the 1.8 Å heavy-atom
fallback radius. This counted hydrogen effects twice: ProtOr's atomic groups
already represent attached hydrogens implicitly. CASTpFold's
[published computation settings](https://cfold.bme.uic.edu/castpfold/infos/allabout/computation_settings.html)
also state that explicit hydrogens are ignored.

Selecting protein heavy atoms recovered all seven 1CGE memberships and all
28 independent SA/MS quantities without changing the probe, heavy-atom radii,
coordinates, alpha-rank predicates or output-rounding allowance. The actual
correction precedes geometric construction in both local CASTp cores when
ProtOr is selected. It uses `molsysmt.select(atom_type == "H", mask=selected_indices)`
and filters the original selection, preserving its order and original atom
indices. It does not remove atoms from the source molecular system.

Explicit radius overrides take precedence and retain selected atoms. Classical
`castp_param`/`castp1_pdb2alf` routes retain their existing behavior. Connectivity
failures needed for ProtOr typing continue to propagate. Small independent
tests cover all three ProtOr dispatches, preserved classical/override behavior
and reordered selections; the molecular guard now asserts seven voids and
twenty-eight measures rather than expecting the old discrepancy.

## Contribution identity explains terminal inclusion

The original bulb audit kept raw supported PDB atoms, including alternate
locations and OXT labels not necessarily admitted by the server. The new
`atom_source='contributions'` audit option reads exact per-atom contribution
records and verifies their original PDB serial, record type, atom name and
residue name. Archive/PDB/bulb/contribution hashes are retained together.
Only identity fields are read; scalar contributions are not used as native
measurements or fitted radius estimates. The parser handles contribution
rows whose large residue number is joined to the chain field without assuming
the later columns have a universal CSV layout.

Across all 89 archives, no explicit hydrogen is listed. Among 80 OXT records
in supported protein residues, all twelve GLY/LEU OXT atoms are listed and all
68 OXT atoms in thirteen other observed residue types are unlisted. Seven
additional OXT records belong to unsupported residues and are also unlisted.
Every other supported heavy atom with a blank alternate-location field is
listed. This independently supports an admission difference, rather than a
uniform terminal-radius change, for the old interior OXT contradictions.

The corpus evidence is pinned in
[the contribution-based radius artifact](artifacts/contribution_radius_audit_2026_10_01.json).
Its original input hashes and all 87 terminal observations have a durable
guard; the original raw-input artifact is retained as dated history.

## Empirical rules implemented in the explicit server profile

| Policy | Explicit H | GLY/LEU OXT | OXT in observed unlisted residues |
|---|---|---|---|
| `protor` | omitted | legacy local O2H1 / 1.46 Å | retained with legacy local typing |
| `castp3_protor` | omitted | retained with 1.50 Å | omitted |
| Explicit expanded sphere override | retained if selected | supplied sphere | supplied sphere |

The thirteen observed omission labels are ALA, ARG, ASN, ASP, GLN, GLU, HIS,
ILE, LYS, MET, PHE, SER and VAL, each paired with atom name OXT. Other atoms
retain the existing profile, including the four 1.40 Å ASP/GLU oxygen labels.
No rule is extrapolated to CYS, PRO, THR, TRP or TYR OXT, for which the corpus
contains no terminal observation. Unobserved labels and variants retain the
legacy policy and are still unvalidated. OXT = 1.46 Å describes our historical
typing assignment, not an independently established universal terminal ProtOr
radius.

GLY/LEU OXT = 1.50 Å was inferred before checking scalar measures. Independent
four-support equal-power solves reproduce the three printed candidate bulbs
in 1A4J and 1CDO within four-decimal rounding. With verified archived atom
membership and the revised numerical profile, **all 59,080 bulbs in all 89
archives are compatible**. Compatible bulbs have at least four noncoplanar
contacts and no interior supported atom under the audited input model.

This is a radius/input compatibility result using archived contribution
membership. It does not certify native input preparation or complete feature
decomposition for every archive. Runtime geometry applies the bounded rules
from labels using MolSysMT; it never reads contribution files or server
outputs to calculate a result. The reason the server distinguishes GLY/LEU
from other terminal residue labels remains unknown. The profile reproduces
observed provider behavior; it is not presented as a better physical model.

Reproduce the contribution-membership audit:

```bash
python -m devtools.castp.audit_castp3_radii --atom-source contributions \
  --output /tmp/castp_contribution_radius_full.json \
  --summary-output /tmp/castp_contribution_radius_summary.json
```

The committed compact artifact adds exact terminal inclusion observations and
the declared numeric profile to that summary. Both raw and contribution-based
audits remain available; their different input models must be stated.

## Molecular validation and remaining scope

1CGE now reproduces seven closed voids and 28 measures. The two proteins
supplying direct terminal-radius evidence also reproduce their entire closed
panels: 1A4J has 39 voids and 156 measures; 1CDO has 43 voids and 172 measures.
Together with the revalidated nineteen controls, the expanded panel reproduces
**22 systems, 225 closed voids and 900 independent SA/MS comparisons**.
All use the exact archived PDB, protein/peptide selection, 1.4 Å probe,
explicit `castp3_protor`, base alpha rank and verified original atom serials.
All twenty-two cases were freshly calculated under the revised preparation
policy. Their exact input hashes and complete comparisons are pinned in
[the prepared-input void artifact](artifacts/void_audit_2026_10_01_prepared_inputs.json).
The earlier twenty-system artifact is retained, including its original failure.

The new cases are permanent membership, per-measure and Topography unit/mapping
regressions. Membership multiplicity and ambiguous scalar association remain
separate; neither aggregate equality nor a matched subset can pass full parity.
The absolute 0.00050001 allowance remains output rounding, with no relative
tolerance or molecule-specific adjustment.

The terminal proposal remains partial. Controlled inputs for absent terminal
labels, protonation variants and current live jobs are still needed. Native
alternate-location preparation has not been certified on all 89 systems by
the contribution-based radius audit. Open-pocket/mouth analytical definitions
remain separate under #41–#52. DFND and public Topography semantics are unchanged.

## Verification boundary

The focused policy/audit selector passes 55 tests, including failing-first
hydrogen and terminal guards. A later added hash/inclusion artifact test also
passes. Repository Ruff lint/format and the bounded audit-module mypy check
pass. A baseline comparison shows the same 38 preexisting type errors in the
two geometry cores before and after this change; typing cleanup is tracked
independently in [#86](https://github.com/uibcdf/topomt/issues/86). A clean
geometry typing gate is not claimed.

The main regression selector passes 686 tests in 795 seconds. The two newly
added molecular controls pass their separate permanent selector: 332 tests in
712 seconds, including delivery to Topography. Reporting-protocol tests pass
and generated indexes are current. HTML builds with the same eight existing heading/toctree
diagnostics tracked under #64. Local numerical verification uses PyUnitWizard source
`23554a7` as in the preceding CASTp checkpoints; this is not a full installed
OS/Python release-matrix certification under #16.

The preceding source `9516716` has separate CI evidence: the completed
Ubuntu/Python 3.13 job `110622317159` in run `36937886645` reports 1,590
passes and the same seven previously tracked failures (four DFND raw hashes,
two missing fpocket executable comparisons and one dependency metadata
assertion). None of its failures belongs to the CASTp selectors. Other matrix
jobs were still running when that completed job was inspected. This does not
certify a passing full matrix or the present unpushed changes.
