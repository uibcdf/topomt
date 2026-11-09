# Clearance problems and candidate construction

The intended local problem is a max–min optimization on a compact closed
simplex. The clearance field is continuous, so its exact maximum exists. It is
nonsmooth where several atoms tie for the minimum, which motivates active-set
candidate generation.

## Tangency equations

At a positive candidate radius $R$, an active atom satisfies

$$\|x-c_i\|=r_i+R.$$

Squaring and subtracting the equation for a reference atom gives

$$2(c_i-c_1)\cdot x
=\|c_i\|^2-\|c_1\|^2-(r_i^2-r_1^2)-2R(r_i-r_1).$$

For four independent active atoms in 3D, the three subtracted equations give
$x=u+Rv$. Inserting that expression into one original equation yields

$$ (v\cdot v-1)R^2
+2((u-c_1)\cdot v-r_1)R
+\|u-c_1\|^2-r_1^2=0.$$

The quadratic can have several, repeated or no real admissible roots. A
singular coefficient system or nearly vanishing quadratic coefficient needs
its own numerical treatment. Selecting the largest algebraic root is not the
full constrained clearance problem.

## Boundary strata

An optimum can lie on a support boundary. For a three-atom candidate restricted
to a plane, combine two subtracted tangency equations with the plane constraint,
then impose the remaining quadratic relation. For two active atoms restricted
to a line, parameterize the center on that line and solve the reduced relations.

The residence implementation enumerates four-atom interior, three-atom
face-plane and two-atom edge-line candidates. The gate calculation uses a local
orthonormal face basis and corresponding three-/two-atom candidates. Both
Apollonius branches matter where they produce admissible centers.

After generation, require center membership in the closed triangle/tetrahedron
and recompute

$$R_{\rm candidate}=\min_{i\in I}(\|x-c_i\|-r_i).$$

Only a positive improving admissible candidate replaces the current nonnegative
result. Diagnostics retain candidate kind and four-atom tangency information.
This describes the solver's construction; a completeness/conditioning theorem
for all degenerate inputs does not follow merely from enumeration or agreement
between scalar and batch implementations.

## Why omitted atoms matter

For a non-face atom at perpendicular distance $h$ from the face plane, its
probe-expanded ball can intersect that plane when $r_i+p>|h|$. The resulting
cross-section has radius

$$\sqrt{(r_i+p)^2-h^2}.$$

Its disk can block a location that the three defining face atoms leave free.
This explains why all-atom free patch computation is stronger than a local
three-atom gate capacity and why an apex diagnostic is not a complete obstacle
search.

## Independent regular-simplex calculation

For an equal-radius regular tetrahedron with edge $a$, place its centroid at
the origin. Each vertex has distance $R_c=\sqrt6\,a/4$ from it. If
$x=\sum_i\lambda_i c_i$, $\lambda_i\ge0$, $\sum_i\lambda_i=1$, then

$$\sum_i\lambda_i\|x-c_i\|^2=R_c^2-\|x\|^2\le R_c^2.$$

At least one vertex distance is therefore at most $R_c$. The centroid attains
that bound for the minimum distance, so the exact four-atom local maximum is
$R_c-r$ when positive. Applying the same argument in an equilateral face gives
$a/\sqrt3-r$. In this four-atom system, the opposite apex is farther from the
face centroid than the three face atoms; the face value is also the all-atom
maximum there.

For $a=5.3$ Å and $r=1.7$ Å the results are 1.545573909 Å and 1.359956427 Å.
The derivation establishes the intended geometric quantities independently of
DFND's numerical solver. The [worked example](../worked_tetrahedron.md) checks
the actual records against them with explicit units.
