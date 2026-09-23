# Revisión formal de CapAssigner v2

**Fecha:** 23-09-2026 · **Versión revisada:** commit `40f2380` (web publicada en GitHub Pages)
**Alcance:** motor Rust (`crates/capcore`), oráculo e interfaz TypeScript (`src/`), página *Teoría y métodos*, README y documentación.

---

## 0. Resumen ejecutivo

**Veredicto.** Los métodos de resolución son **correctos y completos** dentro de su dominio declarado. Lo respaldan las pruebas existentes y seis diagnósticos independientes nuevos, entre ellos una fuerza bruta sobre *todos* los grafos de dos terminales. La teoría publicada es fiel al estado del arte en lo esencial. Hay que corregir **un fallo crítico en la comunicación de garantías**, tres problemas importantes y varias imprecisiones de redacción.

| Id | Severidad | Hallazgo | Estado |
|---|---|---|---|
| **C1** | 🔴 Crítica | Con 9 piezas distintas, o en inventario con K ≥ 5 y muchos valores, el motor **omite los núcleos no serie-paralelo** por un límite de trabajo. Aun así la web afirma «cota garantizada» o «todas las redes». | Confirmado (D2) |
| A1 | 🟠 Alta | El mensaje «Se han considerado todas las redes posibles» aparece también cuando el usuario eligió *solo serie-paralelo* o *solo puentes*. | Confirmado (código) |
| A2 | 🟠 Alta | Un decimal sin unidad (`0.0000000000052`) se interpreta en la unidad por defecto (pF) → 5,2·10⁻²⁴ F. La v1 lo leía en faradios. | Confirmado (prueba) |
| A3 | 🟡 Media | La cota mostrada omite el factor (1+ε_óptimo) de la demostración. | Confirmado (código); inocuo en la práctica (D3) |
| M1–M9 | 🟢 Baja | Huecos teóricos de la rejilla, parámetro `eps` latente, parser, localización, memoria en móvil, CI… | Ver §4 |
| T1–T8 | 📝 Texto | Imprecisiones en *Teoría y métodos*: definición de la clase de redes, alcance de la DP, sensibilidad, límites del modelo físico, referencias clásicas que faltan. | Ver §3 |

**Qué está bien, con evidencia:**
- El motor genera exactamente el conjunto de valores de todas las redes admisibles:
  - **piezas iguales**: OEIS A048211, A174283, A337517 y A006351;
  - **piezas distintas** (diagnóstico nuevo D1): fuerza bruta sobre todos los multigrafos de hasta 6 aristas, 6086 valores, 0 faltantes y 0 sobrantes;
  - **existencias limitadas**: D5.
- La cota de la poda nunca se violó en 1350 ejecuciones podadas (D3, D3b). Es entre 170 y 250 veces más holgada que el error real.
- La reducción de Kron en coma flotante coincide con la exacta con un error relativo ≤ 6,6·10⁻¹³, incluso con valores que abarcan 8 décadas (D4).
- Las series E48 y E96 coinciden con la tabla IEC 60063.

---

## 1. Metodología

1. **Lectura crítica** del código: `engine.rs`, `cores.rs`, `space.rs`, `laplace.rs`, `api.rs`, `physics.ts`, `verify.ts`, `units.ts` y `form.ts`. También de todas las afirmaciones de la web y del README.
2. **Diagnósticos independientes** en [`crates/capcore/tests/review.rs`](../crates/capcore/tests/review.rs). Cada uno contrasta una afirmación con un cálculo que no comparte la lógica que se prueba:

| Diagnóstico | Qué comprueba | Resultado |
|---|---|---|
| **D1** | Completitud con **piezas distintas**: fuerza bruta de *todos* los multigrafos de dos terminales con n ≤ 6 aristas etiquetadas. Admisibilidad: G + AB 2-conexo. Evaluación con racionales exactos. | Coincidencia exacta. n = 4, 5, 6: 48, 465 y 6086 valores; serie-paralelo sola: 48, 435 y 4886. |
| **D2** | ¿Salta el límite `MAX_CORE_WORK` (20 M evaluaciones por estado) con la configuración real de la web? | **Sí**: usar todos con n = 9 distintas, y en inventario con E12×2 y K = 6, o con E24×2/×4 y K ≥ 5. No salta con n ≤ 8, ni con E12×2 y K = 5. |
| **D3** | La cota de la poda sin núcleos: 300 problemas × 3 límites de memoria, n = 6–8. | 0 violaciones; (encontrado − óptimo)/cota ≤ 0,006. |
| **D3b** | Ídem con todos los núcleos y límites mínimos (4–30 valores por estado). | 0 violaciones; ratio ≤ 0,004. |
| **D4** | Kron en f64 frente a racionales exactos en los 20 núcleos, con valores repartidos en hasta 8 décadas. | Error máximo 6,6·10⁻¹³. |
| **D5** | Existencias limitadas: unión de conjuntos de valores frente a la enumeración de todos los submulticonjuntos (40 cajones aleatorios, K ≤ 5, con puentes). | Coincidencia exacta. |

3. **Sondas** del parser y de las series E: 13 entradas límite y la tabla E48/E96 frente a IEC 60063.
4. **Contraste bibliográfico** de cada afirmación teórica (§3.3).

Reproducir: `cargo test --release --test review -- --nocapture --test-threads=1`. D2 se ejecuta con `-- --ignored`.

---

## 2. Corrección de los métodos

### 2.1 Modelo físico — correcto
El modelo usa condensadores ideales, inicialmente descargados y en régimen cuasiestático, con carga nula en los nodos internos. Así C_eq = Q_A con v_A = 1 y v_B = 0, que es el complemento de Schur de la Laplaciana ponderada (reducción de Kron). Esto equivale a la conductancia efectiva de una red resistiva con G_e = c_e. Las identidades que se usan son correctas y están probadas:
- energía: ½C_eq = ½Σc_eΔv_e²;
- sensibilidad: ∂C_eq/∂c_e = Δv_e²;
- monotonía de Rayleigh;
- homogeneidad de grado 1;
- cotas: (Σ1/c)⁻¹ ≤ C_eq ≤ Σc;
- intervalo de tolerancia [(1−δ)C, (1+δ)C] cuando todas las piezas varían ±δ.

La eliminación sin pivotaje es estable porque la matriz sigue siendo una Laplaciana (una M-matriz diagonalmente dominante), y D4 lo confirma.

### 2.2 DP de valores serie-paralelo — correcta
La recurrencia V(S) = ∪ {a+b, ab/(a+b)} sobre particiones no ordenadas es exacta. Se ha verificado contra:
- la recursión ingenua sobre máscaras (proptest);
- A048211 hasta n = 12 y A006351 hasta n = 7;
- D5 para multiconjuntos con existencias.

Las particiones `l ≤ r` con `j ≥ i` cuando `l == r` no pierden combinaciones.

### 2.3 Redes no serie-paralelo (núcleos SPQR) — correcta y completa
Toda red admisible, es decir, aquella en la que cada pieza está en algún camino simple A–B, cumple que G + AB es 2-conexo. Su árbol SPQR enraizado en AB solo tiene nodos S, P y R. Los esqueletos R son grafos 3-conexos simples, y con ≤ 10 aristas tienen ≤ 6 vértices, porque el grado mínimo 3 obliga a e ≥ 3v/2. Enumerarlos todos con etiquetado canónico y rellenar sus aristas con subredes arbitrarias genera exactamente la clase. Evidencia:
- con piezas iguales, A337517 (todas las redes) coincide hasta n = 9 y A174283 (solo puentes) también;
- con piezas distintas, **D1** coincide con la fuerza bruta sobre todos los grafos.

Esto último es más fuerte que OEIS, porque detectaría asignaciones o permutaciones mal generadas, que con piezas iguales pasarían inadvertidas.

### 2.4 Encuentro en el medio en la raíz — correcto
Para cada `a` del lado pequeño y cada operación, el valor combinado es monótono en `b`. La bisección más el barrido en ambos sentidos, hasta que el error no mejore, encuentra el mejor `b` para cada `a`, así que encuentra el mejor par global. La prueba de propiedad `root_query_matches_materialised` compara el top-K con el del estado materializado, con núcleos incluidos. El empate se ordena ahora de forma total (error y luego valor).

### 2.5 Poda con cota — correcta, con tres matices
La demostración es válida. Serie, paralelo y cualquier núcleo son funciones monótonas y 1-homogéneas, luego no expansivas en la métrica de Thompson (escala logarítmica); véase Gaubert–Gunawardena (2004). Por inducción sobre la profundidad, el óptimo tiene un representante conservado a un factor ≤ e^{(n−1)ε}. D3 y D3b la confirman empíricamente. Matices:
1. **A3.** La cota correcta para el error es ε_opt + (e^{(n−1)ε} − 1)(1 + ε_opt). La web muestra solo e^{(n−1)ε} − 1. La diferencia es de segundo orden, pero el texto dice «ninguna red puede mejorar… en más de X».
2. **M1.** En la ruta rápida por rejilla (`build_grid`), el rango [lo, hi] se calcula a partir de los mínimos y máximos *conservados* de los hijos. Un valor de núcleo apenas por debajo de lo, o por encima de hi, se recorta al primer o al último cubo, y en teoría puede quedar a (ancho del cubo + ancho del hijo) de su representante. D3b no lo manifestó porque la holgada cota lo absorbe, pero conviene cerrarlo: ampliar [lo, hi] en el ε de los hijos o calcular el rango exacto en una primera pasada.
3. **M2.** El parámetro `eps > 0` de la API fusiona valores por encadenamiento entre bloques (`absorb`), así que la cota no sería válida con `eps` grande. La web nunca lo usa (vale 10⁻¹²), pero conviene eliminarlo o implementarlo sobre la rejilla absoluta.

### 2.6 Numérica y exactitud — correcta
- Los valores se normalizan por el objetivo antes de la DP. Dos valores a menos de 10⁻¹² relativo se consideran iguales (`FLOAT_EPS`). Por eso «exhaustivo» significa exhaustivo *hasta 10⁻¹² relativo*, que es irrelevante para el error pero debería decirse.
- Los valores de las piezas vuelven bit a bit gracias a `serde_json/float_roundtrip`.
- El oráculo TS es independiente (eliminación gaussiana con pivotaje y fracciones BigInt construidas desde el texto) y verifica cada solución mostrada.

### 2.7 Inventario — correcto
- **Cantidad ilimitada** (espacio por tamaño): correcto, porque cualquier multiconjunto es admisible.
- **Existencias limitadas** (espacio de multiconjuntos acotados): correcto (D5).
- **Existencias ≥ K**: se trata como ilimitada, que es equivalente.

---

## 3. Fidelidad de la teoría publicada y estado del arte

### 3.1 Correcciones de texto necesarias

| Id | Dónde | Dice | Problema | Debería decir |
|---|---|---|---|---|
| **T1** | Teoría §3 | «Toda red … en la que cada pieza almacena carga queda 2-conexa…» y «las redes con piezas que no almacenan carga no se consideran» | Contradicción: el puente equilibrado *sí* se considera y su pieza central no almacena carga. El criterio es estructural, no depende de los valores. | «…en la que cada pieza está en algún camino simple entre A y B (equivalentemente, G + AB es 2-conexo). Se excluyen las piezas colgantes o en lazo, que nunca conducen carga sean cuales sean los valores.» |
| **T2** | Teoría §4.1 | «el número de redes SP distintas crece como A006351 … mientras que los estados solo son 2ⁿ» | Sobrestima la ganancia. Con piezas distintas y genéricas casi no hay colisiones de valor, y cada estado guarda del orden de A006351(k) valores. La memoria crece como n·A006351(n−1): por eso se poda desde n = 9. | Explicar las ganancias reales: se eliminan representaciones duplicadas (árboles conmutativos o asociativos, que eran el problema de v1), se comparten subresultados, el encuentro en el medio evita el último nivel (≈ A006351(n)) y hay colapso por multiplicidades y por colisiones con valores repetidos o racionales. |
| **T3** | Teoría §2 y ayuda de la tabla | «La pieza con más tensión relativa es la que más influye» | Mezcla sensibilidad absoluta (Δv², por faradio) y relativa. La influencia de un error *porcentual* es la elasticidad w_e = c_eΔv_e²/C_eq, que es justo la columna «Energía». | Distinguirlas y señalar que Σw_e = 1 (teorema de Euler para funciones homogéneas). |
| **T4** | Resumen y Teoría §5 | «Ninguna red puede mejorar el error… en más de X» | Falta el factor (1+ε) (A3) y es **falso cuando se han omitido núcleos (C1)**. | Añadir (1+ε), y separar «cota para serie-paralelo» de «exploración parcial de redes no SP». |
| **T5** | Resumen de resultados | «Se han considerado todas las redes posibles» | Falso si la topología elegida es SP o SP + puentes (A1). | «…todas las redes serie-paralelo» / «…con puentes» / «…todas las redes». |
| **T6** | Teoría §7 | «Encajar A337517 prueba que … no se deja ninguna red» | A337517 solo usa piezas iguales. | Citar además la fuerza bruta con piezas distintas (D1). |
| **T7** | Teoría §2 y §8 | «exhaustiva hasta 8 piezas distintas; completa sobre todas las topologías hasta 9» | Con 9 piezas distintas los núcleos se omiten (C1). | Ajustar a la realidad tras corregir C1. |
| **T8** | Teoría §2 | Tolerancias solo en el peor caso | Omite el modelo estadístico, que es el útil en la práctica. | Añadir: con errores independientes de desviación σ_e, σ_C/C ≈ √(Σ w_e² σ_e²), entre σ/√n y σ. Así la topología *sí* afecta a la dispersión estadística aunque no al peor caso común. |

### 3.2 Límites del modelo físico que la web debería explicar
Son importantes para su uso en laboratorio:
- **Reparto de tensión en continua.** La columna «Tensión» es el reparto capacitivo: el de alterna, o el de la carga inicial desde el estado descargado. En continua y a largo plazo, la tensión entre condensadores en serie la fijan las **resistencias de fuga**, no las capacidades. Por eso en la práctica se añaden resistencias de equilibrado.
- **Dieléctricos no lineales.** Las cerámicas de clase II (X7R, Y5V) pierden gran parte de su capacidad con la polarización continua y la temperatura. El valor nominal no es el efectivo.
- **Parásitos.** Con objetivos del orden del pF (los ejercicios de ejemplo), las capacidades parásitas de pistas y cables (0,1–1 pF) son comparables al error buscado. A alta frecuencia también cuentan ESL y ESR.

### 3.3 Posicionamiento en el estado del arte

| Técnica usada | Fundamento | Valoración |
|---|---|---|
| Conjuntos de valores por número o multiconjunto de piezas | Es el método estándar con el que se calculan A048211 y afines en OEIS; aquí se generaliza a piezas etiquetadas y multiplicidades. | ✔ Estado del arte; la generalización es correcta. |
| Caracterización serie-paralelo y puente | **Duffin (1965)**: una red de dos terminales es SP si y solo si no contiene un puente de Wheatstone embebido. | ✔ Coherente. **Falta citar a Duffin** en la web. |
| Descomposición SPQR con núcleos 3-conexos | Hopcroft–Tarjan (1973), Di Battista–Tamassia (1996). | ✔ Más estructurado que la vía de OEIS A180414/A337517, que enumera grafos (nauty) y calcula resistencias. D1 y las series OEIS lo validan. |
| Encuentro en el medio | Técnica clásica de subset-sum. | ✔ |
| Poda en rejilla logarítmica | Recortado tipo Ibarra–Kim (FPTAS). No expansividad: Gaubert–Gunawardena (2004). | ✔ Correcta. En modo inventario da de hecho un **esquema de aproximación** con ε fijo que podría ofrecerse explícitamente (§6). |
| Reducción de Kron | Kron (1939), Dörfler–Bullo (2013). | ✔ Podría usarse la variante GTH (diagonal = −Σ fuera de la diagonal) para más robustez; D4 muestra que hoy no hace falta. |
| MILP (propuesto en informes externos) | Linealización exacta binaria × continua. | No usado: la DP con núcleos ya es exacta en su dominio. Útil para **restricciones** (coste, tensión nominal) y certificación (§6). |
| Complejidad | — | Abierta. Es plausible que sea NP-difícil («usar todos» contiene casos tipo partición: (ΣA)‖ en serie con (ΣB)‖ = S/4), pero esa reducción no es una demostración, porque otras redes podrían alcanzar el mismo valor. No debe afirmarse sin prueba. |

**Referencias que conviene añadir a la web:**
- R. J. Duffin, «Topology of series-parallel networks», *J. Math. Anal. Appl.* 10 (1965) 303–313. [ScienceDirect](https://www.sciencedirect.com/science/article/pii/0022247X65901253)
- J. Riordan, C. E. Shannon, «The number of two-terminal series-parallel networks», *J. Math. Phys.* 21 (1942) 83–93.
- S. Gaubert, J. Gunawardena, «The Perron–Frobenius theorem for homogeneous, monotone functions», *Trans. AMS* 356 (2004) 4931–4950.
- G. Kron, *Tensor Analysis of Networks*, Wiley, 1939.
- W. K. Grassmann, M. I. Taksar, D. P. Heyman, «Regenerative analysis and steady state distributions for Markov chains», *Oper. Res.* 33 (1985).
- OEIS [A180414](https://oeis.org/A180414) y [A337517](https://oeis.org/A337517): cómo se calculan los recuentos de todas las redes.

---

## 4. Hallazgos de implementación

### C1 — 🔴 Núcleos omitidos presentados como búsqueda con garantía
- **Dónde:** `engine.rs::core_candidates` (activa `cores_skipped` si la estimación de trabajo supera `MAX_CORE_WORK` = 2·10⁷), `api.rs` (`exhaustive = eng.exhaustive()`, `bound_rel` solo con ε), `Results.svelte` (mensaje de «cota garantizada»).
- **Evidencia (D2):** «usar todos» con n = 9 distintas → `cores_skipped = true`. Inventario con E12×2 y K = 6, y con E24×2/E24×4 y K ≥ 5 → `true`. En esos casos las redes no SP de ciertos estados no se exploran, pero la web muestra una cota que no las cubre, y la opción se llama «Todas las redes».
- **Arreglo inmediato:**
  1. Exponer `coresComplete` en `StatsOut`; en esta revisión ya se ha añadido `Engine::cores_skipped()`.
  2. En la web, mostrar «serie-paralelo con cota garantizada; redes no serie-paralelo exploradas parcialmente» y no llamarlo exhaustivo.
  3. Ajustar `topoHint` y la Teoría.
- **Arreglo de fondo:** en lugar de omitir, evaluar los núcleos sobre conjuntos hijos podados más gruesos (la misma cota sigue valiendo) o con encuentro en el medio sobre la última arista del núcleo. Así nunca hay que renunciar a la garantía.
- **Test de regresión:** convertir D2 en una aserción de que `exhaustive == false` implica que el mensaje no dice «todas las redes».

### A1 — 🟠 Mensaje de exhaustividad sin tener en cuenta la topología
`Results.svelte` usa `exhaustiveHint` con independencia de `form.topo`. Hay que parametrizar el texto por la topología y por `coresDropped`.

### A2 — 🟠 Decimal sin unidad
`parseCapacitance('0.0000000000052')` → 5,2·10⁻²⁴ F. Opciones: si un número sin unidad es < 10⁻³, interpretarlo en faradios (compatibilidad con v1) o mostrar un aviso «¿querías decir 5,2 pF?». Test: sonda del parser.

### A3 — 🟡 Factor (1+ε) de la cota
`api.rs::bound_rel` o `Results.svelte`: multiplicar por (1+|ε_mejor|) antes de mostrarla.

### Menores
| Id | Hallazgo | Arreglo |
|---|---|---|
| M1 | Rango [lo, hi] de la rejilla basado en valores conservados (§2.5). | Ampliar el rango con el ε de los hijos. |
| M2 | `eps > 0` fusiona por encadenamiento (§2.5). | Eliminar el parámetro o implementarlo con rejilla absoluta. |
| M3 | Parser: `1,2,3` da error (ambigüedad con la coma decimal); `1e-12pF` no se acepta; `5f` es femto, lo que puede confundir. | Mensaje específico para la coma; aceptar exponente con prefijo; documentar `f`. |
| M4 | La estimación de tiempo y la ETA son heurísticas: los pesos 5^k adelantan el progreso y la estimación no prevé C1. | Calibrar con mediciones en navegador; progreso por trabajo real (candidatos generados). |
| M5 | En español se muestran decimales con punto («1.972 %», «9.4 s»). | `Intl.NumberFormat` según el idioma. |
| M6 | En inventario, el detalle nombra las piezas C1…Cn mientras la tabla usa valores. | Nombre por valor también en el detalle. |
| M7 | Memoria: presupuesto fijo de 6 M valores (unos 150–250 MB). Puede agotar la memoria en móviles. | Ajustar con `navigator.deviceMemory` y dar un mensaje claro de falta de memoria. |
| M8 | CI: acciones con Node 20 (obsoleto); Rust, wasm-pack y Node sin fijar; los 7 tests de `legacy/` que ya fallaban no se ejecutan. | Actualizar las acciones; `rust-toolchain.toml`, `.nvmrc` y versión de wasm-pack fijadas; marcar los tests de legacy como `xfail` o retirarlos. |
| M9 | Rendimiento: los núcleos se evalúan sin cociente por automorfismos (el puente tiene 4 automorfismos que fijan {A, B}). | Enumerar órbitas: acelera ×2–8 y reduce C1. |

---

## 5. Tests

**Añadidos en esta revisión** (`crates/capcore/tests/review.rs`, unos 45 s en release): D1, D3, D3b, D4 y D5 como tests; D2 como diagnóstico `#[ignore]`.

**Pendientes, por prioridad:**
1. Regresión de C1: estadísticas `coresComplete` y texto de la interfaz coherente con ellas.
2. Mensaje del resumen según la topología (A1): e2e.
3. Parser: decimales sin unidad, coma ambigua y exponente con prefijo (A2, M3).
4. Propiedades de la tabla de reparto: Σ energía = 1, Σ carga en los nodos = 0 y la fórmula estadística σ_C (T8).
5. D1 ampliado a n = 7 (multigrafos de 7 aristas y hasta 8 vértices) como test nocturno.
6. Serie E96 frente a la tabla IEC (hoy verificada solo con una sonda).
7. e2e en Firefox y WebKit (workers de módulo y WASM), accesibilidad (axe), regresión visual de esquemas y *fuzzing* del hash de la URL.

---

## 6. Plan de acción

**Ahora (antes de difundir la herramienta):** C1 (al menos el arreglo de mensajes), A1, A2, A3; correcciones de texto T1–T7; tests 1–3 de §5.

**Corto plazo:** M1–M8; tolerancia estadística (T8) en la tabla de reparto; sección «Límites del modelo físico» (§3.2); referencias de §3.3.

**Líneas futuras:**
- **Núcleos sin omisiones** (arreglo de fondo de C1) y cociente por automorfismos (M9).
- **Modo exacto certificado**: el motor ya es genérico sobre racionales (`Q`); se puede exponer para n pequeño con detección de desbordamiento y paso a BigInt.
- **Esquema de aproximación explícito**: elegir ε a partir del «error aceptable» del usuario, para que la búsqueda sea más rápida y la garantía se exprese en sus términos.
- **Restricciones de diseño con MILP** (HiGHS en un worker): coste, **tensión nominal** de cada pieza (con el modelo de fugas de §3.2) y número de nodos.
- **Más de 12 piezas**: ALNS con reparación exacta por la DP, guiada por la elasticidad w_e.
- **Robustez**: tolerancias distintas por pieza (basta con los dos extremos), Monte Carlo y frente de Pareto error/piezas/coste.
- **Paralelismo**: hilos WASM con `coi-serviceworker` en GitHub Pages, o varios workers.
- **Núcleos de más de 10 aristas** (grafos 3-conexos con 7 vértices) para completitud con más de 9 piezas.
- **Benchmark abierto** con objetivos racionales exactos, medida de la brecha SP / no SP y estudio de la complejidad.
- **Resistencias e inductancias**: misma matemática, intercambiando el papel de serie y paralelo.
