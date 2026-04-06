# TopoMT: definición formal fina de tipos topológicos y semánticos

## Propósito

Este documento propone una formulación **rigurosa, extensible y programable** para el modelo de entidades topográficas de **TopoMT**. La meta no es sólo detectar *pockets*, sino construir una ontología geométrico-topológica del espacio molecular que permita representar de manera explícita:

- regiones cóncavas y convexas,
- fronteras y cuellos,
- conexiones entre regiones,
- jerarquías internas,
- y, más adelante, su evolución temporal.

La propuesta está pensada para ser:

1. **matemáticamente limpia**,  
2. **útil en implementación**,  
3. **estable frente a extensiones**,  
4. **alineada con el pipeline geométrico heredado de CAST**,  
5. **más general que CAST**.

---

# 1. Espacio de partida

## 1.1 Sólido molecular

Sea una estructura molecular modelada como una unión de bolas cerradas:

\[
U = \bigcup_{i=1}^{N} B(c_i, r_i)
\]

donde:

- \(c_i \in \mathbb{R}^3\) es el centro del átomo \(i\),
- \(r_i > 0\) es su radio efectivo,
- \(B(c_i, r_i)\) es la bola cerrada correspondiente.

La frontera del sólido molecular se denota por:

\[
\partial U
\]

---

## 1.2 Descomposición del espacio vacío

A partir de una **regular triangulation** (weighted Delaunay triangulation) y del **alpha complex**, definimos el conjunto de tetraedros vacíos:

\[
E = \{ T \;|\; T \in \text{RegularTriangulation}, \; T \notin \text{AlphaComplex} \}
\]

Estos tetraedros vacíos representan una discretización geométricamente coherente del **espacio negativo** alrededor y dentro de la molécula.

---

## 1.3 Grafo del vacío

Definimos un grafo no dirigido:

\[
G_E = (E, A)
\]

donde:

- los nodos son tetraedros vacíos,
- existe una arista \((T_i, T_j)\) si y sólo si \(T_i\) y \(T_j\) comparten una cara triangular.

Este grafo es el dominio natural para:

- componentes conexas,
- flujos discretos,
- clasificación topológica,
- construcción de features.

---

# 2. Principio central del modelo

TopoMT no debe confundir:

- **región geométrica**,  
- **tipo topológico**,  
- **rol semántico**,  
- **objeto de frontera**,  
- **objeto derivado**.

Por eso proponemos una separación explícita entre:

## 2.1 `shape_type`
Clasifica la naturaleza topográfica general:

- `concavity`
- `convexity`
- `boundary`
- `mixed`

## 2.2 `feature_type`
Clasifica la entidad concreta:

- `pocket`
- `cavity`
- `channel`
- `mouth`
- `neck`
- `ridge`
- `apex`
- `interface`
- etc.

## 2.3 `dimensionality`
Indica la dimensión topológica o geométrica dominante:

- `3` → región volumétrica
- `2` → superficie o parche frontera
- `1` → línea, reborde, cuello, borde
- `0` → punto especial o extremo

Esta separación es importante porque, por ejemplo:

- `Pocket` y `Cavity` comparten `shape_type = concavity`,
- `Mouth` y `Neck` comparten `shape_type = boundary`,
- pero tienen distinta semántica y distinta dimensionalidad operativa.

---

# 3. Clase base: `Feature`

## 3.1 Definición abstracta

Una `Feature` es una entidad geométrico-topológica definida sobre el espacio molecular o sobre la frontera molecular y caracterizada por:

- una región soporte,
- una conectividad interna,
- una frontera asociada,
- relaciones con otras features,
- y una interpretación semántica.

## 3.2 Atributos mínimos recomendados

```python
class Feature:
    feature_id: str
    shape_type: str
    feature_type: str
    dimensionality: int
    data: object | None

    cells: tuple | list
    boundary_cells: tuple | list
    parent_id: str | None

    adjacent_feature_ids: tuple | list
    metrics: dict
    metadata: dict
```

## 3.3 Interpretación de los campos

- `cells`: celdas geométricas de soporte principal  
- `boundary_cells`: celdas que forman su frontera explícita  
- `parent_id`: útil para subfeatures o features frontera asociadas  
- `adjacent_feature_ids`: grafo semántico de relaciones  
- `metrics`: volumen, área, profundidad, abertura, etc.  
- `metadata`: radios usados, tolerancias, frame, score, flags

---

# 4. Definición formal de región feature

Sea \(C(F)\) el conjunto de celdas asociadas a una feature \(F\).

Diremos que \(F\) es una feature válida si cumple:

## 4.1 No vacuidad
\[
C(F) \neq \emptyset
\]

## 4.2 Conectividad
El subgrafo inducido por \(C(F)\) en \(G_E\) debe ser conexo cuando \(F\) es volumétrica.

## 4.3 Coherencia de tipo
Las celdas que la forman deben satisfacer el criterio topológico asociado a su tipo.

## 4.4 Maximalidad local
Si \(F\) es una feature principal, no debe poder extenderse con celdas vecinas sin perder su definición.

Este criterio evita trocear artificialmente una región salvo que exista una razón topológica o semántica.

---

# 5. Tipos topográficos generales (`shape_type`)

## 5.1 Concavity

### Definición intuitiva
Una **concavidad** es una región del espacio vacío que se introduce en el sólido molecular o queda confinada por él.

### Definición formal propuesta
Una feature \(F\) es una `Concavity` si:

1. \(C(F) \subseteq E\),  
2. \(C(F)\) induce un subgrafo conexo,  
3. una parte no trivial de su frontera está definida por \(\partial U\),  
4. no coincide con la región exterior libre completa.

### Observación importante
Esta definición incluye tanto regiones:
- abiertas al exterior,
- como totalmente internas.

Por tanto, `Pocket`, `Cavity` y `Channel` son subtipos de `Concavity`.

---

## 5.2 Convexity

### Idea general
Una **convexidad** no vive primariamente en el volumen vacío, sino en la **superficie molecular** y su geometría local. Representa una protrusión o relieve saliente del sólido.

### Definición operativa propuesta
Una región superficial \(S \subseteq \partial U\) puede clasificarse como `Convexity` si:

1. es conexa como parche superficial,  
2. exhibe una geometría local saliente con respecto a una vecindad o a una envolvente de referencia,  
3. constituye una entidad distinguible por curvatura, prominencia o separación topográfica.

### Nota
Aquí TopoMT va más allá de CAST. Para la v1, estas features pueden derivarse de:
- curvatura local,
- prominencia relativa,
- o una dualidad con regiones cóncavas cercanas.

---

## 5.3 Boundary

### Idea general
Una `Boundary` no representa un volumen del vacío por sí mismo, sino una entidad de menor dimensión que separa, conecta o delimita regiones mayores.

### Definición formal propuesta
Una feature \(B\) es `Boundary` si:

1. su soporte está formado por caras, aristas o vértices frontera,  
2. su dimensionalidad dominante es menor que 3,  
3. actúa como interfaz entre una o más regiones volumétricas o entre una región y el exterior.

Ejemplos:
- `Mouth`
- `Neck`
- `BaseRim`

---

## 5.4 Mixed

### Idea general
Una feature `Mixed` representa una zona de transición o interfaz cuya interpretación no es puramente cóncava, convexa o de frontera simple.

### Uso recomendado
Reservar `Mixed` para entidades como:
- `Interface`
- fronteras complejas entre subfeatures,
- regiones de transición semántica.

No es imprescindible para la primera implementación, pero sí valioso para extensiones.

---

# 6. Tipos concretos (`feature_type`)

## 6.1 Pocket

### Intuición
Una `Pocket` es una concavidad abierta al exterior por una o varias bocas.

### Definición formal
Sea \(F\) una concavidad. Diremos que \(F\) es `Pocket` si:

1. existe al menos una componente de frontera que la conecta con la región exterior,  
2. el acceso al exterior está mediado por una o más regiones `Mouth`,  
3. \(F\) no es la región exterior misma.

### Casos
- 1 mouth → pocket clásico
- >1 mouths → puede seguir siendo pocket o reclasificarse como `Channel` según criterio global

### Recomendación
Clasificar como:
- `Pocket` si el número de accesos exteriores es 1,
- `Channel` si es 2 o más.

---

## 6.2 Cavity

### Intuición
Una `Cavity` es una concavidad completamente enterrada, sin acceso al exterior.

### Definición formal
Sea \(F\) una concavidad. Diremos que \(F\) es `Cavity` si:

1. \(F\) es conexa,  
2. ninguna componente de su frontera conecta con la región exterior,  
3. toda su frontera está cerrada por el sólido molecular.

---

## 6.3 Channel

### Intuición
Un `Channel` es una concavidad que comunica dos o más accesos exteriores distintos.

### Definición formal
Sea \(F\) una concavidad. Diremos que \(F\) es `Channel` si:

1. \(F\) es conexa,  
2. posee al menos dos mouths topológicamente distintas,  
3. dichas mouths conectan con el exterior por componentes separadas o accesos distinguibles.

### Nota
Esto permite representar:
- túneles,
- poros,
- trayectorias solvente-solvente,
- conducciones internas.

---

## 6.4 Subpocket

### Intuición
Un `Subpocket` es una subregión jerárquica de una concavidad mayor.

### Definición operativa
Sea \(P\) un pocket. Una región \(S \subset P\) puede definirse como `Subpocket` si:

1. es conexa,  
2. presenta una separación topográfica interna razonable (cuello, estrangulamiento o cambio geométrico),  
3. posee identidad geométrica útil a nivel funcional.

### Uso
Es muy útil en:
- diseño de ligandos,
- comparación apo/holo,
- análisis de ocupación parcial.

---

## 6.5 Mouth

### Intuición
Una `Mouth` es la región de frontera que comunica una concavidad con el exterior.

### Definición formal
Sea \(F\) una concavidad abierta. Una feature \(M\) es `Mouth` si:

1. \(M\) es una componente conexa de la frontera de \(F\),  
2. \(M\) está en contacto con la región exterior,  
3. \(M\) actúa como portal de acceso entre \(F\) y el exterior.

### Dimensionalidad
Usualmente:
- geométricamente 2D si se representa como conjunto de caras,
- conceptualmente 1D si se abstrae a un reborde o rim.

Por eso conviene distinguir:
- `mouth_surface`
- `mouth_rim`
si en el futuro quieres mayor precisión semántica.

---

## 6.6 Neck

### Intuición
Un `Neck` es una región estrecha que constriñe la conectividad entre dos regiones mayores.

### Definición operativa
Una feature \(N\) es `Neck` si:

1. pertenece a una frontera o interfaz interna,  
2. su sección transversal local es mínima o cercana a mínima,  
3. conecta dos subregiones de una misma concavidad o dos concavidades adyacentes.

### Importancia
Un `Neck` puede ser crucial para:
- apertura/cierre,
- gating,
- accesibilidad de ligandos,
- subdivisión de pockets en subpockets.

---

## 6.7 BaseRim

### Intuición
`BaseRim` es el reborde de frontera asociado a una convexidad o a la base de una protrusión.

### Uso
Esta entidad no es prioritaria en la primera versión, pero encaja muy bien en un sistema general de topografía.

---

## 6.8 Interface

### Intuición
Una `Interface` representa una frontera compartida entre dos features o entre dos subregiones topográficamente distinguibles.

### Ejemplos
- frontera pocket-subpocket
- interfaz concavity-channel
- interfaz entre regiones con distinta química superficial

---

## 6.9 Ridge y Apex

Estos son tipos naturales para convexidades:

### Ridge
Estructura lineal prominente sobre la superficie.

### Apex
Máximo local de prominencia o extremo de una convexidad.

---

# 7. Operadores geométrico-topológicos

## 7.1 Operador frontera

Para una feature volumétrica \(F\), definimos:

\[
\partial F = \{ f \;|\; f \text{ es cara de una celda de } F \text{ y la celda adyacente no pertenece a } F \}
\]

Esto produce el conjunto de caras frontera.

---

## 7.2 Frontera exterior

\[
\partial_{\text{ext}} F \subseteq \partial F
\]

es el subconjunto de la frontera de \(F\) cuyas caras lindan con una región exterior.

Las componentes conexas de \(\partial_{\text{ext}} F\) son candidatas naturales a `Mouth`.

---

## 7.3 Frontera interna

\[
\partial_{\text{int}} F = \partial F \setminus \partial_{\text{ext}} F
\]

Puede contener:
- interfaces internas,
- necks,
- divisorias entre subpockets.

---

# 8. Relaciones entre features

Conviene modelarlas explícitamente.

## 8.1 Adjacency
Dos features \(F_1, F_2\) son adyacentes si comparten una frontera no vacía.

## 8.2 Incidence
Una feature frontera \(B\) es incidente a una feature volumétrica \(F\) si \(B \subseteq \partial F\).

## 8.3 Parent-child
Útil para:
- mouth → pocket
- subpocket → pocket
- neck → pocket/channel

## 8.4 Containment
Para relaciones jerárquicas:
- subpocket contenido en pocket
- apex contenido en convexity mayor

---

# 9. Jerarquía recomendada en Python

```python
Feature
├── VolumetricFeature
│   ├── Concavity
│   │   ├── Pocket
│   │   ├── Cavity
│   │   ├── Channel
│   │   └── Subpocket
│   └── MixedVolume
├── SurfaceFeature
│   ├── Convexity
│   │   ├── Vexity
│   │   ├── Ridge
│   │   └── Apex
│   └── Interface
└── BoundaryFeature
    ├── Mouth
    ├── Neck
    └── BaseRim
```

Si prefieres una jerarquía más simple, puedes mantener:

```python
Feature
├── Concavity
├── Convexity
├── Mixed
└── Boundary
```

y distinguir con `feature_type`.

---

# 10. Recomendación práctica para la v1

Para no sobrecargar el desarrollo inicial, la v1 de TopoMT debería implementar formalmente sólo:

- `Pocket`
- `Cavity`
- `Channel`
- `Mouth`
- `Neck`
- `Interface` (opcional)
- `Subpocket` (si ya existe criterio geométrico claro)

Y dejar para v2:
- `Convexity`
- `Ridge`
- `Apex`
- `BaseRim`

---

# 11. Ejemplo de instancia conceptual

```python
Pocket(
    feature_id="pocket_3",
    shape_type="concavity",
    feature_type="pocket",
    dimensionality=3,
    cells=[...],
    boundary_cells=[...],
    parent_id=None,
    adjacent_feature_ids=["mouth_3_1", "subpocket_3_1"],
    metrics={
        "volume": 412.7,
        "surface_area": 365.4,
        "depth": 11.2,
        "n_mouths": 1,
    },
    metadata={
        "probe_radius": 1.4,
        "frame": 0,
        "algorithm_version": "topomt-0.1",
    },
)
```

---

# 12. Idea fuerte para paper

La aportación conceptual de TopoMT no sería “otro detector de pockets”, sino:

> representar la topografía molecular como una colección explícita de features geométrico-topológicas de distintas dimensiones, con semántica propia, relaciones explícitas y extensión natural a dinámica.

---

# 13. Resumen ejecutivo

La propuesta fina del modelo es:

- el espacio vacío se discretiza en tetraedros vacíos;
- las features volumétricas se definen como regiones conexas clasificadas topológicamente;
- las fronteras se representan como entities propias;
- `shape_type` y `feature_type` se separan explícitamente;
- la jerarquía admite pockets, cavities, channels, mouths, necks y, a futuro, convexidades.

Esto le da a TopoMT una base conceptual mucho más fuerte, extensible y publicable que una taxonomía centrada sólo en pockets.
