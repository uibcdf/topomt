# Conditional properties and proof scope

These arguments refer to explicitly defined geometric fields and supports.
They separate properties of exact reference objects from numerical guarantees
that an implementation would need to establish independently.

## Adding obstacles

If $I\subseteq J$, then $c_J(x)\le c_I(x)$ at every $x$. On the same compact
support $K$,

$$\max_K c_J\le\max_K c_I.$$

Thus an exact local maximum below $p$ excludes an all-atom-admissible center
there. A local maximum above $p$ does not establish all-atom admissibility:
omitted obstacles can remove the candidate or the entire free subset.

Do not apply the exact bound to an unqualified approximate maximum as if its
numerical error were known. The software must justify the attained value and
decision margin before using it as a certificate.

## Same-field face and cell bounds

For $f\subset T$ and one fixed obstacle field $c_I$,

$$\max_f c_I\le\max_T c_I.$$

The current face and cell operators use different obstacle lists. Their values
do not gain this ordering merely by sharing the names gate and residence.
Changing support and changing obstacles are two distinct operations.

(residence-and-paths)=
## Residence along a physical path

Suppose a continuous probe-center path $\gamma$ satisfies
$c_{\rm all}(\gamma(t))\ge p$. If $x=\gamma(t)\in T$, then

$$R_T^*=\max_{y\in T}c_{I_T}(y)
\ge c_{I_T}(x)\ge c_{\rm all}(x)\ge p.$$

Under the exact existential closed-cell definition, a cell with $R_T^*<p$
cannot contain a center position on such a path. Allowing the probe sphere to
extend across an artificial face does not change this argument about its center.

This is why "the probe passes through but cannot reside" is not by itself a
physical justification of the current nonresident-connector policy. Different
obstacle lists, attained numerical values and generous tolerance bands need
reconciliation. The argument does not remove connectors from the code or
announce a replacement policy; the wider scientific review remains open.

## Existence does not identify connected subsets

A scalar maximum answers whether at least one admissible position exists. It
does not count free connected subsets or establish which admitted ports belong
to the same subset. Even all-atom maxima on a cell and its faces do not supply
a path joining arbitrary face witnesses.

For a route certificate, establish compatible paths on the relevant supports
with every selected obstacle and the declared clearance convention. A graph
path or a line drawn between candidate centers is a different kind of evidence.

## A hull point and infinity

Let $x$ lie on a convex-hull face with outward unit normal $n$. Every atomic
center is on its inward side, so $n\cdot(x-c_i)\ge0$. For $t\ge0$,

$$\|x+tn-c_i\|^2
=\|x-c_i\|^2+2t\,n\cdot(x-c_i)+t^2
\ge\|x-c_i\|^2.$$

If $x$ is all-atom-admissible, the outward-normal ray remains admissible and
reaches infinity; strict clearance remains strict as well. This result requires
an all-atom-valid starting point. A successful three-atom face calculation
alone does not supply it, nor prove the path from a particular component to $x$.

## Increasing the probe

If $p_2\ge p_1$, directly from the definition $F_{p_2}\subseteq F_{p_1}$.
With fixed geometry and fixed numerical/intrusion/transit policies, resident
and admitted-face availability also shrink with $p$. With connectors enabled,
finite transit membership is equivalently

$$N_p(T)=r_p(T)\ \lor\ [k_p(T)\ge2].$$

Both terms shrink under those fixed conditions, as do internal transit edges.
The component partition can split or lose components; no monotonic component
**count** follows. Retriangulating a changed structure or changing policies is
outside the argument. Bank complements grow, but their interpretation remains
that of the chosen discrete bank graph.

## Invariance and what must be tested

Euclidean rigid transformations preserve clearance and the physical reference
sets. Consistent length scaling transforms capacities by that factor, areas by
its square and volumes by its cube. Atom relabeling preserves the geometric
model when correspondence is explicit.

Physical equivariance is not automatic bitwise numerical identity. Near a
degeneracy, different valid triangulations can exist. Numerical epsilon,
candidate conditioning, floating arithmetic and stable source maps need their
own guards. Equality of a digest after dropping correspondence is not an
invariance proof.

## The graph has an exact discrete meaning

Given its admitted node/edge sets, connected-component search partitions the
finite graph exactly under ordinary graph connectivity. That discrete fact
does not imply homotopy or component equivalence with the full continuous
physical free space. Such a theorem would need additional hypotheses about
local free subsets, compatible contacts and the finite boundary convention.

The [validation chapter](../validation_and_scope.md) links the current evidence
and owners of the uncompleted physical/numerical questions.
