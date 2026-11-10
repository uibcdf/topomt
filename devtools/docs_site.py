"""Validate the TopoMT documentation candidate and retain its byte identity."""

import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REQUIRED = (
    'index.html',
    'content/dfnd/index.html',
    'content/benchlab/index.html',
    'content/benchlab/synthetic/index.html',
    'content/benchlab/molecular/index.html',
    *(
        f'content/benchlab/synthetic/{case}/{page}.html'
        for case in ('regular_tetrahedron', 'closed_shell', 'shell_with_opening')
        for page in ('index', 'system', 'dfnd')
    ),
)


class _Page(HTMLParser):
    def __init__(self, path: Path):
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.feed(path.read_text())

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        anchor = values.get('id')
        if anchor:
            self.ids.add(anchor)
        for key in ('href', 'src'):
            target = values.get(key)
            if target:
                self.links.append(target)


def verify_site(
    directory: Path,
    commit: str,
    *,
    required: tuple[str, ...] = REQUIRED,
) -> dict:
    """Check navigation and write a source/byte manifest after success.

    Parameters
    ----------
    directory : Path
        Built HTML root, including copied resources.
    commit : str
        Full source commit checked out by the documentation producer.
    required : tuple of str
        Required pages relative to the HTML root.

    Returns
    -------
    dict
        Build receipt also written as ``build.json``.

    Raises
    ------
    ValueError
        Identity, required content or local navigation is invalid.

    Examples
    --------
    Run ``python devtools/docs_site.py HTML --commit FULL_SOURCE_SHA`` after
    the Sphinx build. This does not upload or deploy anything.
    """
    root = directory.resolve()
    receipt = root / 'build.json'
    receipt.unlink(missing_ok=True)
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise ValueError('Source identity must be a full commit SHA')
    for relative in required:
        if not (root / relative).is_file():
            raise ValueError(f'Required page missing: {relative}')
    home = (root / 'index.html').read_text()
    title = re.search(r'<title>(.*?)</title>', home, flags=re.S)
    if not title or 'TopoMT' not in title[1] or 'PocketMT' in title[1]:
        raise ValueError('Home must identify the site as TopoMT')
    documents = {
        p: _Page(p)
        for p in root.rglob('*.html')
        if not p.relative_to(root).parts[0] == '_static'
    }
    failures = []
    links = 0
    for path, document in documents.items():
        for link in document.links:
            url = urlsplit(link)
            if url.scheme or url.netloc or url.path.startswith('/'):
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= 'index.html'
            links += 1
            if not target.is_relative_to(root) or not target.is_file():
                failures.append((str(path.relative_to(root)), link))
            elif url.fragment and target.suffix == '.html':
                target_page = documents.get(target) or _Page(target)
                if unquote(url.fragment) not in target_page.ids:
                    failures.append((str(path.relative_to(root)), link))
    if failures:
        raise ValueError(f'Unresolved local navigation: {failures[:20]}')
    result = {
        'schema': 'topomt.documentation-build/1',
        'source_commit': commit,
        'html_pages': len(documents),
        'local_links': links,
        'notebook_execution': 'off',
        'files': {
            str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob('*'))
            if path.is_file()
        },
    }
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    result = verify_site(args.directory, args.commit)
    print(json.dumps({key: value for key, value in result.items() if key != 'files'}))
