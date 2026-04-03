# Testing

The current test suite is useful for development, but still uneven.

## What is covered

There is meaningful coverage for:

- `Topography`
- pocket feature basics
- alpha-spheres
- CASTp integration paths
- import smoke tests

There is also a separate DFND-oriented test file, but DFND is not the current
stabilization priority.

## What is still weak

- direct tests for several prioritized engines;
- deeper geometry validation;
- cross-engine output consistency;
- loader coverage, especially for CASTp file-loading workflows.

## Current testing priority

The current priority is to strengthen tests around the non-DFND engine path and
the common `Topography` contract.
