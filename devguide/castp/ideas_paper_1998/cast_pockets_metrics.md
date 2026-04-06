# CAST: Mouths, Boundaries y Métricas de Pockets (Volumen, Área, Profundidad)

## 📌 Objetivo

Este documento completa la implementación de CAST añadiendo:

- identificación de **mouths (bocas)**
- definición de **fronteras (boundaries)**
- cálculo de **métricas geométricas**:
  - volumen
  - área superficial
  - profundidad

Este nivel permite pasar de una representación topológica a una caracterización cuantitativa útil en drug design.

---

## 🧠 Idea central

Una vez identificados los **pockets** como conjuntos de *empty tetrahedra*:

👉 necesitamos describir:
- su conexión con el exterior
- su tamaño
- su forma

---

# 🔺 1. Definición de frontera (boundary)

Un tetraedro pertenece a la frontera de un pocket si:

👉 tiene al menos un vecino que:
- no pertenece al mismo pocket
- o es exterior

---

## 💻 Algoritmo

```python
def compute_boundary(pocket, graph):

    boundary_faces = []

    for T in pocket:
        for face, neighbor in graph[T].items():

            if neighbor not in pocket:
                boundary_faces.append(face)

    return boundary_faces
```

---

# 🔴 2. Identificación de mouths

## 🧠 Definición

Un **mouth** es:

> una región de la frontera del pocket que conecta con el exterior

---

## 🔍 Criterio

Una cara pertenece a un mouth si:

- el tetraedro vecino:
  - es exterior
  - o su flujo va al infinito

---

## 💻 Algoritmo

```python
def compute_mouths(boundary_faces, exterior_tetrahedra):

    mouths = []

    for face in boundary_faces:
        T, neighbor = face.adjacent

        if neighbor in exterior_tetrahedra:
            mouths.append(face)

    return mouths
```

---

## 🧩 Agrupación de mouths

Las caras deben agruparse en componentes conexas:

```python
def group_mouths(faces):

    return connected_components(faces)
```

---

# 📦 3. Volumen del pocket

## 🧠 Idea

El volumen es la suma de volúmenes de los tetrahedra:

```python
V_pocket = sum(volume(T) for T in pocket)
```

---

## 💻 Volumen de un tetraedro

```python
def tetrahedron_volume(a, b, c, d):
    return abs(np.dot(a-d, np.cross(b-d, c-d))) / 6.0
```

---

# 📐 4. Área superficial

## 🧠 Idea

El área se calcula sobre las caras de la frontera:

```python
A = sum(area(face) for face in boundary_faces)
```

---

## 💻 Área de triángulo

```python
def triangle_area(a, b, c):
    return 0.5 * np.linalg.norm(np.cross(b-a, c-a))
```

---

# 📏 5. Profundidad

## 🧠 Definición conceptual

La profundidad mide:

👉 qué tan lejos está el interior del pocket de su mouth

---

## 🔍 Definición operativa

Opción 1:

```python
depth = max(distance_to_mouth(T) for T in pocket)
```

---

## 💻 Implementación

1. construir grafo
2. calcular distancia geodésica desde mouths

```python
def compute_depth(pocket, mouths, graph):

    distances = multi_source_shortest_path(mouths, graph)

    return max(distances[T] for T in pocket)
```

---

# 🧠 Interpretación geométrica

- volumen → tamaño
- área → exposición
- profundidad → enterramiento

---

# 🔥 Insight importante

CAST separa claramente:

- geometría (tetrahedra)
- topología (flow)
- métricas (post-procesado)

👉 Esto es clave para TopoMT

---

# 🧩 Relación con TopoMT

Esto sugiere clases como:

- `Mouth` → subconjunto de boundary
- `Cavity` → conjunto de tetrahedra
- `Interface` → conexión entre regiones

---

# 🚀 Resultado final

A partir de una proteína:

1. construir triangulación
2. extraer empty tetrahedra
3. aplicar discrete flow
4. agrupar pockets
5. calcular:
   - volumen
   - área
   - profundidad
   - mouths

👉 obtienes una descripción completa del espacio funcional

---

# 📚 Referencias

- Liang et al., 1998
- Edelsbrunner alpha shapes
