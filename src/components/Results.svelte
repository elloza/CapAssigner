<script lang="ts">
  import { i18n, t } from '../lib/i18n.svelte';
  import { formatCapacitance, formatPercent } from '../lib/units';
  import { coreLabel, formula } from '../lib/export';
  import type { Built, FormState } from '../lib/form';
  import type { SolveResponse } from '../lib/types';
  import SolutionDetail from './SolutionDetail.svelte';

  interface Props {
    result: { res: SolveResponse; ms: number; built: Built; form: FormState } | null;
    error: string | null;
    running: boolean;
  }
  let { result, error, running }: Props = $props();

  let selected = $state(0);
  $effect(() => {
    // New result → show its best solution.
    void result;
    selected = 0;
  });

  const coreMap = $derived(new Map((result?.res.cores ?? []).map((c) => [c.id, c])));
</script>

<section class="results" aria-live="polite">
  {#if error}
    <p class="note bad">{error}</p>
  {/if}
  {#if !result}
    <div class="empty muted">{running ? t().computing : t().noResults}</div>
  {:else}
    {@const { res, ms, built, form } = result}
    {@const st = res.stats}
    <div class="summary" class:ok={st.exhaustive} class:warn={!st.exhaustive}>
      <strong>{st.exhaustive ? t().exhaustive : t().approximate}</strong>
      <span>
        {#if st.exhaustive}{t().exhaustiveHint}{:else}{t().approximateHint} {formatPercent(st.boundRel)}.{/if}
      </span>
      <span class="muted stats">{t().stats(st.states, st.entries, ms)}</span>
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>{t().colRank}</th>
            <th>{t().colCeq}</th>
            <th>{t().colError}</th>
            <th>{t().colParts}</th>
            <th class="net">{t().colNetwork}</th>
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
  .empty {
    border: 1px dashed var(--line);
    border-radius: var(--radius);
    padding: 3rem 1rem;
    text-align: center;
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
