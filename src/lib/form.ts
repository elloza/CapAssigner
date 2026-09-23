// Form state, its URL-hash encoding (shareable links) and request building.

import { Frac } from './exact';
import { seriesValues, type Series } from './eseries';
import { parseCapacitance, parseList, tokenize, type ParseError, type Parsed, type Prefix } from './units';
import type { Mode, SolveRequest } from './types';

export type Topo = 'sp' | 'bridge' | 'all';

export interface FormState {
  mode: Mode;
  target: string;
  caps: string;
  unit: Prefix;
  source: 'series' | 'custom';
  series: Series;
  /** Decades as powers of ten in farads, [from, to). */
  decFrom: number;
  decTo: number;
  inventory: string;
  maxParts: number;
  minParts: number;
  topo: Topo;
  /** Percent. */
  tol: number;
  partTol: number;
  topK: number;
}

export const DEFAULT_FORM: FormState = {
  mode: 'all',
  target: '1pF',
  caps: '3pF 2pF 3pF 1pF',
  unit: 'p',
  source: 'series',
  series: 'E12',
  decFrom: -12,
  decTo: -9,
  inventory: '1pF×4 2.2pF×2 4.7pF×2 10pF×3',
  maxParts: 3,
  minParts: 1,
  topo: 'all',
  tol: 1,
  partTol: 5,
  topK: 20,
};

/** Largest "use all" problem for which non-series-parallel cores are explored. */
export const MAX_CORE_PARTS = 8;
export const MAX_ALL_PARTS = 12;
/** Beyond 6 parts an E-series already hits targets exactly and time grows fast. */
export const MAX_INVENTORY_PARTS = 6;
/** Stored-value budget for inventory searches (smaller sets, much faster). */
const INVENTORY_BUDGET = 1_000_000;

/**
 * Stored-value budget for "use all" searches, scaled to the device: each
 * value takes ~24 bytes plus working buffers, so 6 M values peak at a few
 * hundred MB of WASM memory, too much for small phones.
 */
export function memoryBudget(): number {
  const gb = typeof navigator !== 'undefined' ? ((navigator as { deviceMemory?: number }).deviceMemory ?? 8) : 8;
  return gb >= 8 ? 6_000_000 : gb >= 4 ? 3_000_000 : 1_500_000;
}

export const EXAMPLES: { id: string; es: string; en: string; form: Partial<FormState> }[] = [
  {
    id: 'classroom',
    es: 'Ejercicio de clase: 3, 2, 3, 1 pF → 1 pF',
    en: 'Classroom: 3, 2, 3, 1 pF → 1 pF',
    form: { mode: 'all', caps: '3pF 2pF 3pF 1pF', target: '1pF', topo: 'all' },
  },
  {
    id: 'bridge',
    es: 'Cinco iguales → C (solo con puente)',
    en: 'Five equal → C (needs a bridge)',
    form: { mode: 'all', caps: '10nF 10nF 10nF 10nF 10nF', target: '10nF', topo: 'all' },
  },
  {
    id: 'bridge5',
    es: 'Puente 1–5 pF → 170/71 pF (SP se queda a 0,23 %)',
    en: 'Bridge 1–5 pF → 170/71 pF (SP misses by 0.23 %)',
    form: { mode: 'all', caps: '1pF 2pF 3pF 4pF 5pF', target: '170/71pF', topo: 'all' },
  },
  {
    id: 'pdf1',
    es: 'Ejercicio PDF 01: 15, 3, 6, 20 µF',
    en: 'PDF exercise 01: 15, 3, 6, 20 µF',
    form: { mode: 'all', caps: '15µF 3µF 6µF 20µF', target: '5.9649µF', topo: 'all' },
  },
  {
    id: 'e12',
    es: 'Inventario E12: 3,14 pF con ≤ 3 piezas',
    en: 'E12 inventory: 3.14 pF with ≤ 3 parts',
    form: { mode: 'inventory', source: 'series', series: 'E12', decFrom: -12, decTo: -10, target: '3.14pF', maxParts: 3 },
  },
  {
    id: 'stock',
    es: 'Cajón limitado: 7,5 pF',
    en: 'Limited drawer: 7.5 pF',
    form: { mode: 'inventory', source: 'custom', inventory: '1pF×4 2.2pF×2 4.7pF×2 10pF×3', target: '7.5pF', maxParts: 4 },
  },
];

export function toHash(f: FormState): string {
  const p = new URLSearchParams();
  (Object.keys(DEFAULT_FORM) as (keyof FormState)[]).forEach((k) => {
    if (f[k] !== DEFAULT_FORM[k]) p.set(k, String(f[k]));
  });
  return p.toString();
}

export function fromHash(hash: string): FormState {
  const p = new URLSearchParams(hash.replace(/^#/, ''));
  const f: FormState = { ...DEFAULT_FORM };
  for (const [k, v] of p) {
    if (!(k in DEFAULT_FORM)) continue;
    const key = k as keyof FormState;
    const d = DEFAULT_FORM[key];
    (f as unknown as Record<string, unknown>)[key] = typeof d === 'number' ? Number(v) || d : v;
  }
  return f;
}

export interface InventoryItem {
  parsed: Parsed;
  /** null = unlimited */
  count: number | null;
}

export function parseInventory(text: string, unit: Prefix): { items: InventoryItem[]; errors: ParseError[] } {
  const items: InventoryItem[] = [];
  const errors: ParseError[] = [];
  for (const tok of tokenize(text)) {
    const m = /^(.*?)(?:[×xX*](\d+))?$/.exec(tok)!;
    const r = parseCapacitance(m[1]!, unit);
    if (r.ok) items.push({ parsed: r.value, count: m[2] === undefined ? null : Number(m[2]) });
    else errors.push(r.error);
  }
  return { items, errors };
}

/**
 * Sanity checks on the input, run before searching. `warn` findings are
 * advice (the search still runs); `block` ones stop it with an explanation.
 */
export type Check =
  | { level: 'warn'; code: 'unreachableLow' | 'unreachableHigh'; min: number; max: number }
  | { level: 'warn'; code: 'spread'; decades: number }
  | { level: 'warn'; code: 'tiny'; value: number }
  | { level: 'warn'; code: 'huge'; value: number }
  | { level: 'block'; code: 'ratio' }
  | { level: 'block'; code: 'classes'; count: number };

/** Below this a "capacitor" is smaller than typical stray capacitance. */
const TINY = 1e-13;
/** Above this it is a supercapacitor: probably a unit slip. */
const HUGE = 1;
/** More decades than this between parts is almost surely a unit mistake. */
const SPREAD_DECADES = 6;
/** Largest number of distinct values the engine accepts with limited stock. */
const MAX_LIMITED_CLASSES = 32;

export function sanityChecks(
  mode: Mode,
  values: number[],
  target: number,
  maxParts: number,
  limitedStock: boolean,
): Check[] {
  const out: Check[] = [];
  if (values.length === 0 || !(target > 0)) return out;
  const lo = Math.min(...values);
  const hi = Math.max(...values);
  if (values.some((v) => !(v / target >= 1e-150 && v / target <= 1e150))) out.push({ level: 'block', code: 'ratio' });
  const distinct = new Set(values).size;
  if (mode === 'inventory' && limitedStock && distinct > MAX_LIMITED_CLASSES)
    out.push({ level: 'block', code: 'classes', count: distinct });
  // Reachable range: every network lies between "all in series" and "all in parallel".
  const [min, max] =
    mode === 'all'
      ? [1 / values.reduce((s, v) => s + 1 / v, 0), values.reduce((s, v) => s + v, 0)]
      : [lo / maxParts, hi * maxParts];
  if (target < min * (1 - 1e-12)) out.push({ level: 'warn', code: 'unreachableLow', min, max });
  else if (target > max * (1 + 1e-12)) out.push({ level: 'warn', code: 'unreachableHigh', min, max });
  const decades = Math.log10(hi / lo);
  if (decades > SPREAD_DECADES) out.push({ level: 'warn', code: 'spread', decades: Math.round(decades) });
  if (lo < TINY) out.push({ level: 'warn', code: 'tiny', value: lo });
  if (hi > HUGE) out.push({ level: 'warn', code: 'huge', value: hi });
  return out;
}

export interface Built {
  req: SolveRequest | null;
  errors: ParseError[];
  /** Exact value of each request value, from the text typed. */
  exactValues: Frac[];
  exactTarget: Frac | null;
  /** Names for each request value (C1… in mode all, the value otherwise). */
  names: string[];
  /** Cores were requested but switched off for size. */
  coresDropped: boolean;
  tooMany: boolean;
  checks: Check[];
}

export function buildRequest(f: FormState): Built {
  const errors: ParseError[] = [];
  const tr = parseCapacitance(f.target, f.unit);
  if (!tr.ok) errors.push(tr.error);
  let values: Parsed[] = [];
  let stock: (number | null)[] = [];
  if (f.mode === 'all') {
    const r = parseList(f.caps, f.unit);
    values = r.values;
    errors.push(...r.errors);
  } else if (f.source === 'series') {
    values = seriesValues(f.series, f.decFrom, f.decTo).map((s) => {
      const r = parseCapacitance(s);
      if (!r.ok) throw new Error(`bad series value ${s}`);
      return r.value;
    });
    stock = values.map(() => null);
  } else {
    const r = parseInventory(f.inventory, f.unit);
    values = r.items.map((i) => i.parsed);
    stock = r.items.map((i) => i.count);
    errors.push(...r.errors);
  }
  const parts = f.mode === 'all' ? values.length : f.maxParts;
  const wantsCores = f.topo !== 'sp';
  const coreEdges = f.topo === 'sp' ? 0 : f.topo === 'bridge' ? 5 : 9;
  const coresDropped = wantsCores && parts > MAX_CORE_PARTS;
  const tooMany = f.mode === 'all' ? values.length > MAX_ALL_PARTS : f.maxParts > MAX_INVENTORY_PARTS;
  const names = values.map((v, i) => (f.mode === 'all' ? `C${i + 1}` : v.text.replace(' ', '')));
  const base = {
    errors,
    exactValues: values.map((v) => v.exact),
    exactTarget: tr.ok ? tr.value.exact : null,
    names,
    coresDropped,
    tooMany,
    checks: tr.ok
      ? sanityChecks(
          f.mode,
          values.map((v) => v.farads),
          tr.value.farads,
          f.maxParts,
          f.mode === 'inventory' && stock.some((c) => c !== null),
        )
      : [],
  };
  const blocked = base.checks.some((c) => c.level === 'block');
  if (errors.length || !tr.ok || values.length === 0 || tooMany || blocked) return { req: null, ...base };
  const limited = stock.some((c) => c !== null);
  const req: SolveRequest = {
    mode: f.mode,
    values: values.map((v) => v.farads),
    target: tr.value.farads,
    topK: f.topK,
    maxCoreEdges: coresDropped ? 0 : coreEdges,
    maxEntries: memoryBudget(),
    ...(f.mode === 'inventory'
      ? {
          maxParts: f.maxParts,
          minParts: Math.min(f.minParts, f.maxParts),
          stock: limited ? stock.map((c) => c ?? f.maxParts) : null,
          maxEntries: INVENTORY_BUDGET,
        }
      : {}),
  };
  return { req, ...base };
}
