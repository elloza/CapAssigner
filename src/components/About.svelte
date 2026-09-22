<script lang="ts">
  import { onMount } from 'svelte';
  import { i18n } from '../lib/i18n.svelte';

  let engine = $state('…');
  onMount(async () => {
    const mod = await import('../wasm/pkg/capcore.js');
    await mod.default();
    engine = mod.version();
  });
</script>

<article class="about">
  {#if i18n.lang === 'es'}
    <h2>Acerca de CapAssigner v2</h2>
    <p>
      Herramienta docente y de ingeniería para diseñar asociaciones de condensadores. Es una reescritura de la v1 (Python/Streamlit, en
      <code>legacy/</code>) como aplicación web estática: el motor está escrito en Rust y compilado a WebAssembly, se ejecuta en un Web Worker
      y no necesita servidor, así que funciona en GitHub Pages y sin conexión una vez cargada.
    </p>
    <h3>Novedades respecto a v1</h3>
    <ul>
      <li>Búsqueda sobre <b>todas</b> las topologías (puentes y núcleos 3-conexos) hasta 9 piezas, exhaustiva hasta 8 distintas, y serie-paralelo hasta 12 con cota garantizada.</li>
      <li>Modo inventario (series E3–E96 o cajón con existencias limitadas).</li>
      <li>Verificación independiente de cada resultado con aritmética exacta, balance de energía y tensiones por pieza.</li>
      <li>Exportación a SPICE, CircuiTikZ, SVG y JSON; enlaces para compartir el problema.</li>
    </ul>
  {:else}
    <h2>About CapAssigner v2</h2>
    <p>
      A teaching and engineering tool for designing capacitor combinations. It rewrites v1 (Python/Streamlit, kept in <code>legacy/</code>)
      as a static web app: the engine is written in Rust and compiled to WebAssembly, runs in a Web Worker and needs no server, so it works on
      GitHub Pages and offline once loaded.
    </p>
    <h3>What is new since v1</h3>
    <ul>
      <li>Search over <b>all</b> topologies (bridges and 3-connected cores) up to 9 parts, exhaustive up to 8 distinct ones, and series-parallel up to 12 with a proven bound.</li>
      <li>Inventory mode (E3–E96 series or a drawer with limited stock).</li>
      <li>Independent verification of every result with exact arithmetic, energy balance and per-part voltages.</li>
      <li>Export to SPICE, CircuiTikZ, SVG and JSON; shareable problem links.</li>
    </ul>
  {/if}
  <p class="muted">Engine <span class="mono">capcore {engine}</span> · MIT · <a href="https://github.com/elloza/CapAssigner">github.com/elloza/CapAssigner</a></p>
</article>

<style>
  .about {
    max-width: 46rem;
    margin: 0 auto;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: clamp(1rem, 3vw, 2rem);
    line-height: 1.6;
  }
  h2 {
    margin-top: 0;
  }
</style>
