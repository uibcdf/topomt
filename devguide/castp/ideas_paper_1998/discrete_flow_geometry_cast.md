# CAST: Criterio Geométrico Exacto (Agudo vs Obtuso) y Dirección de Flow

## 📌 Objetivo

Este documento complementa la implementación de CAST con:

- definición geométrica precisa de tetraedros **agudos vs obtusos**
- criterio riguroso para definir la **dirección del discrete flow**

Este es el nivel necesario para una implementación fiel al algoritmo original.

---

## 🧠 Idea clave

El discrete flow depende de una propiedad geométrica:

👉 la posición del **circuncentro (power center)** respecto al tetraedro

---

## 🔺 Clasificación: agudo vs obtuso

Un tetraedro puede ser:

- **Agudo** → su circuncentro está **dentro**
- **Obtuso** → su circuncentro está **fuera**

---

## 📐 Definición formal

Sea un tetraedro T con power center v.

Entonces:

- si v está dentro del tetraedro → T es **agudo**
- si v está fuera → T es **obtuso**

---

## 🔍 Test computacional

Dado un tetraedro con vértices (ci, cj, ck, cl):

### Método: coordenadas baricéntricas

Calcular coordenadas baricéntricas de v:

```python
bary = compute_barycentric(v, ci, cj, ck, cl)
```

Entonces:

- si todas las coordenadas ≥ 0 → punto dentro → **agudo**
- si alguna < 0 → punto fuera → **obtuso**

---

## 💻 Implementación

```python
def is_acute_tetrahedron(v, ci, cj, ck, cl):

    bary = compute_barycentric(v, ci, cj, ck, cl)

    return all(b >= 0 for b in bary)
```

---

## ⚙️ Dirección del flow

Para un tetraedro obtuso:

👉 el flujo se dirige hacia el vecino que comparte la cara opuesta al vértice “problemático”

---

## 🔑 Regla geométrica

- El circuncentro cae fuera a través de una cara
- Esa cara define la dirección del flujo

---

## 💻 Algoritmo

```python
def select_flow_neighbor(T, neighbors, v):

    for face, neighbor in neighbors.items():
        if is_face_visible_from_point(face, v):
            return neighbor
```

---

## 🧠 Intuición

- flujo sigue la dirección en la que el vacío “se abre”
- equivalente a un descenso en el campo topológico

---

## 🔁 Propiedad importante

El flow es:

- determinista
- acíclico
- converge a un sink o al infinito

---

## ⚠️ Nota importante

Este criterio es el núcleo matemático del método.

Sin esto:
- el algoritmo pierde consistencia topológica

---

## 🚀 Resultado

Con esto puedes:

- implementar CAST completamente
- construir topología del espacio vacío
- detectar pockets de forma robusta

---

## 📚 Referencias

- Liang et al., 1998
- Edelsbrunner (alpha shapes)
