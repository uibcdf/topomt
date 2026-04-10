# Data, I/O, and Demos

## Purpose

TopoMT includes both detection logic and support for working with bundled
reference data and external-result formats.

This document summarizes the current role of demo systems, packaged data, and
input/output helpers.

## Demo systems

[topomt/demo.py](/home/diego/repos@uibcdf/topomt/topomt/demo.py) defines demo entries used in tests
and exploratory workflows.

At the moment, the demo registry mainly covers:

- TcTIM and CASTp-derived data;
- HIV-1 Protease and CASTp-derived data;
- fpocket sample systems.

The demos are useful, but they should be understood as a lightweight registry,
not as a formal benchmark suite.

## Bundled data

The repository includes packaged data under `topomt.data`.

This data supports:

- demos;
- CASTp loader workflows;
- sample fpocket inputs and outputs.

The role of bundled data should remain pragmatic:

- support tests and examples;
- avoid dependence on remote downloads for basic workflows;
- keep a small set of reproducible reference systems.

## CASTp loading

[topomt/io/load_CASTp.py](/home/diego/repos@uibcdf/topomt/topomt/io/load_CASTp.py) is an important
part of the repository because it is not simply a detector wrapper.

It allows TopoMT to import external CASTp results and turn them into a
`Topography` object with:

- pockets;
- mouths;
- feature relations;
- geometric attributes such as areas, volumes, and lengths.

This is one of the clearest examples of TopoMT as a representation layer, not
only a detection layer.

## CASTp as method vs CASTp as imported result

There are two distinct ideas that should not be confused:

- using a TopoMT method path related to CASTp;
- loading precomputed CASTp outputs from files.

The `devguide` should keep these concepts separate because they imply different
engineering concerns:

- method integration is about wrappers, contracts, and feature normalization;
- file loading is about parsing, reproducibility, and preserving metadata.

## Wrappers and external artifacts

The fpocket material under
[topomt/third_party/fpocket/testdata/](/home/diego/repos@uibcdf/topomt/topomt/third_party/fpocket/testdata) shows that the
repository also acts as a bridge to external tools and their artifacts.

This wrapper-oriented layer is currently under-documented and should be made
more explicit in future developer documentation.

## Documentation gap

At present, the project still lacks a consolidated explanation of:

- which demo systems are considered canonical;
- which packaged datasets are just samples;
- which loaders are considered stable;
- how external artifacts should be validated and tested.

This should be improved over time, but the current document at least makes that
surface visible.
