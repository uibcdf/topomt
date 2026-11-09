"""Check TopoMT comparative-finding lifecycle metadata against owning reports.

Scientific analysis stays in Discussions and reproducible evidence in BenchLab.
This check detects bookkeeping contradictions; it cannot establish an advantage,
prove a fix, or approve a manuscript claim for an unreviewed software profile.
"""

import argparse
import json
import re
import tomllib
from datetime import date
from pathlib import Path
from typing import Any, Optional

if __package__:
    from . import devguide_reports
else:
    import devguide_reports

ROOT = Path(__file__).resolve().parents[1]
CURRENT = {'current', 'documented_limit'}
STATUSES = CURRENT | {
    'candidate',
    'needs_review',
    'resolved',
    'superseded',
    'withdrawn',
}
KINDS = {'dfnd_advantage', 'third_party_limitation', 'dfnd_limitation'}


def current_entries(register: dict[str, Any]) -> list[dict[str, Any]]:
    """Select version-scoped current records, excluding resolved history.

    Parameters
    ----------
    register : dict
        Parsed, already validated lifecycle/navigation register.

    Returns
    -------
    list[dict]
        Current and consciously documented-limit entries. Selection alone is
        not fresh verification or permission to cite a present-day limitation.
    """
    return [row for row in register['findings'] if row['status'] in CURRENT]


def validate_register(
    register: dict[str, Any],
    reports: dict[str, dict[str, object]],
    root: Path,
    *,
    snapshot: Optional[dict[str, Any]] = None,
) -> list[str]:
    """Detect inconsistent comparative-finding lifecycle and evidence metadata.

    Parameters
    ----------
    register : dict
        Parsed TOML index, not a replacement for scientific Discussion cards.
    reports : dict
        Owning issue references mapped to existing report front matter.
    root : pathlib.Path
        Repository root for retained evidence paths.
    snapshot : dict, optional
        Explicit live readback with issue states, card status/URL and current
        index IDs. An absent snapshot makes this an offline check only.

    Returns
    -------
    list[str]
        Actionable metadata contradictions; an empty list proves consistency
        within supplied inputs, not scientific correctness or freshness.

    Examples
    --------
    A current DFND limitation linked to a resolved report must be reconciled.
    """
    errors: list[str] = []
    if register.get('schema_version') != 1 or not isinstance(
        register.get('findings'), list
    ):
        return ['Invalid comparative-findings register schema']
    rows = register['findings']
    ids = [row.get('id') for row in rows if isinstance(row, dict)]
    if len(ids) != len(rows) or any(not isinstance(key, str) for key in ids):
        return ['Finding records require string identities']
    if len(ids) != len(set(ids)):
        errors.append('Duplicate finding identity')
    hub = register.get('hub_url', '')
    if not isinstance(hub, str) or not re.fullmatch(
        r'https://github.com/uibcdf/topomt/discussions/[1-9]\d*', hub
    ):
        errors.append('Missing canonical findings hub URL')

    def paths(row: dict, field: str) -> None:
        values = row.get(field)
        if not isinstance(values, list) or not values:
            errors.append(f'{row["id"]}: missing {field}')
            return
        for value in values:
            if not isinstance(value, str):
                errors.append(f'{row["id"]}: invalid {field} path')
                continue
            target = (root / value.split('#', 1)[0]).resolve()
            if not target.is_relative_to(root.resolve()) or not target.is_file():
                errors.append(
                    f'{row["id"]}: missing repository evidence in {field}: {value}'
                )

    for row in rows:
        key = row['id']
        prefix = f'{key}:'
        for field in ('summary', 'scope', 'owner', 'reviewed_on', 'discussion_url'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f'{prefix} missing {field}')
        try:
            date.fromisoformat(row.get('reviewed_on', ''))
        except (ValueError, TypeError):
            errors.append(f'{prefix} invalid reviewed_on date')
        if not re.fullmatch(
            r'https://github.com/uibcdf/topomt/discussions/[1-9]\d*(?:#discussioncomment-[1-9]\d*)?',
            row.get('discussion_url', ''),
        ):
            errors.append(f'{prefix} invalid finding discussion URL')
        kind, status = row.get('kind'), row.get('status')
        if kind not in KINDS or status not in STATUSES:
            errors.append(f'{prefix} unsupported kind or status')
        paths(row, 'evidence')
        issue = row.get('issue')
        pending_action = status == 'needs_review' or (
            status == 'current'
            and kind in {'dfnd_limitation', 'third_party_limitation'}
        )
        if issue is not None or kind == 'dfnd_limitation' or status == 'needs_review':
            if (
                not isinstance(issue, str)
                or not devguide_reports.OWN_ISSUE.fullmatch(issue)
                or issue not in reports
            ):
                errors.append(f'{prefix} missing owning issue/local report')
            else:
                local = reports[issue].get('status')
                if pending_action and local in devguide_reports.CLOSED_STATUSES:
                    errors.append(
                        f'{prefix} current/pending finding has a closed local report'
                    )
                if status == 'resolved' and local != 'resolved':
                    errors.append(
                        f'{prefix} resolved limitation has an unresolved local report'
                    )
        if status == 'resolved':
            revision = row.get('fix_revision', '')
            if (
                not isinstance(revision, str)
                or not revision
                or (
                    kind == 'dfnd_limitation'
                    and not re.fullmatch(r'[0-9a-f]{40}', revision)
                )
            ):
                errors.append(f'{prefix} missing or invalid fix_revision')
            guard = row.get('regression_guard', '')
            if not isinstance(guard, str) or not guard:
                errors.append(f'{prefix} missing regression_guard')
            else:
                errors.extend(
                    f'{prefix} {error}'
                    for error in devguide_reports.validate_guard(guard)
                )
            if not row.get('resolution_scope'):
                errors.append(f'{prefix} missing resolution_scope')
            paths(row, 'resolution_evidence')
        if status in {'documented_limit', 'withdrawn'}:
            if not row.get('disposition_reason'):
                errors.append(f'{prefix} missing disposition_reason')
            paths(row, 'disposition_evidence')
        if status == 'documented_limit':
            if kind == 'dfnd_advantage' or not row.get('revisit_condition'):
                errors.append(
                    f'{prefix} documented_limit requires a limitation and revisit_condition'
                )
        if status == 'superseded' and (
            row.get('superseded_by') not in ids or row.get('superseded_by') == key
        ):
            errors.append(f'{prefix} missing distinct superseded_by finding')
        if status == 'current' and kind == 'dfnd_advantage':
            for field in ('comparison_protocol', 'independent_reference'):
                paths(row, field)
        if status == 'current' and kind == 'third_party_limitation':
            paths(row, 'applicability_evidence')
        if snapshot is not None:
            if issue:
                remote = snapshot.get('issues', {}).get(issue, {})
                state = str(remote.get('state', '')).upper()
                if state not in {'OPEN', 'CLOSED'}:
                    errors.append(f'{prefix} missing live issue state')
                if pending_action and state == 'CLOSED':
                    errors.append(
                        f'{prefix} current/pending finding has a closed live issue'
                    )
                if status == 'resolved' and state == 'OPEN':
                    errors.append(f'{prefix} resolved finding has an open live issue')
            if 'findings' in snapshot:
                card = snapshot['findings'].get(key, {})
                if card.get('status') != status or card.get(
                    'discussion_url'
                ) != row.get('discussion_url'):
                    errors.append(f'{prefix} live card differs from lifecycle register')
    if snapshot is not None and 'current_ids' in snapshot:
        if set(snapshot['current_ids']) != {
            row['id'] for row in current_entries(register)
        }:
            errors.append('The live current index differs from the lifecycle register')
    return errors


def check_repository(snapshot: Optional[dict[str, Any]] = None) -> list[str]:
    """Check this repository's register using its existing report parser.

    Parameters
    ----------
    snapshot : dict, optional
        Explicit live readback; no network request is made by this tool.

    Returns
    -------
    list[str]
        Register parsing or lifecycle contradictions.
    """
    try:
        register = tomllib.loads(
            (ROOT / 'devguide/comparative_findings.toml').read_text()
        )
    except (OSError, tomllib.TOMLDecodeError) as error:
        return [str(error)]
    reports, errors = devguide_reports.load_reports()
    errors.extend(
        validate_register(
            register,
            {str(report.fields['issue']): report.fields for report in reports},
            ROOT,
            snapshot=snapshot,
        )
    )
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--check', action='store_true', help='Validate metadata without modifying it.'
    )
    parser.add_argument(
        '--snapshot',
        type=Path,
        help='Explicit live GitHub readback JSON; no fetching is done here.',
    )
    parser.add_argument(
        '--current',
        action='store_true',
        help='Show scoped current metadata after validation; not publication approval.',
    )
    options = parser.parse_args()
    snapshot = json.loads(options.snapshot.read_text()) if options.snapshot else None
    problems = check_repository(snapshot)
    if problems:
        for problem in problems:
            print(problem)
        raise SystemExit(1)
    print(
        'Comparative findings are consistent'
        + (
            ' with supplied live readback.'
            if snapshot is not None
            else ' (offline only).'
        )
    )
    if options.current:
        data = tomllib.loads((ROOT / 'devguide/comparative_findings.toml').read_text())
        print(json.dumps(current_entries(data), indent=2))
