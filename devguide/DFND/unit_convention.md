# DFND unit convention

Status: settled. This records why DFND computes internally in ångström while all
its public, suite-facing values are nanometre quantities — and why a full
internal nm rescale was considered and rejected.

## The convention

- **Interchange / storage (MolSysSuite native): nanometre.** Every public value
  DFND exposes is a PyUnitWizard quantity, and is standardized to the suite unit
  (nm) before it leaves the engine. Consumers must read it through `puw`
  (`puw.get_value(x, to_unit=...)`), never by stripping the magnitude and
  assuming a unit.
- **Internal kernel: ångström.** The DFND tessellation, clearances
  (`R_gate`, `R_residence`), raw records, and numerical tolerances (`epsilon`)
  work in ångström. This is the domain-native unit of cavity detection (CASTp's
  canonical `1.4 Å` probe, fpocket, the literature), and the calibration of the
  clearance thresholds and `epsilon` is tuned at that scale.
- **Boundary conversions are explicit.** Ingestion converts molecular-system
  coordinates and radii from MolSysMT via `puw.get_value(..., to_unit='angstroms')`
  (`topomt/dfnd/graph.py`). Output construction standardizes Å values to the suite
  unit via `puw.standardize(...)` (`topomt/dfnd/api.py`), so `Feature.center`,
  `Feature.volume_*`, `Feature.mouth_area` and `Mouth.area` are nm quantities,
  consistent with the legacy alpha-sphere path and with what the
  `molsysviewer_topomt` payloads request.

## Why internal ångström, not full nm

A full internal nm rescale was evaluated and rejected:

- the benchmark systems are built from raw arrays (`DelaunayFlowNetwork.from_arrays`)
  in ångström via `topomt/dfnd/synthetic.py`, and the benchmark assertions read
  **raw records** (e.g. `void['volume_solvent_estimate']`) in ångström;
- the `epsilon` tolerances in `topomt/dfnd/core/clearance.py` are tuned at
  ångström scale;
- ångström is the established idiom of the cavity-detection domain.

Rescaling the kernel to nm would force re-baselining every benchmark, retuning
every tolerance, and touching the synthetic builders — a large, risky change for
**purity**, not **correctness**. The suite convention is honoured where it
matters: at the interchange boundary, every public value is an nm-standardized
quantity. The internal unit of a kernel is an implementation detail as long as it
converts cleanly at its edges.

## Presentation

Convenience-on-screen (ångström) is a presentation concern, already handled
downstream: `molsysviewer` stores nm and converts to ångström at the canvas
boundary (`scene.py`, `coords * 10`). Internal storage in nm does not make the
canvas less convenient, and is not a reason to store ångström.

## Rule for new code

- Compute in ångström inside the DFND kernel if it keeps the calibration simple;
- always return public values as `puw.standardize(...)` quantities (nm);
- never expose a bare float as a length/area/volume; never strip a unit and
  assume one.
