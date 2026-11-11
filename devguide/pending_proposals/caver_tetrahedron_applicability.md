---
summary: Investigate the retained CAVER four-atom failure and supported input scope.
issue: uibcdf/topomt#155
status: open
opened: 2026-11-08
closed:
severity: medium
verification: inspected
area: [third-party, validation]
guard:
normative:
blocked_by: []
supersedes: []
---

# Investigate the retained CAVER four-atom failure and supported input scope.

## What

The retained original CAVER standard execution on the four-atom
regular tetrahedron failed. The comparative finding `caver-four-atom-execution` remains
needs_review; applicability and cause are not established.

## How

Inspect original_observations/caver-standard/observation.json and failed.zip
under docs/content/benchlab/synthetic/regular_tetrahedron/artifacts/comparisons_v1/.
Review the exact original diagnostic, input, settings and selected source. Establish
supported tiny-input eligibility before proposing a bounded controlled rerun.

## Why

A Discussion-only pending task can disappear from the work queue. This issue owns
the investigation; the scientific finding remains in the comparative hub #154.

## What was refuted

Execution failure does not prove zero findings, inability to characterize access
or a DFND accuracy advantage. Unsupported input and integration/environment
failure are distinct from a scientific algorithm defect.

## Scope and exclusions

One retained input/provider diagnostic first. No new original execution is claimed.
No upstream publication or general provider rewrite is authorized by this record.
Follow shared-resource limits if a rerun is necessary.

## Acceptance criteria

Reproduce/diagnose a supported-scope defect or document the actual applicability
restriction/remaining uncertainty. Add a regression for a confirmed fix. Reconcile
the canonical card, hub view, metadata, method/case summaries and this report/issue.
Retain original artifacts and exact affected/corrected profiles. Investigation
closure alone must not be presented as a scientific fix or superiority result.

Maintained finding card: https://github.com/uibcdf/topomt/discussions/154#discussioncomment-19482190 .

## Three-case checkpoint disposition — 2026-11-10

The retained stderr identifies starting-point-outside-search-region and missing tunnel output; shell/origin settings remain a configuration/applicability lead, not a zero-tunnel result or a supported-domain diagnosis.

No additional execution is selected for the current native acceptance. The
[comparison disposition](../../docs/content/benchlab/synthetic/comparison_disposition.md)
retains this investigation under its open owner and the finding stays
`needs_review`. Before any rerun, establish an eligible input/operator/origin
question and freeze a bounded protocol. No comparative disadvantage is established.
