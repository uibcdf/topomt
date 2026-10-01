# Modern CASTp radius profile and expanded closed-void panel

Date: 2026-10-01. Owning issue:
[#80](https://github.com/uibcdf/topomt/issues/80).
This extends the [first closed-void milestone](checkpoint_2026_10_01_modern_void_measurements.md).

## What the expanded panel revealed

The exact archived PDBs, protein/peptide selection, a 1.4 Å probe and the
standard `protor` profile reproduced all thirteen closed-void lining-atom sets
in 2PK4, 1IFB, 3PHV and 1HEW. Forty-four of fifty-two SA/MS values matched the
server's three-decimal reporting precision. The eight remaining scalar values
belonged to 1IFB cavity 1 and 1HEW cavity 7. The initial permanent regression
run reproduced precisely those eight failures, with 56 other tests passing.

For 1HEW cavity 7, standard ProtOr gave SA area 1.224731627 Å² instead of
1.255 Å². Independent exploratory Sobol integration over the eight local
spheres and six tetrahedra gave 1.224404258 and 1.224744086 Å², using two seeds
and 4,194,304 samples per sphere. This supports the local geometric calculation
for those balls; it does not itself define a modern-server oracle or establish
a certified error bound. No nonintersecting alpha-complex triangle was found
in that cavity. These probes motivated checking the input sphere model.

## Independent radius evidence from server geometry

The pinned `.bulb.json` for 1HEW cavity 7 exports six sphere centers and radii.
Four agree with local weighted orthospheres under standard ProtOr. The two
remaining tetrahedra contain ASP 66 OD1, PDB serial 528. Each has three other
atoms consistent with the existing profile. From the server center `c`, bulb
radius `r` and archived atom position `x`, the expanded atomic radius is
inferred as `sqrt(||x-c||²-r²)`; subtracting the probe gives the atomic radius.

The two independently exported bulbs imply 1.399964066 and 1.400057776 Å for
that oxygen, consistent with 1.40 Å and the four-decimal geometric output.
Standard ProtOr currently assigns 1.42 Å. An exploratory scan of the pinned
1IFB, 1HEW, 3PHV, 1TCD and 3PTB bulbs corroborates the 1.40 Å assignment for
ASP OD1/OD2 and GLU OE1/OE2 with three unchanged radius anchors. This is an
empirical inference from exported geometry, not a claim about unpublished
server source or a new universal ProtOr table. The scan found no such evidence
in the selected 2PK4 artifacts.

The durable 1HEW guard independently solves equal-power linear equations from
the input balls, rather than calling the kernel's determinant-center routine.
It matches all six exported centers and radii one-to-one with absolute
tolerance 0.000050001, justified by their four-decimal output.

## Explicit profile and owning implementation

`build_castp_geometry(..., radii_model='castp3_protor')` now selects the
identified modern-server profile. It reuses the existing ProtOr assignment
operation and changes only the four named ASP/GLU carboxylate labels to 1.40 Å.
The existing `protor` policy, historical radius tables and defaults retain
their definitions. Carbonyl oxygen and hydroxyl assignments are not changed;
unverified protonation variants are not assigned new server overrides.

The operation belongs to the provider-specific geometry module, behind its
existing reusable builder. It requires no new dependency, scientific quantity
class or Topography concept. The profile helper has its own radius-policy tests;
consumers select it through `radii_model`, not by editing atom radii. Both
typing profiles retain connectivity requirements and propagate failures.
Explicit already-expanded radius arrays still take precedence and bypass typing.

No metric-formula change, molecule-specific adjustment, output-value fit or
geometric epsilon change was needed. The new profile is an explicit hypothesis
derived from server geometry and verified independently against SA/MS values.

## Result

| Pinned CASTpFold archive | Closed voids | Exact atom sets | SA/MS values at server precision |
|---|---:|---:|---:|
| 2PK4 | 4 | 4 | 16/16 |
| 1IFB | 4 | 4 | 16/16 |
| 3PHV | 2 | 2 | 8/8 |
| 1HEW | 3 | 3 | 12/12 |
| Total | 13 | 13 | 52/52 |

All comparisons use `castp3_protor`, base alpha rank, a 1.4 Å probe, exact PDB
serial-set matching, no cusp correction, absolute SA/MS tolerance 0.00050001
and zero relative tolerance. Job-ID archive member names are retained when
locating data; the extracted PDB contents are unchanged. Tests assert that
neither original nor local atom-set dictionaries collapse duplicate features.
Geometry and analytical measurements are cached once per case inside the test
fixture; each scalar comparison remains independently addressable.

Initial corrected selector: 85 passed, with no skips or expected failures.
The final selector passed 125 tests, including unit-bearing Topography delivery
on all four systems and original-result/regression/governance routes.
Full-repository Ruff lint and format checks pass. HTML documentation builds with
the same eleven diagnostics outside the changed page. Bounded mypy on
the geometry module reports the same nineteen existing diagnostics before and
after this change; it is not a clean typing certificate.

## Reproduction and next work

```python
import topomt as tmt

topography = tmt.third_party.castp3.get_topography(
    'protein.pdb', backend='native', radii_model='castp3_protor', probe_radius=1.4
)
```

```bash
python -m pytest --receptor=llm \
  tests/methods/castp/test_castp_modern_void_measurements.py \
  tests/test_castp3_protor.py \
  tests/methods/castp/test_castp_geometry_metadata.py
```

Next re-audit the previously discrepant void/classification cases with the
correct sphere model before changing their alpha-complex predicates. Then
address analytical open-pocket and mouth boundaries under #41–#52. The profile
is still experimental outside its tested panel; it does not establish all-server
parity, alter DFND or enable native results through the original-output route.
