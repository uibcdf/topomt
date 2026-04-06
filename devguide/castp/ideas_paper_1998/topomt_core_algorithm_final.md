# TopoMT: core algorithm final

## Propósito

Este documento propone una formulación **integral, rigurosa y programable** del algoritmo central de TopoMT. La meta es disponer de una especificación que pueda servir simultáneamente como:

- guía de implementación,
- documento de diseño de arquitectura,
- borrador de sección **Methods** para un paper,
- y puente conceptual entre CAST y una teoría más general de topografía molecular.

TopoMT parte de una idea heredada de CAST:

> la topografía molecular puede inferirse a partir de la estructura del espacio vacío alrededor y dentro del sólido molecular.

Pero la amplía en tres sentidos:

1. hace explícita la noción de **feature** como entidad geométrico-topológica,
2. separa con claridad **geometría**, **topología**, **semántica** y **métricas**,
3. y prepara el terreno para dinámica, jerarquías y análisis semántico.

---

# 1. Entrada y objetos básicos

## 1.1 Estructura molecular

La entrada mínima del algoritmo es una estructura molecular formada por átomos:

\[
\mathcal{A} = \{(c_i, r_i)\}_{i=1}^{N}
\]

donde:

- \(c_i \in \mathbb{R}^3\) es el centro del átomo \(i\),
- \(r_i > 0\) es su radio efectivo.

El sólido molecular se representa como la unión de bolas:

\[
U = \bigcup_{i=1}^{N} B(c_i, r_i)
\]

---

## 1.2 Parámetros relevantes

El algoritmo debe registrar explícitamente los parámetros geométricos y numéricos:

- modelo de radios,
- radio de sonda, si aplica en alguna capa semántica,
- tolerancias numéricas,
- política de clasificación alpha,
- política de flow,
- backend de triangulación.

Nada de esto debe quedar implícito.

---

# 2. Visión global del pipeline

El pipeline completo puede descomponerse en siete fases:

1. **Geometría base**
2. **Extracción del espacio vacío**
3. **Grafo del vacío**
4. **Discrete flow**
5. **Segmentación topológica**
6. **Clasificación semántica**
7. **Métricas y relaciones**

En notación compacta:

\[
\mathcal{A}
\rightarrow
\text{RegularTriangulation}
\rightarrow
\text{AlphaComplex}
\rightarrow
E
\rightarrow
G_E
\rightarrow
\text{Flow}
\rightarrow
\text{Regions}
\rightarrow
\text{Features}
\]

---

# 3. Fase I: geometría base

## 3.1 Regular triangulation

A partir de los centros y radios se construye la **regular triangulation** o weighted Delaunay triangulation.

Denotemos por:

\[
\mathcal{T}_{reg}
\]

el conjunto de tetraedros resultante.

Cada tetraedro \(T \in \mathcal{T}_{reg}\) está definido por cuatro átomos índice:

\[
T = (i,j,k,l)
\]

y tiene objetos derivados:
- caras triangulares,
- adyacencias,
- power center,
- valor alpha,
- orientación local,
- volumen euclídeo del simplex.

## 3.2 Alpha complex

Se construye el **alpha complex** o dual complex asociado al sólido molecular.

Denotemos por:

\[
\mathcal{K}_\alpha
\subseteq
\mathcal{T}_{reg}
\]

el subconjunto de tetraedros que pertenecen al complejo.

La manera más fiel a CAST de proceder es:

- usar el alpha complex directamente si el backend lo proporciona;
- o reconstruir pertenencia mediante el criterio del power center y el signo de \(\alpha\).

---

# 4. Fase II: extracción del espacio vacío

## 4.1 Definición de tetraedros vacíos

Definimos:

\[
E = \mathcal{T}_{reg} \setminus \mathcal{K}_\alpha
\]

Los tetraedros de \(E\) son los **empty tetrahedra**.

Éste es el dominio sobre el que se define el core topológico de TopoMT.

## 4.2 Clasificación robusta

Si no se dispone del alpha complex explícito, para cada tetraedro \(T\) se calcula su power center \(v_T\) y el valor:

\[
\alpha_T = \|v_T - c_i\|^2 - r_i^2
\]

para cualquiera de sus cuatro vértices.

La clasificación recomendada es ternaria:

- `inside` si \(\alpha_T < -\varepsilon\)
- `outside` si \(\alpha_T > \varepsilon\)
- `uncertain` si \(|\alpha_T| \le \varepsilon\)

Los tetraedros `outside` se consideran vacíos.
Los `uncertain` deben resolverse mediante una política explícita.

---

# 5. Fase III: construcción del grafo del vacío

## 5.1 Grafo de adyacencia

Definimos el grafo:

\[
G_E = (E, A)
\]

donde:
- cada nodo es un tetraedro vacío,
- hay una arista entre dos tetraedros si comparten una cara.

Esto captura la conectividad volumétrica del espacio vacío.

## 5.2 Caras frontera

Para cada tetraedro \(T \in E\), una cara \(f \subset T\) es una **cara frontera** si el tetraedro adyacente a través de esa cara no pertenece a \(E\).

Conviene distinguir después entre:
- frontera respecto al sólido,
- frontera respecto al exterior,
- frontera entre regiones vacías distintas.

---

# 6. Fase IV: discrete flow

Ésta es la fase topológica central del algoritmo.

La intuición es que el espacio vacío no debe segmentarse únicamente por conectividad, sino por una estructura de flujo discreto que permita distinguir:

- mínimos locales del vacío,
- regiones atrapadas,
- regiones abiertas al infinito.

---

## 6.1 Idea del flow

Cada tetraedro vacío puede ser:

- un **sink** local,
- o un tetraedro que “fluye” hacia otro tetraedro vacío vecino.

El discrete flow define una aplicación parcial:

\[
\phi : E \to E
\]

tal que, para un tetraedro vacío \(T\):
- o bien \(\phi(T)\) está definido y es un vecino de \(T\),
- o bien \(T\) es sink,
- o bien el flujo de \(T\) conduce al exterior/infinito.

---

## 6.2 Clasificación agudo / obtuso

Una forma geométrica operativa de distinguir sinks potenciales es estudiar la posición del power center \(v_T\) respecto al simplex \(T\).

### Criterio operativo recomendado
- si \(v_T\) cae **dentro** del tetraedro, \(T\) se considera candidato a **sink**,
- si \(v_T\) cae **fuera**, \(T\) se considera tetraedro con dirección de salida.

Esta prueba puede implementarse con coordenadas baricéntricas del power center en el tetraedro.

### Clasificación robusta
Usar de nuevo una política ternaria:
- `inside_simplex`
- `outside_simplex`
- `uncertain_simplex`

---

## 6.3 Selección de dirección de salida

Si el power center cae fuera del tetraedro, debe identificarse la cara a través de la cual “sale”.

### Principio geométrico
La salida se produce a través de la cara respecto a la cual el power center queda del lado externo.

Formalmente:
- cada cara del tetraedro induce un semiespacio,
- la cara de salida es aquella cuya orientación muestra al power center del lado exterior.

En casos no degenerados, esto induce una única cara de salida.

## 6.4 Definición del vecino de flow

Sea \(T \in E\) un tetraedro no sink y sea \(f\) su cara de salida.

Si existe un tetraedro vacío vecino \(T'\) adyacente a \(T\) a través de \(f\), definimos:

\[
\phi(T) = T'
\]

Si no existe tal tetraedro vacío y la salida conduce a una región abierta, el flujo de \(T\) se considera dirigido al exterior.

---

## 6.5 Validación global del flow

Una vez definida la relación de flow, conviene validar:

- unicidad de salida por tetraedro,
- ausencia de ciclos espurios,
- sinks consistentes,
- conectividad razonable de las cuencas.

En implementación, puede ser útil distinguir:
- `candidate_flow_edge`
- `validated_flow_edge`

---

# 7. Fase V: cuencas, exterior y segmentación topológica

## 7.1 Trayectorias de flow

Para cada tetraedro \(T \in E\), iteramos el flow:

\[
T,\; \phi(T),\; \phi^2(T),\; \dots
\]

hasta que ocurra una de tres cosas:

1. se alcanza un sink,
2. se alcanza el exterior,
3. se detecta una situación incierta o degenerada.

## 7.2 Cuencas de atracción

Si un tetraedro \(T\) termina en el sink \(s\), entonces pertenece a la cuenca de atracción de \(s\):

\[
\mathcal{B}(s) = \{ T \in E \;|\; \phi^n(T)=s \text{ para algún } n \}
\]

Estas cuencas son candidatas naturales a regiones topográficas básicas.

## 7.3 Región exterior

Definimos la región exterior como el subconjunto de tetraedros vacíos cuya traza de flow alcanza una salida abierta o pertenece a una componente conectada al infinito.

Denotemos esta región por:

\[
E_{\infty}
\]

Esta región no debe etiquetarse como feature topográfica interna.

---

# 8. Fase VI: construcción de regiones volumétricas

## 8.1 Regiones sink-based

Cada sink genera una región volumétrica principal:

\[
R_s = \mathcal{B}(s)
\]

Estas regiones constituyen el núcleo de la segmentación.

## 8.2 Regiones no sink-based
Puede haber, según la política final, regiones:
- abiertas al exterior,
- ambiguas,
- o conectadas de manera compleja.

En la v1, la recomendación práctica es:
- centrar la semántica principal en regiones ligadas a sinks,
- usar la región exterior como referencia para mouths y accesibilidad,
- tratar casos ambiguos por separado.

---

# 9. Fase VII: frontera y mouths

## 9.1 Operador frontera de una región

Sea \(R \subseteq E\) una región volumétrica. Su frontera discreta viene dada por las caras:

\[
\partial R = \{ f \;|\; f \text{ es cara de un tetraedro de } R \text{ y el tetraedro adyacente no pertenece a } R \}
\]

## 9.2 Frontera exterior

Definimos:

\[
\partial_{\text{ext}} R \subseteq \partial R
\]

como el subconjunto de caras frontera que están en contacto con la región exterior \(E_\infty\) o con una salida al exterior.

## 9.3 Mouths

Las componentes conexas de \(\partial_{\text{ext}} R\) son candidatas naturales a `Mouth`.

Si:

\[
\partial_{\text{ext}} R = M_1 \cup \dots \cup M_k
\]

con \(M_i\) componentes conexas, entonces el número de mouths de \(R\) es \(k\).

---

# 10. Clasificación semántica: pocket, cavity, channel

Sea \(R\) una región volumétrica definida por una cuenca de flow o una región segmentada equivalente.

## 10.1 Cavity
\(R\) es `Cavity` si no tiene conexión con el exterior:

\[
\partial_{\text{ext}} R = \emptyset
\]

## 10.2 Pocket
\(R\) es `Pocket` si tiene una única mouth topológicamente distinguible:

\[
\#\text{Mouths}(R)=1
\]

## 10.3 Channel
\(R\) es `Channel` si tiene dos o más mouths:

\[
\#\text{Mouths}(R)\geq 2
\]

## 10.4 Casos límite
En la práctica puede haber:
- mouths muy próximas,
- mouths fusionadas geométricamente,
- accesos anchos tipo depresión abierta.

Por eso conviene que la clasificación final admita políticas configurables, pero siempre explícitas.

---

# 11. Métricas geométricas principales

Una vez construidas las features volumétricas y de frontera, se calculan sus métricas.

## 11.1 Volumen
Para una región \(R\):

\[
V(R) = \sum_{T \in R} \mathrm{vol}(T)
\]

En una implementación más refinada puede hacerse la corrección geométrica propia del sólido molecular, pero para ciertas fases internas puede bastar la suma de volúmenes simpliciales.

## 11.2 Área de frontera
Para una feature volumétrica:

\[
A(\partial R) = \sum_{f \in \partial R} \mathrm{area}(f)
\]

## 11.3 Área de mouth
Para una mouth \(M\):

\[
A(M) = \sum_{f \in M} \mathrm{area}(f)
\]

## 11.4 Profundidad
Puede definirse como una distancia geodésica o de grafo desde las mouths hacia el interior de \(R\):

\[
D(R) = \max_{T\in R} d(T, M)
\]

donde \(M\) es el conjunto de tetraedros o caras asociados a las mouths.

## 11.5 Otras métricas futuras
- cuello mínimo,
- elongación,
- ramificación,
- tortuosidad,
- descriptors químicos del lining.

---

# 12. Relación con la semántica de features

El core algorithm no debe codificar semántica de alto nivel de forma rígida.
Debe producir:

1. regiones volumétricas,
2. fronteras,
3. relaciones con exterior,
4. mouths,
5. métricas básicas,

y luego una capa semántica decide si una región es:
- pocket,
- cavity,
- channel,
- subpocket,
- neck-associated region,
- etc.

Esta separación mejora:
- mantenibilidad,
- reproducibilidad,
- extensibilidad científica.

---

# 13. Pseudocódigo end-to-end

```python
def compute_topography(centers, radii, params):

    # Phase I: geometry
    regtri = build_regular_triangulation(centers, radii, params.backend)
    alpha_complex = build_alpha_complex(regtri, params)

    # Phase II: empty tetrahedra
    empty_tetrahedra = classify_empty_tetrahedra(regtri, alpha_complex, params)

    # Phase III: empty-space graph
    graph = build_empty_graph(empty_tetrahedra)

    # Phase IV: discrete flow
    flow = {}
    sinks = set()
    exterior_seed = set()

    for T in empty_tetrahedra:
        status = classify_simplex_position(T, params)

        if status == "sink":
            sinks.add(T)
            continue

        exit_face = compute_exit_face(T, params)

        if exit_face is None:
            exterior_seed.add(T)
            continue

        neighbor = get_empty_neighbor_across_face(T, exit_face, graph)

        if neighbor is None:
            exterior_seed.add(T)
        else:
            flow[T] = neighbor

    flow = validate_flow(flow, sinks, exterior_seed, params)

    # Phase V: basin tracing
    sink_basins = {s: [] for s in sinks}
    exterior_region = []

    for T in empty_tetrahedra:
        outcome = trace_flow(T, flow, sinks, exterior_seed)

        if outcome.kind == "sink":
            sink_basins[outcome.sink].append(T)
        elif outcome.kind == "exterior":
            exterior_region.append(T)
        else:
            pass  # uncertain / unresolved policy

    # Phase VI: feature regions
    regions = []
    for sink, cells in sink_basins.items():
        region = make_region_from_cells(cells, sink=sink)
        regions.append(region)

    # Phase VII: boundaries and mouths
    features = []
    for region in regions:
        boundary_faces = compute_boundary_faces(region, graph)
        exterior_faces = compute_exterior_boundary_faces(region, exterior_region, graph)
        mouths = connected_components_of_faces(exterior_faces)

        feature_type = classify_region_from_mouths(region, mouths, params)
        metrics = compute_region_metrics(region, boundary_faces, mouths, params)

        feature = build_feature(
            region=region,
            feature_type=feature_type,
            boundary_faces=boundary_faces,
            mouths=mouths,
            metrics=metrics,
            params=params,
        )
        features.append(feature)

    return Topography(
        empty_tetrahedra=empty_tetrahedra,
        graph=graph,
        flow=flow,
        sinks=sinks,
        exterior_region=exterior_region,
        features=features,
        metadata=collect_metadata(params),
    )
```

---

# 14. Puntos donde conviene dejar flexibilidad

## 14.1 Política de clasificación alpha
Porque depende de backend y tolerancia.

## 14.2 Política de inside/outside del power center
Porque hay degeneraciones y casos frontera.

## 14.3 Política de mouths
Porque dos mouths pequeñas muy cercanas pueden querer fusionarse o no.

## 14.4 Política de channels
Porque una depresión muy abierta puede no ser deseable como “channel” funcional.

La clave no es evitar esta flexibilidad, sino **hacerla explícita**.

---

# 15. Qué hereda de CAST y qué excede a CAST

## 15.1 Herencia
TopoMT hereda de CAST:
- uso del espacio vacío discretizado,
- tetraedros vacíos,
- discrete flow,
- sinks y cuencas,
- mouths,
- pockets y cavities.

## 15.2 Extensión
TopoMT va más allá al:
- convertir regiones y fronteras en features explícitas,
- separar shape type y feature type,
- preparar jerarquías y subfeatures,
- admitir channels, necks y interfaces,
- preparar análisis dinámico.

---

# 16. Recomendación de implementación por etapas

## Etapa 1
Implementar el core estático mínimo:
- empty tetrahedra,
- graph,
- flow,
- sinks,
- exterior,
- pocket/cavity/channel,
- mouths.

## Etapa 2
Añadir métricas más ricas:
- depth,
- neck,
- subpockets,
- lining atoms.

## Etapa 3
Añadir dinámica:
- tracking entre frames,
- events,
- persistent features.

---

# 17. Idea fuerte para paper

Una formulación compacta del mensaje central podría ser:

> TopoMT models molecular topography by decomposing the empty space around a molecular solid into flow-structured volumetric regions and explicit boundary features, enabling a unified representation of pockets, cavities, channels, mouths, and their higher-level semantic relations.

---

# 18. Resumen ejecutivo

La versión final del core algorithm de TopoMT consiste en:

1. construir la triangulación regular y el alpha complex;
2. extraer los tetraedros vacíos;
3. construir el grafo del vacío;
4. definir un discrete flow sobre ese grafo;
5. trazar cuencas hacia sinks o hacia el exterior;
6. construir regiones volumétricas;
7. identificar fronteras y mouths;
8. clasificar semánticamente las regiones como pockets, cavities o channels;
9. calcular métricas y relaciones para producir una topografía explícita y extensible.

Ésta es, probablemente, la pieza que convierte el proyecto desde una buena intuición geométrica en un framework algorítmico completo.
