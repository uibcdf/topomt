# Molecular interfaces and localized geometry

An interface concerns the relationship between participants and the geometry
through which that relationship is expressed. It can include a pocket, a buried
cavity, facing surface patches or direct contact without a bounded wet region.

## Participants and banks

A participant is a named molecular selection with an explicit atom mapping.
It can be a chain, molecule or user-defined assembly. A dry bank is a connected
geometric support under a probe/query policy. Neither determines the other:

- a tightly contacting dimer can form one bank;
- one participant can contribute to several banks;
- atoms can line several regions and have several roles simultaneously.

Do not silently replace a failed multi-bank criterion with a chain-label
criterion. Both may be useful, but they are different definitions with different
provenance.

## Three levels of interface description

| Level | Evidence it carries |
| --- | --- |
| Mesh incidence | Which cells/faces or banks touch under the discrete construction. |
| Interface association | Which molecular participants are associated and under what criterion. |
| Localized realization | The actual facing patches, wet subregion or contact support realizing that association. |

Two endpoint identifiers establish neither localization nor a geometric area.
Whole-component multi-participant lining can be informative without defining a
crisp interface patch. A buried interface needs no mouth; a contact-only interface
needs no fabricated cavity volume.

## Existing descriptors and their scope

Typed native wet components and promoted features carry bank-derived interface
descriptors, including lining-bank identities and `is_interface`. The separate
prototype helpers in `topomt.dfnd.interfaces` can also classify raw records using
explicit per-atom body labels and stated contribution thresholds.

These routes are not identical. Explicit labels in a helper do not imply that
the normal promotion path automatically ingests chain identities. Bank-derived
labels can miss tightly packed molecular interfaces when banks fuse. The full
public participant/relation/localized-support model is still being adopted.

Interface status is orthogonal to the primary Void/Pocket/Channel classification.
A region can be both a pocket and an interface-associated finding. Future mixed
interface features need their own support and promotion invariants.

## The analysis context changes the question

Analyzing an assembled receptor–ligand system changes the input ball union.
Characterizing a previously defined receptor pocket with a ligand pose asks a
different question: how the pose contacts, occupies or relates to that fixed
reference region. Do not treat the disappearance of empty space after adding
ligand atoms as the same operation as measuring occupancy of the old region.

Contact and complementarity evaluations must state their supports, atom roles,
pose, distances and numerical policy. `accessible_atom_indices` is a declared
probe-related atom role, not a list of contacts measured for an arbitrary ligand.

## Biological interpretation

A narrow gap, shared lining or small empty volume can motivate a hypothesis
about recognition or packing. It does not calculate affinity, stabilization free
energy or solvent occupancy probability. Chemical characterization is an
additional layer; it does not change the geometric family merely by making a
pocket polar or hydrophobic.

Use selected participants, explicit geometric criteria and independent biological
evidence when moving from an interface descriptor to a functional interpretation.
The three introductory BenchLab systems explain geometry and access; they do not
qualify a molecular interface detector.
