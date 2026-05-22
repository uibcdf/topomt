from pathlib import Path

from devtools.castp.download_castpfold_oracles import (
    existing_zip_ids,
    parse_pdb_id_list,
    pending_pdb_ids,
)


def test_parse_pdb_id_list_preserves_first_seen_unique_ids(tmp_path):
    list_file = tmp_path / 'ids.md'
    list_file.write_text('1ABC\n# comment\n1abc\n2DEF extra\n\n3ghi\n')

    assert parse_pdb_id_list(list_file) == ['1abc', '2def', '3ghi']


def test_pending_pdb_ids_skips_existing_zip_files(tmp_path):
    output_dir = tmp_path / 'oracles'
    output_dir.mkdir()
    (output_dir / '1abc.zip').write_bytes(b'zip')

    assert existing_zip_ids(output_dir) == {'1abc'}
    assert pending_pdb_ids(['1abc', '2def'], output_dir) == ['2def']
