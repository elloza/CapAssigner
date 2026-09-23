<script lang="ts">
  import { onMount } from 'svelte';
  import katex from 'katex';
  import { i18n } from '../lib/i18n.svelte';
  import { layout, vertexPositions } from '../lib/render/layout';
  import { toSvg } from '../lib/render/svg';
  import type { Core, Tree } from '../lib/types';

  const m = (s: string, display = false) => katex.renderToString(s, { throwOnError: false, displayMode: display });

  let cores: Core[] = $state([]);
  onMount(async () => {
    const mod = await import('../wasm/pkg/capcore.js');
    await mod.default();
    cores = JSON.parse(mod.cores(9)) as Core[];
  });

  const leaves = (core: Core): Tree => ({ t: 'core', core: core.id, c: core.edges.map((_, k) => ({ t: 'leaf', k })) });

  /** Bridge example {1,2,3,4,5} pF: A–u 1, A–v 3, B–u 2, B–v 4, u–v 5. */
  const bridgeSvg = $derived.by(() => {
    const core = cores.find((c) => c.edges.length === 5);
    if (!core) return '';
    const fromA = core.edges.filter(([x, y]) => x === 0 || y === 0).map(([x, y]) => (x === 0 ? y : x));
    const [u, v] = fromA as [number, number];
    const value = core.edges.map(([x, y]) => {
      const s = new Set([x, y]);
      if (s.has(0)) return s.has(u) ? 1 : 3;
      if (s.has(1)) return s.has(u) ? 2 : 4;
      return 5;
    });
    const d = layout(leaves(core), [core]);
    return toSvg(d.main, (k) => ({ name: `C${value[k]}`, value: `${value[k]} pF` }));
  });

  /** A core drawn as a bare graph: each edge stands for a capacitor or a sub-network. */
  function coreGraph(core: Core): string {
    const p = vertexPositions(core).map(([x, y]) => [12 + x * 136, 10 + y * 80] as const);
    const edges = core.edges
      .map(([u, v]) => `<line x1="${p[u]![0]}" y1="${p[u]![1]}" x2="${p[v]![0]}" y2="${p[v]![1]}"/>`)
      .join('');
    const nodes = p
      .map(([x, y], i) => `<circle cx="${x}" cy="${y}" r="${i < 2 ? 4.5 : 3}" class="${i < 2 ? 'term' : ''}"/>`)
      .join('');
    const labels = `<text x="${p[0]![0]}" y="${p[0]![1] - 8}">A</text><text x="${p[1]![0]}" y="${p[1]![1] - 8}">B</text>`;
    return `<svg viewBox="0 0 160 100" width="160" height="100" role="img">${edges}${nodes}${labels}</svg>`;
  }

  const gallery = $derived(cores.map((core) => ({ core, svg: coreGraph(core) })));

  const oeis = [
    { id: 'A048211', es: 'valores serie-paralelo con n piezas iguales', en: 'series-parallel values from n equal parts', v: '1, 2, 4, 9, 22, 53, 131, 337, 869, 2213, 5691, 14517' },
    { id: 'A174283', es: 'serie-paralelo + puentes', en: 'series-parallel + bridges', v: '1, 2, 4, 9, 23, 57, 151, 415, 1157' },
    { id: 'A337517', es: 'todas las redes de dos terminales', en: 'all two-terminal networks', v: '1, 2, 4, 9, 23, 57, 151, 427, 1263' },
    { id: 'A006351', es: 'redes serie-paralelo con n piezas distintas', en: 'series-parallel networks of n distinct parts', v: '1, 2, 8, 52, 472, 5504, 78416' },
  ];

  const perf = [
    { n: '≤ 6', sp: '< 0,1 s', all: '< 0,1 s', g: 'exhaustiva' },
    { n: '7', sp: '≈ 0,1 s', all: '≈ 0,1 s', g: 'exhaustiva' },
    { n: '8', sp: '≈ 0,4 s', all: '≈ 1,5 s', g: 'exhaustiva' },
    { n: '9', sp: '≈ 6 s', all: '—', g: 'cota ≤ 0,05 %' },
    { n: '10', sp: '≈ 5 s', all: '—', g: 'cota ≤ 0,3 %' },
    { n: '12', sp: '≈ 50 s', all: '—', g: 'cota ≤ 5 %' },
  ];

  const toc = $derived(
    i18n.lang === 'es'
      ? ['Qué resuelve', 'Modelo físico', 'Qué redes existen', 'Cómo busca', 'Garantías', 'Verificación', 'Validación', 'Límites y rendimiento', 'Líneas futuras', 'Referencias']
      : ['What it solves', 'Physical model', 'Which networks exist', 'How it searches', 'Guarantees', 'Verification', 'Validation', 'Limits and performance', 'Future work', 'References'],
  );
</script>

<article class="theory">
  <nav class="toc" aria-label="toc">
    {#each toc as title, i (i)}<a href={`#s${i + 1}`}>{i + 1}. {title}</a>{/each}
  </nav>

  {#if i18n.lang === 'es'}
    <h2 id="s1">1. Qué resuelve</h2>
    <p>
      Dados unos condensadores y una capacidad objetivo {@html m('C^\\ast')}, CapAssigner busca las redes entre dos terminales A y B
      cuya capacidad equivalente {@html m('C_{eq}')} se acerca más a {@html m('C^\\ast')}. Ordena las soluciones por el error relativo
      {@html m('\\varepsilon = |C_{eq}-C^\\ast|/C^\\ast')}; a igualdad de valor, prefiere la red con menos piezas. Cada valor distinto aparece
      una sola vez en la lista, con una red que lo produce.
    </p>
    <ul>
      <li><b>Usar todos</b>: cada condensador de la lista se usa exactamente una vez. Es el ejercicio clásico de clase (hasta 12 piezas).</li>
      <li>
        <b>Inventario</b>: se eligen entre 1 y K piezas (K ≤ 6). Pueden salir de una serie normalizada E3–E96 en las décadas elegidas, con
        cantidad ilimitada, o de «mi cajón», una lista con existencias como <code>10pF×2 4.7pF×3</code>.
      </li>
    </ul>
    <p>
      El <em>error aceptable</em> solo sirve para marcar en verde las soluciones que lo cumplen. La <em>tolerancia de las piezas</em> se usa
      para calcular el intervalo en el que puede quedar {@html m('C_{eq}')} con componentes reales.
    </p>

    <h2 id="s2">2. Modelo físico</h2>
    <p>
      Se consideran condensadores ideales, inicialmente descargados, en régimen cuasiestático. Para dos elementos, en paralelo las capacidades se
      suman y en serie se suman sus inversas (las elastancias):
    </p>
    {@html m('C_\\parallel = C_1 + C_2, \\qquad \\frac{1}{C_{\\text{serie}}} = \\frac{1}{C_1} + \\frac{1}{C_2}', true)}
    <p>
      Para una red cualquiera se usa análisis nodal. Sea {@html m('L = B\\,\\mathrm{diag}(c)\\,B^{\\mathsf T}')} la Laplaciana del grafo
      ponderada por las capacidades. Se aplica 1 V entre A y B ({@html m('v_A = 1,\\ v_B = 0')}). En cada nodo interno la carga neta es nula
      (ley de Kirchhoff para la carga), lo que da un sistema lineal para los potenciales internos:
    </p>
    {@html m('L_{II}\\, v_I = -L_{IA}, \\qquad C_{eq} = Q_A = \\sum_{j \\sim A} c_{Aj}\\,(1 - v_j).', true)}
    <p>
      Equivalentemente, {@html m('C_{eq}')} es el complemento de Schur de la Laplaciana sobre los terminales (reducción de Kron): al eliminar los
      nodos internos queda una Laplaciana 2×2 cuyo elemento fuera de la diagonal es {@html m('-C_{eq}')}.
    </p>
    {@html m('L_{\\text{eff}} = L_{BB} - L_{BI}\\,L_{II}^{-1}\\,L_{IB} = \\begin{pmatrix} C_{eq} & -C_{eq} \\\\ -C_{eq} & C_{eq}\\end{pmatrix}', true)}
    <p>Es la misma matemática que la conductancia efectiva de una red de resistencias con {@html m('G_e = c_e')}. De ella se deducen las propiedades que usa la aplicación:</p>
    <ul>
      <li><b>Energía</b>: {@html m('\\tfrac12 C_{eq} V^2 = \\sum_e \\tfrac12 c_e\\, \\Delta v_e^2')}. La tabla «Piezas y reparto» muestra la tensión, la carga y la energía de cada pieza.</li>
      <li>
        <b>Sensibilidad</b>: {@html m('\\partial C_{eq}/\\partial c_e = \\Delta v_e^2')} es la sensibilidad absoluta, por faradio. Para errores
        <em>porcentuales</em> importa la sensibilidad relativa o elasticidad {@html m('w_e = \\frac{c_e}{C_{eq}}\\frac{\\partial C_{eq}}{\\partial c_e} = \\frac{c_e\\,\\Delta v_e^2}{C_{eq}}')},
        que es la fracción de energía de la pieza (columna «Energía»). Por el teorema de Euler para funciones homogéneas, {@html m('\\sum_e w_e = 1')}. Una pieza
        sin tensión (puente equilibrado) no influye.
      </li>
      <li><b>Monotonía</b> (Rayleigh): aumentar cualquier {@html m('c_e')} nunca disminuye {@html m('C_{eq}')}. <b>Homogeneidad</b>: {@html m('C_{eq}(k\\,c) = k\\,C_{eq}(c)')}.</li>
      <li><b>Cotas</b>: {@html m('\\big(\\sum_e 1/c_e\\big)^{-1} \\le C_{eq} \\le \\sum_e c_e')}.</li>
      <li>
        <b>Tolerancias</b>: si cada pieza puede variar ±δ, por monotonía y homogeneidad {@html m('C_{eq} \\in [(1-\\delta)\\,C_{eq},\\,(1+\\delta)\\,C_{eq}]')}.
        Ninguna topología reduce ese peor caso común de escala.
      </li>
      <li>
        <b>Dispersión estadística</b>: si los errores de las piezas son independientes, con desviación relativa {@html m('\\sigma')}, a primer orden
        {@html m('\\sigma_{C}/C_{eq} \\approx \\sigma\\,\\sqrt{\\textstyle\\sum_e w_e^2}')}, que está entre {@html m('\\sigma/\\sqrt n')} (reparto uniforme) y
        {@html m('\\sigma')}. Aquí la topología <em>sí</em> importa: repartir la energía entre muchas piezas promedia sus errores. Se muestra en cada solución.
      </li>
    </ul>
    <h3>Límites del modelo</h3>
    <ul>
      <li>
        <b>Tensión en continua</b>: la columna «Tensión» es el reparto capacitivo, válido en alterna o al cargar desde el estado descargado. En continua,
        a largo plazo, la tensión entre condensadores en serie la fijan sus <em>resistencias de fuga</em>; por eso se añaden resistencias de equilibrado.
      </li>
      <li><b>Dieléctricos</b>: las cerámicas de clase II (X7R, Y5V…) pierden buena parte de su capacidad con la tensión continua aplicada y con la temperatura.</li>
      <li>
        <b>Parásitos</b>: con objetivos de pocos pF, las capacidades parásitas de pistas y cables (0,1–1 pF) son del orden del error buscado. A alta
        frecuencia cuentan también la inductancia y la resistencia serie (ESL, ESR).
      </li>
    </ul>

    <h2 id="s3">3. Qué redes existen</h2>
    <p>
      Una red <b>serie-paralelo</b> (SP) se construye combinando subredes en serie o en paralelo. Tiene nodos internos, pero siempre se puede
      reducir paso a paso con las dos fórmulas anteriores. No todas las redes son así. La más pequeña que no se puede reducir es el
      <b>puente de Wheatstone</b>: cinco piezas, con una de ellas entre los dos nodos centrales. De hecho, Duffin (1965) demostró que una red de dos
      terminales es serie-paralelo si y solo si no contiene un puente de Wheatstone embebido.
    </p>
    <figure class="fig">
      <div class="svg">{@html bridgeSvg}</div>
      <figcaption>
        Con {@html m('\\{1,2,3,4,5\\}\\,\\text{pF}')} este puente da exactamente {@html m('C_{eq} = 170/71\\ \\text{pF} \\approx 2{,}3944\\ \\text{pF}')}. La
        mejor red SP con las mismas piezas da {@html m('43/18\\ \\text{pF}')}, un 0,229 % por debajo: esta es la «brecha SP». Con cinco piezas
        iguales, el puente equilibrado da exactamente {@html m('C')}, algo imposible en SP.
      </figcaption>
    </figure>
    <p>
      Para no dejarse ninguna red, CapAssigner usa la <b>descomposición SPQR</b>. Toda red de dos terminales en la que cada pieza está en algún
      camino simple entre A y B (una condición estructural, que no depende de los valores) queda 2-conexa al añadirle una arista virtual A–B. Esa red se descompone de forma única en nodos de tres tipos: <em>serie</em>,
      <em>paralelo</em> y <em>rígido</em>. Un nodo rígido es un grafo 3-conexo cuyas aristas se sustituyen por subredes de dos terminales.
      Por tanto, basta conocer los grafos 3-conexos pequeños («núcleos»). La aplicación los genera por fuerza bruta con etiquetado canónico:
      todos los de hasta 10 aristas, que tienen como mucho 6 vértices (K₄, la rueda W₄, K₅−e, K₅, el prisma, K₃,₃…). Después quita la arista
      A–B. Con ellos, la recurrencia cubre <b>todas las redes posibles de hasta 9 piezas</b>. En la web se usan hasta 8 piezas en «usar todos»: con 9
      piezas distintas hay millones de formas de repartirlas entre las aristas de los núcleos.
    </p>
    {#if gallery.length}
      <div class="gallery">
        {#each gallery as g (g.core.id)}
          <figure>
            <div class="svg small">{@html g.svg}</div>
            <figcaption>{g.core.edges.length} aristas · {g.core.nv} nodos</figcaption>
          </figure>
        {/each}
      </div>
      <p class="muted small">
        Catálogo generado por el propio motor: {gallery.length} núcleos (A y B son los terminales). En cada arista puede ir un condensador o cualquier subred.
      </p>
    {/if}
    <p>
      Se excluyen las piezas que no están en ningún camino entre A y B (colgando de un solo nodo o en un lazo cerrado): nunca conducen carga, sean
      cuales sean los valores, así que su red equivale a una más pequeña, y en «usar todos» serían trampas. Sí se incluyen redes en las que una
      pieza no conduce solo por casualidad de valores, como el puente equilibrado.
    </p>

    <h2 id="s4">4. Cómo busca</h2>
    <h3>4.1 Estados y conjuntos de valores</h3>
    <p>
      Las piezas de igual valor son intercambiables y forman una <em>clase</em>. Un <em>estado</em> {@html m('S')} es un multiconjunto de piezas,
      es decir, cuántas de cada clase se usan. Con {@html m('\\{3,2,3,1\\}\\,\\text{pF}')} hay tres clases (3 pF ×2, 2 pF, 1 pF) y
      {@html m('3\\cdot2\\cdot2-1 = 11')} estados en lugar de {@html m('2^4-1 = 15')} subconjuntos. Para cada estado se guarda el conjunto ordenado
      {@html m('V(S)')} de capacidades <em>distintas</em> alcanzables con exactamente esas piezas, cada una con un puntero a una red que la produce:
    </p>
    {@html m('V(S) = \\bigcup_{S = L \\uplus R} \\big\\{\\, a + b,\\ \\tfrac{ab}{a+b} \\;:\\; a \\in V(L),\\ b \\in V(R) \\,\\big\\} \\;\\cup\\; \\bigcup_{\\text{núcleos } \\mathcal R} \\big\\{\\, C_{eq}^{\\mathcal R}(x_1,\\dots,x_m) : x_i \\in V(S_i),\\ S = S_1 \\uplus \\dots \\uplus S_m \\big\\}', true)}
    <p>
      Los estados se construyen de menor a mayor tamaño. Dos redes con el mismo valor se funden al generarse, así que nunca se enumeran árboles
      repetidos, como los árboles equivalentes por conmutatividad y asociatividad que enumeraba la v1. Además, cada subresultado se comparte entre
      todos los estados que lo usan, y con valores repetidos o racionales muchas redes coinciden en valor y se funden. Con piezas distintas y
      genéricas casi no hay coincidencias: el conjunto de un estado de {@html m('k')} piezas tiene del orden de tantos valores como redes SP distintas
      (1, 2, 8, 52, 472, 5504, 78416…, OEIS A006351). Por eso la memoria crece rápido y a partir de unas 9 piezas hay que podar (§5). El valor de un
      núcleo con sus aristas rellenas se calcula por reducción de Kron sobre como mucho 6 nodos.
    </p>
    <h3>4.2 Encuentro en el medio en la raíz</h3>
    <p>
      El estado completo (todas las piezas) no se llega a construir. Para cada partición {@html m('L \\uplus R')} y cada {@html m('a \\in V(L)')}, se
      despeja el valor exacto que haría falta en el otro lado ({@html m('b^\\ast = C^\\ast - a')} en paralelo, {@html m('b^\\ast = aC^\\ast/(a - C^\\ast)')}
      en serie). Ese valor se busca por bisección en {@html m('V(R)')} y se exploran sus vecinos mientras puedan entrar entre los mejores. Los núcleos
      de la raíz se evalúan directamente.
    </p>
    <h3>4.3 Modo inventario</h3>
    <p>
      Con cantidad ilimitada, el estado es solo el número de piezas {@html m('k')}: {@html m('V(k)')} combina {@html m('V(i)')} y {@html m('V(k-i)')}.
      Con existencias limitadas se usa el multiconjunto, con cada clase acotada por su existencia. Se consultan todos los tamaños entre el mínimo y el
      máximo de piezas.
    </p>
    <h3>4.4 Reconstrucción</h3>
    <p>
      Cada valor guarda de dónde viene (hoja, serie, paralelo o núcleo, y qué valores lo forman). Siguiendo los punteros se obtiene la red como
      árbol, que da la fórmula, y como grafo, que da el esquema, el análisis nodal y las exportaciones SPICE y CircuiTikZ.
    </p>

    <h2 id="s5">5. Garantías</h2>
    <p>
      Si todos los estados caben en memoria, la búsqueda es <b>exhaustiva</b> dentro de la topología elegida: ninguna red da un error menor que el
      primer resultado (dos valores a menos de {@html m('10^{-12}')} relativo se consideran iguales). Si no caben
      (a partir de unas 9 piezas distintas), los valores de cada estado se agrupan en una rejilla logarítmica de anchura {@html m('\\varepsilon')} y se
      conserva uno por celda. Serie, paralelo y cualquier núcleo son monótonos y 1-homogéneos en sus entradas, luego no expansivos en escala
      logarítmica: si cada entrada cambia como mucho un factor {@html m('e^{\\delta}')}, la salida también. Por inducción sobre la profundidad de la red,
      para la red óptima existe una conservada cuyo valor difiere en un factor como mucho {@html m('e^{(n-1)\\varepsilon}')}, así que
    </p>
    {@html m('\\varepsilon_{\\text{encontrado}} \\;\\le\\; \\varepsilon_{\\text{óptimo}} + \\big(e^{(n-1)\\varepsilon} - 1\\big)\\,(1+\\varepsilon_{\\text{óptimo}}).', true)}
    <p>
      Esa cota se muestra en el resumen («búsqueda con cota garantizada»). Es un peor caso; en la práctica el error encontrado suele ser muchos órdenes
      de magnitud menor. Nunca se descarta una subred por estar «lejos del objetivo», porque combinada con otra podría dar el óptimo.
    </p>
    <p>
      Los núcleos no serie-paralelo tienen además un presupuesto de evaluaciones. Si un estado lo supera, sus núcleos se evalúan sobre copias de los
      conjuntos hijos adelgazadas con la misma rejilla, y esa anchura se suma a la cota. Si ni así cabe con una anchura útil, esos núcleos no se
      exploran y el resumen lo indica como «búsqueda parcial»: la cota solo cubre entonces las redes que no los necesitan.
    </p>

    <h2 id="s6">6. Verificación</h2>
    <p>Cada solución mostrada se comprueba dos veces, con código independiente:</p>
    <ol>
      <li>El motor (Rust) evalúa la red reconstruida como árbol y como grafo, y exige que coincida con el valor de la búsqueda.</li>
      <li>
        La interfaz (TypeScript, sin compartir código con el motor) resuelve de nuevo el análisis nodal en coma flotante. Comprueba el balance de
        energía y la carga nula en los nodos internos. Además repite el cálculo con <b>fracciones exactas</b> construidas a partir del texto que has
        escrito: <code>4.7pF</code> es exactamente 47/10 pF, y también se admiten fracciones como <code>170/71pF</code>. Por eso el «valor exacto» y el
        «error exacto» no dependen del redondeo.
      </li>
    </ol>

    <h2 id="s7">7. Validación</h2>
    <p>El número de valores distintos que se obtienen con {@html m('n')} piezas iguales coincide <b>exactamente</b> (aritmética racional) con las secuencias publicadas:</p>
  {:else}
    <h2 id="s1">1. What it solves</h2>
    <p>
      Given some capacitors and a target {@html m('C^\\ast')}, CapAssigner looks for the networks between terminals A and B whose equivalent
      capacitance {@html m('C_{eq}')} is closest to {@html m('C^\\ast')}. Solutions are ranked by the relative error
      {@html m('\\varepsilon = |C_{eq}-C^\\ast|/C^\\ast')}; for equal values, the network with fewer parts wins. Each distinct value appears once,
      with a network that produces it.
    </p>
    <ul>
      <li><b>Use all</b>: every capacitor in the list is used exactly once. This is the classic classroom exercise (up to 12 parts).</li>
      <li>
        <b>Inventory</b>: between 1 and K parts are chosen (K ≤ 6). They come from a standard E3–E96 series over the chosen decades, in unlimited
        quantity, or from "my drawer", a list with stock such as <code>10pF×2 4.7pF×3</code>.
      </li>
    </ul>
    <p>
      The <em>acceptable error</em> only marks the solutions that meet it in green. The <em>part tolerance</em> is used to compute the interval
      {@html m('C_{eq}')} can fall in with real components.
    </p>

    <h2 id="s2">2. Physical model</h2>
    <p>
      Capacitors are ideal, initially uncharged and quasi-static. For two elements, parallel capacitances add and series ones add their inverses
      (the elastances):
    </p>
    {@html m('C_\\parallel = C_1 + C_2, \\qquad \\frac{1}{C_{\\text{series}}} = \\frac{1}{C_1} + \\frac{1}{C_2}', true)}
    <p>
      Any network is handled with nodal analysis. Let {@html m('L = B\\,\\mathrm{diag}(c)\\,B^{\\mathsf T}')} be the capacitance-weighted graph
      Laplacian. 1 V is applied across A–B ({@html m('v_A = 1,\\ v_B = 0')}). Every internal node has zero net charge (Kirchhoff's law for
      charge), which gives a linear system for the internal potentials:
    </p>
    {@html m('L_{II}\\, v_I = -L_{IA}, \\qquad C_{eq} = Q_A = \\sum_{j \\sim A} c_{Aj}\\,(1 - v_j).', true)}
    <p>
      Equivalently, {@html m('C_{eq}')} is the Schur complement of the Laplacian onto the terminals (Kron reduction): eliminating the internal nodes
      leaves a 2×2 Laplacian whose off-diagonal entry is {@html m('-C_{eq}')}.
    </p>
    {@html m('L_{\\text{eff}} = L_{BB} - L_{BI}\\,L_{II}^{-1}\\,L_{IB} = \\begin{pmatrix} C_{eq} & -C_{eq} \\\\ -C_{eq} & C_{eq}\\end{pmatrix}', true)}
    <p>This is the same mathematics as the effective conductance of a resistor network with {@html m('G_e = c_e')}. The app relies on these consequences:</p>
    <ul>
      <li><b>Energy</b>: {@html m('\\tfrac12 C_{eq} V^2 = \\sum_e \\tfrac12 c_e\\, \\Delta v_e^2')}. The "Parts and sharing" table shows the voltage, charge and energy of each part.</li>
      <li>
        <b>Sensitivity</b>: {@html m('\\partial C_{eq}/\\partial c_e = \\Delta v_e^2')} is the absolute sensitivity, per farad. For <em>percentage</em>
        errors what matters is the relative sensitivity or elasticity {@html m('w_e = \\frac{c_e}{C_{eq}}\\frac{\\partial C_{eq}}{\\partial c_e} = \\frac{c_e\\,\\Delta v_e^2}{C_{eq}}')},
        which is the part's energy share ("Energy" column). By Euler's theorem for homogeneous functions, {@html m('\\sum_e w_e = 1')}. A part with no
        voltage (balanced bridge) has no influence.
      </li>
      <li><b>Monotonicity</b> (Rayleigh): raising any {@html m('c_e')} never lowers {@html m('C_{eq}')}. <b>Homogeneity</b>: {@html m('C_{eq}(k\\,c) = k\\,C_{eq}(c)')}.</li>
      <li><b>Bounds</b>: {@html m('\\big(\\sum_e 1/c_e\\big)^{-1} \\le C_{eq} \\le \\sum_e c_e')}.</li>
      <li>
        <b>Tolerances</b>: if every part may vary by ±δ, monotonicity and homogeneity give {@html m('C_{eq} \\in [(1-\\delta)\\,C_{eq},\\,(1+\\delta)\\,C_{eq}]')}.
        No topology removes that common worst-case scale error.
      </li>
      <li>
        <b>Statistical spread</b>: if the parts' errors are independent with relative standard deviation {@html m('\\sigma')}, to first order
        {@html m('\\sigma_{C}/C_{eq} \\approx \\sigma\\,\\sqrt{\\textstyle\\sum_e w_e^2}')}, which lies between {@html m('\\sigma/\\sqrt n')} (even sharing) and
        {@html m('\\sigma')}. Here the topology <em>does</em> matter: sharing the energy among many parts averages their errors. It is shown for each solution.
      </li>
    </ul>
    <h3>Limits of the model</h3>
    <ul>
      <li>
        <b>DC voltage</b>: the "Voltage" column is the capacitive sharing, valid for AC or when charging from the uncharged state. At DC, in the long
        run, the voltage across series capacitors is set by their <em>leakage resistances</em>; that is why balancing resistors are added.
      </li>
      <li><b>Dielectrics</b>: class II ceramics (X7R, Y5V…) lose much of their capacitance with applied DC voltage and with temperature.</li>
      <li>
        <b>Parasitics</b>: with targets of a few pF, the stray capacitance of tracks and wires (0.1–1 pF) is of the order of the error sought. At high
        frequency series inductance and resistance (ESL, ESR) also count.
      </li>
    </ul>

    <h2 id="s3">3. Which networks exist</h2>
    <p>
      A <b>series-parallel</b> (SP) network is built by combining sub-networks in series or in parallel. It has internal nodes, but it can always
      be reduced step by step with the two formulas above. Not every network is like that. The smallest one that cannot be reduced is the
      <b>Wheatstone bridge</b>: five parts, with one of them between the two middle nodes. In fact Duffin (1965) proved that a two-terminal
      network is series-parallel if and only if no Wheatstone bridge is embedded in it.
    </p>
    <figure class="fig">
      <div class="svg">{@html bridgeSvg}</div>
      <figcaption>
        With {@html m('\\{1,2,3,4,5\\}\\,\\text{pF}')} this bridge gives exactly {@html m('C_{eq} = 170/71\\ \\text{pF} \\approx 2.3944\\ \\text{pF}')}. The best
        SP network with the same parts gives {@html m('43/18\\ \\text{pF}')}, 0.229 % lower: this is the "SP gap". With five equal parts, the
        balanced bridge gives exactly {@html m('C')}, which SP cannot.
      </figcaption>
    </figure>
    <p>
      To miss no network, CapAssigner uses the <b>SPQR decomposition</b>. Every two-terminal network in which each part lies on some simple
      path between A and B (a structural condition, independent of the values) becomes 2-connected once a virtual edge A–B is added. That network decomposes uniquely into nodes of three kinds: <em>series</em>,
      <em>parallel</em> and <em>rigid</em>. A rigid node is a 3-connected graph whose edges are replaced by two-terminal sub-networks. It is
      therefore enough to know the small 3-connected graphs ("cores"). The app generates them by brute force with canonical labelling: all of
      those with up to 10 edges, which have at most 6 vertices (K₄, the wheel W₄, K₅−e, K₅, the prism, K₃,₃…). It then removes the A–B edge.
      With them the recurrence covers <b>every possible network up to 9 parts</b>. The web app uses up to 8 parts in "use all": with 9 distinct
      parts there are millions of ways to share them among the edges of the cores.
    </p>
    {#if gallery.length}
      <div class="gallery">
        {#each gallery as g (g.core.id)}
          <figure>
            <div class="svg small">{@html g.svg}</div>
            <figcaption>{g.core.edges.length} edges · {g.core.nv} nodes</figcaption>
          </figure>
        {/each}
      </div>
      <p class="muted small">Catalogue generated by the engine itself: {gallery.length} cores (A and B are the terminals). Each edge can hold a capacitor or any sub-network.</p>
    {/if}
    <p>
      Parts that lie on no path between A and B (hanging from a single node, or in a closed loop) are excluded: they never carry charge whatever the
      values, so their network is equivalent to a smaller one, and in "use all" mode they would be cheating. Networks in which a part carries no
      charge only because of the values, such as the balanced bridge, are included.
    </p>

    <h2 id="s4">4. How it searches</h2>
    <h3>4.1 States and value sets</h3>
    <p>
      Parts with equal values are interchangeable and form a <em>class</em>. A <em>state</em> {@html m('S')} is a multiset of parts, that is, how
      many of each class are used. With {@html m('\\{3,2,3,1\\}\\,\\text{pF}')} there are three classes (3 pF ×2, 2 pF, 1 pF) and
      {@html m('3\\cdot2\\cdot2-1 = 11')} states instead of {@html m('2^4-1 = 15')} subsets. For each state the engine keeps the sorted set
      {@html m('V(S)')} of <em>distinct</em> capacitances reachable with exactly those parts, each with a pointer to a network that produces it:
    </p>
    {@html m('V(S) = \\bigcup_{S = L \\uplus R} \\big\\{\\, a + b,\\ \\tfrac{ab}{a+b} \\;:\\; a \\in V(L),\\ b \\in V(R) \\,\\big\\} \\;\\cup\\; \\bigcup_{\\text{cores } \\mathcal R} \\big\\{\\, C_{eq}^{\\mathcal R}(x_1,\\dots,x_m) : x_i \\in V(S_i),\\ S = S_1 \\uplus \\dots \\uplus S_m \\big\\}', true)}
    <p>
      States are built from smallest to largest. Networks with the same value merge as they are generated, so repeated trees are never
      enumerated, such as the trees equivalent by commutativity and associativity that v1 listed. Each sub-result is also shared by all the states
      that use it, and with repeated or rational values many networks coincide in value and merge. With distinct generic parts there are few
      coincidences: the set of a state of {@html m('k')} parts has about as many values as there are distinct SP networks (1, 2, 8, 52, 472, 5504,
      78416…, OEIS A006351). That is why memory grows fast and pruning is needed from about 9 parts (§5). The value of a core with its edges filled
      in is computed by Kron reduction on at most 6 nodes.
    </p>
    <h3>4.2 Meet in the middle at the root</h3>
    <p>
      The full state (all the parts) is never built. For each split {@html m('L \\uplus R')} and each {@html m('a \\in V(L)')}, the engine solves
      for the exact value the other side would need ({@html m('b^\\ast = C^\\ast - a')} in parallel, {@html m('b^\\ast = aC^\\ast/(a - C^\\ast)')} in
      series). It finds that value in {@html m('V(R)')} by bisection and scans its neighbours while they can still enter the top list. Root-level
      cores are evaluated directly.
    </p>
    <h3>4.3 Inventory mode</h3>
    <p>
      With unlimited quantity the state is just the number of parts {@html m('k')}: {@html m('V(k)')} combines {@html m('V(i)')} and {@html m('V(k-i)')}.
      With limited stock the multiset is used, with each class capped by its stock. Every size between the minimum and maximum number of parts is
      queried.
    </p>
    <h3>4.4 Reconstruction</h3>
    <p>
      Each value records where it came from (leaf, series, parallel or core, and which values form it). Following the pointers gives the network
      as a tree, which yields the formula, and as a graph, which yields the schematic, the nodal analysis and the SPICE and CircuiTikZ exports.
    </p>

    <h2 id="s5">5. Guarantees</h2>
    <p>
      If every state fits in memory the search is <b>exhaustive</b> within the chosen topology: no network has a smaller error than the first result
      (two values within {@html m('10^{-12}')} relative are treated as equal). If they do not fit
      (from about 9 distinct parts), each state's values are bucketed on a logarithmic grid of width {@html m('\\varepsilon')} and one value per
      bucket is kept. Series, parallel and every core are monotone and 1-homogeneous in their inputs, hence non-expansive in log scale: if every
      input changes by at most a factor {@html m('e^{\\delta}')}, so does the output. By induction over the depth of the network, the optimal network
      has a kept counterpart within a factor {@html m('e^{(n-1)\\varepsilon}')}, so
    </p>
    {@html m('\\varepsilon_{\\text{found}} \\;\\le\\; \\varepsilon_{\\text{optimal}} + \\big(e^{(n-1)\\varepsilon} - 1\\big)\\,(1+\\varepsilon_{\\text{optimal}}).', true)}
    <p>
      That bound is shown in the summary ("search with a guaranteed bound"). It is a worst case; in practice the error found is usually many
      orders of magnitude smaller. A sub-network is never discarded for being "far from the target", because combined with another it could
      give the optimum.
    </p>
    <p>
      Non-series-parallel cores also have an evaluation budget. If a state exceeds it, its cores are evaluated on copies of the child sets thinned
      on the same grid, and that width is added to the bound. If even that does not fit with a useful width, those cores are not explored and the
      summary says "partial search": the bound then only covers the networks that do not need them.
    </p>

    <h2 id="s6">6. Verification</h2>
    <p>Every solution shown is checked twice, by independent code:</p>
    <ol>
      <li>The engine (Rust) evaluates the reconstructed network as a tree and as a graph, and requires both to match the value from the search.</li>
      <li>
        The interface (TypeScript, sharing no code with the engine) solves the nodal analysis again in floating point. It checks the energy balance
        and zero charge at internal nodes. It also repeats the computation with <b>exact fractions</b> built from the text you typed:
        <code>4.7pF</code> is exactly 47/10 pF, and fractions such as <code>170/71pF</code> are accepted too. So the "exact value" and "exact error"
        do not depend on rounding.
      </li>
    </ol>

    <h2 id="s7">7. Validation</h2>
    <p>The number of distinct values obtained from {@html m('n')} equal parts matches the published sequences <b>exactly</b> (rational arithmetic):</p>
  {/if}

  <div class="table-wrap">
    <table>
      <thead><tr><th>OEIS</th><th>{i18n.lang === 'es' ? 'Qué cuenta' : 'What it counts'}</th><th>n = 1, 2, …</th></tr></thead>
      <tbody>
        {#each oeis as o (o.id)}
          <tr>
            <td><a href={`https://oeis.org/${o.id}`} target="_blank" rel="noopener">{o.id}</a></td>
            <td>{o[i18n.lang]}</td>
            <td class="mono">{o.v}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  {#if i18n.lang === 'es'}
    <p>
      Encajar A337517 muestra que el catálogo de núcleos y la recurrencia no se dejan ninguna red con piezas iguales. Con piezas <em>distintas</em>, una
      fuerza bruta independiente sobre todos los multigrafos de dos terminales de hasta 6 aristas da exactamente los mismos valores (6086 con 6
      piezas); esa prueba detectaría repartos de piezas mal generados, que con piezas iguales pasarían inadvertidos. Además, la batería de pruebas comprueba en redes
      aleatorias: cotas, homogeneidad, invariancia al reetiquetar, monotonía de Rayleigh, dualidad serie↔paralelo, reciprocidad A↔B,
      transformación Y–Δ, puente equilibrado y la fórmula cerrada del puente. También comprueba que el encuentro en el medio da lo mismo que
      construir el estado completo, que la cota de la poda se cumple y que casos de referencia (ejercicios de clase y el puente de 1–5 pF) salen
      exactos. Todo ello se ejecuta en integración continua, junto con pruebas de la web en un navegador real.
    </p>

    <h2 id="s8">8. Límites y rendimiento</h2>
    <p>Tiempos orientativos en un portátil, modo «usar todos» con piezas de valores distintos (con valores repetidos es mucho más rápido):</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Piezas distintas</th><th>Serie-paralelo</th><th>Todas las redes</th><th>Resultado</th></tr></thead>
        <tbody>
          {#each perf as p (p.n)}<tr><td>{p.n}</td><td>{p.sp}</td><td>{p.all}</td><td>{p.g}</td></tr>{/each}
        </tbody>
      </table>
    </div>
    <p>
      Límites actuales: 12 piezas en «usar todos»; núcleos no SP hasta 8 piezas en «usar todos»; inventario hasta 6 piezas (con series E ya se alcanzan valores
      exactos). El cálculo usa un solo hilo. Antes de buscar, la aplicación estima el tiempo, y durante la búsqueda muestra el progreso y el tiempo
      restante.
    </p>

    <h2 id="s9">9. Líneas futuras</h2>
    <ul>
      <li><b>Restricciones de diseño</b>: coste, tensión nominal de cada pieza (con las tensiones de la tabla de reparto) o número de nodos, con un modelo de programación entera mixta (MILP) que además certifique el óptimo.</li>
      <li><b>Más de 12 piezas</b>: búsqueda local de gran vecindario (ALNS) que destruya una parte de la red y la reconstruya de forma exacta con la programación dinámica, guiada por la sensibilidad {@html m('\\Delta v_e^2')}.</li>
      <li><b>Robustez</b>: optimizar el peor caso con tolerancias distintas por pieza (basta evaluar los dos extremos, por monotonía) y añadir análisis estadístico por Monte Carlo.</li>
      <li><b>Varios objetivos</b>: frente de Pareto error / número de piezas / coste.</li>
      <li><b>Rendimiento</b>: paralelizar la construcción de estados con varios hilos y generar núcleos de más de 10 aristas.</li>
      <li><b>Certificación exacta en el motor</b>: aritmética racional de principio a fin para certificar óptimos sin coma flotante.</li>
      <li><b>Otros componentes</b>: resistencias e inductancias comparten la misma matemática, solo cambia el papel de serie y paralelo.</li>
      <li><b>Benchmark abierto</b>: un conjunto público de instancias con objetivos exactos para comparar métodos y medir la brecha SP / no SP.</li>
    </ul>
  {:else}
    <p>
      Matching A337517 shows that the core catalogue and the recurrence miss no network with equal parts. With <em>distinct</em> parts, an
      independent brute force over every two-terminal multigraph with up to 6 edges gives exactly the same values (6086 with 6 parts); that test
      would catch badly generated assignments of parts, which equal parts would hide. The test suite also checks, on random networks: bounds,
      homogeneity, relabelling invariance, Rayleigh monotonicity, series↔parallel duality, A↔B reciprocity, the Y–Δ transform, the balanced bridge
      and the bridge's closed form. It also checks that meet-in-the-middle gives the same result as building the full state, that the pruning bound
      holds, and that reference cases (classroom exercises and the 1–5 pF bridge) come out exact. All of this runs in continuous integration,
      together with tests of the web app in a real browser.
    </p>

    <h2 id="s8">8. Limits and performance</h2>
    <p>Indicative times on a laptop, "use all" mode with parts of distinct values (repeated values are much faster):</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Distinct parts</th><th>Series-parallel</th><th>All networks</th><th>Result</th></tr></thead>
        <tbody>
          {#each perf as p (p.n)}<tr><td>{p.n}</td><td>{p.sp.replace(',', '.')}</td><td>{p.all.replace(',', '.')}</td><td>{p.g.replace('exhaustiva', 'exhaustive').replace('cota', 'bound').replace(',', '.')}</td></tr>{/each}
        </tbody>
      </table>
    </div>
    <p>
      Current limits: 12 parts in "use all"; non-SP cores up to 8 parts in "use all"; inventory up to 6 parts (E-series already reach exact values). The
      computation uses a single thread. Before searching the app estimates the time, and while it runs it shows the progress and the time left.
    </p>

    <h2 id="s9">9. Future work</h2>
    <ul>
      <li><b>Design constraints</b>: cost, the voltage rating of each part (using the voltages in the sharing table) or the number of nodes, with a mixed-integer (MILP) model that also certifies the optimum.</li>
      <li><b>More than 12 parts</b>: large-neighbourhood search (ALNS) that destroys part of the network and rebuilds it exactly with the dynamic programme, guided by the sensitivity {@html m('\\Delta v_e^2')}.</li>
      <li><b>Robustness</b>: optimise the worst case with different tolerances per part (by monotonicity the two extremes suffice) and add Monte Carlo statistics.</li>
      <li><b>Several objectives</b>: a Pareto front of error / number of parts / cost.</li>
      <li><b>Performance</b>: build states on several threads, and generate cores with more than 10 edges.</li>
      <li><b>Exact certification in the engine</b>: rational arithmetic end to end, to certify optima without floating point.</li>
      <li><b>Other components</b>: resistors and inductors share the same mathematics; only the roles of series and parallel change.</li>
      <li><b>Open benchmark</b>: a public set of instances with exact targets, to compare methods and measure the SP / non-SP gap.</li>
    </ul>
  {/if}

  <h2 id="s10">{i18n.lang === 'es' ? '10. Referencias' : '10. References'}</h2>
  <ul class="refs">
    <li>F. Dörfler, F. Bullo, “Kron Reduction of Graphs with Applications to Electrical Networks”, <em>IEEE Trans. Circuits Syst. I</em> 60(1), 2013.</li>
    <li>R. J. Duffin, “Topology of series-parallel networks”, <em>J. Math. Anal. Appl.</em> 10(2), 303–313, 1965.</li>
    <li>J. Riordan, C. E. Shannon, “The number of two-terminal series-parallel networks”, <em>J. Math. Phys.</em> 21, 83–93, 1942.</li>
    <li>G. Kron, <em>Tensor Analysis of Networks</em>, Wiley, 1939.</li>
    <li>S. Gaubert, J. Gunawardena, “The Perron–Frobenius theorem for homogeneous, monotone functions”, <em>Trans. AMS</em> 356, 4931–4950, 2004 (non-expansiveness used in §5).</li>
    <li>J. E. Hopcroft, R. E. Tarjan, “Dividing a graph into triconnected components”, <em>SIAM J. Comput.</em> 2(3), 1973.</li>
    <li>G. Di Battista, R. Tamassia, “On-line maintenance of triconnected components with SPQR-trees”, <em>Algorithmica</em> 15, 1996.</li>
    <li>S. Khan, “The bounds of the set of equivalent resistances of n equal resistors combined in series and in parallel”, arXiv:1004.3346.</li>
    <li>O. H. Ibarra, C. E. Kim, “Fast approximation algorithms for the knapsack and sum of subset problems”, <em>J. ACM</em> 22(4), 1975.</li>
    <li>J. W. S. Rayleigh, <em>The Theory of Sound</em> (monotonicity principle); P. G. Doyle, J. L. Snell, <em>Random Walks and Electric Networks</em>, MAA, 1984.</li>
    <li>OEIS Foundation: <a href="https://oeis.org/A048211">A048211</a>, <a href="https://oeis.org/A174283">A174283</a>, <a href="https://oeis.org/A337517">A337517</a>, <a href="https://oeis.org/A006351">A006351</a>, <a href="https://oeis.org/A180414">A180414</a>.</li>
  </ul>
</article>

<style>
  .theory {
    max-width: 54rem;
    margin: 0 auto;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: clamp(1rem, 3vw, 2.2rem);
  }
  .toc {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem 1rem;
    font-size: 0.85rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--line);
  }
  .toc a {
    color: var(--muted);
    text-decoration: none;
  }
  .toc a:hover {
    color: var(--accent);
  }
  h2 {
    font-size: 1.25rem;
    margin: 2rem 0 0.6rem;
    scroll-margin-top: 1rem;
  }
  h3 {
    font-size: 1.02rem;
    margin: 1.3rem 0 0.4rem;
  }
  p,
  li {
    line-height: 1.65;
  }
  :global(.katex-display) {
    overflow-x: auto;
    overflow-y: hidden;
    padding: 0.2rem 0;
  }
  .fig {
    margin: 1rem 0;
  }
  .fig figcaption {
    font-size: 0.9rem;
    color: var(--muted);
    margin-top: 0.4rem;
  }
  .svg {
    background: var(--paper);
    border-radius: 8px;
    padding: 0.5rem;
    overflow-x: auto;
  }
  .svg :global(svg) {
    display: block;
    margin: 0 auto;
    max-width: 100%;
    height: auto;
  }
  .gallery {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(11rem, 1fr));
    gap: 0.6rem;
    margin: 1rem 0 0.3rem;
  }
  .gallery figure {
    margin: 0;
  }
  .gallery :global(line) {
    stroke: var(--ink);
    stroke-width: 1.6;
  }
  .gallery :global(circle) {
    fill: var(--ink);
  }
  .gallery :global(circle.term) {
    fill: var(--paper);
    stroke: var(--accent);
    stroke-width: 2;
  }
  .gallery :global(text) {
    font: 600 10px system-ui, sans-serif;
    fill: var(--muted);
    text-anchor: middle;
  }
  .gallery figcaption {
    font-size: 0.78rem;
    color: var(--muted);
    text-align: center;
  }
  .small {
    font-size: 0.85rem;
  }
  .table-wrap {
    overflow-x: auto;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
  }
  th,
  td {
    text-align: left;
    padding: 0.35rem 0.6rem;
    border-bottom: 1px solid var(--line);
  }
  th {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
  }
  .refs li {
    font-size: 0.9rem;
  }
</style>
