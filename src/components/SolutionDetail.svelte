<script lang="ts">
  import katex from 'katex';
  import { i18n, t } from '../lib/i18n.svelte';
  import { formatCapacitance, formatPercent } from '../lib/units';
  import { layout } from '../lib/render/layout';
  import { toSvg } from '../lib/render/svg';
  import { circuitikz, coreLabel, formulaTex, spice } from '../lib/export';
  import { verifySolution } from '../lib/verify';
  import { toleranceInterval } from '../lib/physics';
  import { Frac } from '../lib/exact';
  import type { Built, FormState } from '../lib/form';
  import type { Core, Solution } from '../lib/types';

  interface Props {
    sol: Solution;
    rank: number;
    cores: Core[];
    built: Built;
    form: FormState;
  }
  let { sol, rank, cores, built, form }: Props = $props();

  let hover: number | null = $state(null);
  let copied: string | null = $state(null);

  // Inventory parts have no fixed label: name them by value, as in the table.
  const name = (k: number) => {
    const leaf = sol.leaves[k]!;
    return leaf.index !== null ? built.names[leaf.index]! : formatCapacitance(leaf.value).replace(' ', '');
  };
  const value = (k: number) => formatCapacitance(sol.leaves[k]!.value);
  const leafExact = (k: number) => {
    const leaf = sol.leaves[k]!;
    if (leaf.index !== null) return built.exactValues[leaf.index]!;
    const i = built.names.findIndex((_, j) => built.exactValues[j]!.toNumber() === leaf.value);
    return i >= 0 ? built.exactValues[i]! : Frac.fromNumber(leaf.value);
  };

  const diagram = $derived(layout(sol.tree, cores));
  const svg = $derived(toSvg(diagram.main, (k) => ({ name: name(k), value: value(k) }), { highlight: hover }));
  const subSvgs = $derived(
    diagram.subs.map((s) => ({ label: s.label, svg: toSvg(s.drawing, (k) => ({ name: name(k), value: value(k) }), { highlight: hover }) })),
  );
  const check = $derived(built.exactTarget ? verifySolution(sol, cores, built.exactTarget, leafExact) : null);
  const interval = $derived(toleranceInterval(sol.value, form.partTol / 100));
  const tex = $derived(katex.renderToString(`C_{eq} = ${formulaTex(sol.tree, name, (id) => coreLabel(cores.find((c) => c.id === id), i18n.lang))}`, { throwOnError: false, displayMode: true }));

  /** Per-part rows in the order of the graph edges (= leaf order). */
  const rows = $derived(
    check
      ? sol.graph.edges.map(([, , k], i) => {
          const a = check.analysis;
          // Round-off below 1e-12 V/V (e.g. a balanced bridge) is shown as zero.
          const v = Math.abs(a.voltages[i]!) < 1e-12 ? 0 : Math.abs(a.voltages[i]!);
          return { k, v, q: sol.leaves[k]!.value * v, e: (sol.leaves[k]!.value * v * v) / 2 / a.energy };
        })
      : [],
  );

  function exactText(f: Frac): string {
    // Show in the unit of the target, e.g. "3/2 pF".
    const s = formatCapacitance(sol.value);
    const unit = s.split(' ')[1]!;
    const exp = { fF: -15, pF: -12, nF: -9, µF: -6, mF: -3, F: 0 }[unit] ?? 0;
    const scaled = exp < 0 ? f.mul(new Frac(10n ** BigInt(-exp))) : f;
    return scaled.d === 1n ? `${scaled.n} ${unit}` : `${scaled.n}/${scaled.d} ${unit}`;
  }

  async function copy(kind: string, text: string) {
    await navigator.clipboard.writeText(text);
    copied = kind;
    setTimeout(() => (copied = null), 1500);
  }

  function download(file: string, text: string, type: string) {
    const url = URL.createObjectURL(new Blob([text], { type }));
    const a = document.createElement('a');
    a.href = url;
    a.download = file;
    a.click();
    URL.revokeObjectURL(url);
  }

  const title = $derived(`CapAssigner #${rank}: C_eq = ${formatCapacitance(sol.value, 8)}`);
  const exports = $derived([
    { id: 'spice', label: 'SPICE', file: 'capassigner.cir', type: 'text/plain', text: () => spice(sol, name, title) },
    { id: 'tikz', label: 'CircuiTikZ', file: 'capassigner.tex', type: 'text/x-tex', text: () => circuitikz(diagram, name, value) },
    {
      id: 'svg',
      label: 'SVG',
      file: 'capassigner.svg',
      type: 'image/svg+xml',
      text: () => toSvg(diagram.main, (k) => ({ name: name(k), value: value(k) }), { title }),
    },
    { id: 'json', label: 'JSON', file: 'capassigner.json', type: 'application/json', text: () => JSON.stringify(sol, null, 2) },
  ]);
</script>

<article class="detail">
  <header>
    <h2>{t().detail} #{rank}</h2>
    <span class="mono big">{formatCapacitance(sol.value, 8)}</span>
    <span class="mono muted">{formatPercent(sol.relError, 5)}</span>
  </header>

  <div class="formula">{@html tex}</div>

  <figure>
    <figcaption>{t().diagram}</figcaption>
    <div class="svg">{@html svg}</div>
    {#each subSvgs as s (s.label)}
      <div class="sub">
        <span class="mono">{s.label} =</span>
        <div class="svg">{@html s.svg}</div>
      </div>
    {/each}
  </figure>

  <div class="grid">
    <section class="card">
      <h3>{t().verification}</h3>
      {#if check}
        {#if check.ok}
          <p class="ok">✓ {t().verifiedOk}</p>
        {:else}
          <p class="bad">✗ {t().verifiedBad}: {check.problems.join('; ')}</p>
        {/if}
        {#if check.exact}
          <dl>
            <dt>{t().exactValue}</dt>
            <dd class="mono">{exactText(check.exact)}</dd>
            <dt>{t().exactError}</dt>
            <dd class="mono">{check.exactRelError === 0 ? t().exactZero : formatPercent(check.exactRelError!, 6)}</dd>
          </dl>
        {/if}
      {/if}
    </section>
    <section class="card">
      <h3>{t().interval}</h3>
      <p class="mono">[{formatCapacitance(interval[0], 6)}, {formatCapacitance(interval[1], 6)}]</p>
      <p class="muted small">{t().intervalHint(`${form.partTol} %`)}</p>
      {#if rows.length > 1}
        {@const spread = Math.sqrt(rows.reduce((s, r) => s + r.e * r.e, 0))}
        <p class="stat">
          {t().statSpread}: <b class="mono">±{(form.partTol * spread).toFixed(2)} %</b>
          <span class="muted small">({t().statHint(`${form.partTol} %`, spread.toFixed(3))})</span>
        </p>
      {/if}
    </section>
  </div>

  {#if rows.length}
    <section class="card">
      <h3>{t().parts}</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>{t().colPart}</th><th>{t().colValue}</th><th>{t().colVoltage}</th><th>{t().colCharge}</th><th>{t().colEnergy}</th></tr>
          </thead>
          <tbody>
            {#each rows as r (r.k)}
              <tr onmouseenter={() => (hover = r.k)} onmouseleave={() => (hover = null)}>
                <td><b>{name(r.k)}</b></td>
                <td class="mono">{value(r.k)}</td>
                <td class="mono">
                  <span class="bar" style:--w={`${(r.v * 100).toFixed(1)}%`}></span>{(r.v * 100).toFixed(2)} %
                </td>
                <td class="mono">{r.q === 0 ? '0' : `${formatCapacitance(r.q).replace('F', 'C')}/V`}</td>
                <td class="mono">{(r.e * 100).toFixed(1)} %</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <p class="muted small">{t().partsHint}</p>
    </section>
  {/if}

  <section class="card">
    <h3>{t().export}</h3>
    <div class="exports">
      {#each exports as x (x.id)}
        <div class="exp">
          <span>{x.label}</span>
          <button onclick={() => copy(x.id, x.text())}>{copied === x.id ? t().copied : t().copy}</button>
          <button onclick={() => download(x.file, x.text(), x.type)}>{t().download}</button>
        </div>
      {/each}
      <div class="exp">
        <span>{t().share}</span>
        <button onclick={() => copy('link', location.href)}>{copied === 'link' ? t().copied : t().copy}</button>
      </div>
    </div>
  </section>
</article>

<style>
  .detail {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem;
    min-width: 0;
  }
  header {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem 1rem;
    align-items: baseline;
  }
  h2 {
    margin: 0;
    font-size: 1.05rem;
  }
  h3 {
    margin: 0 0 0.5rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
  }
  .big {
    font-size: 1.25rem;
    font-weight: 600;
  }
  .formula {
    overflow-x: auto;
    overflow-y: hidden;
  }
  figure {
    margin: 0;
  }
  figcaption {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    font-weight: 600;
    margin-bottom: 0.3rem;
  }
  .svg {
    overflow-x: auto;
    background: var(--paper);
    border-radius: 8px;
    padding: 0.5rem;
  }
  .svg :global(svg) {
    display: block;
    max-width: none;
    height: auto;
  }
  .sub {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.5rem;
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
    gap: 1rem;
  }
  .card {
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.75rem;
    min-width: 0;
  }
  .card p {
    margin: 0.2rem 0;
  }
  .ok {
    color: var(--ok);
  }
  .bad {
    color: var(--bad);
  }
  .small {
    font-size: 0.82rem;
  }
  .stat {
    margin-top: 0.5rem !important;
  }
  dl {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0.2rem 0.8rem;
    margin: 0.5rem 0 0;
  }
  dt {
    color: var(--muted);
  }
  dd {
    margin: 0;
    overflow-wrap: anywhere;
  }
  .table-wrap {
    overflow-x: auto;
  }
  table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.88rem;
  }
  th,
  td {
    text-align: left;
    padding: 0.3rem 0.5rem;
    border-bottom: 1px solid var(--line);
    white-space: nowrap;
  }
  th {
    font-size: 0.75rem;
    color: var(--muted);
    text-transform: uppercase;
  }
  .bar {
    display: inline-block;
    width: 3rem;
    height: 0.5rem;
    margin-right: 0.4rem;
    border-radius: 3px;
    background: linear-gradient(to right, var(--accent) var(--w), var(--line) var(--w));
  }
  .exports {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem 1.2rem;
  }
  .exp {
    display: flex;
    align-items: center;
    gap: 0.35rem;
  }
  .exp span {
    font-weight: 600;
    margin-right: 0.2rem;
  }
  .exp button {
    padding: 0.25rem 0.6rem;
    font-size: 0.85rem;
  }
</style>
