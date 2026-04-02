**Proposal: Capture PharmacophoreMT Needs Here**

PharmacophoreMT complements TopoMT with pharmacophore-focused surface analysis. When implementing TopoMT we sometimes encounter requirements (e.g., pharmacophore sampling helpers, shared pharmacophore descriptors, or viewer hooks specific to that domain) that would be better served inside PharmacoPhoreMT. Rather than embedding custom logic here, document the need below so we can raise an issue or PR upstream and keep the shared code base coherent.

Describe the capability, the user scenario, and why an upstream helper makes sense. That keeps our TopoMT work lean and lets PharmacophoreMT evolve with the same insights we gain while implementing cavity scoring/contact details.
