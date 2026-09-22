<script lang="ts">
  import { onMount } from 'svelte';
  import SolverForm from './components/SolverForm.svelte';
  import Results from './components/Results.svelte';
  import Theory from './components/Theory.svelte';
  import About from './components/About.svelte';
  import { i18n, setLang, t } from './lib/i18n.svelte';
  import { buildRequest, fromHash, toHash, type Built, type FormState } from './lib/form';
  import { CancelledError, SolverClient } from './lib/solver';
  import type { SolveResponse } from './lib/types';

  type Tab = 'solve' | 'theory' | 'about';

  // Read before the hash-sync effect normalises it (a link equal to the defaults becomes empty).
  const sharedLink = location.hash.length > 1;
  let form: FormState = $state(fromHash(location.hash));
  let tab: Tab = $state('solve');
  let running = $state(false);
  let progress = $state(0);
  let error: string | null = $state(null);
  let result: { res: SolveResponse; ms: number; built: Built; form: FormState } | null = $state(null);
  let theme: 'auto' | 'light' | 'dark' = $state('auto');

  const built = $derived(buildRequest(form));
  const client = new SolverClient();

  $effect(() => {
    const h = toHash(form);
    history.replaceState(null, '', h ? `#${h}` : location.pathname + location.search);
  });

  $effect(() => {
    if (theme === 'auto') document.documentElement.removeAttribute('data-theme');
    else document.documentElement.setAttribute('data-theme', theme);
    try {
      localStorage.setItem('capassigner.theme', theme);
    } catch {
      // Not persisted in private mode.
    }
  });

  onMount(() => {
    document.documentElement.lang = i18n.lang;
    try {
      const saved = localStorage.getItem('capassigner.theme');
      if (saved === 'light' || saved === 'dark') theme = saved;
    } catch {
      // Keep the automatic theme.
    }
    client.warmUp();
    if (sharedLink && built.req) solve();
    // A pasted link on an open tab only changes the hash.
    const onHash = () => {
      form = fromHash(location.hash);
      tab = 'solve';
      queueMicrotask(solve);
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  });

  async function solve() {
    const b = built;
    if (!b.req) return;
    running = true;
    progress = 0;
    error = null;
    try {
      const { res, ms } = await client.run(b.req, (d, total) => (progress = total ? d / total : 0));
      result = { res, ms, built: b, form: { ...form } };
    } catch (e) {
      error = e instanceof CancelledError ? t().cancelled : e instanceof Error ? e.message : String(e);
    } finally {
      running = false;
    }
  }

  function cancel() {
    client.cancel();
  }
</script>

<header>
  <div class="brand">
    <svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true"
      ><path d="M2 16h11M19 16h11M13 6v20M19 6v20" stroke="var(--accent)" stroke-width="3" fill="none" stroke-linecap="round" /></svg
    >
    <div>
      <h1>{t().appName} <span class="ver">v2</span></h1>
      <p class="muted">{t().tagline}</p>
    </div>
  </div>
  <nav aria-label="main">
    {#each [['solve', t().tabSolve], ['theory', t().tabTheory], ['about', t().tabAbout]] as [id, label] (id)}
      <button class:active={tab === id} aria-current={tab === id ? 'page' : undefined} onclick={() => (tab = id as Tab)}>{label}</button>
    {/each}
  </nav>
  <div class="prefs">
    <label>
      <span class="sr-only">{t().language}</span>
      <select value={i18n.lang} onchange={(e) => setLang((e.currentTarget as HTMLSelectElement).value as 'es' | 'en')}>
        <option value="es">ES</option>
        <option value="en">EN</option>
      </select>
    </label>
    <label>
      <span class="sr-only">{t().theme}</span>
      <select bind:value={theme}>
        <option value="auto">◐</option>
        <option value="light">☀</option>
        <option value="dark">☾</option>
      </select>
    </label>
  </div>
</header>

<main>
  {#if tab === 'solve'}
    <div class="solve">
      <SolverForm bind:form {built} {running} {progress} onsolve={solve} oncancel={cancel} />
      <Results {result} {error} {running} />
    </div>
  {:else if tab === 'theory'}
    <Theory />
  {:else}
    <About />
  {/if}
</main>

<footer class="muted">
  <span>{t().offline}</span>
  <a href="https://github.com/elloza/CapAssigner">GitHub</a>
</footer>

<style>
  header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 0.75rem 1.5rem;
    padding: 1rem clamp(1rem, 3vw, 2rem);
    border-bottom: 1px solid var(--line);
    background: var(--panel);
  }
  .brand {
    display: flex;
    gap: 0.7rem;
    align-items: center;
    flex: 1 1 18rem;
  }
  h1 {
    margin: 0;
    font-size: 1.3rem;
    letter-spacing: -0.01em;
  }
  .ver {
    font-size: 0.75rem;
    color: var(--accent);
    font-weight: 600;
    vertical-align: super;
  }
  .brand p {
    margin: 0;
    font-size: 0.85rem;
  }
  nav {
    display: flex;
    gap: 0.25rem;
    flex-wrap: wrap;
  }
  nav button {
    border: none;
    background: none;
    color: var(--muted);
  }
  nav button.active {
    color: var(--ink);
    background: var(--accent-soft);
    font-weight: 600;
  }
  .prefs {
    display: flex;
    gap: 0.4rem;
  }
  .prefs select {
    width: auto;
  }
  main {
    padding: 1.25rem clamp(1rem, 3vw, 2rem) 2rem;
    max-width: 1400px;
    margin: 0 auto;
  }
  .solve {
    display: grid;
    grid-template-columns: minmax(0, 360px) minmax(0, 1fr);
    gap: 1.5rem;
    align-items: start;
  }
  @media (max-width: 900px) {
    .solve {
      grid-template-columns: minmax(0, 1fr);
    }
  }
  footer {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    gap: 0.5rem;
    padding: 1rem clamp(1rem, 3vw, 2rem);
    border-top: 1px solid var(--line);
    font-size: 0.85rem;
  }
</style>
