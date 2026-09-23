<script lang="ts">
  import { i18n, t } from '../lib/i18n.svelte';
  import { formatCapacitance, formatPercent } from '../lib/units';
  import { coreLabel, formula } from '../lib/export';
  import { EXAMPLES, type Built, type FormState } from '../lib/form';
  import type { SolveResponse } from '../lib/types';
  import SolutionDetail from './SolutionDetail.svelte';
  import ErrorChart from './ErrorChart.svelte';

  interface Props {
    result: { res: SolveResponse; ms: number; memoryMB: number; built: Built; form: FormState } | null;
    error: string | null;
    running: boolean;
    /** Share of the estimated work done (0–1). */
    progress: number;
    /** Seconds since the search started. */
    elapsed: number;
    /** Estimated total seconds before starting. */
    expected: number;
    oncancel: () => void;
    onexample: (id: string) => void;
  }
  let { result, error, running, progress, elapsed, expected, oncancel, onexample }: Props = $props();

  let selected = $state(0);
  $effect(() => {
    // New result → show its best solution.
    void result;
    selected = 0;
  });

  const coreMap = $derived(new Map((result?.res.cores ?? []).map((c) => [c.id, c])));

  /**
   * Remaining time: the prior estimate early on, then more and more an
   * extrapolation from the measured progress.
   */
  const remaining = $derived.by(() => {
    const prior = Math.max(expected - elapsed, 0);
    if (progress < 0.05 || elapsed < 0.3) return prior;
    const measured = (elapsed * (1 - progress)) / progress;
    // Progress front-loads (late states cost more than their weight), so
    // trust it only gradually.
    const w = progress * progress;
    return w * measured + (1 - w) * prior;
  });
</script>

<section class="results" aria-live="polite">
  {#if running}
    <div class="running" role="status">
      <div class="head">
        <span class="spinner" aria-hidden="true"></span>
        <strong>{t().computing}</strong>
        <button type="button" onclick={oncancel}>{t().cancel}</button>
      </div>
      <progress max="1" value={progress} aria-label={t().progress}></progress>
      <div class="times mono">
        <span>{t().elapsed}: {t().duration(elapsed)}</span>
        <span>{t().remaining}: {remaining < 1 ? '< 1 s' : `≈ ${t().duration(remaining)}`}</span>
      </div>
      <p class="muted small">{t().runningHint}</p>
    </div>
  {/if}

  {#if error}
    <p class="note bad">{error}</p>
  {/if}

  {#if !result && !running}
    <div class="empty">
      <svg viewBox="0 0 120 40" width="120" height="40" aria-hidden="true">
        <path d="M4 20h44M72 20h44M48 6v28M72 6v28" stroke="var(--accent)" stroke-width="4" fill="none" stroke-linecap="round" />
      </svg>
      <h2>{t().emptyTitle}</h2>
      <ol>
        {#each t().emptySteps as step, i (i)}<li>{step}</li>{/each}
      </ol>
      <p class="muted">{t().tryExample}</p>
      <div class="ex">
        {#each EXAMPLES as ex (ex.id)}
          <button type="button" onclick={() => onexample(ex.id)}>{ex[i18n.lang]}</button>
        {/each}
      </div>
    </div>
  {:else if result}
    {@const { res, ms, memoryMB, built, form } = result}
    {@const st = res.stats}
    {@const scope = form.topo === 'sp' || built.coresDropped ? t().scopeSP : form.topo === 'bridge' ? t().scopeBridge : t().scopeAll}
    {@const bound = formatPercent(st.boundRel).replace('+', '')}
    <div class="summary" class:ok={st.exhaustive} class:warn={!st.exhaustive} class:stale={running}>
      <strong>{st.exhaustive ? t().exhaustive : st.coresComplete ? t().approximate : t().partial}</strong>
      <span>
        {st.exhaustive ? t().exhaustiveHint(scope) : st.coresComplete ? t().approximateHint(scope, bound) : t().partialHint(bound)}
      </span>
      <span class="muted stats">{t().stats(st.states, st.entries, ms)} · {Math.round(memoryMB)} MB</span>
    </div>

    {#if res.solutions.length > 1}
      <ErrorChart solutions={res.solutions} tol={form.tol / 100} {selected} onselect={(i) => (selected = i)} />
    {/if}

    <div class="table-wrap" class:stale={running}>
      <table>
        <thead>
          <tr>
            <th>{t().colRank}</th>
            <th>{t().colCeq}</th>
            <th>{t().colError}</th>
            <th>{t().colParts}</th>
            <th class="net">{t().colNetwork} <span class="legend">({t().legend})</span></th>
          </tr>
        </thead>
        <tbody>
          {#each res.solutions as s, i (i)}
            {@const inTol = Math.abs(s.relError) <= form.tol / 100 + 1e-15}
            <tr class:sel={selected === i} onclick={() => (selected = i)}>
              <td>{i + 1}</td>
              <td class="mono">{formatCapacitance(s.value, 6)}</td>
              <td class="mono">
                <span class="badge" class:in={inTol} class:out={!inTol} title={inTol ? t().within : t().outside}
                  >{formatPercent(s.relError)}</span
                >
              </td>
              <td>{s.parts}</td>
              <td class="net mono">
                <button class="link" onclick={() => (selected = i)}>
                  {formula(
                    s.tree,
                    (k) => (s.leaves[k]!.index !== null ? built.names[s.leaves[k]!.index!]! : formatCapacitance(s.leaves[k]!.value).replace(' ', '')),
                    (id) => coreLabel(coreMap.get(id), i18n.lang),
                  )}
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    {#if res.solutions[selected]}
      {#key `${selected}-${ms}`}
        <SolutionDetail sol={res.solutions[selected]!} rank={selected + 1} cores={res.cores} {built} {form} />
      {/key}
    {/if}
  {/if}
</section>

<style>
  .results {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    min-width: 0;
  }
  .running {
    background: var(--panel);
    border: 1px solid var(--accent);
    border-radius: var(--radius);
    padding: 0.9rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  .head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }
  .head button {
    margin-left: auto;
  }
  .spinner {
    width: 1rem;
    height: 1rem;
    border-radius: 50%;
    border: 2px solid var(--accent-soft);
    border-top-color: var(--accent);
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  @media (prefers-reduced-motion: reduce) {
    .spinner {
      animation: none;
    }
  }
  progress {
    width: 100%;
    height: 0.6rem;
    accent-color: var(--accent);
  }
  .times {
    display: flex;
    justify-content: space-between;
    font-size: 0.85rem;
  }
  .small {
    font-size: 0.82rem;
    margin: 0;
  }
  .stale {
    opacity: 0.45;
  }
  .empty {
    border: 1px dashed var(--line);
    border-radius: var(--radius);
    padding: 2rem clamp(1rem, 4vw, 2.5rem);
    background: var(--panel);
  }
  .empty h2 {
    margin: 0.6rem 0 0.8rem;
    font-size: 1.25rem;
  }
  .empty ol {
    margin: 0 0 1rem;
    padding-left: 1.2rem;
    line-height: 1.7;
  }
  .ex {
    display: flex;
    flex-wrap: wrap;
    gap: 0.45rem;
  }
  .ex button {
    font-size: 0.85rem;
    border-radius: 999px;
    padding: 0.3rem 0.8rem;
  }
  .ex button:hover {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .note {
    margin: 0;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
  }
  .bad {
    background: var(--bad-soft);
    color: var(--bad);
  }
  .summary {
    display: flex;
    flex-wrap: wrap;
    gap: 0.25rem 0.75rem;
    align-items: baseline;
    border-radius: var(--radius);
    padding: 0.7rem 0.9rem;
    border: 1px solid var(--line);
  }
  .summary.ok {
    background: var(--ok-soft);
    border-color: color-mix(in srgb, var(--ok) 35%, transparent);
  }
  .summary.ok strong {
    color: var(--ok);
  }
  .summary.warn {
    background: var(--warn-soft);
    border-color: color-mix(in srgb, var(--warn) 35%, transparent);
  }
  .summary.warn strong {
    color: var(--warn);
  }
  .stats {
    margin-left: auto;
    font-size: 0.82rem;
  }
  .table-wrap {
    overflow: auto;
    max-height: 26rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: var(--panel);
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.9rem;
  }
  th {
    position: sticky;
    top: 0;
    background: var(--panel);
    text-align: left;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    border-bottom: 1px solid var(--line);
    padding: 0.5rem 0.6rem;
  }
  .legend {
    text-transform: none;
    letter-spacing: 0;
    font-weight: 400;
  }
  td {
    padding: 0.4rem 0.6rem;
    border-bottom: 1px solid var(--line);
    white-space: nowrap;
  }
  td.net {
    white-space: normal;
    min-width: 12rem;
  }
  tr {
    cursor: pointer;
  }
  tr:hover td {
    background: color-mix(in srgb, var(--accent-soft) 45%, transparent);
  }
  tr.sel td {
    background: var(--accent-soft);
  }
  .badge {
    border-radius: 6px;
    padding: 0.05rem 0.4rem;
  }
  .badge.in {
    background: var(--ok-soft);
    color: var(--ok);
  }
  .badge.out {
    background: var(--bad-soft);
    color: var(--bad);
  }
  .link {
    border: none;
    background: none;
    padding: 0;
    text-align: left;
    font: inherit;
    color: inherit;
  }
</style>
