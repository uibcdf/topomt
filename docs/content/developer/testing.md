# Testing

The current test suite is useful for development, but still uneven.

## What is covered

There is meaningful coverage for:

- `Topography`
- pocket feature basics
- alpha-spheres
- CASTp integration paths
- import smoke tests

There is also a separate AFND-oriented test file, but AFND is not the current
stabilization priority.

## What is still weak

- direct tests for several prioritized engines;
- deeper geometry validation;
- cross-engine output consistency;
- loader coverage, especially for CASTp file-loading workflows.

## Current testing priority

The current priority is to strengthen tests around the non-AFND engine path and
the common `Topography` contract.
