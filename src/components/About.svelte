<script lang="ts">
  import { onMount } from 'svelte';
  import { i18n } from '../lib/i18n.svelte';

  const repo = 'https://github.com/elloza/CapAssigner';
  let engine = $state('…');
  onMount(async () => {
    const mod = await import('../wasm/pkg/capcore.js');
    await mod.default();
    engine = mod.version();
  });
</script>

<article class="about">
  {#if i18n.lang === 'es'}
    <h2>Acerca de CapAssigner</h2>
    <p>
      CapAssigner es una herramienta docente y de ingeniería para diseñar asociaciones de condensadores. Dado un valor objetivo, encuentra las
      mejores redes con los condensadores disponibles (serie, paralelo, puentes y cualquier otra topología), dice cuándo la respuesta es
      óptima y verifica cada circuito con aritmética exacta.
    </p>

    <h3>Para qué sirve</h3>
    <ul>
      <li><b>En clase</b>: resolver y comprobar ejercicios de asociación de condensadores, ver el esquema y el reparto de tensiones y cargas.</li>
      <li><b>En el laboratorio</b>: conseguir un valor que no existe en el cajón combinando piezas de una serie E o de las que tengas.</li>
      <li><b>En documentos</b>: exportar la red a SPICE para simularla o a CircuiTikZ para incluirla en LaTeX.</li>
    </ul>

    <h3>Privacidad y funcionamiento</h3>
    <p>
      Es una página estática. El motor de cálculo está escrito en Rust, se compila a WebAssembly y se ejecuta en tu navegador, en un hilo
      aparte. No hay servidor ni se envía ningún dato. Una vez cargada, funciona sin conexión. Los problemas se pueden compartir con un enlace:
      los datos van en la propia dirección.
    </p>

    <h3>Tecnología</h3>
    <p>
      Rust + wasm-bindgen (motor), Svelte 5 y TypeScript (interfaz), KaTeX (fórmulas). La interfaz verifica cada resultado con código
      independiente del motor. El proyecto tiene pruebas automáticas de física, de combinatoria (secuencias OEIS) y de la web en un navegador
      real, que se ejecutan en cada cambio.
    </p>

    <h3>Código, errores y sugerencias</h3>
    <p>
      El código es abierto (licencia MIT) y está en <a href={repo}>GitHub</a>. Para avisar de un error o proponer una mejora, abre una
      <a href={`${repo}/issues`}>incidencia</a>. Si usas CapAssigner en un trabajo, cita el repositorio.
    </p>
  {:else}
    <h2>About CapAssigner</h2>
    <p>
      CapAssigner is a teaching and engineering tool for designing capacitor combinations. Given a target value, it finds the best networks with
      the capacitors available (series, parallel, bridges and any other topology), tells you when the answer is optimal, and verifies every
      circuit with exact arithmetic.
    </p>

    <h3>What it is for</h3>
    <ul>
      <li><b>In class</b>: solve and check capacitor-combination exercises, and see the schematic and how voltage and charge are shared.</li>
      <li><b>In the lab</b>: get a value you do not have by combining parts from an E-series or from your own stock.</li>
      <li><b>In documents</b>: export the network to SPICE to simulate it, or to CircuiTikZ to include it in LaTeX.</li>
    </ul>

    <h3>Privacy and how it runs</h3>
    <p>
      It is a static page. The computation engine is written in Rust, compiled to WebAssembly and run in your browser, on a separate thread.
      There is no server and no data is sent anywhere. Once loaded, it works offline. Problems can be shared as links: the data travels in the
      address itself.
    </p>

    <h3>Technology</h3>
    <p>
      Rust + wasm-bindgen (engine), Svelte 5 and TypeScript (interface), KaTeX (formulas). The interface verifies each result with code
      independent of the engine. The project has automated tests for the physics, for the combinatorics (OEIS sequences) and for the web app in
      a real browser, run on every change.
    </p>

    <h3>Code, bugs and suggestions</h3>
    <p>
      The code is open source (MIT licence) and lives on <a href={repo}>GitHub</a>. To report a bug or suggest an improvement, open an
      <a href={`${repo}/issues`}>issue</a>. If you use CapAssigner in your work, please cite the repository.
    </p>
  {/if}
  <p class="muted meta">capcore <span class="mono">{engine}</span> · MIT</p>
</article>

<style>
  .about {
    max-width: 46rem;
    margin: 0 auto;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: clamp(1rem, 3vw, 2rem);
    line-height: 1.65;
  }
  h2 {
    margin-top: 0;
  }
  h3 {
    font-size: 1rem;
    margin: 1.4rem 0 0.3rem;
  }
  .meta {
    margin-top: 1.5rem;
    font-size: 0.85rem;
  }
</style>
