# Sampled closed shell: public Topography receiving

This stage follows the frozen atomic model through the actual public
`get_topography(method='dfnd')` route. It verifies full-precision coordinates,
received radii and source atom correspondence before inspecting the registry.
The original system/native notebooks and scientific artifacts remain unchanged.

| Probe (Å) | Public objects | Native wet components | Native dry components |
| --- | --- | --- | --- |
| 0.05 | 1 `Channel`, 10 `Mouth` | 1 | 29 |
| 1.4 | 1 `Void` | 1 | 1 |
| 5 | No features | 0 | 1 |

The public region type matches its native catalog classification. Registry
lookups by type, shape and legacy dimensionality return the same objects.
Each promoted `Mouth` has its expected parent, and the reverse child relation
is consistent. Native components/source/support keys and physical quantities
retain their correspondence. The full [receiving walkthrough](../public_topography.md)
explains the class/refinement distinction and provides executable public code.

At 1.4 Å, `min_size=34` hides all public features
and child mouths while retaining the raw support and physical result identity.
For the declared largest probe, an empty public result also has no native
resident wet component; the mesh and native dry decomposition remain available.

Native dry components are not already public convexity or interface objects.
Mouth objects represent native contact clusters; their physical connectedness
and exact mouth count retain separate validation requirements. Classification
threshold confidence is not scientific probability, and the original volume estimates were
unqualified at this audit checkpoint. The later [volume receiving](../volume_measurements.md)
qualifies the new conditional on-demand contract in source `b7b5a60`; the fast
local stencil remains provisional. Full neutral public support adoption is #60.

## Versioned evidence

Download the {download}`receiving protocol <artifacts/public_topography_v1/protocol.json>`
and {download}`actual public receiving report <artifacts/public_topography_v1/report.json>`.
The report retains Python classes, registry summaries, region/Mouth relations,
parent/source atom indices, contextual support keys, dimensional descriptors,
actual source/software identities and one-CPU execution measurements.
The protocol was committed at `3206fc6` before recorded receiving; initial
public tests and historical native outputs were already known. This is
characterization rather than a blind evaluation or installed release check.

The [new 0.2 Å wall certificate](closure_at_0p2.md) establishes an enclosed
free origin at that historical probe. The additional actual public control
produces one `Void`, no `Mouth` and zero native exterior links. Its certificate
identity and public registry are retained in the same receiving report.
Earlier notebook statements about their weaker bound remain historical.

Development remains with the first three units while their physical
mouth/path connectivity, volume accuracy and public support questions are
resolved. No provider or server is run by this receiving stage.
