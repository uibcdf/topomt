# CAST: Discrete Flow y Identificación de Pockets/Cavities

## 📌 Objetivo

Este documento describe el siguiente paso en CAST tras identificar los **empty tetrahedra**:

👉 cómo aplicar **discrete flow**  
👉 cómo identificar **pockets, cavities y exterior**

Basado en:
Liang et al., 1998

---

## 🧠 Idea central

CAST no detecta pockets directamente.

Primero:
- construye el **espacio vacío** (empty tetrahedra)

Luego:
- define un **flujo discreto** sobre ese espacio

👉 Los pockets emergen como **regiones que convergen a un mínimo (sink)**

---

## 🔺 Dominio del algoritmo

El discrete flow se define SOLO sobre:

```python
empty_tetrahedra
```

No se usa:
- tetrahedra llenos
- geometría de átomos directamente

---

## 🧩 Estructura: grafo dual

Construimos un grafo:

- nodos → tetrahedra vacíos
- aristas → tetrahedra vecinos (comparten cara)

```python
graph[T] = neighbors(T)
```

---

## ⚙️ Paso 1: clasificar tetrahedra (agudo vs obtuso)

El paper distingue:

- tetraedros **agudos**
- tetraedros **obtusos**

### 🔑 Regla clave

- **Agudo** → sink (mínimo)
- **Obtuso** → fluye hacia vecino

---

## 🧠 Intuición geométrica

- un tetraedro agudo → región local "cerrada"
- un tetraedro obtuso → región "abierta" → flujo

---

## ⚙️ Paso 2: definir dirección de flujo

Para cada tetraedro obtuso:

- se selecciona un vecino hacia el cual fluye

Criterio (conceptual del paper):
👉 flujo hacia el tetraedro que representa una región más "abierta"

Implementación típica:

```python
flow[T] = neighbor_with_larger_void_measure
```

---

## ⚙️ Paso 3: propagación del flujo

Cada tetraedro sigue el flujo hasta:

- llegar a un **sink (agudo)**  
- o escapar al **infinito**

```python
def follow_flow(T):
    while T not in sinks:
        T = flow[T]
    return T
```

---

## ⚙️ Paso 4: agrupación

Todos los tetrahedra que llegan al mismo sink forman:

```python
pocket = {T | follow_flow(T) == sink}
```

---

## 🔴 Clasificación final

### 1. Pocket

- flujo termina en un sink interno

### 2. Cavity

- pocket completamente encerrado

### 3. Exterior

- flujo no termina (escapa al infinito)

---

## 🧠 Detección de infinito

Un tetraedro pertenece al exterior si:

- su flujo no converge
- o conecta con frontera infinita

---

## 💻 Pseudocódigo completo

```python
def compute_pockets(empty_tetrahedra):

    graph = build_adjacency(empty_tetrahedra)

    sinks = set()
    flow = {}

    for T in empty_tetrahedra:

        if is_acute(T):
            sinks.add(T)
        else:
            flow[T] = select_neighbor(T, graph[T])

    def find_sink(T):
        while T not in sinks:
            if T not in flow:
                return None  # infinito
            T = flow[T]
        return T

    pockets = {}

    for T in empty_tetrahedra:
        s = find_sink(T)
        if s is not None:
            pockets.setdefault(s, []).append(T)

    return pockets
```

---

## 🔥 Interpretación topológica

CAST está haciendo:

👉 segmentación del espacio vacío  
👉 basada en dinámica de flujo  
👉 no en umbrales geométricos directos

---

## 🧩 Relación con TopoMT

Esto se traduce naturalmente a:

- nodo → tetraedro
- flujo → operador topológico
- sink → núcleo de cavidad

Clases naturales:

- `Cavity`
- `Pocket`
- `Mouth`

---

## 🚀 Resultado final

A partir de:

- geometría molecular

obtienes:

- descomposición topológica del espacio vacío

---

## 📚 Referencias

- Liang et al., 1998
- Edelsbrunner alpha shapes
