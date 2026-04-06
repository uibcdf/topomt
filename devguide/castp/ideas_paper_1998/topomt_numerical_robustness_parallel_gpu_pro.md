# TopoMT: Numerical Robustness and Parallelization (Detailed)

## 1. Critical Numerical Issues

- Nearly degenerate tetrahedra
- Ill-conditioned linear systems (power center)
- Floating point sign instability

---

## 2. Robustness Strategy

### 2.1 Epsilon Policy

Use scale-aware epsilon:
eps = 1e-12 * characteristic_length^2

---

### 2.2 Stable Classification

alpha > eps → outside
alpha < -eps → inside
else → uncertain → resolve later

---

### 2.3 Degeneracy Handling

- fallback to symbolic perturbation (conceptual)
- or skip and reclassify using neighborhood

---

## 3. Parallelization Breakdown

### Embarrassingly parallel
- power centers
- alpha values
- volumes

### Graph operations
- adjacency construction
- BFS/DFS for components

---

## 4. GPU Strategy

GPU-friendly:
- vectorized alpha computation
- distance fields
- depth maps

Avoid GPU initially:
- triangulation
- flow graph logic

---

## 5. Hybrid Pipeline

CPU:
- triangulation
- topology

GPU:
- metrics
- analysis

---

## 6. Suggested Stack

- CPU: Python + compiled backend
- Parallel: multiprocessing / numba
- GPU: CuPy / PyTorch (optional)

---

## 7. Reproducibility

Store:
- radii
- eps
- algorithm version

---

## 8. Key Insight

Robust topology > fast geometry
