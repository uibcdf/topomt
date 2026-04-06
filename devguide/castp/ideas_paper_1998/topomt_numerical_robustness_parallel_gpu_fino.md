# TopoMT: robustez numérica, reproducibilidad y estrategia de paralelización/GPU

## Propósito

Este documento propone una estrategia **seria y de producción** para implementar TopoMT con:

- robustez geométrica razonable,
- comportamiento reproducible,
- buen rendimiento en sistemas grandes,
- y una separación clara entre lo que debe ser **robusto** y lo que puede ser **rápido**.

La tesis central es:

> en TopoMT, la corrección topológica vale más que la aceleración prematura.

---

# 1. Capas computacionales del problema

Conviene separar el pipeline en capas, porque no todas tienen el mismo perfil numérico ni el mismo potencial de paralelización.

## 1.1 Capa geométrica crítica
Incluye:

- triangulación regular,
- cálculo del alpha complex,
- clasificación de tetraedros vacíos/llenos,
- conectividad del espacio vacío,
- discrete flow,
- clasificación pocket/cavity/channel.

Esta capa es la más sensible numéricamente.

## 1.2 Capa geométrica derivada
Incluye:

- volúmenes,
- áreas,
- centros,
- profundidades,
- métricas por mouth,
- estadísticas por feature.

Aquí suele ser aceptable usar flotante estándar.

## 1.3 Capa analítica
Incluye:

- comparación entre estructuras,
- clustering de features,
- análisis temporal,
- histogramas, perfiles y descriptores.

Esta capa es muy paralelizable y, en general, menos delicada.

---

# 2. Fuentes reales de inestabilidad numérica

## 2.1 Degeneraciones geométricas
Casos donde la geometría se aproxima a configuraciones singulares:

- tetraedros casi coplanares,
- vértices casi cosféricos en sentido ponderado,
- caras casi degeneradas,
- power centers mal condicionados.

## 2.2 Sensibilidad de signo
Muchas decisiones del pipeline dependen del signo de una magnitud:

- `alpha > 0` o no,
- “dentro / fuera”,
- visibilidad a través de una cara,
- pertenencia a exterior,
- orientación de una cara,
- selección de vecino en flow.

Cerca de cero, estas decisiones se vuelven frágiles.

## 2.3 Dependencia de tolerancias
Si cada módulo usa un `eps` distinto, aparecen inconsistencias:

- un tetraedro puede ser “vacío” en un módulo y “frontera” en otro,
- una mouth puede abrirse o cerrarse artificialmente,
- el número de componentes puede variar.

## 2.4 Propagación de errores
Una mala clasificación local puede escalar:

- cambia una arista de flow,
- cambia el sink,
- cambia la componente,
- cambia la identidad completa de un pocket.

---

# 3. Política general de robustez

## 3.1 Una única filosofía
Definir una política centralizada para decisiones geométricas:

- `inside`
- `outside`
- `boundary_or_uncertain`

Nunca dispersar criterios “ad hoc” por todo el código.

## 3.2 Topología primero
Las decisiones que afectan:

- conectividad,
- flow,
- clasificación exterior/interior,
- mouths,
- identity tracking,

deben hacerse con la parte más estable del pipeline.

## 3.3 Métricas después
Volumen, área y profundidad pueden calcularse después, incluso con kernels vectorizados o GPU.

---

# 4. Política de epsilon

## 4.1 Por qué no usar comparaciones exactas
Nunca conviene usar:

```python
if alpha > 0:
```

ni:

```python
if det == 0:
```

en coma flotante.

## 4.2 Epsilon absoluto vs relativo
Un `eps` absoluto fijo puede fallar cuando:
- la molécula es muy grande,
- las coordenadas están en otra escala,
- o la magnitud evaluada cambia de orden.

Conviene usar un epsilon **adaptativo**.

## 4.3 Recomendación
Definir una longitud característica \(L\), por ejemplo:

- radio atómico medio,
- distancia media entre centros vecinos,
- o caja envolvente normalizada.

Y usar:

\[
\varepsilon_\alpha = \eta \, L^2
\]

con \(\eta\) pequeño, por ejemplo \(10^{-12}\) a \(10^{-10}\) según backend y escala.

## 4.4 Clasificación ternaria
En vez de binaria, usar clasificación ternaria:

- `alpha > eps` → `outside`
- `alpha < -eps` → `inside`
- `|alpha| <= eps` → `uncertain`

Esto es mucho más sano que forzar una decisión inestable.

---

# 5. Manejo de casos inciertos

## 5.1 Estrategia recomendada
Cuando una decisión cae en zona gris:

1. marcar el objeto como `uncertain`,
2. resolverlo en una fase posterior,
3. usar información del entorno local si es necesario,
4. registrar que hubo una resolución no primaria.

## 5.2 Resolución por contexto
Algunas opciones:
- mayoría entre vecinos,
- criterio conservador,
- reevaluación con mayor precisión,
- reclasificación diferida.

## 5.3 Principio conservador
Si una decisión afecta conectividad global, es mejor:
- aplazarla,
- o resolverla con un criterio más robusto,
que introducir una arista o un sink erróneo.

---

# 6. Predicados geométricos críticos

Estos son los predicados que conviene encapsular y versionar.

## 6.1 `classify_alpha_sign`
Decide si un tetraedro es:
- dentro,
- fuera,
- incierto.

## 6.2 `is_point_inside_simplex`
Para decidir si un power center cae dentro del tetraedro.

## 6.3 `oriented_face_visibility`
Para decidir por qué cara “sale” un tetraedro obtuso.

## 6.4 `is_boundary_connection_to_exterior`
Para mouths y acceso al exterior.

## 6.5 `is_local_minimum_of_flow`
Para sinks.

Todos estos predicados deben residir en una capa central.

---

# 7. Triangulación regular: estrategia recomendada

## 7.1 Recomendación de arquitectura
No implementar desde cero la triangulación regular robusta en una primera versión si puedes evitarlo.

Lo recomendable es:

- usar una librería consolidada si la hay,
- o encapsular una backend externa,
- o separar la triangulación en un módulo backend con API estable.

## 7.2 Por qué
Porque la triangulación regular robusta concentra gran parte de la dificultad:
- degeneraciones,
- exactitud combinatoria,
- consistencia del complejo.

## 7.3 Diseño recomendable
```python
class RegularTriangulationBackend:
    def build(self, centers, radii): ...
    def tetrahedra(self): ...
    def faces(self): ...
    def adjacency(self): ...
    def alpha_complex(self): ...
```

Así TopoMT desacopla:
- la lógica topológica,
- del backend geométrico concreto.

---

# 8. Flow y robustez

## 8.1 Sensibilidad del flow
El discrete flow suele ser mucho más sensible que el cálculo de métricas.

Errores en:
- clasificación agudo/obtuso,
- selección de cara de salida,
- o conectividad,

pueden cambiar completamente la feature final.

## 8.2 Estrategia
Separar:
- `flow_candidate_edges`
- `validated_flow_edges`

y validar después consistencia global:
- aciclicidad,
- sinks bien definidos,
- trazas no contradictorias.

## 8.3 Comprobaciones útiles
- que un nodo no tenga dos salidas distintas tras resolución,
- que no aparezcan ciclos,
- que los sinks no sean espurios por ruido numérico.

---

# 9. Reproducibilidad

## 9.1 Todo resultado debe registrar contexto
Cada `Topography` debería almacenar:

```python
metadata = {
    "algorithm_version": "topomt-0.1",
    "backend": "...",
    "probe_radius": 1.4,
    "radii_model": "...",
    "eps_alpha": ...,
    "eps_inside_simplex": ...,
    "flow_policy": "...",
}
```

## 9.2 Por qué es esencial
Si cambias:
- radios,
- tolerancias,
- backend,
- política de flow,

pueden cambiar las features.

Sin trazabilidad no hay reproducibilidad científica.

---

# 10. Qué partes paralelizar

## 10.1 Masivamente paralelizables
Estas tareas son casi embarrassingly parallel:

- power center por tetraedro,
- alpha por tetraedro,
- volumen por tetraedro,
- área por cara,
- etiquetas locales,
- descriptores por feature una vez segmentadas.

## 10.2 Moderadamente paralelizables
- construcción de tablas de caras compartidas,
- ensamblado de adyacencias,
- distancias sobre grafo,
- BFS multi-source,
- clustering entre features.

## 10.3 Menos recomendables para GPU en la v1
- triangulación regular robusta,
- lógica de flow con muchas bifurcaciones,
- resolución de incertidumbres geométricas complejas.

---

# 11. Estrategia CPU / GPU híbrida

## 11.1 Núcleo robusto en CPU
La propuesta recomendada para v1 es mantener en CPU:

- triangulación regular,
- alpha complex,
- clasificación vacío/lleno,
- adyacencia,
- discrete flow,
- componentes conexas,
- mouths y clasificación topológica final.

## 11.2 Aceleración posterior
Enviar a GPU o a kernels paralelos:

- cómputo masivo de métricas,
- mapas de profundidad,
- distancias desde mouths,
- histogramas y análisis de trayectorias,
- matching entre frames si está bien vectorizado.

## 11.3 Ventaja
Este diseño permite:
- corrección topológica,
- y aceleración donde realmente compensa.

---

# 12. GPU: qué sí y qué no

## 12.1 Buenas candidatas a GPU
- arrays grandes de tetraedros,
- cómputo de volúmenes,
- distancias punto-celda,
- centroides,
- áreas de caras,
- features temporales por frame en lote.

## 12.2 Malas candidatas tempranas
- triangulación robusta,
- decisiones simbólicas o casi exactas,
- predicados con mucha lógica condicional,
- reconstrucción combinatoria compleja.

## 12.3 Regla práctica
No intentar “GPU-first”.
Hacer **correct first**, luego **fast where safe**.

---

# 13. Diseño de software recomendado

## 13.1 Separar capas
```python
topomt/
    geometry/
    topology/
    metrics/
    dynamics/
    backends/
```

## 13.2 Responsabilidades
- `geometry/` → power centers, alpha, volumes, faces
- `topology/` → flow, components, mouths, classification
- `metrics/` → depth, surface area, shape descriptors
- `dynamics/` → tracking entre frames
- `backends/` → triangulación y aceleración opcional

## 13.3 Ventaja
Esto evita mezclar:
- decisiones robustas,
- con cómputos rápidos y descriptores.

---

# 14. Pruebas necesarias para robustez

## 14.1 Tests unitarios
- power center en casos simples,
- clasificación alpha controlada,
- barycentric inside/outside,
- volumen y área.

## 14.2 Tests de degeneración
- tetraedros casi planos,
- casos con alpha casi cero,
- configuraciones simétricas,
- radios iguales y desiguales.

## 14.3 Tests de invariancia
- translación,
- rotación,
- reordenamiento de átomos.

## 14.4 Tests de regresión
Guardar snapshots de:
- número de pockets,
- mouths,
- volúmenes clave,
- comparativas entre versiones.

---

# 15. Estrategia de escalado

## 15.1 v1
- CPU robusto
- multi-thread ligero
- métricas paralelas

## 15.2 v2
- backend compilado
- kernels vectorizados
- depth y descriptores acelerados

## 15.3 v3
- soporte GPU opcional
- batches de frames
- análisis dinámico a gran escala

---

# 16. Recomendación tecnológica

## Opción pragmática
- Python como capa de usuario
- backend compilado o externo para triangulación
- NumPy para prototipos
- Numba para kernels rápidos
- CuPy/PyTorch/JAX sólo cuando haya un caso claro

## Opción científica limpia
- núcleo combinatorio robusto en C++ o backend externo
- wrappers Python
- métricas y análisis en Python

---

# 17. Principio rector

La recomendación fina es:

> mantener la geometría combinatoria y topológica en el entorno más robusto disponible, y reservar la paralelización agresiva para métricas, estadísticas y dinámica.

Ésta es, probablemente, la forma más sensata de construir TopoMT sin hipotecar ni la ciencia ni la mantenibilidad.

---

# 18. Resumen ejecutivo

La estrategia recomendada para TopoMT es:

- usar una política centralizada de tolerancias;
- adoptar clasificación ternaria cuando el signo sea dudoso;
- desacoplar backend geométrico y lógica topológica;
- mantener en CPU la capa crítica;
- paralelizar y acelerar sólo donde el riesgo numérico sea bajo;
- almacenar suficiente metadata para reproducibilidad;
- introducir GPU como aceleración opcional, no como dependencia esencial.

Ese enfoque es más lento al principio que una implementación “rápida”, pero mucho más sólido y científicamente defendible.
