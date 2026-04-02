**Proposal: Track depdigest Needs Here**

`depdigest` ingrains dependency-aware features into MolSysMT. As we evolve TopoMT,
whenever we find ourselves wrapping optional dependencies with ad hoc `try` blocks or
duplicating capability registries, capture the idea in this document. If another engine
needs the same guard, it makes sense to address it upstream rather than scattering
custom logic across TopoMT modules.

Use this note to describe the capability (e.g., a new optional backend guard or warning),
the intended public API (decorator, `is_installed`, etc.), and why a centralized
registration would benefit sibling projects. Keeping this log helps us open a targeted
proposal or issue for `depdigest` when the need crystallizes.
