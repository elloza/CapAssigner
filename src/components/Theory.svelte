<script lang="ts">
  import katex from 'katex';
  import { i18n } from '../lib/i18n.svelte';

  const m = (s: string, display = false) => katex.renderToString(s, { throwOnError: false, displayMode: display });

  const oeis = [
    { id: 'A048211', es: 'valores serie-paralelo con n iguales', en: 'series-parallel values of n equal parts', v: '1, 2, 4, 9, 22, 53, 131, 337, 869, 2213, 5691, 14517' },
    { id: 'A174283', es: 'serie-paralelo + puentes', en: 'series-parallel + bridges', v: '1, 2, 4, 9, 23, 57, 151, 415, 1157' },
    { id: 'A337517', es: 'todas las redes de dos terminales', en: 'all two-terminal networks', v: '1, 2, 4, 9, 23, 57, 151, 427, 1263' },
    { id: 'A006351', es: 'redes serie-paralelo con n elementos distinguibles', en: 'series-parallel networks with n labelled parts', v: '1, 2, 8, 52, 472, 5504, 78416' },
  ];
</script>

<article class="theory">
  {#if i18n.lang === 'es'}
    <h2>El problema</h2>
    <p>
      Dados unos condensadores y una capacidad objetivo {@html m('C^\\ast')}, buscar las redes entre dos terminales A y B cuya
      capacidad equivalente {@html m('C_{eq}')} se acerque más a {@html m('C^\\ast')}. Hay dos variantes:
      <b>usar todos</b> (cada condensador exactamente una vez, el ejercicio clásico de clase) y <b>inventario</b> (elegir entre
      1 y K piezas de una lista con o sin existencias limitadas, p. ej. una serie E12).
    </p>

    <h2>Física</h2>
    <p>Para dos elementos, en paralelo las capacidades se suman y en serie se suman sus inversas (elastancias):</p>
    {@html m('C_\\parallel = C_1 + C_2, \\qquad C_{\\text{serie}} = \\frac{C_1 C_2}{C_1 + C_2}', true)}
    <p>
      Para una red cualquiera (puentes incluidos) se usa análisis nodal. Con {@html m('L = B\\,\\mathrm{diag}(c)\\,B^{\\mathsf T}')} la
      Laplaciana ponderada por las capacidades, {@html m('V_A = 1')}, {@html m('V_B = 0')} y nodos internos neutros:
    </p>
    {@html m('L_{II}\\, v_I = -L_{IA}, \\qquad C_{eq} = Q_A = \\sum_{(A,j)} c_{Aj}\\,(1 - v_j)', true)}
    <p>
      Equivalentemente, {@html m('C_{eq}')} es el complemento de Schur de {@html m('L')} sobre los terminales (reducción de Kron). Se cumplen
      identidades que la aplicación comprueba en cada resultado:
    </p>
    <ul>
      <li>Energía: {@html m('\\tfrac12 C_{eq} V^2 = \\sum_e \\tfrac12 c_e\\, \\Delta v_e^2')} y carga neta nula en cada nodo interno.</li>
      <li>Sensibilidad: {@html m('\\partial C_{eq} / \\partial c_e = \\Delta v_e^2')} (tensión relativa al cuadrado).</li>
      <li>Cotas: {@html m('\\left(\\sum 1/c_e\\right)^{-1} \\le C_{eq} \\le \\sum c_e')}; monotonía de Rayleigh y homogeneidad {@html m('C_{eq}(k c) = k\\,C_{eq}(c)')}.</li>
      <li>
        Tolerancias: por monotonía y homogeneidad, si todas las piezas varían ±δ, {@html m('C_{eq} \\in [(1-\\delta)C_{eq}, (1+\\delta)C_{eq}]')}; ninguna
        topología reduce ese peor caso común.
      </li>
    </ul>

    <h2>Cómo busca</h2>
    <h3>1. Programación dinámica de valores</h3>
    <p>
      Para cada <em>estado</em> (el multiconjunto de piezas disponibles; las piezas de igual valor se agrupan) se guarda el conjunto
      ordenado {@html m('V(S)')} de capacidades <em>distintas</em> alcanzables, con un puntero a una red testigo:
    </p>
    {@html m('V(S) = \\bigcup_{S = L \\uplus R} \\{\\, a + b,\\ \\tfrac{ab}{a+b} : a \\in V(L),\\ b \\in V(R) \\,\\} \\;\\cup\\; \\text{núcleos}(S)', true)}
    <p>
      No se construyen árboles duplicados: dos redes con el mismo valor se funden al generarse. v1 enumeraba todos los árboles y
      deduplicaba al final.
    </p>
    <h3>2. Encuentro en el medio en la raíz</h3>
    <p>
      El estado completo nunca se materializa. Para cada partición y cada {@html m('a \\in V(L)')} se despeja el complemento exacto
      ({@html m('b^\\ast = C^\\ast - a')} en paralelo, {@html m('b^\\ast = aC^\\ast/(a - C^\\ast)')} en serie) y se busca por bisección en {@html m('V(R)')}.
    </p>
    <h3>3. Redes no serie-paralelo (puentes y más)</h3>
    <p>
      Toda red de dos terminales en la que cada pieza conduce carga es 2-conexa al añadir la arista virtual A–B, y su descomposición
      SPQR solo tiene nodos serie, paralelo y <em>rígidos</em>. Un nodo rígido es un grafo 3-conexo cuyas aristas se sustituyen por
      subredes. La aplicación genera por fuerza bruta con etiquetado canónico todos los grafos 3-conexos de hasta 10 aristas (K₄, rueda W₄,
      K₅−e, K₅, prisma, K₃,₃…) y los usa como «núcleos». El más pequeño es el puente de Wheatstone. Así la búsqueda es
      <b>completa sobre todas las topologías hasta 9 piezas</b> (exhaustiva hasta 8 piezas distintas; con 9 entra en juego la poda con cota).
    </p>
    <h3>4. Poda con garantía</h3>
    <p>
      Si la memoria no basta (unas 9 piezas o más), los valores de cada estado se agrupan en una rejilla logarítmica de anchura ε.
      Serie, paralelo y cualquier núcleo son monótonos y 1-homogéneos, luego no expansivos en escala logarítmica. Por inducción, el mejor
      valor conservado está a menos de {@html m('(e^{(n-1)\\varepsilon} - 1)')} (relativo) del óptimo verdadero, y la aplicación muestra esa
      cota. Nunca se poda por «cercanía al objetivo» de una subred, porque eso puede eliminar el óptimo.
    </p>

    <h2>Validación</h2>
    <p>Los recuentos de valores distintos con n condensadores iguales coinciden <b>exactamente</b> (aritmética racional) con OEIS:</p>
  {:else}
    <h2>The problem</h2>
    <p>
      Given some capacitors and a target {@html m('C^\\ast')}, find the networks between terminals A and B whose equivalent capacitance
      {@html m('C_{eq}')} is closest to {@html m('C^\\ast')}. Two variants: <b>use all</b> (each capacitor exactly once, the classic
      classroom exercise) and <b>inventory</b> (choose between 1 and K parts from a list with limited or unlimited stock, e.g. an E12 series).
    </p>

    <h2>Physics</h2>
    <p>For two elements, parallel capacitances add and series ones add their inverses (elastances):</p>
    {@html m('C_\\parallel = C_1 + C_2, \\qquad C_{\\text{series}} = \\frac{C_1 C_2}{C_1 + C_2}', true)}
    <p>
      For any network (bridges included) nodal analysis is used. With {@html m('L = B\\,\\mathrm{diag}(c)\\,B^{\\mathsf T}')} the
      capacitance-weighted Laplacian, {@html m('V_A = 1')}, {@html m('V_B = 0')} and neutral internal nodes:
    </p>
    {@html m('L_{II}\\, v_I = -L_{IA}, \\qquad C_{eq} = Q_A = \\sum_{(A,j)} c_{Aj}\\,(1 - v_j)', true)}
    <p>
      Equivalently, {@html m('C_{eq}')} is the Schur complement of {@html m('L')} onto the terminals (Kron reduction). The app checks these
      identities on every result:
    </p>
    <ul>
      <li>Energy: {@html m('\\tfrac12 C_{eq} V^2 = \\sum_e \\tfrac12 c_e\\, \\Delta v_e^2')} and zero net charge at each internal node.</li>
      <li>Sensitivity: {@html m('\\partial C_{eq} / \\partial c_e = \\Delta v_e^2')} (squared relative voltage).</li>
      <li>Bounds: {@html m('\\left(\\sum 1/c_e\\right)^{-1} \\le C_{eq} \\le \\sum c_e')}; Rayleigh monotonicity and homogeneity {@html m('C_{eq}(k c) = k\\,C_{eq}(c)')}.</li>
      <li>
        Tolerances: by monotonicity and homogeneity, if every part varies by ±δ, {@html m('C_{eq} \\in [(1-\\delta)C_{eq}, (1+\\delta)C_{eq}]')}; no topology
        removes that common worst case.
      </li>
    </ul>

    <h2>How it searches</h2>
    <h3>1. Value dynamic programming</h3>
    <p>
      For every <em>state</em> (the multiset of available parts; equal values are grouped) the engine keeps the sorted set {@html m('V(S)')} of
      <em>distinct</em> reachable capacitances, each with a pointer to a witness network:
    </p>
    {@html m('V(S) = \\bigcup_{S = L \\uplus R} \\{\\, a + b,\\ \\tfrac{ab}{a+b} : a \\in V(L),\\ b \\in V(R) \\,\\} \\;\\cup\\; \\text{cores}(S)', true)}
    <p>
      No duplicate trees are built: networks with equal values merge as they are generated. v1 enumerated every tree and deduplicated at the end.
    </p>
    <h3>2. Meet in the middle at the root</h3>
    <p>
      The full state is never materialised. For each split and each {@html m('a \\in V(L)')} the exact partner is solved for
      ({@html m('b^\\ast = C^\\ast - a')} in parallel, {@html m('b^\\ast = aC^\\ast/(a - C^\\ast)')} in series) and found in {@html m('V(R)')} by bisection.
    </p>
    <h3>3. Non-series-parallel networks (bridges and beyond)</h3>
    <p>
      Every two-terminal network in which each part carries charge becomes 2-connected once the virtual edge A–B is added, and its SPQR
      decomposition has only series, parallel and <em>rigid</em> nodes. A rigid node is a 3-connected graph whose edges are replaced by
      sub-networks. The app enumerates, by brute force with canonical labelling, every 3-connected graph with up to 10 edges (K₄, wheel W₄,
      K₅−e, K₅, prism, K₃,₃…) and uses them as "cores". The smallest is the Wheatstone bridge. The search is therefore
      <b>complete over all topologies up to 9 parts</b> (exhaustive up to 8 distinct parts; at 9 the bounded pruning below applies).
    </p>
    <h3>4. Pruning with a guarantee</h3>
    <p>
      When memory runs short (around 9 parts or more), each state's values are bucketed on a logarithmic grid of width ε. Series, parallel
      and every core are monotone and 1-homogeneous, hence non-expansive in log scale. By induction, the best kept value is within
      {@html m('(e^{(n-1)\\varepsilon} - 1)')} (relative) of the true optimum, and the app displays that bound. Sub-networks are never pruned
      by "closeness to the target", because that can discard the optimum.
    </p>

    <h2>Validation</h2>
    <p>The counts of distinct values from n equal capacitors match OEIS <b>exactly</b> (rational arithmetic):</p>
  {/if}

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

  {#if i18n.lang === 'es'}
    <p>
      Además: propiedades aleatorias (proptest y fast-check) de acotación, homogeneidad, invariancia por permutación, monotonía de Rayleigh,
      dualidad serie↔paralelo, reciprocidad, transformación Y–Δ, puente equilibrado y fórmula cerrada del puente. Cada resultado del motor
      Rust/WASM se recalcula con un oráculo TypeScript independiente, en coma flotante y con fracciones exactas obtenidas del texto
      decimal introducido. También se comparan con los resultados de v1 sobre sus ejercicios: v2 nunca es peor.
    </p>
    <h2>Otros enfoques considerados</h2>
    <ul>
      <li><b>Enumeración de árboles</b> (v1): genera duplicados y crece como {@html m('n!\\cdot\\text{Catalan}')}; sustituida por la DP de valores.</li>
      <li>
        <b>MILP</b> (asignar piezas a pares de nodos, potenciales y cargas con linealización exacta del producto binario-continuo): útil como
        referencia o para restricciones extra, pero depende de un número fijo de nodos. La DP con núcleos ya es exhaustiva hasta 8 piezas distintas.
      </li>
      <li><b>Metaheurísticas</b> (aleatorio, recocido, ALNS): sin certificado. Aquí se prefiere la poda con cota demostrada.</li>
      <li><b>WebGPU / Pyodide</b>: la combinatoria es muy ramificada y las matrices son diminutas (≤ 6 nodos por núcleo), así que la GPU no aporta. Pyodide añadiría unos 10 MB y sería más lento que Rust→WASM.</li>
    </ul>
  {:else}
    <p>
      Also: randomised properties (proptest and fast-check) for bounds, homogeneity, permutation invariance, Rayleigh monotonicity,
      series↔parallel duality, reciprocity, the Y–Δ transform, the balanced bridge and the bridge's closed form. Every result of the
      Rust/WASM engine is recomputed by an independent TypeScript oracle, in floating point and with exact fractions built from the decimal
      text typed. Results are also compared with v1 on its exercises: v2 is never worse.
    </p>
    <h2>Other approaches considered</h2>
    <ul>
      <li><b>Tree enumeration</b> (v1): produces duplicates and grows like {@html m('n!\\cdot\\text{Catalan}')}; replaced by the value DP.</li>
      <li>
        <b>MILP</b> (assign parts to node pairs, potentials and charges with an exact linearisation of the binary-continuous product): useful as a
        reference or for extra constraints, but it depends on a fixed number of nodes. The core-based DP is already exhaustive up to 8 distinct parts.
      </li>
      <li><b>Metaheuristics</b> (random, annealing, ALNS): no certificate. A pruning with a proven bound is preferred here.</li>
      <li><b>WebGPU / Pyodide</b>: the combinatorics branch heavily and the matrices are tiny (≤ 6 nodes per core), so a GPU does not help. Pyodide would add about 10 MB and run slower than Rust→WASM.</li>
    </ul>
  {/if}

  <h2>{i18n.lang === 'es' ? 'Referencias' : 'References'}</h2>
  <ul class="refs">
    <li>F. Dörfler, F. Bullo, “Kron Reduction of Graphs with Applications to Electrical Networks”, <em>IEEE TCAS-I</em> 60(1), 2013.</li>
    <li>J. Hopcroft, R. Tarjan, “Dividing a graph into triconnected components”, <em>SIAM J. Comput.</em> 2(3), 1973 (SPQR).</li>
    <li>S. Khan, “The bounds of the set of equivalent resistances of n equal resistors combined in series and in parallel”, arXiv:1004.3346.</li>
    <li>O. Ibarra, C. Kim, “Fast approximation algorithms for the knapsack and sum of subset problems”, <em>J. ACM</em> 22(4), 1975 (trimming).</li>
    <li>E. Weissler et al., “Enumeration of all superconducting circuits up to 5 nodes”, arXiv:2410.18497.</li>
    <li>OEIS Foundation, sequences <a href="https://oeis.org/A048211">A048211</a>, <a href="https://oeis.org/A174283">A174283</a>, <a href="https://oeis.org/A337517">A337517</a>, <a href="https://oeis.org/A006351">A006351</a>.</li>
  </ul>
</article>

<style>
  .theory {
    max-width: 52rem;
    margin: 0 auto;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: clamp(1rem, 3vw, 2rem);
  }
  h2 {
    font-size: 1.2rem;
    margin: 1.8rem 0 0.6rem;
  }
  h2:first-child {
    margin-top: 0;
  }
  h3 {
    font-size: 1rem;
    margin: 1.2rem 0 0.4rem;
  }
  p,
  li {
    line-height: 1.6;
  }
  :global(.katex-display) {
    overflow-x: auto;
    overflow-y: hidden;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
    display: block;
    overflow-x: auto;
  }
  th,
  td {
    text-align: left;
    padding: 0.35rem 0.6rem;
    border-bottom: 1px solid var(--line);
  }
  .refs li {
    font-size: 0.9rem;
  }
</style>
