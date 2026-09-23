# Novedades / Changelog

La versión publicada se ve en el pie de la web (versión · commit · fecha de build).

## 2.1.0 — 2026-09-23

Arreglos de la revisión formal ([docs/REVISION.md](docs/REVISION.md)) y de la auditoría externa.

- **Garantías honestas**:
  - las redes no serie-paralelo ya no se omiten en silencio (presupuesto de núcleos con cota válida, o «búsqueda parcial» explícita);
  - el resumen indica el alcance de la búsqueda (serie-paralelo, con puentes o cualquier topología);
  - la cota incluye el factor (1 + ε).
- Núcleos no serie-paralelo hasta 8 piezas en «usar todos».
- **Nueva gráfica** «Dónde caen las soluciones respecto al objetivo».
- **Error típico estadístico** en cada solución (errores independientes de las piezas).
- **Entrada de valores**:
  - decimales sin unidad menores que 10⁻³ en faradios;
  - `1,2,3` como lista;
  - `1.5e3pF`.
- **Memoria**: se muestra la memoria WASM usada, el presupuesto se ajusta a la RAM del dispositivo y hay un mensaje claro si se agota.
- **Interfaz**:
  - coma decimal en español;
  - el desplegable de ejemplos conserva la selección;
  - en inventario, las piezas se nombran por su valor.
- Corrección del SPICE exportado en modo inventario.
- **Teoría y métodos** revisada:
  - clase de redes, alcance de la DP;
  - sensibilidad relativa, dispersión estadística;
  - límites del modelo físico y referencias.
- **Tests nuevos**:
  - «el esquema es la red», que incluye el caso del error de dibujo de la v1;
  - fuerza bruta sobre todos los grafos con piezas distintas;
  - regresión de las garantías.

## 2.0.0 — 2026-09-23

Primera versión web (Rust → WebAssembly + Svelte, en GitHub Pages).

- Todas las topologías.
- Modo inventario.
- Verificación exacta.
- Exportaciones.
- Interfaz bilingüe.
