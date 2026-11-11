---
summary: Refresh deprecated Action runtimes in the documentation workflow at a grouped checkpoint.
issue: uibcdf/topomt#177
status: open
opened: 2026-11-10
closed:
severity: low
verification: inspected
area: [ci, docs]
guard:
normative:
blocked_by: []
supersedes: []
---

# Documentation Action runtime refresh

## What

Successful run `42935688025`, source `63e0897`, reports actions declaring
Node.js 20 that GitHub forces to Node.js 24. Strict Sphinx and deployment pass;
this platform notice is distinct from a Sphinx diagnostic.

## How

At the next grouped workflow-maintenance checkpoint, inspect exact reviewed
upstream and transitive action revisions, update needed pins/callers, and run
the exact-candidate build/artifact/deploy/served receiving route. Keep the
current one-worker/resource settings and source identity checks.

## Why

Explicit runtime compatibility should replace reliance on the platform's
forced transition. Ordinary incremental commits must not trigger repeated CI.

## What was refuted

A deprecation notice does not mean the observed documentation failed. The
resolved site-identity and Sphinx issues need not be reopened for this notice.
No unverified version bump or additional hosted execution is made here.

## Scope and exclusions

Documentation workflow and relevant transitive actions. Package qualification,
full scientific/support matrices and releases retain their own gates under #16.

## Acceptance criteria

Record reviewed revision/runtime identities and passing exact-candidate
build/artifact/deploy/served checks after the bounded update. Preserve historical
run/artifact identity and keep source publication distinct from installed claims.
