# Validation, scope and justified interpretation

A complete method explanation must say which conclusions follow from its
definitions, which are discrete implementation results and which have independent
physical evidence. These are complementary forms of support.

## An evidence ladder

| Evidence | Establishes | Does not establish by itself |
| --- | --- | --- |
| Definition | The object an operator intends to represent. | Correct numerical implementation. |
| Conditional mathematical argument | A consequence under named assumptions. | That all software outputs meet those assumptions. |
| Engineering regression | A guarded behavior of the implementation. | Independent physical truth for that behavior. |
| Independent case reference | A geometric conclusion for fixed inputs/model/tolerances. | Accuracy on arbitrary molecular systems. |
| Matched provider comparison | Differences under compatible definitions and inputs. | Universal superiority or novelty. |
| Biological evidence | Support for a functional interpretation in context. | Automatic transfer to every geometric finding. |

The declared software maturity (`canonical`, `provisional`, `experimental`,
`diagnostic`, `deferred`) is another dimension. A canonical software output can
still have an open scientific interpretation or accuracy question.

## What the introductory panel establishes

The canonical [BenchLab collection](../benchlab/synthetic/index.md) retains exact
inputs, independent reasoning, native/public observations and versioned evidence.

| Case/control | Independently justified statement |
| --- | --- |
| Regular tetrahedron, 1.2 Å | Four strict-free hull patches, each connected to the common free centroid and infinity. |
| Regular tetrahedron, 1.4 Å | Covered hull with an admissible interior centroid. |
| Regular tetrahedron, 1.7 Å | No free center anywhere in the finite hull. |
| Closed shell, 0.2 Å | Complete expanded-ball cover of the hull and a free enclosed origin. |
| Shell with opening, 1.4 Å | One free hull patch and an origin-to-exterior witness. |

The wall is a sampled union of balls, not a continuum sphere with an assumed
inner radius. A certificate for the origin-containing region does not prescribe
every cavity or its exact volume. These references were strengthened during
development and are not a held-out biological detector benchmark.

## Current scientific and public-support boundaries

At the documented source, the following owners retain the unresolved work:

- [#151](https://github.com/uibcdf/topomt/issues/151): physical boundary patches,
  component attachment and their relation to native links/Mouth/Percolating.
- [#76](https://github.com/uibcdf/topomt/issues/76): independent reference
  assumptions, physical graph/path interpretation and the broader panel.
- [#75](https://github.com/uibcdf/topomt/issues/75): volume precision and
  finite-sample uncertainty claims.
- [#60](https://github.com/uibcdf/topomt/issues/60) and
  [#61](https://github.com/uibcdf/topomt/issues/61): full public support/context
  and localized interface/relation adoption.

These links are navigation to maintained work, not a permanent assertion that
every issue will stay open. The
[current comparative-findings register](https://github.com/uibcdf/topomt/discussions/154)
retains scoped conclusions and correction history. Check the target version
before reusing a limitation or an advantage in a paper; historical failure does
not automatically describe a later release.

## Extending the evidence

A valid reference fixes the atomic-ball model, probe, support/envelope,
strictness and numerical margins. It is independent of the solver being tested.
A synthetic geometry's name or agreement with another detector is insufficient.

Tests that deliberately preserve fragmentation or other observed pathologies
are useful regressions, but their asserted outcome is not necessarily an ideal
physical result. Changing atom density at fixed atomic radius changes the
represented wall; changing radii changes the model. Probe growth can split a
component. Those possibilities must be resolved before calling a discrepancy
an algorithmic defect.

Original-provider comparisons retain exact execution/version/input scope.
Unsupported, unavailable, failed and completed-empty results differ. A failed
four-atom invocation of another engine supplies no zero-pocket or geometric
inferiority conclusion. The [references](references.md) acknowledge antecedents
without turning integration success into a contribution claim.

## From geometry to biology

A buried empty region can motivate a packing hypothesis; an accessible route
can motivate a transport hypothesis; shared participant-facing support can
motivate an interface hypothesis. None alone measures binding affinity, entry
rates, solvent populations or folding free energy. These need additional
physical/chemical models and biological evidence.

The current teaching work does not initiate new native protein characterization.
The selected three synthetic systems remain the development focus. Source-level
examples and a built documentation site also do not qualify an installed package,
platform/interpreter matrix or every provider route.

**Reading check:** for a scientific claim you would make from a result, identify
its measured set, model, inference, independent support and target software scope.

```{dropdown} One worked answer
Claim: the 1.4 Å tetrahedron has an enclosed admissible center region. The model
is the four 1.7 Å atomic balls with the frozen coordinates and a strict center
convention. Its centroid has clearance above 1.4 Å, while the complete hull is
covered by expanded balls; any center path to infinity would have to cross that
hull. The independent certificate supplies both statements. DFND's public Void
agrees for the documented source/input, but this example gives no exact cavity
volume and no blanket qualification of Void detection in arbitrary proteins.
```
