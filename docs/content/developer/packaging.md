# Packaging and Environments

TopoMT packaging is currently functional but still transitional.

## Current picture

- `pyproject.toml` is the main build configuration.
- Some packaging metadata is still incomplete.
- The repository still contains packaging drift from older tooling phases.
- `devtools/` contains useful environment files, but also legacy material.

## Practical interpretation

Developers should treat packaging and environments as an area still being
consolidated, not as a fully polished distribution story.

This is especially important when working on:

- dependency declarations;
- optional dependency handling;
- test environments;
- release preparation.
