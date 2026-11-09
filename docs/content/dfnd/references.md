# References and development context

The references below ground the geometric family, molecular probe tradition
and relevant antecedents. They do not imply that current DFND implements the
same operators or inherits another method's guarantees.

## Primary scientific references

```{bibliography}
:filter: key % "^DFND"
```

- Lee and Richards establish an important historical reference for static
  molecular accessibility. Surface accessibility, admissible center space and
  region volume retain their separate definitions.
- Edelsbrunner and Mücke develop the three-dimensional alpha-shape family from
  Delaunay geometry. The current DFND carrier is ordinary Delaunay without an
  alpha-complex construction.
- Edelsbrunner, Facello and Liang give a formal alpha-complex pocket construction.
  Its definition and algorithm are antecedents rather than a hidden specification
  for DFND's threshold graph.
- Sehnal and colleagues describe MOLE 2.0's Delaunay/Voronoi, accommodation,
  cavity and channel-path pipeline. Accommodation and cavity preprocessing are
  prior concepts; novelty requires comparison of precise operators and evidence.

These are selected references, not a comprehensive literature review. Original
provider citations also remain available through
[scientific attribution](../user/scientific_attribution.md).

## Implementation references

- [SciPy Delaunay reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html):
  backend, neighbor indexing and precision qualifications.
- [SciPy spatial tutorial](https://docs.scipy.org/doc/scipy/tutorial/spatial.html):
  introductory Delaunay and Voronoi constructions.
- [CGAL 3D triangulations manual](https://doc.cgal.org/latest/Triangulation_3/index.html):
  empty-sphere and regular-triangulation definitions. This is a geometric
  reference; current DFND uses SciPy/Qhull, not the CGAL implementation.
- [Current native source](https://github.com/uibcdf/topomt/tree/main/topomt/dfnd):
  clearance operators, query graph, catalog, typed results, measurements and
  lineage helpers. The book describes the November 2026 source account; inspect
  the target revision when reproducing or publishing a result.
- [BenchLab](../benchlab/index.md): canonical inputs, independent references,
  actual observations, source profiles and comparison evidence.

(development-context)=
## Development context

The earliest project proposal explored regular triangulation, alpha complexes
and directed sink/basin flow. Current DFND instead uses ordinary Delaunay and
an undirected local-capacity threshold graph. The motivations of recoverable
support, boundaries and hierarchical characterization survive that change;
the original flow specification is not the runtime algorithm.

Repository [design records](https://github.com/uibcdf/topomt/tree/main/devguide/DFND)
retain that history and accepted contracts. The
[theory review](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/core_theory_review_2026_11_06.md)
and [antecedent comparison](https://github.com/uibcdf/topomt/blob/main/devguide/DFND/mole_comparison_2026_11_07.md)
make conditional reasoning and originality scope explicit. They are project
analysis, not a published DFND paper or a completed validation theorem.

For current scoped advantages/limitations and their correction histories, use
the [maintained register](https://github.com/uibcdf/topomt/discussions/154).
Documentary descriptions, original execution, algorithmic equivalence and
demonstrated comparative accuracy remain separate forms of evidence.
