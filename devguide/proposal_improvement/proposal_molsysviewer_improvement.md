**Proposal: Record MolSysViewer Needs Here**

TopoMT sometimes ships visualization helpers or exports (e.g., `nglview`, `py3Dmol` snippets).
When a visualization feature would benefit MolSysViewer (like a shared snapshot exporter or viewer
hook), jot the idea here rather than hardcoding another custom script. This keeps visualization
improvements centralized and ensures MolSysViewer evolves in step with the rest of the ecosystem.

Describe the desired capability, the user scenario, and why it belongs in MolSysViewer instead
of TopoMT alone. That way we can open an issue/PR there once the need solidifies.

---

## Logged needs

### From the DFND component-visualization implementation plan

Source: [../DFND/component_visualization_implementation.md](../DFND/component_visualization_implementation.md)
§2 (decision D6). These are generic rendering/UX primitives — any molecular
system, not just DFND, would use them — so they belong upstream in MolSysViewer.
`molsysviewer_topomt` would only feed them DFND-derived geometry/scalars.
(`add_channel_tube` and the `pharmacophore` shape already followed this pattern.)

- **Ring / stacked-ring shape** — circles perpendicular to a path axis, radius and
  colour per station (HOLE-style pore profile; also the accent/bottleneck ring for
  channels). Scenario: any channel/pore/tunnel visualization. Phase 1/4.
- **Focus-with-fade** — dim (low alpha) the molecular representation *outside* a
  given selection/region, to expose a buried feature without a clipping plane.
  Scenario: isolating any internal cavity/site. Phase 5.
- **Clipping-plane primitive** — a programmatic section plane through a point/normal.
  Scenario: sectioning any buried volume. Phase 6.
- **Per-vertex surface scalar / curvature coloring** — project a per-vertex scalar
  (e.g. curvature) onto a molecular surface. Scenario: any surface-shape or
  property heatmap (convexity, electrostatics, conservation). Phase 6.
- **Legend overlay + CVD-safe palette catalog** — a reusable legend widget and a
  built-in colour-blind-safe palette (Okabe–Ito) any addon can draw from.
  Scenario: any multi-feature scene. Phase 0/5.
- **2D–3D synchronized plot widget** — an interactive 2D trace (volume, distance,
  any per-frame scalar) linked to the 3D view: click a time point → set the frame;
  mark events on the timeline. Scenario: any trajectory inspection. Phase 6.
