# CAST: cómo quedarse con los *empty tetrahedra* a partir de una *weighted Delaunay triangulation*

## Propósito

Este documento resume, de forma fiel al paper de Liang, Edelsbrunner y Woodward (1998), cómo entender e implementar el paso geométrico que separa los tetraedros de la triangulación regular en dos grupos:

- tetraedros que forman parte del **alpha shape / dual complex**
- tetraedros que quedan **fuera** del alpha shape, es decir, los **empty tetrahedra**

Estos *empty tetrahedra* son la base sobre la que CAST define después el **discrete flow** para identificar *pockets* y *cavities*.

---

## 1. Qué dice el paper

El paper describe el pipeline conceptual de CAST así:

1. Se asignan radios atómicos a la estructura.
2. Se calcula la **weighted Delaunay triangulation**.
3. Se calcula el **alpha shape** o **dual complex**.
4. Los tetraedros de Delaunay que **no pertenecen** al alpha shape son los **empty tetrahedra**.
5. El **discrete flow** se define sobre esos *empty tetrahedra* para agruparlos en *pockets* o distinguir regiones que fluyen al infinito.

El artículo explica esta idea primero en 2D con *empty triangles* y luego la extiende a 3D con *empty tetrahedra*. También dice de forma explícita que el *discrete flow* se define únicamente sobre los simplex vacíos.

---

## 2. Definición operativa correcta

### Definición conceptual

Un **empty tetrahedron** es:

> un tetraedro de la triangulación de Delaunay ponderada que **no pertenece al alpha shape**.

Ésta es la definición más fiel al paper.

### Interpretación geométrica estándar

En la teoría de **alpha shapes** para bolas ponderadas, esa pertenencia puede decidirse usando el **power center** del tetraedro y su valor de **alpha**.

Esta formulación es una reconstrucción algorítmica estándar de la teoría subyacente de Edelsbrunner. Es compatible con el paper, pero el paper no la da como pseudocódigo.

---

## 3. Objetos geométricos implicados

Supongamos una colección de átomos modelados como bolas:

- centros: `c_i ∈ R^3`
- radios: `r_i`

A partir de ellas se construye:

- la **regular triangulation** o **weighted Delaunay triangulation**
- el **power diagram** o Voronoi ponderado
- el **alpha shape / dual complex**

Cada tetraedro `T = (i, j, k, l)` de la triangulación regular tiene asociado un punto dual `v_T`, llamado **power center**.

---

## 4. Criterio algorítmico para decidir si un tetraedro es vacío

### 4.1 Distancia de potencia

Para un punto `x`, la distancia de potencia al átomo `i` es:

```text
π_i(x) = ||x - c_i||^2 - r_i^2
```

El **power center** `v_T` de un tetraedro `T = (i, j, k, l)` es el punto que satisface:

```text
π_i(v_T) = π_j(v_T) = π_k(v_T) = π_l(v_T)
```

Ese valor común se suele llamar `α_T`.

### 4.2 Clasificación

Una forma estándar de clasificar el tetraedro es:

- si `α_T <= 0`, el punto dual está dentro o sobre la unión de bolas  
  → el tetraedro pertenece al **alpha complex**  
  → lo consideramos **lleno** en este contexto

- si `α_T > 0`, el punto dual está fuera de la unión de bolas  
  → el tetraedro **no pertenece** al alpha complex  
  → es un **empty tetrahedron**

---

## 5. Algoritmo recomendado

## Opción A: la más fiel a CAST

Si tu librería geométrica te da directamente el **alpha complex**, entonces la implementación más limpia es:

```python
empty_tetrahedra = all_regular_tetrahedra - alpha_complex_tetrahedra
```

Esta opción es la más cercana a la formulación del paper, porque no introduce ninguna reinterpretación extra.

## Opción B: reconstrucción algorítmica mediante `alpha`

Si no tienes el alpha complex ya calculado, puedes reconstruir la pertenencia evaluando el **power center** del tetraedro.

---

## 6. Cálculo del power center

Para el tetraedro `T = (i, j, k, l)`, el punto `v` cumple:

```text
||v - c_i||^2 - r_i^2 = ||v - c_j||^2 - r_j^2
||v - c_i||^2 - r_i^2 = ||v - c_k||^2 - r_k^2
||v - c_i||^2 - r_i^2 = ||v - c_l||^2 - r_l^2
```

Al expandir estas ecuaciones se obtiene un sistema lineal 3x3:

```text
2(c_j - c_i) · v = ||c_j||^2 - ||c_i||^2 + r_i^2 - r_j^2
2(c_k - c_i) · v = ||c_k||^2 - ||c_i||^2 + r_i^2 - r_k^2
2(c_l - c_i) · v = ||c_l||^2 - ||c_i||^2 + r_i^2 - r_l^2
```

Resolviendo ese sistema obtienes `v`.

Luego calculas:

```text
α_T = ||v - c_i||^2 - r_i^2
```

y clasificas con el criterio anterior.

---

## 7. Pseudocódigo

```python
def classify_tetrahedra_as_empty_or_full(tetrahedra, centers, radii, eps=1e-12):
    empty_tetrahedra = []
    full_tetrahedra = []

    for T in tetrahedra:
        i, j, k, l = T.vertices

        ci = centers[i]
        cj = centers[j]
        ck = centers[k]
        cl = centers[l]

        ri = radii[i]
        rj = radii[j]
        rk = radii[k]
        rl = radii[l]

        v = compute_power_center(ci, ri, cj, rj, ck, rk, cl, rl)
        alpha_T = ((v - ci) ** 2).sum() - ri**2

        if alpha_T > eps:
            empty_tetrahedra.append(T)
        else:
            full_tetrahedra.append(T)

    return empty_tetrahedra, full_tetrahedra
```

---

## 8. Implementación en Python del power center

```python
import numpy as np

def compute_power_center(ci, ri, cj, rj, ck, rk, cl, rl):
    A = np.array([
        2.0 * (cj - ci),
        2.0 * (ck - ci),
        2.0 * (cl - ci),
    ], dtype=float)

    b = np.array([
        np.dot(cj, cj) - np.dot(ci, ci) + ri**2 - rj**2,
        np.dot(ck, ck) - np.dot(ci, ci) + ri**2 - rk**2,
        np.dot(cl, cl) - np.dot(ci, ci) + ri**2 - rl**2,
    ], dtype=float)

    return np.linalg.solve(A, b)
```

---

## 9. Notas numéricas importantes

### 9.1 Tolerancia

No conviene usar el criterio `alpha_T > 0` de forma exacta en coma flotante. Usa una tolerancia pequeña, por ejemplo:

```python
eps = 1e-12
```

o una tolerancia adaptativa según la escala geométrica del sistema.

### 9.2 Degeneraciones

Puede haber tetraedros casi degenerados o configuraciones coplanares/cosféricas ponderadas. En ese caso:

- el sistema lineal puede estar mal condicionado
- la triangulación regular puede requerir predicados robustos

Si quieres una implementación robusta de producción, lo ideal es apoyarte en una librería geométrica que ya maneje bien la triangulación regular y el alpha complex.

---

## 10. Qué NO conviene hacer

Para mantenerte cerca del espíritu de CAST, no conviene clasificar tetraedros usando:

- voxels
- grids
- tests heurísticos de intersección con átomos
- reglas del tipo “si el tetraedro está muy cerca de átomos entonces está lleno”

El paper insiste justamente en la ventaja de usar geometría computacional exacta frente a métodos discretizados o con parámetros arbitrarios.

---

## 11. Relación con el discrete flow

Una vez identificados los **empty tetrahedra**, el paper define el **discrete flow** sólo sobre ellos.

En otras palabras:

- primero separas el conjunto total de tetraedros en `full` y `empty`
- después construyes conectividad y flujo únicamente sobre `empty`
- ese flujo permite distinguir:
  - *pockets*
  - *cavities*
  - regiones que fluyen al infinito

Así que el algoritmo de este documento sólo cubre la **fase de filtrado geométrico**, no todavía la clasificación topológica final.

---

## 12. Resumen corto

La forma más fiel de quedarte con los tetraedros vacíos, siguiendo CAST, es:

1. construir la **weighted Delaunay triangulation**
2. construir el **alpha shape / dual complex**
3. definir como **empty tetrahedra** todos los tetraedros de Delaunay que **no pertenecen** al alpha shape

Si necesitas implementarlo sin una librería que te dé el alpha complex directamente, puedes usar el criterio del **power center**:

- calcular `v_T`
- calcular `α_T = ||v_T - c_i||^2 - r_i^2`
- si `α_T > 0`, el tetraedro es **vacío**

---

## 13. Referencias

- Liang J., Edelsbrunner H., Woodward C. (1998). *Anatomy of protein pockets and cavities: Measurement of binding site geometry and implications for ligand design*. Protein Science.
- Edelsbrunner H., Mücke E. P. (1994). *Three-dimensional alpha shapes*.
- Edelsbrunner H. (1995). *The union of balls and its dual shape*.

---

## 14. Comentario final de honestidad metodológica

Este documento distingue dos niveles:

### Lo que sí está dicho explícitamente en el paper
- CAST usa triangulación de Delaunay ponderada
- CAST usa alpha shape / dual complex
- los tetraedros fuera del dual complex son los *empty tetrahedra*
- el discrete flow se define sobre ellos

### Lo que aquí se reconstruye algorítmicamente a partir de la teoría estándar
- el test computable mediante **power center** y signo de `alpha`

Esa reconstrucción no es una invención arbitraria: es la traducción operativa estándar de la teoría de alpha shapes subyacente al método.
