<script lang="ts">
  // Where the solutions fall relative to the target: signed relative error on a
  // symmetric-log axis (so 0.001 % and 10 % are both readable), one row per
  // part count, the acceptable-error band shaded. Dots select a solution.
  import { t } from '../lib/i18n.svelte';
  import { formatCapacitance, formatPercent, localNumber } from '../lib/units';
  import type { Solution } from '../lib/types';

  interface Props {
    solutions: Solution[];
    /** Acceptable error, relative (0.01 = 1 %). */
    tol: number;
    selected: number;
    onselect: (i: number) => void;
  }
  let { solutions, tol, selected, onselect }: Props = $props();

  const W = 640;
  const PAD_L = 76;
  const PAD_R = 20;
  const ROW = 30;
  const TOP = 26;
  const BOTTOM = 34;
  /** Linear zone of the symlog axis: 0.001 %. */
  const LIN = 1e-5;

  const f = (e: number) => Math.sign(e) * Math.log10(1 + Math.abs(e) / LIN);

  const rows = $derived([...new Set(solutions.map((s) => s.parts))].sort((a, b) => a - b));
  const span = $derived(Math.max(f(tol) * 1.15, ...solutions.map((s) => Math.abs(f(s.relError)) * 1.08), f(1e-4)));
  const H = $derived(TOP + rows.length * ROW + BOTTOM);
  const x = (e: number) => PAD_L + ((f(e) + span) / (2 * span)) * (W - PAD_L - PAD_R);
  const y = (parts: number) => TOP + rows.indexOf(parts) * ROW + ROW / 2;

  const ticks = $derived(
    [0, 1e-4, 1e-3, 1e-2, 1e-1, 1].flatMap((v) => (v === 0 ? [0] : [-v, v])).filter((v) => Math.abs(f(v)) <= span),
  );

  let hover: number | null = $state(null);

  function tickLabel(v: number): string {
    if (v === 0) return '0';
    return `${v > 0 ? '+' : '−'}${localNumber(String(+(Math.abs(v) * 100).toPrecision(2)))}%`;
  }
</script>

<figure class="chart">
  <figcaption>{t().chartTitle}</figcaption>
  <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={t().chartTitle}>
    <!-- acceptable-error band -->
    <rect class="band" x={x(-tol)} y={TOP - 6} width={x(tol) - x(-tol)} height={rows.length * ROW + 12} rx="4" />
    <text class="band-label" x={Math.min(x(tol) + 4, W - PAD_R - 40)} y={TOP - 10}>±{localNumber(String(+(tol * 100).toPrecision(3)))} %</text>

    {#each ticks as v (v)}
      <line class="grid" x1={x(v)} x2={x(v)} y1={TOP - 6} y2={TOP + rows.length * ROW + 6} />
      <text class="tick" x={x(v)} y={H - 14} text-anchor="middle">{tickLabel(v)}</text>
    {/each}
    <line class="target" x1={x(0)} x2={x(0)} y1={TOP - 8} y2={TOP + rows.length * ROW + 8} />
    <text class="target-label" x={x(0) + 4} y={TOP - 10}>{t().chartTarget}</text>

    {#each rows as p (p)}
      <text class="row" x={PAD_L - 10} y={y(p) + 4} text-anchor="end">{t().chartParts(p)}</text>
    {/each}

    {#each solutions as s, i (i)}
      <g
        class="pt"
        class:sel={i === selected}
        role="button"
        tabindex="0"
        aria-label={`#${i + 1} ${formatCapacitance(s.value, 6)} ${formatPercent(s.relError)}`}
        onclick={() => onselect(i)}
        onkeydown={(e) => (e.key === 'Enter' || e.key === ' ') && onselect(i)}
        onmouseenter={() => (hover = i)}
        onmouseleave={() => (hover = null)}
      >
        <circle class="hit" cx={x(s.relError)} cy={y(s.parts)} r="11" />
        <circle class="dot" cx={x(s.relError)} cy={y(s.parts)} r={i === selected ? 6 : 4.5} />
      </g>
    {/each}

    {#if hover !== null && solutions[hover]}
      {@const s = solutions[hover]!}
      {@const tx = Math.min(Math.max(x(s.relError), PAD_L + 70), W - PAD_R - 70)}
      <g class="tip" transform={`translate(${tx} ${y(s.parts) - 16})`}>
        <rect x="-70" y="-26" width="140" height="22" rx="5" />
        <text x="0" y="-11" text-anchor="middle">#{hover + 1} · {formatCapacitance(s.value, 5)} · {formatPercent(s.relError, 2)}</text>
      </g>
    {/if}
  </svg>
  <p class="muted note">{t().chartNote}</p>
</figure>

<style>
  .chart {
    margin: 0;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.7rem 0.9rem 0.5rem;
  }
  figcaption {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
  }
  svg {
    width: 100%;
    height: auto;
    display: block;
  }
  .band {
    fill: var(--ok-soft);
  }
  .band-label,
  .target-label,
  .tick,
  .row {
    font: 11px var(--sans);
    fill: var(--muted);
  }
  .band-label {
    fill: var(--ok);
  }
  .grid {
    stroke: var(--line);
    stroke-width: 1;
  }
  .target {
    stroke: var(--ink);
    stroke-width: 1.5;
    stroke-dasharray: 3 3;
  }
  .target-label {
    fill: var(--ink);
    font-weight: 600;
  }
  .pt {
    cursor: pointer;
    outline: none;
  }
  .hit {
    fill: transparent;
  }
  .dot {
    fill: var(--accent);
    stroke: var(--panel);
    stroke-width: 2;
    opacity: 0.75;
  }
  .pt:hover .dot,
  .pt:focus-visible .dot {
    opacity: 1;
  }
  .pt.sel .dot {
    opacity: 1;
    stroke: var(--ink);
  }
  .tip rect {
    fill: var(--ink);
  }
  .tip text {
    font: 11px var(--mono);
    fill: var(--panel);
  }
  .note {
    font-size: 0.8rem;
    margin: 0.2rem 0 0;
  }
</style>
