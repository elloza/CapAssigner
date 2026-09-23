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
export const MAX_CORE_PARTS = 9;
export const MAX_ALL_PARTS = 12;
/** Beyond 6 parts an E-series already hits targets exactly and time grows fast. */
export const MAX_INVENTORY_PARTS = 6;
/** Stored-value budget for inventory searches (smaller sets, much faster). */
const INVENTORY_BUDGET = 1_000_000;

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
  };
  if (errors.length || !tr.ok || values.length === 0 || tooMany) return { req: null, ...base };
  const limited = stock.some((c) => c !== null);
  const req: SolveRequest = {
    mode: f.mode,
    values: values.map((v) => v.farads),
    target: tr.value.farads,
    topK: f.topK,
    maxCoreEdges: coresDropped ? 0 : coreEdges,
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
