---
summary: Determine terminal-oxygen radius and inclusion policy before extending the empirical CASTp profile.
issue: uibcdf/topomt#84
status: open
opened: 2026-10-01
closed:
severity: medium
verification: measured
area: [castp, geometry, validation]
guard: tests/methods/castp/test_castp_radius_audit.py::test_terminal_oxygen_hypothesis_reconstructs_independent_archived_bulbs
normative:
blocked_by: []
supersedes: []
---

# Terminal-oxygen radius and inclusion policy

## What

Three unique one-change candidates in two archived proteins support an OXT
radius near 1.50 Å rather than local O2H1 / 1.46 Å. Two bulbs share GLY L217
serial 1668 in 1A4J; a third uses LEU B374 serial 5607 in 1CDO.

## How

The corpus audit reports exact archive hashes, three unchanged noncoplanar
anchors and rounding-bounded inferred intervals. Independently solve the four
equal-power equations with the hypothesized radius. Identify which terminal
atoms each archived job actually included before changing any assignment.

## Why

Additional OXT atoms are interior to bulbs with four compatible anchors in
1BID, 1BLH, 1BMQ, 1YPI, 2YPI, 5CNA and 7CPA. Increasing their radius would
worsen the conflict. Terminal inclusion, typing and job/version identity must
be investigated together rather than inferred from the candidate subset.

## What was refuted

A uniform 1.50 Å override alone cannot explain all observed terminal conflicts.
Bulbs do not export supporting atom IDs; association remains conditional.

## Scope and exclusions

Terminal protein oxygens. No global override, inferred author rationale or
claim of live-server equivalence. Unsupported residue variants and simultaneous
unknown changes remain outside the current evidence.

## Acceptance criteria

Establish reproducible inclusion and typing rules with independent archived
and, where necessary, controlled new inputs. Validate affected topology and
SA/MS measures before adopting an explicit provider-specific policy.
