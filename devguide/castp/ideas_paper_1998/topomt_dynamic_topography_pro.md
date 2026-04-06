# TopoMT: Dynamic Topography for MD (Detailed)

## 1. Formal Model

Let:
T(t) = Topography at time t

We define a mapping:
Φ: Features(t) → Features(t+1)

---

## 2. Matching Score

For features F_t and G_{t+1}:

S = w1 overlap + w2 centroid_distance + w3 lining_similarity

---

## 3. Overlap Metric

overlap = |cells(F_t ∩ G_{t+1})| / |cells(F_t)|

---

## 4. Event Detection

If:
- no match → death
- new feature → birth
- multiple matches → split
- multiple parents → merge

---

## 5. Temporal Features

Persistent:
- exists > threshold

Transient:
- short-lived

---

## 6. Metrics

- lifetime
- persistence ratio
- volume variance
- mouth openness

---

## 7. Graph Extension

Temporal graph:
nodes = features
edges = temporal mapping

---

## 8. Pipeline

for each frame:
    compute topology

for each pair:
    match features

build temporal graph

analyze events

---

## 9. Applications

- cryptic pockets
- gating
- allosteric transitions

---

## 10. Key Insight

TopoMT extends geometry → topology → time
