# Pocket Geometry Approaches (alpha-sphere sets)

- Voxel / Monte Carlo: carve a local box around the pocket; fill a dense grid or random points; volume ≈ fraction of points inside the cavity × box volume. Marching cubes on the occupancy grid yields a mesh for volume/area.
- Union of spheres: treat each alpha-sphere as a ball; compute union volume/area (exact with computational geometry libs such as CGAL; approximate by sampling). Useful when spheres already approximate the cavity envelope.
- Alpha shape / triangulated surface: build an alpha shape from contact points (atoms touching the alpha-spheres) with α set to the pocket scale; the resulting mesh gives enclosed volume and surface area. Intersect with a mouth plane to measure mouth area.
- Isosurface on distance field: define a scalar field (e.g., minimum distance to any sphere/atom); extract an isosurface via marching cubes; measure volume/area on the mesh; mouth area via intersection of the mesh with a local plane.
- Sectional profiles: define a principal axis (e.g., between mouths); project boundary points onto planes along the axis; compute polygon area per slice to estimate widths and bottlenecks (minimum cross-section).
- Concave hulls: build a concave hull (k-NN based) of boundary/contact atoms; mouth area = area of the hull in a fitted mouth plane; a 3D concave hull of internal points approximates cavity volume if you lack a mesh.
- Medial axis + local radii: compute a medial axis/skeleton (on point cloud or mesh); local radii from nearest boundary give bottleneck radii and width profiles.
- SES/SAS restriction: compute solvent-excluded or solvent-accessible surface for the whole protein; restrict to the region tagged by pocket atoms/alphas; use that patch area as mouth or internal surface metric.
- Power diagram / weighted Voronoi: model spheres as weighted sites; compute cell decomposition; use cell unions or clipped cells to get smoother cavity boundaries before meshing.
- Point-in-mesh with contact atoms: if you have only contact atoms, build a watertight mesh (alpha shape/Poisson reconstruction), then compute volume/area directly on that mesh; cross-sections give mouth properties.
