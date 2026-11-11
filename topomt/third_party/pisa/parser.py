"""Read original supplied-assembly PISA XML, not predicted assemblies."""

import re
import xml.etree.ElementTree as ET

from topomt.provider_output import ProviderRun
from topomt.third_party._protocol import artifact, finite, measurement
from topomt.third_party._specialist import validate_inputs
from topomt.third_party.output import ProviderRecord

from .output import PisaOutput

VERSION = '2.1.2'
CONTACT_TYPES = ('h-bonds', 'salt-bridges', 'ss-bonds', 'cov-bonds', 'other-bonds')
ASSEMBLY_FIELDS = {
    'asa': ('accessible_surface_area', 'angstroms**2'),
    'bsa': ('buried_surface_area', 'angstroms**2'),
    'diss_area': ('dissociation_area', 'angstroms**2'),
    'diss_energy': ('dissociation_energy', 'kilocalories/mol'),
    'entropy': ('entropy_term', 'kilocalories/mol'),
    'int_energy': ('solvation_energy', 'kilocalories/mol'),
}


def xml_root(data: bytes, expected: str) -> ET.Element:
    """Accept ordinary original XML without DTDs or entity declarations."""
    if b'<!DOCTYPE' in data.upper() or b'<!ENTITY' in data.upper():
        raise ValueError('PISA XML document/entity declarations are not admitted')
    try:
        node = ET.fromstring(data)
    except ET.ParseError as cause:
        raise ValueError('Malformed or incomplete original PISA XML') from cause
    if node.tag != expected:
        raise ValueError('Unexpected original PISA XML root')
    return node


def text(node: ET.Element, key: str, *, empty: bool = False) -> str:
    matches = node.findall(key)
    if len(matches) != 1 or len(matches[0]):
        raise ValueError(f'PISA requires a unique scalar {key}')
    value = (matches[0].text or '').strip()
    if not empty and not value:
        raise ValueError(f'PISA field is empty: {key}')
    return value


def integer(node: ET.Element, key: str) -> int:
    value = text(node, key)
    if not value.isdecimal():
        raise ValueError(f'PISA field requires a nonnegative integer: {key}')
    return int(value)


def packet(node: ET.Element, key: str, unit: str, *, nonnegative: bool = False) -> dict:
    token = text(node, key)
    return {
        'value': finite(token, nonnegative=nonnegative),
        'unit': unit,
        'original_token': token,
        'source_field': key,
    }


def _participant(node: ET.Element) -> dict:
    data: dict = {key: text(node, key) for key in ['id', 'chain_id', 'class']}
    data.update({key: integer(node, key) for key in ['int_natoms', 'int_nres']})
    data['buried_surface_area'] = packet(
        node, 'int_area', 'angstroms**2', nonnegative=True
    )
    data['solvation_energy'] = packet(node, 'int_solv_en', 'kilocalories/mol')
    data['pvalue'] = packet(node, 'pvalue', 'dimensionless', nonnegative=True)
    if data['pvalue']['value'] > 1:
        raise ValueError('PISA probability is outside [0,1]')
    data['residues'] = []
    seen = set()
    for residue in node.findall('residues/residue'):
        item: dict = {
            key: text(residue, key, empty=key in {'ins_code', 'bonds'})
            for key in [
                'ser_no',
                'name',
                'seq_num',
                'label_seq_num',
                'ins_code',
                'bonds',
            ]
        }
        identity = (item['seq_num'], item['ins_code'])
        if identity in seen:
            raise ValueError('Duplicate original PISA residue')
        seen.add(identity)
        item.update(
            {
                key: packet(residue, key, unit, nonnegative=key != 'solv_en')
                for key, unit in [
                    ('asa', 'angstroms**2'),
                    ('bsa', 'angstroms**2'),
                    ('solv_en', 'kilocalories/mol'),
                ]
            }
        )
        data['residues'].append(item)
    if data['int_nres'] > len(data['residues']):
        raise ValueError('PISA participant residue inventory is incomplete')
    return data


def decode_reports(interfaces: bytes, assemblies: bytes) -> dict:
    """Keep interface sides, contact identities and the supplied-assembly summary."""
    root = xml_root(interfaces, 'pdb_entry')
    assembly_root = xml_root(assemblies, 'pisa_results')
    if text(root, 'status') != 'Ok' or text(assembly_root, 'status') != 'Ok':
        raise ValueError('Original PISA XML does not report success')
    description = ' '.join(text(assembly_root, 'status_description').split())
    if 'Assemblies not calculated' not in description:
        raise ValueError(
            'PISA reader requires supplied-assembly analysis without assembly prediction'
        )
    summary = assembly_root.findall('asu_complex/assembly')
    if len(summary) != 1:
        raise ValueError(
            'Original PISA supplied-assembly summary is absent or ambiguous'
        )
    assembly = {
        key: packet(summary[0], key, unit, nonnegative=unit == 'angstroms**2')
        for key, (_, unit) in ASSEMBLY_FIELDS.items()
    }
    result = []
    identities = set()
    for interface in root.findall('interface'):
        identity = text(interface, 'id')
        if not identity.isdecimal() or int(identity) <= 0 or identity in identities:
            raise ValueError('Invalid or duplicated PISA interface identity')
        identities.add(identity)
        participants = [_participant(p) for p in interface.findall('molecule')]
        if len(participants) != 2 or len({p['chain_id'] for p in participants}) != 2:
            raise ValueError(
                'PISA supplied interface requires two distinct participants'
            )
        fields: dict = {
            'source_id': identity,
            'participants': participants,
            'interface_type': integer(interface, 'type'),
            'occurrences': integer(interface, 'n_occ'),
            'measures': {
                name: packet(
                    interface, key, unit, nonnegative=key in {'int_area', 'pvalue'}
                )
                for name, key, unit in [
                    ('interface_area', 'int_area', 'angstroms**2'),
                    ('solvation_energy', 'int_solv_en', 'kilocalories/mol'),
                    ('stabilisation_energy', 'stab_en', 'kilocalories/mol'),
                    ('pvalue', 'pvalue', 'dimensionless'),
                ]
            },
            'contacts': {},
            'contact_counts': {},
        }
        if fields['measures']['pvalue']['value'] > 1:
            raise ValueError('PISA interface probability is outside [0,1]')
        for kind in CONTACT_TYPES:
            groups = interface.findall(kind)
            if len(groups) != 1:
                raise ValueError('PISA contact group is absent or duplicated')
            contacts = []
            for contact in groups[0].findall('bond'):
                original = {child.tag: (child.text or '').strip() for child in contact}
                if len(original) != len(contact):
                    raise ValueError('Duplicate PISA contact field')
                for side in ['1', '2']:
                    for key in ['chain', 'res', 'seqnum', 'inscode', 'atname']:
                        text(
                            contact, key + '-' + side, empty=key in {'chain', 'inscode'}
                        )
                contacts.append(
                    {
                        'original': original,
                        'distance': packet(
                            contact, 'dist', 'angstroms', nonnegative=True
                        ),
                    }
                )
            count = integer(groups[0], 'n_bonds')
            if count != len(contacts):
                raise ValueError('PISA contact count disagrees with its rows')
            fields['contacts'][kind] = contacts
            fields['contact_counts'][kind] = count
        result.append(fields)
    if integer(root, 'n_interfaces') != len(result):
        raise ValueError('PISA interface count disagrees with original rows')
    return {
        'interfaces': result,
        'assembly': assembly,
        'assembly_policy': 'supplied_as_is',
    }


def monomer_atom_count(data: str) -> int:
    """Read the original Nat inventory; unknown/omitted atoms are not empty success."""
    if 'LIST OF MONOMERS' not in data or f'PISA v.{VERSION}' not in data:
        raise ValueError('Unsupported or missing PISA monomer inventory')
    rows = re.findall(
        r'^\s*\d+\s+\d+\s*\|[^|]+\|\s*\S+\s+(\d+)\s+\d+\s+\d+\s+\d+\s+\S+\s+\S+\s*$',
        data,
        re.M,
    )
    if not rows:
        raise ValueError('PISA monomer atom inventory is absent')
    return sum(map(int, rows))


def _contact_mapping(run: ProviderRun, fields: dict) -> tuple[int, ...] | None:
    if run.metadata.get('adapter_protocol') != 'topomt.original-local@1':
        return None
    rows = [
        line
        for line in run.get_artifact('input/input.pdb').decode().splitlines()
        if line.startswith(('ATOM  ', 'HETATM'))
    ]
    indices = run.metadata['selected_atom_indices']
    if len(rows) != len(indices):
        raise ValueError('PISA submitted row/source-index mapping is incomplete')
    mapping = {}
    for line, index in zip(rows, indices):
        key = (
            line[21].strip(),
            str(int(line[22:26])),
            line[26].strip(),
            line[17:20].strip(),
            line[12:16].strip(),
        )
        if key in mapping:
            raise ValueError('Ambiguous PISA submitted atom identity')
        mapping[key] = index
    contact_indices = set()
    for contacts in fields['contacts'].values():
        for contact in contacts:
            raw = contact['original']
            pair = []
            for side in ['1', '2']:
                key = tuple(
                    raw[key + '-' + side]
                    for key in ['chain', 'seqnum', 'inscode', 'res', 'atname']
                )
                if key not in mapping:
                    raise ValueError(
                        'PISA contact identity does not resolve to a submitted atom'
                    )
                pair.append(mapping[key])
            contact['source_atom_indices'] = pair
            contact_indices.update(pair)
    return tuple(sorted(contact_indices))


def parse_output(run: ProviderRun) -> PisaOutput:
    """Bind contact atoms only when exact submitted/source identities are known."""
    data = decode_reports(
        artifact(run, 'interfaces.txt'), artifact(run, 'assemblies.txt')
    )
    validate_inputs(run, ('pisa.cfg',))
    if run.metadata.get('adapter_protocol') == 'topomt.original-local@1':
        if (
            run.metadata.get('version') != VERSION
            or run.metadata.get('assembly_policy') != 'supplied_as_is'
        ):
            raise ValueError('PISA saved version or supplied-assembly policy disagrees')
        count = sum(
            line.startswith(('ATOM  ', 'HETATM'))
            for line in run.get_artifact('input/input.pdb').decode().splitlines()
        )
        if monomer_atom_count(artifact(run, 'monomers.txt').decode()) != count:
            raise ValueError('PISA omitted or expanded submitted atoms')
    records = []
    for fields in data['interfaces']:
        indices = _contact_mapping(run, fields)
        fields['external_measurements'] = {
            name: measurement(
                run,
                value['value'],
                value['unit'],
                f'interface/{fields["source_id"]}/{value["source_field"]}',
                'interfaces.txt',
                'Original supplied-assembly PISA interface measure; interface area averages the two buried sides, energies are model estimates, and no biological-interface classification is inferred',
            )
            for name, value in fields.pop('measures').items()
        }
        records.append(
            ProviderRecord(
                fields['source_id'],
                'interface',
                run,
                atom_indices=indices,
                atom_role='reported_contact_atoms'
                if indices is not None
                else 'unavailable_contact_atom_map',
                _fields=fields,
            )
        )
    return PisaOutput(run, tuple(records))
