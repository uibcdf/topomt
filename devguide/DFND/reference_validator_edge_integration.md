# Certified analytic edge integration

Owner [#76](https://github.com/uibcdf/topomt/issues/76), S4/D/E continuation of
the [face-flux construction](reference_validator_face_flux.md).
This is an independently checked developer reference route, not a public DFND
operator. It preserves the exact atom balls, probe, strict contact convention,
finite domain, complete power partition and original precision requirements.

The range-based face prototype converges slowly because every leaf retains
the full variation of its integrand. The construction below evaluates the
face integral analytically, including its sphere cuts. Geometry decisions are
rational; square roots and arctangents have certified outward rational bounds.

## Radial Green reduction on a face

Let c be the owner center and R its expanded radius. On a planar face choose
an outward unit normal n and signed height h=(x-c).n. Put H=h² and let u be
the component of x-c in that plane, with s=|u|². The original face integrand is

```text
w(s) = max(0, 1 - R³/(H+s)^(3/2)).
```

Define a radial planar field G(u)=u*g(s), with

```text
g(s) = (1/(2s)) * integral from 0 to s of w(q) dq.
```

Then `div_2 G = 2g+2s*g' = w`. Green's theorem reduces the integral over a
polygon to its oriented edge integrals. The radial field has a continuous
extension at s=0. Where the plane intersects the ball, it is identically zero
on the circle and its interior; no omitted cut-arc flux remains.

Explicitly:

```text
H <= R², s <= R²-H:  g(s) = 0
H <= R², s >  R²-H:  g(s) = 1/2 + (H-3R²)/(2s) + R³/(s*sqrt(H+s))
H >  R²:             g(s) = 1/2 - R³/(sqrt(H)*s) + R³/(s*sqrt(H+s)).
```

The first nonzero expression follows by integrating w from the circle radius;
the second integrates from the planar origin. They agree when H=R². Faces
with h=0 have zero original flux and are omitted before any division by h.
R=0 is evaluated by the exact rational oriented-volume limit, without atan.

## Rational edge geometry and primitives

For one oriented triangle take the rational area normal N=(b-a) cross (d-a),
alpha=(a-c).N, and H=alpha²/|N|². For an oriented edge a to b let

```text
y = a-c, e=b-a, A=e.e, B=y.e
D = y.y-H-B²/A,     v=A*t+B,     s=D+v²/A
K = alpha * y.(e cross N) / (3*|N|²).
```

The triangle's signed 3D face flux is the sum of
`K * integral_0^1 g(s(t)) dt` over its three edges. This incorporates both
the planar outward-normal factor and h/3 without normalizing N numerically.
K may be negative. When K=0 its contribution is exactly zero; otherwise D>0.
In particular a radial edge through the projected center has D=0 and K=0,
so no singular primitive is evaluated on it.

Two primitives suffice:

```text
J1(v) = atan(v/sqrt(A*D)) / sqrt(A*D)
J2(v) = atan(sqrt(H)*v / (sqrt(A*D)*sqrt(H+D+v²/A)))
         / (sqrt(H)*sqrt(A*D)).
```

Their t-derivatives are respectively `1/s(t)` and
`1/(s(t)*sqrt(H+s(t)))`. For J2, substitute
`x=sqrt(A)*(t+B/A)` and then `z=x/sqrt(x²+H+D)`; the remaining integral is
`integral dz/(D+H*z²)`. Thus each admitted outside-ball interval contributes

```text
K * [ delta(v)/(2A) + C*delta(J1) + R³*delta(J2) ],
C=(H-3R²)/2 if H<=R², otherwise C=-R³/sqrt(H).
```

If `T=A*(R²-H-D)<=0`, the whole edge is admitted. Otherwise only
`v<-sqrt(T)` and `v>sqrt(T)` contribute. Ordering a rational endpoint against
these algebraic roots uses its sign and exact squared comparison with T.
Equality is a zero-measure contact, not a tolerance decision. Only after those
branches are decided are the cut roots enclosed numerically. These rules also
handle exact tangencies and endpoints on the sphere.

## Complete assignment to global regions

The reader reconstructs all original clipped cells and outward facet cycles.
Identical positive-volume cells require identical owner balls and are counted
once; lower-dimensional cells have zero 3D volume. Closed owner-ball coverage
of every facet vertex proves zero free facet flux. Nothing is inferred from a
finite point sample about a cut face.

Every strict free point of a convex face reaches a strict free face vertex
along a segment whose distance from the owner center never decreases. Choose
a vertex maximizing `(x-c).(v-c)`; since x is a convex combination of the face
vertices, this maximum is at least |x-c|². This is the same supporting-root
argument used by the independently checked topology.

Consequently, if all strict free vertices of a face have the same checked
global region ID, its entire free portion belongs to that region, even if the
portion is locally disconnected. A standard convex fan triangulates this face.

When a face has different global vertex-region labels:

1. Find its closest point p to c exactly. Use the rational orthogonal plane
   projection if it is inside the convex face; otherwise minimize over exact
   clamped projections on every boundary edge. It must lie in the closed owner
   ball, since a wholly free convex face cannot join distinct global regions.
2. Fan the polygon from p. A fan triangle with no strict free vertex is covered
   by the ball. A triangle whose free vertices all have one label belongs to
   that global region by the supporting-root argument.
3. If its two outer vertices have different labels, their edge must meet the
   closed ball. Its exact closest point q is rational and blocked or on contact.
   The segment p--q is covered by convexity of the ball. Split the triangle
   along that segment. Each resulting piece has only one strict free vertex,
   and therefore one proved region label.

The convex fan and the edge split cover every face once with disjoint interiors.
Triangles of zero signed volume contribute no flux. This removes ambiguous
region allocation without discarding small positive regions. Every signed
contribution is integrated and summed exactly once for its region and once
for the total. Internal faces use their respective owner fields; they are not
canceled by assuming the fields are equal.

## Arithmetic, records and trust boundary

`power_edge_volume` certificates store the complete untrusted topology, original
`VolumeRequest`, scheme `power-face-edge-antiderivative/1` and dyadic bit count.
They contain no producer-selected face inventory, region labels or numerical
totals to trust. The independent reader reconstructs those objects itself.
An exclusive fresh saved read has the same scientific requirements as a direct
call. Raw records cannot assert successful precision.

Dyadic square roots and Machin pi reuse the existing exact primitives.
The atan evaluator uses the same half-angle identity and certified series
tail as the retained Fraction implementation, with integer interval Horner
arithmetic on a dyadic grid. Atan endpoint results are immutable and have a bounded 512-entry
cache; a fresh reader needs no cache. Every cut, sign, coverage and region
decision precedes interval approximation. All interval operations preserve
enclosure, and each edge/triangle reduction rounds outward in canonical nm³.
Insufficient positive denominator bounds raise `ArithmeticError`; the producer
may increase only the declared bit count, never weaken a geometric decision.

Admitted precision is 64/128/256/512/1024/2048 bits and at most 4096 assigned
face pieces, within the existing complete power-cell envelope. Absolute and
relative requirements are applied to the total and every region. Literal
zero error is met only by an exact result; complete exclusion and independently
proved whole-domain availability keep their explicit exact shortcuts.

The shared trusted base includes exact convex face ordering, supporting-root
completeness and elementary interval arithmetic. This is not a machine-checked
proof or a second independent implementation of every primitive. The new
geometric reduction has separate cap/wedge, contained-union, signed-owner,
three-region, tiny-region, exact-contact and covariance controls. It executes
no original external software and invents no DFND publication. P6/public
quantity/attribution/installed admission remains separate.

### Integer interval evaluation and the measured cost

The first larger attempt reaches its 180 CPU-second ceiling without a complete
certificate. A separate cost profile on original dumbbell faces localizes the
integral's cost in Fraction-based atan evaluation. Matched, unprofiled repeats
on the same 32 face pieces compare that implementation with the integer dyadic
one; these are primitive costs, not a full-analysis speedup denominator.

For requested b bits the new evaluator works at b+32 guard bits. Half-angle
reduction gives `t=x/(1+sqrt(1+x²))`, with a certified interval `0<=t<1/2`.
Coefficients `(-1)^k/(2k+1)` are rounded outward on the working grid, and signed
integer interval multiplication bounds each Horner step. With
`N=ceil((b+32)/2)+2`, the omitted alternating tail is bounded by
`2^(-(2N+1))/(2N+1)`. Its ceiling on that grid is added before doubling for
the half-angle identity. Reciprocal reduction uses certified pi/2; oddness
handles negative arguments. Final endpoints round outward to b bits. Integer
arguments are normalized to exact Fractions before reciprocal division.

Only immutable pi values and atan endpoint intervals are cached, with explicit
entry ceilings. A fresh process reconstructs every required value. Maximum
2048-bit output remains admitted even on the reciprocal branch; internal guard
arithmetic does not request an unsupported output precision. These changes
reduce arithmetic work while preserving every bound and original request.

### Declarative proposal and actual independent execution

`edge_volume_proposal` only detaches Model binding, topology, request, scheme and
an explicit bit count. It executes no integral, supplies no accepted/precision
status and earns no scientific completion credit. Malformed topology remains
untrusted and is rejected by the reader. `edge_volume_certificate` retains the
convenient adaptive producer route when advance bit selection is desired.

For panel receiving, a declarative proposal avoids computing the entire
integral once to prepare a record and again to read it. The actual receiving
saves Model/proposal, reconstructs a new Model from saved bytes, and independently
checks the topology, all face pieces and the final error. An unmet request can
only increase arithmetic precision in a new explicit proposal; it cannot reuse
an accepted flag or relax geometry. Source, failed attempts and phase/resource
receipts retain these different execution paths.

See the [versioned receiving](../evidence/reference_validator_edge_volume_v1/README.md)
for the exact original Models, requests, arithmetic, timing/resource receipts
and qualified scope. Earlier face-range and box evidence retains its original
source and precision status rather than being retroactively relabeled.
