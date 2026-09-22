<script lang="ts">
  import { i18n, t } from '../lib/i18n.svelte';
  import { DEFAULT_FORM, EXAMPLES, MAX_ALL_PARTS, MAX_INVENTORY_PARTS, type Built, type FormState } from '../lib/form';
  import { formatCapacitance, parseList, UNITS, type ParseError } from '../lib/units';
  import type { Series } from '../lib/eseries';

  interface Props {
    form: FormState;
    built: Built;
    running: boolean;
    progress: number;
    onsolve: () => void;
    oncancel: () => void;
  }
  let { form = $bindable(), built, running, progress, onsolve, oncancel }: Props = $props();

  const series: Series[] = ['E3', 'E6', 'E12', 'E24', 'E48', 'E96'];
  const decades = Array.from({ length: 16 }, (_, i) => i - 15);

  const chips = $derived(form.mode === 'all' ? parseList(form.caps, form.unit).values : []);

  function errText(e: ParseError): string {
    return e.code === 'empty' ? '∅' : e.input;
  }

  function loadExample(id: string) {
    const ex = EXAMPLES.find((e) => e.id === id);
    if (ex) form = { ...DEFAULT_FORM, ...ex.form };
  }

  function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!running) onsolve();
  }
</script>

<form class="panel" onsubmit={submit} aria-label={t().tabSolve}>
  <label class="examples">
    <span>{t().examples}</span>
    <select value="" onchange={(e) => loadExample((e.currentTarget as HTMLSelectElement).value)}>
      <option value="" disabled>—</option>
      {#each EXAMPLES as ex (ex.id)}
        <option value={ex.id}>{ex[i18n.lang]}</option>
      {/each}
    </select>
  </label>

  <fieldset class="mode">
    <legend>{t().mode}</legend>
    <label class:on={form.mode === 'all'}>
      <input type="radio" name="mode" value="all" bind:group={form.mode} />
      <strong>{t().modeAll}</strong>
      <small class="muted">{t().modeAllHint}</small>
    </label>
    <label class:on={form.mode === 'inventory'}>
      <input type="radio" name="mode" value="inventory" bind:group={form.mode} />
      <strong>{t().modeInventory}</strong>
      <small class="muted">{t().modeInventoryHint}</small>
    </label>
  </fieldset>

  <div class="row">
    <label class="grow">
      <span>{t().target}</span>
      <input class="mono" bind:value={form.target} autocomplete="off" spellcheck="false" />
    </label>
    <label>
      <span>{t().defaultUnit}</span>
      <select bind:value={form.unit}>
        {#each UNITS as u (u)}<option value={u}>{u}F</option>{/each}
      </select>
    </label>
  </div>

  {#if form.mode === 'all'}
    <label>
      <span>{t().capacitors} <em class="muted">({chips.length}/{MAX_ALL_PARTS})</em></span>
      <textarea rows="3" bind:value={form.caps} spellcheck="false"></textarea>
      <small class="muted">{t().capacitorsHint}</small>
    </label>
    {#if chips.length}
      <ul class="chips" aria-label={t().capacitors}>
        {#each chips as c, i (i)}<li><b>C{i + 1}</b> {formatCapacitance(c.farads)}</li>{/each}
      </ul>
    {/if}
  {:else}
    <fieldset>
      <legend>{t().inventorySource}</legend>
      <div class="seg">
        <label class:on={form.source === 'series'}><input type="radio" value="series" bind:group={form.source} />{t().eSeries}</label>
        <label class:on={form.source === 'custom'}><input type="radio" value="custom" bind:group={form.source} />{t().customList}</label>
      </div>
      {#if form.source === 'series'}
        <div class="row">
          <label>
            <span>{t().eSeries}</span>
            <select bind:value={form.series}>{#each series as s (s)}<option>{s}</option>{/each}</select>
          </label>
          <label>
            <span>{t().decades}: {t().from}</span>
            <select bind:value={form.decFrom}>
              {#each decades as d (d)}<option value={d}>{formatCapacitance(10 ** d)}</option>{/each}
            </select>
          </label>
          <label>
            <span>{t().to}</span>
            <select bind:value={form.decTo}>
              {#each decades.filter((d) => d > form.decFrom) as d (d)}<option value={d}>{formatCapacitance(10 ** d)}</option>{/each}
            </select>
          </label>
        </div>
      {:else}
        <label>
          <textarea rows="3" bind:value={form.inventory} spellcheck="false"></textarea>
          <small class="muted">{t().stockHint}</small>
        </label>
      {/if}
    </fieldset>
    <div class="row">
      <label>
        <span>{t().minParts}</span>
        <input type="number" min="1" max={form.maxParts} bind:value={form.minParts} />
      </label>
      <label>
        <span>{t().maxParts}</span>
        <input type="number" min="1" max={MAX_INVENTORY_PARTS} bind:value={form.maxParts} />
      </label>
    </div>
  {/if}

  <label>
    <span>{t().topology}</span>
    <select bind:value={form.topo}>
      <option value="sp">{t().topoSP}</option>
      <option value="bridge">{t().topoBridge}</option>
      <option value="all">{t().topoAll}</option>
    </select>
    <small class="muted">{built.coresDropped ? t().topoDisabled : t().topoHint}</small>
  </label>

  <div class="row">
    <label>
      <span>{t().tolerance} (%)</span>
      <input type="number" min="0" step="0.1" bind:value={form.tol} />
    </label>
    <label>
      <span>{t().partTolerance} (%)</span>
      <input type="number" min="0" step="0.5" bind:value={form.partTol} />
    </label>
    <label>
      <span>{t().results}</span>
      <input type="number" min="1" max="200" bind:value={form.topK} />
    </label>
  </div>

  {#if built.errors.length}
    <p class="err" role="alert">{t().errorsIn}: <span class="mono">{built.errors.map(errText).join(', ')}</span></p>
  {/if}
  {#if built.tooMany}
    <p class="err" role="alert">max {form.mode === 'all' ? MAX_ALL_PARTS : MAX_INVENTORY_PARTS}</p>
  {/if}

  <div class="actions">
    {#if running}
      <button type="button" onclick={oncancel}>{t().cancel}</button>
      <progress max="1" value={progress} aria-label={t().progress}></progress>
    {:else}
      <button class="primary" type="submit" disabled={!built.req}>{t().solve}</button>
    {/if}
  </div>
</form>

<style>
  .panel {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 1rem;
    position: sticky;
    top: 1rem;
  }
  @media (max-width: 900px) {
    .panel {
      position: static;
    }
  }
  label {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    font-size: 0.9rem;
  }
  label > span {
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
  }
  fieldset {
    border: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  legend {
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--muted);
    margin-bottom: 0.35rem;
  }
  .mode label {
    display: grid;
    grid-template-columns: auto 1fr;
    column-gap: 0.5rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.55rem 0.7rem;
    cursor: pointer;
  }
  .mode label.on {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .mode input {
    width: auto;
    grid-row: span 2;
    margin-top: 0.25rem;
  }
  .mode small {
    grid-column: 2;
  }
  .seg {
    display: flex;
    gap: 0.4rem;
  }
  .seg label {
    flex-direction: row;
    align-items: center;
    gap: 0.35rem;
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.35rem 0.6rem;
    cursor: pointer;
  }
  .seg label.on {
    border-color: var(--accent);
    background: var(--accent-soft);
  }
  .seg input {
    width: auto;
  }
  .row {
    display: flex;
    gap: 0.6rem;
  }
  .row > label {
    flex: 1 1 0;
    min-width: 0;
  }
  .row > .grow {
    flex: 2 1 0;
  }
  .examples {
    flex-direction: row;
    align-items: center;
    gap: 0.5rem;
  }
  .examples select {
    flex: 1;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 0.3rem;
    list-style: none;
    margin: -0.4rem 0 0;
    padding: 0;
    font-size: 0.8rem;
  }
  .chips li {
    background: var(--paper);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 0.05rem 0.55rem;
  }
  .chips b {
    color: var(--accent);
  }
  .err {
    margin: 0;
    color: var(--bad);
    background: var(--bad-soft);
    border-radius: 8px;
    padding: 0.45rem 0.6rem;
    font-size: 0.88rem;
  }
  .actions {
    display: flex;
    gap: 0.7rem;
    align-items: center;
  }
  .actions .primary {
    flex: 1;
    padding: 0.6rem;
  }
  progress {
    flex: 1;
    accent-color: var(--accent);
  }
</style>
