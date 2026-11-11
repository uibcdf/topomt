# PISA: interfaces of a supplied assembly

[PISA](https://github.com/PDBe-KB/pisa) analyzes macromolecular interfaces.
TopoMT invokes an externally acquired PISA 2.1.2 executable with `--as-is`:
the supplied coordinates define the assembly to analyze. This route omits
assembly prediction and does not infer biological relevance.

```python
import topomt as tmt

output = tmt.get_provider_output(
    'assembly.pdb', method='pisa', pisa_cmd='/tools/pisa',
    pisa_home='/tools/pisa-source', workers=1, timeout=120,
)
for interface in output.interfaces:
    area = interface.measurements['interface_area']
    participants = interface.fields['participants']
    contacts = interface.fields['contacts']
    print(interface.source_id, area.value, participants)

assembly = output.assembly_measurements
assert output.assembly_policy == 'supplied_as_is'
```

`pisa_home` points either to the original source/distribution containing `setup/`
or directly to that setup directory. It supplies SRS, MolRef, PISA parameters
and symmetry resources. TopoMT records their fingerprints and creates a private
session directory for each execution. It does not ship the executable or those
datasets.

## What the fields mean

The original interface area averages the buried surface areas of its two
participants. It is reported in Å². Participant areas and residue ASA/BSA remain
separate. The supplied assembly's total buried area is a different measure.
Solvation, stabilization, dissociation and entropy **energy terms** retain
kcal/mol. They are estimates from PISA's model, not experimental binding energies.

Hydrogen bonds, salt bridges, disulfides, covalent contacts and other contacts
retain their original groups, counts, atom/residue/chain identities and distances
in Å. The 4 Å other-contact set can contain atoms outside the buried-atom set;
TopoMT preserves those two definitions. With source-bound execution,
`interface.atom_indices` maps the reported contact atoms to the source system.
It does not label every atom in an interface residue as a contact atom.

Author chain/residue identifiers and label identifiers remain distinguishable.
The adapter rejects ambiguous source/contact identities and omitted input atoms
rather than manufacturing a map. Raw XML imports without source-bound provenance
retain an unavailable contact map. An explicit zero-interface result is valid;
missing XML or an unsuccessful status is a failure. The supplied-assembly summary
remains available even when no interfaces are found.

## Acquisition and scope

PDBe documents local compilation and research use. CCP4 provides a free academic
acquisition route under its agreement; see [CCP4's information](https://www.ccp4.ac.uk/ccp4-commercial-users/)
and [PDBe's protocol](https://doi.org/10.1002/cpz1.70446). The precise standalone
engine/resource redistribution grant remains unconfirmed. Apache-2.0 on
`pisa-analysis` and CC-BY on public results are separate grants. This adapter
uses the user's external installation, without redistributing PISA or its data.

The route uses one worker, `max_atoms=25000`, and a 120-second default timeout
per original command. It accepts one selected source frame and its reference
chemical state. It performs no remote coordinate upload. Crystal assembly
prediction, arbitrary symmetry generation and native Topography admission are
outside this route. Source controls use two small synthetic chains in contacting
and separated arrangements; they do not validate biological-interface prediction
or energy accuracy.

```python
output.save('pisa.zip')
restored = tmt.load_provider_output('pisa.zip', molecular_system='assembly.pdb')
```

The saved reader needs neither PISA nor its setup resources, and verifies source
identity and the supplied-assembly policy. It preserves original XML, resource
fingerprints, software version and optional Ackredit bibliography without
crediting another calculation. Fresh successful runs credit PISA's original
and enhanced-interface descriptions at the accepted result boundary.
