# Boundary integration: an eight-region precision control

Owner: [#76](https://github.com/uibcdf/topomt/issues/76). Date: 2026-11-15 UTC.
Status: source admission and 22 focused test-first controls pass; all sixteen
frozen k=8/16/24/32 receiving controls complete at `86b95d3`.
This is D/E's small clipped-boundary feasibility control, not a new BenchLab
system or a general original-hull integrator.

The [retained summary](../evidence/reference_validator_boundary_volume_v1/summary.json)
binds every protocol, saved/read-back proof, requested/achieved bound and
resource record. All totals and all eight regions meet both enabled constraints.
The four radii use 64/64/256/512 dyadic bits at k=32; no volume cutoff removes
a tiny region. Sixteen sequential workers take 14.547 wall / 14.020 CPU seconds,
peak RSS 24,024 KiB, one CPU and 2 GiB each. These small internal controls do
not qualify the original positive hulls or comparative runtime.

## Exact admission and region assignment

Take the cube `c+[-a,a]^3`, `a>0`, and exactly one expanded ball centered at c,
of radius R with `2*a^2<R^2<3*a^2`. Translation is removed algebraically; all
received centers, radii, probe and box endpoints remain exact rational nm.
The complete same-model power proof must enumerate eight regions.

There is also an elementary independent region argument. Every coordinate
midplane is covered, because its farthest cube point has squared distance
`2*a^2<R^2`. Each corner is strictly free. Within an orthant, increasing any
absolute coordinate toward its corner cannot decrease distance from c, so
every free point connects to that corner through free positions. There are
exactly eight regions. Coordinate reflections map them transitively and
preserve volume, giving each checked region precisely one eighth of the total.
No ordinal region-to-orthant matching or sampled label is required.

## Cap/wedge formula and its coverage

Write `t=sqrt(R^2-2*a^2)`, `phi=atan(t/a)` and
`gamma=atan(R*t/a^2)`. Every adjacent pair of cube faces cuts the same spherical
wedge, of volume W. A single outside-face cap has volume

`C=pi*(R-a)^2*(2*R+a)/3`.

For the wedge `ball(R) intersect {x>=a,y>=a}`, the plane face at x=a has area
`A=(R^2-a^2)*phi-a*t`, the elementary circular-segment integral. Its spherical
patch has solid angle

`Omega=2*gamma-4*(a/R)*phi`.

To obtain this angle, apply Gauss--Bonnet to its two small-circle arcs. Each
arc contributes integrated geodesic curvature `2*(a/R)*phi`; the two corner
turns are `pi-gamma` each. The interior angle follows from projected face
normals: `cos(gamma)=a^2/(R^2-a^2)`, so its positive tangent is `R*t/a^2`.
All admitted angles lie in `(0,pi/2)`, fixing the inverse-trigonometric branch.

Applying the divergence theorem to `X/3`, whose divergence is one, gives
`W=(R^3*Omega-2*a*A)/3`: the sphere has outward flux `R^3*Omega/3` and each
plane contributes `-a*A/3`. Thus

`W=[2*R^3*gamma-2*a*(3*R^2-a^2)*phi+2*a^2*t]/3`.

There are six caps and twelve adjacent-face wedges. Opposite caps are disjoint.
A three-face outside intersection needs distance at least `sqrt(3)*a>R`, so
there is no triple correction. Inclusion--exclusion therefore proves

`V_free=8*a^3-(4/3)*pi*R^3+6*C-12*W`.

Strict excluded contact surfaces have zero volume; their topological role is
kept in the region proof. This derivation concerns the stated cube/ball geometry,
without replacing clipped power cells or their boundaries by that geometry.

## Certified arithmetic and a separate check

The proposed checker reconstructs these expressions from the admitted Model
and a strict scheme/precision record. It accepts no producer-supplied numeric
volume, root value, component count or error estimate. It uses the existing
rational interval operations, dyadic square-root enclosure and Machin bound
for pi. Arithmetic rounds outward to a finite dyadic grid after operations.

For positive x, reciprocal reduction and
`atan(x)=2*atan(x/(1+sqrt(1+x^2)))` reduce the argument to less than one half.
Interval Horner evaluation encloses the alternating Taylor polynomial. Its
first omitted term is bounded by `2^(-2*N-1)/(2*N+1)`; monotonicity gives atan
on input intervals and oddness covers negative arguments. No binary floating
trigonometric function supplies a certificate endpoint.

Precision is increased through a finite declared ladder, with total and each
region checked against every enabled `VolumeRequest` constraint. A literal
zero-error request cannot acquire an exact nontrivial value from a positive-
width rational interval. Geometry, scheme and precision admissions are checked
separately from the requested/achieved precision status.

The trusted base includes this cap/wedge derivation, standard divergence/
Gauss--Bonnet identities, interval arithmetic and series-tail inequalities.
The topology producer is separate; the transcendental arithmetic primitives
are shared, not two independent implementations or a formal proof.

## Independent geometric bounds, including tiny regions

Let `delta=3*a^2-R^2`, so `0<delta<a^2`, and put `u_i=a-|x_i-c_i|` in one
orthant. Availability is equivalent to
`2*a*sum(u_i)-sum(u_i^2)<delta`. Consequently the free corner region contains
the simplex `sum(u_i)<delta/(2*a)` and is contained in
`sum(u_i)<delta/a`. Both fit inside that orthant's cube. Its volume is bounded by

`delta^3/(48*a^3) <= V_corner <= delta^3/(6*a^3)`.

A sharper upper bound follows from `sum(u_i^2)<=sum(u_i)^2`. On the already
admitted range `s=sum(u_i)<delta/a<a`, the function `2*a*s-s^2` is increasing,
so availability requires `s<a-sqrt(a^2-delta)`. Rationalizing this root and
using `sqrt(a^2-delta)>=a-delta/a` gives

`V_corner <= [delta*a/(2*a^2-delta)]^3/6`.

The ratio of this upper bound to the lower is
`(1-delta/(2*a^2))^(-3)`. For sufficiently small delta, this separately
derived rational enclosure itself satisfies the high-precision request,
providing an independent narrow check on cancellation in the cap/wedge route.

A second normalization control approaches `R0=sqrt(2)*a` from above. At R0
the adjacent cap overlaps have zero volume; direct cap integration gives
`V0=a^3*[8+(16*sqrt(2)/3-10)*pi]`. A radius increase removes at most the full
sphere's annular volume. Rational radii just above R0 can therefore be checked
against this separate narrow enclosure, without using the wedge formula.

This bound uses only elementary polynomial inequalities and simplex volume,
independently of the cap/wedge formula. It supplies a positive rational lower
reference even for sub-binary64 gaps. Controls must include ordinary radii,
exact translations/scaling, a radius approaching `sqrt(3)*a`,
rejected geometry and altered arithmetic/topology records. These are internal
controls; no new molecular or provider comparison is selected.

## Remaining original-hull gate

Even a successful k=32 control here does not qualify the nineteen original
center-hull Models. Their clipped cells need complete facet integration and
region labeling across circle/face intersection pieces. Owner #76 retains
that task and the unchanged k=24 original total/per-region target. Do not
substitute a cube, assign a total by symmetry where symmetry is absent, or
silently turn this bounded control into general P5 qualification.
