# TopoMT: extensión fina a dinámica y trayectorias de dinámica molecular

## Propósito

Este documento propone una formulación detallada para extender TopoMT desde un análisis estático de una estructura a una **topografía dinámica** definida sobre una trayectoria molecular.

La idea central es que TopoMT no sólo detecte features en un frame aislado, sino que pueda representar:

- su persistencia,
- su transformación,
- su aparición y desaparición,
- su apertura o cierre,
- y sus relaciones causales con la dinámica conformacional.

En otras palabras, pasar de:

\[
\text{Topography}
\]

a:

\[
\text{Topography}(t)
\]

y, finalmente, a una teoría de **trayectorias de features**.

---

# 1. Modelo temporal básico

Sea una trayectoria molecular discretizada en frames:

\[
t_0, t_1, \dots, t_n
\]

Para cada frame \(t_k\), construimos una topografía:

\[
\mathcal{T}_k = \mathcal{T}(t_k)
\]

donde \(\mathcal{T}_k\) contiene un conjunto de features:

\[
\mathcal{F}_k = \{F_k^{(1)}, F_k^{(2)}, \dots \}
\]

Cada feature puede ser:
- pocket,
- cavity,
- channel,
- mouth,
- neck,
- subpocket,
- etc.

---

# 2. Problema central de la dinámica

En estático, basta con detectar features.
En dinámica, hay que resolver además:

1. **identidad temporal**,  
2. **correspondencia entre frames**,  
3. **eventos topológicos**,  
4. **métricas temporales**,  
5. **interpretación funcional**.

La pregunta fundamental ya no es sólo:

> “¿existe un pocket?”

sino:

> “¿es el mismo pocket que en el frame anterior?”  
> “¿se ha dividido?”  
> “¿se abrió una mouth?”  
> “¿es persistente o transitorio?”  
> “¿es un pocket críptico?”

---

# 3. Representación de features dinámicas

## 3.1 Trayectoria de feature

Definimos una **feature trajectory** como una secuencia temporal de features enlazadas entre frames:

\[
\Gamma = (F_{k_1}, F_{k_2}, \dots, F_{k_m})
\]

tal que cada par consecutivo satisface un criterio de correspondencia temporal.

## 3.2 DynamicFeature

Conceptualmente:

```python
class DynamicFeature:
    dynamic_feature_id: str
    feature_type: str
    instances_by_frame: dict[int, str]   # frame -> feature_id
    events: list
    metrics_time_series: dict
    metadata: dict
```

Esto permite separar:
- la feature instantánea en un frame,
- de su identidad dinámica global.

---

# 4. Correspondencia temporal entre frames

## 4.1 Objetivo
Dadas dos topografías consecutivas \(\mathcal{T}_k\) y \(\mathcal{T}_{k+1}\), queremos construir una aplicación parcial:

\[
\Phi_k : \mathcal{F}_k \to \mathcal{F}_{k+1}
\]

o, más generalmente, una relación ponderada de correspondencias.

## 4.2 Dificultad
Las features pueden:
- desplazarse,
- deformarse,
- cambiar de volumen,
- fusionarse,
- dividirse,
- abrir o cerrar accesos.

Por eso no basta un criterio geométrico único.

---

# 5. Score de matching

## 5.1 Propuesta general
Definimos un score compuesto:

\[
S(F, G) = w_1 S_{\text{overlap}} + w_2 S_{\text{centroid}} + w_3 S_{\text{lining}} + w_4 S_{\text{mouth}} + w_5 S_{\text{shape}}
\]

donde \(F \in \mathcal{F}_k\) y \(G \in \mathcal{F}_{k+1}\).

## 5.2 Componentes sugeridas

### a) Solapamiento espacial
Mide cuánto se superponen las regiones geométricas.

Puede definirse por:
- intersección de celdas,
- proximidad de tetraedros,
- solapamiento volumétrico aproximado.

Ejemplo:

\[
S_{\text{overlap}}(F,G) = \frac{|C(F)\cap C(G)|}{|C(F)\cup C(G)|}
\]

o una variante adaptada si las celdas no son comparables frame a frame.

### b) Proximidad de centroides
Sea \(x_F, x_G\) el centroide de cada feature.

\[
S_{\text{centroid}} = \exp\left(-\frac{\|x_F - x_G\|^2}{\sigma^2}\right)
\]

### c) Similitud de lining atoms / residues
Muy útil cuando el pocket se deforma pero sigue asociado al mismo entorno químico.

Ejemplo:
- índice de Jaccard sobre residuos lining,
- o score ponderado por proximidad.

### d) Similitud de mouths
Compara:
- número de mouths,
- área total de apertura,
- posición de las mouths,
- existencia de un neck persistente.

### e) Similitud de forma
Puede incluir:
- volumen,
- área,
- profundidad,
- elongación,
- descriptors más ricos.

---

# 6. Estrategia de matching

## 6.1 Matching local codicioso
Para cada feature en \(k\):
- buscar candidatas en \(k+1\),
- elegir el score máximo si supera umbral.

Es simple, pero puede fallar en fusiones/escisiones complejas.

## 6.2 Matching global
Construir una matriz de scores y resolver un matching bipartito máximo con restricciones.

Esto es mejor para:
- trayectorias densas,
- muchas features competidoras.

## 6.3 Recomendación pragmática
Empezar con:

1. filtro de candidatas por distancia,
2. score compuesto,
3. matching bipartito simple,
4. reglas especiales para merge/split.

---

# 7. Eventos topológicos

## 7.1 Birth
Una feature en \(k+1\) no tiene precursor claro en \(k\).

## 7.2 Death
Una feature en \(k\) no tiene sucesor claro en \(k+1\).

## 7.3 Continuation
Una feature se corresponde de forma dominante con una feature posterior.

## 7.4 Split
Una feature \(F\) en \(k\) da lugar a varias features en \(k+1\).

Formalmente, si existen \(G_1, G_2, \dots\) con scores altos y partición razonable.

## 7.5 Merge
Varias features en \(k\) se corresponden con una sola en \(k+1\).

## 7.6 OpenMouth / CloseMouth
Eventos donde:
- aparece una mouth nueva,
- desaparece una mouth previa,
- una cavity pasa a pocket,
- un pocket pasa a cavity,
- un pocket pasa a channel.

## 7.7 Gating
Cambio reversible entre estados de acceso:
- abierto,
- parcialmente abierto,
- cerrado.

---

# 8. Estados dinámicos de alto nivel

## 8.1 PersistentPocket
Pocket presente durante una fracción significativa de la trayectoria.

## 8.2 TransientPocket
Pocket breve o esporádico.

## 8.3 CrypticPocket
Pocket ausente o casi ausente en un estado de referencia, pero que emerge repetidamente o funcionalmente bajo ciertas conformaciones.

## 8.4 BreathingCavity
Cavidad cuyo volumen oscila significativamente.

## 8.5 GatedChannel
Canal cuya conectividad exterior varía en el tiempo.

Estas categorías pueden definirse más adelante como etiquetas derivadas, no necesariamente como clases base del núcleo.

---

# 9. Métricas temporales

## 9.1 Lifetime
Número de frames consecutivos durante los que una feature dinámica existe.

## 9.2 Persistence ratio
Fracción de frames del intervalo estudiado en los que la feature aparece.

\[
P = \frac{\#\text{frames con feature}}{\#\text{frames totales}}
\]

## 9.3 Volume fluctuation
Varianza, desviación estándar o rango del volumen a lo largo del tiempo.

## 9.4 Mouth openness
Serie temporal del área total de mouths o del cuello mínimo.

## 9.5 Accessibility
Fracción temporal en la que una concavity está conectada al exterior.

## 9.6 Topological stability
Mide cuán estable es la identidad topológica:
- número de merges/splits,
- cambios en número de mouths,
- cambios de tipo pocket/cavity/channel.

---

# 10. Grafo temporal de topografía

Una forma potente de representar la dinámica es mediante un **temporal feature graph**:

- nodos: instancias de feature en frames concretos,
- aristas: correspondencias temporales,
- etiquetas de arista: continuation, split, merge, etc.

Formalmente:

\[
G_T = (V_T, E_T)
\]

donde:
- \(V_T = \bigcup_k \mathcal{F}_k\)
- \(E_T\) contiene las correspondencias temporales.

Este grafo permite:
- reconstruir trayectorias,
- detectar eventos,
- resumir estabilidad.

---

# 11. Pipeline dinámico recomendado

## 11.1 Por frame
Para cada frame:
1. construir topografía estática,
2. detectar features,
3. calcular métricas locales,
4. almacenar descriptors útiles para matching.

## 11.2 Entre pares de frames
5. generar candidatas,
6. calcular matriz de scores,
7. resolver matching,
8. detectar births/deaths/merges/splits,
9. actualizar `DynamicFeature`.

## 11.3 Postproceso global
10. resumir trayectorias dinámicas,
11. calcular métricas temporales,
12. clasificar persistent/transient/cryptic/gated.

---

# 12. Relación con muestreo temporal

## 12.1 Dependencia del stride
Si el stride entre frames es grande:
- se pueden perder openings transitorios,
- merges/splits pueden parecer saltos bruscos.

## 12.2 Recomendación
Guardar en metadata:
- timestep físico,
- stride,
- ventana de suavizado si la hay.

La interpretación de lifetime y gating depende críticamente de esto.

---

# 13. Suavizado temporal

En dinámica real puede haber flickering espurio:
- aperturas que duran 1 frame,
- micro-splits no significativos,
- fluctuaciones de volumen irrelevantes.

Conviene permitir un postproceso opcional:

- filtrar eventos de un solo frame,
- exigir persistencia mínima,
- usar ventanas de mayoría temporal.

Pero este suavizado debe ser **opcional y explícito**, nunca oculto.

---

# 14. Qué hace a TopoMT realmente nuevo aquí

CAST es esencialmente estático.
TopoMT puede introducir algo mucho más potente:

> una representación explícita de la evolución topológica de cavities, pockets, mouths y channels a lo largo del tiempo.

Esto abre la puerta a estudiar formalmente:

- pockets crípticos,
- gating,
- accesibilidad transitoria,
- rutas dinámicas de difusión,
- reorganización de subpockets,
- acoplamiento topografía-función.

---

# 15. Integración con la semántica estática

La dinámica no debe inventar un modelo aparte.
Debe extender el modelo de `Feature` ya existente.

Por ejemplo:

- `Pocket` en un frame → instancia estática
- `DynamicFeature` → entidad temporal que referencia muchas instancias `Pocket`

Esto evita duplicación conceptual y mantiene limpieza arquitectónica.

---

# 16. Ejemplo conceptual

```python
DynamicFeature(
    dynamic_feature_id="dyn_pocket_7",
    feature_type="pocket",
    instances_by_frame={
        0: "pocket_3",
        1: "pocket_2",
        2: "pocket_2",
        3: "pocket_5",
    },
    events=[
        {"frame": 0, "type": "birth"},
        {"frame": 3, "type": "open_mouth"},
    ],
    metrics_time_series={
        "volume": [210.1, 225.4, 219.7, 248.9],
        "n_mouths": [0, 1, 1, 2],
    },
    metadata={
        "trajectory_id": "traj_A",
        "stride": 10,
        "time_unit": "ps",
    },
)
```

---

# 17. Estrategia de desarrollo recomendada

## Etapa 1
Dinámica mínima:
- matching simple frame a frame,
- lifetime,
- persistence,
- volume fluctuation.

## Etapa 2
Eventos:
- birth,
- death,
- merge,
- split,
- mouth opening/closure.

## Etapa 3
Semántica avanzada:
- cryptic pockets,
- gated channels,
- dynamic subpockets,
- correlación con estados funcionales.

---

# 18. Resumen ejecutivo

La versión fina de la extensión dinámica de TopoMT propone:

- construir una topografía por frame;
- enlazar features entre frames mediante un score compuesto;
- representar esa evolución como trayectorias de features y/o un grafo temporal;
- detectar eventos topológicos explícitos;
- calcular métricas temporales interpretables;
- y usar todo ello para estudiar función, accesibilidad y plasticidad conformacional.

Éste puede ser uno de los diferenciadores más fuertes de TopoMT frente a métodos clásicos centrados sólo en la geometría estática.
