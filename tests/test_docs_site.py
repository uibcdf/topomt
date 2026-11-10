"""Public documentation candidates must be attributable and navigable."""

import json

import pytest

from devtools.docs_site import verify_site


def test_site_receipt_identifies_validated_bytes_and_source(tmp_path):
    (tmp_path / 'index.html').write_text(
        '<title>TopoMT</title><a href="case.html#result">Case</a>'
    )
    (tmp_path / 'case.html').write_text('<h1 id="result">Result</h1>')
    result = verify_site(tmp_path, 'a' * 40, required=('index.html', 'case.html'))
    assert result['source_commit'] == 'a' * 40
    assert result['html_pages'] == 2 and result['local_links'] == 1
    assert json.loads((tmp_path / 'build.json').read_text()) == result
    assert result['files']['case.html']


@pytest.mark.parametrize('target', ['missing.html', 'case.html#missing'])
def test_invalid_site_never_receives_a_passing_receipt(tmp_path, target):
    (tmp_path / 'index.html').write_text(
        f'<title>TopoMT</title><a href="{target}">x</a>'
    )
    (tmp_path / 'case.html').write_text('<h1>Case</h1>')
    with pytest.raises(ValueError, match='Unresolved local'):
        verify_site(tmp_path, 'a' * 40, required=('index.html',))
    assert not (tmp_path / 'build.json').exists()


def test_old_identity_and_missing_required_pages_cannot_be_published(tmp_path):
    (tmp_path / 'index.html').write_text('<title>PocketMT</title>')
    with pytest.raises(ValueError, match='TopoMT'):
        verify_site(tmp_path, 'a' * 40, required=('index.html',))
    (tmp_path / 'index.html').write_text('<title>TopoMT</title>')
    with pytest.raises(ValueError, match='Required page'):
        verify_site(tmp_path, 'a' * 40, required=('content/benchlab/index.html',))


def test_links_outside_the_candidate_are_rejected(tmp_path):
    (tmp_path / 'index.html').write_text('<title>TopoMT</title><a href="../x">x</a>')
    with pytest.raises(ValueError, match='Unresolved local'):
        verify_site(tmp_path, 'a' * 40, required=('index.html',))


def test_theme_template_is_an_asset_rather_than_a_rendered_page(tmp_path):
    (tmp_path / 'index.html').write_text('<title>TopoMT</title>')
    (tmp_path / '_static').mkdir()
    (tmp_path / '_static/template.html').write_text('<a href="{{ pathto() }}">x</a>')
    result = verify_site(tmp_path, 'a' * 40, required=('index.html',))
    assert result['html_pages'] == 1
    assert '_static/template.html' in result['files']
