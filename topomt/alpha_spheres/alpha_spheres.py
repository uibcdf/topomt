from topomt import pyunitwizard as puw
import numpy as np
from scipy.spatial import Voronoi
from scipy.spatial.distance import euclidean
from topomt._private.puw_utils import get_magnitudes, get_magnitude

class AlphaSpheres():

    """Set of alpha-spheres

    Object with a set of alpha-spheres. Internal data is stored as pure NumPy arrays 
    (magnitudes) in nanometers (nm) to ensure high performance.
    """

    def __init__(self, points=None, radii=None, method='voronoi', skip_digestion=False):

        self.points=None
        self.n_points=None
        self.centers=None
        self.points_of_alpha_sphere=None
        self.radii=None
        self.n_alpha_spheres=None
        self._neighbors = None

        if points is not None:

            # Safe magnitude extraction to NM
            points_value = get_magnitudes(points, unit='nm')

            self.points = points_value
            self.n_points = points_value.shape[0]

            # Voronoi class to build the alpha-spheres
            voronoi = Voronoi(points_value)

            # Internal storage as pure magnitudes in nm
            self.centers = voronoi.vertices
            self.n_alpha_spheres = voronoi.vertices.shape[0]

            # Let's compute the 4 atoms' sets in contact with each alpha-sphere
            self.points_of_alpha_sphere = [[] for ii in range(self.n_alpha_spheres)]
            point_to_region = voronoi.point_region
            
            for p_idx, r_idx in enumerate(point_to_region):
                region = voronoi.regions[r_idx]
                for v_idx in region:
                    if v_idx != -1:
                        self.points_of_alpha_sphere[v_idx].append(p_idx)
            
            for ii in range(self.n_alpha_spheres):
                self.points_of_alpha_sphere[ii] = sorted(self.points_of_alpha_sphere[ii])

            # Compute radii as magnitudes in nm
            self.radii = np.zeros(self.n_alpha_spheres)
            for ii in range(self.n_alpha_spheres):
                if len(self.points_of_alpha_sphere[ii]) > 0:
                    self.radii[ii] = euclidean(voronoi.vertices[ii], points_value[self.points_of_alpha_sphere[ii][0]])

            self.points_of_alpha_sphere = np.asarray(self.points_of_alpha_sphere, dtype=int)

            from scipy.spatial import Delaunay
            tri = Delaunay(points_value)
            self._neighbors = {}
            for i, neighs in enumerate(tri.neighbors):
                self._neighbors[i] = [n for n in neighs if n != -1]

    def get_neighbors(self, criterion='face'):
        return self._neighbors

    def remove_alpha_spheres(self, indices):
        mask = np.ones(self.n_alpha_spheres, dtype=bool)
        mask[indices] = False
        self._neighbors = None 
        self.centers = self.centers[mask,:]
        self.points_of_alpha_sphere = self.points_of_alpha_sphere[mask]
        self.radii = self.radii[mask]
        self.n_alpha_spheres = np.count_nonzero(mask)

    def remove_small_alpha_spheres(self, minimum_radius):
        min_val = get_magnitude(minimum_radius, unit='nm')
        indices_to_remove = np.where(self.radii < min_val)[0]
        self.remove_alpha_spheres(indices_to_remove)

    def remove_big_alpha_spheres(self, maximum_radius):
        max_val = get_magnitude(maximum_radius, unit='nm')
        indices_to_remove = np.where(self.radii > max_val)[0]
        self.remove_alpha_spheres(indices_to_remove)

    def get_points_of_alpha_spheres(self, indices):
        return np.unique(self.points_of_alpha_sphere[indices].reshape(-1))
