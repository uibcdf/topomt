"""Guards for obsolete vocabulary in current contract docs."""

from pathlib import Path

CURRENT_CONTRACT_DOCS = [
    Path('devguide/api_contract_v0.md'),
    Path('devguide/api_surface.md'),
    Path('devguide/DFND/abstract_contract.md'),
    Path('devguide/DFND/api_contract_v1.md'),
    Path('devguide/DFND/component_identity_contract.md'),
    Path('devguide/DFND/data_model_v1.md'),
    Path('devguide/DFND/metrics_contract.md'),
    Path('devguide/DFND/object_model.md'),
    Path('devguide/DFND/residence_transit_contract.md'),
    Path('devguide/DFND/unit_convention.md'),
]

OBSOLETE_TERMS = (
    'dry_depth',
    'channel_centerline',
    'dfnd.raw.nm.v1',
)


def test_current_contract_docs_do_not_use_obsolete_dfnd_terms():
    offenders = []
    for path in CURRENT_CONTRACT_DOCS:
        text = path.read_text()
        for term in OBSOLETE_TERMS:
            if term in text:
                offenders.append(f'{path}: {term}')

    assert offenders == []
