# Pending TopoMT Proposals

This directory is the intake area for proposals that may change TopoMT itself.
It must remain present even when no concrete proposal is pending, because it is
the agreed place where contributors and automated agents record new ideas before
they are evaluated.

## What Belongs Here

Use this directory for proposals concerning TopoMT or `molsysviewer_topomt` that
are not yet accepted contracts or executable backlog items, including:

- new scientific capabilities or algorithms;
- substantial API or object-model changes;
- cross-cutting refactors whose direction is not decided;
- performance strategies that require profiling or dependency decisions;
- exploratory integration designs.

Do not use this directory for:

- confirmed defects: add them to the active code-review backlog or issue tracker;
- accepted architecture: document it in the relevant authoritative `devguide/`
  contract;
- implementation checkpoints: place them with the relevant subsystem;
- improvements that belong in a sibling MolSysSuite repository: write the
  proposal in that repository's own `devguide/pending_proposals/` directory.

## Proposal Lifecycle

Every proposal should declare:

```text
Status: pending | under review | accepted | accepted with changes | rejected | superseded
Owner: optional
Created: YYYY-MM-DD
Last reviewed: YYYY-MM-DD
```

A pending proposal should state the problem, scientific or user value,
alternatives, risks, dependencies, validation plan, and decision questions. It
must not present unmeasured performance claims or speculative implementation
choices as established facts.

After evaluation:

- move accepted contracts and rationale into the appropriate authoritative
  document;
- add executable correction work to the technical backlog or issue tracker;
- delete proposals whose useful content has been fully integrated;
- retain rejected proposals only when the rejection rationale prevents likely
  repetition.
