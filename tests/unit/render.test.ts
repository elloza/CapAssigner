// The schematic must be the network it claims to be. A v1 bug drew a shorted
// capacitor and joined plates, so the drawing no longer matched the formula.
// Here the drawing's own geometry (wires, junctions, capacitors) is turned back
// into a circuit and solved by nodal analysis; it must give the formula's value.

import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { layout, type Drawing, type Pt } from '../../src/lib/render/layout';
import { analyze, evalTree } from '../../src/lib/physics';
import type { Core, Tree } from '../../src/lib/types';
import { cores as engineCores } from './wasm-engine';

const key = ([x, y]: Pt) => `${x.toFixed(6)},${y.toFixed(6)}`;

/** Circuit drawn by `d`: union wires (including T-junctions on segments). */
function drawnCircuit(d: Drawing, leafValue: (k: number) => number, boxValue: (label: string) => number) {
  const parent = new Map<string, string>();
  const find = (a: string): string => {
    let r = a;
    while (parent.get(r) !== r) r = parent.get(r)!;
    parent.set(a, r);
    return r;
  };
  const add = (p: Pt) => {
    const k = key(p);
    if (!parent.has(k)) parent.set(k, k);
    return k;
  };
  const union = (a: string, b: string) => parent.set(find(a), find(b));

  const points: Pt[] = [];
  const segments: [Pt, Pt][] = [];
  const elements: { a: Pt; b: Pt; c: number }[] = [];
  let A: Pt | null = null;
  let B: Pt | null = null;
  for (const p of d.prims) {
    if (p.t === 'wire') {
      p.pts.forEach((q) => points.push(q));
      for (let i = 1; i < p.pts.length; i++) segments.push([p.pts[i - 1]!, p.pts[i]!]);
    } else if (p.t === 'cap') {
      elements.push({ a: p.from, b: p.to, c: leafValue(p.leaf) });
      points.push(p.from, p.to);
    } else if (p.t === 'box') {
      elements.push({ a: p.from, b: p.to, c: boxValue(p.label) });
      points.push(p.from, p.to);
    } else if (p.t === 'term') {
      points.push(p.at);
      if (p.name === 'A') A = p.at;
      else B = p.at;
    }
  }
  points.forEach(add);
  const onSeg = ([x, y]: Pt, [[x1, y1], [x2, y2]]: [Pt, Pt]) => {
    const cross = (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1);
    const within = Math.min(x1, x2) - 1e-9 <= x && x <= Math.max(x1, x2) + 1e-9 && Math.min(y1, y2) - 1e-9 <= y && y <= Math.max(y1, y2) + 1e-9;
    return Math.abs(cross) < 1e-6 && within;
  };
  for (const s of segments) {
    union(add(s[0]), add(s[1]));
    for (const p of points) if (onSeg(p, s)) union(add(p), add(s[0]));
  }
  const ids = new Map<string, number>();
  const id = (p: Pt) => {
    const r = find(add(p));
    if (!ids.has(r)) ids.set(r, ids.size);
    return ids.get(r)!;
  };
  const a = id(A!);
  const b = id(B!);
  const edges = elements.map((e) => ({ u: id(e.a), v: id(e.b), c: e.c }));
  return { n: ids.size, a, b, edges };
}

function checkTree(tree: Tree, values: number[], cores: Core[]) {
  const coreMap = new Map(cores.map((c) => [c.id, c]));
  const d = layout(tree, cores);
  // Sub-networks drawn as boxes: their value is the formula value of the subtree.
  const subValue = new Map<string, number>();
  const collect = (t: Tree) => {
    if (t.t === 'core') {
      t.c.forEach((c) => {
        if (c.t !== 'leaf') subValue.set(`N${subValue.size + 1}`, evalTree(c, (k) => values[k]!, coreMap));
      });
    }
    if (t.t !== 'leaf') t.c.forEach(collect);
  };
  collect(tree);
  const circ = drawnCircuit(d.main, (k) => values[k]!, (l) => subValue.get(l)!);
  expect(circ.a).not.toBe(circ.b);
  const drawn = analyze(circ.n, circ.a, circ.b, circ.edges).ceq;
  const formula = evalTree(tree, (k) => values[k]!, coreMap);
  expect(Math.abs(drawn - formula) / formula).toBeLessThan(1e-9);
  // No capacitor may be shorted (both plates on the same node).
  for (const e of circ.edges) expect(e.u).not.toBe(e.v);
}

/** Random series-parallel tree over leaves 0..n−1. */
const spTree = (n: number): fc.Arbitrary<Tree> =>
  fc.array(fc.tuple(fc.nat(), fc.boolean()), { minLength: n - 1, maxLength: n - 1 }).map((steps) => {
    let pool: Tree[] = Array.from({ length: n }, (_, k) => ({ t: 'leaf', k }) as Tree);
    for (const [pick, ser] of steps) {
      const i = pick % pool.length;
      const a = pool.splice(i, 1)[0]!;
      const j = (pick >> 3) % pool.length;
      const b = pool.splice(j, 1)[0]!;
      const op = ser ? 'series' : 'parallel';
      const flat = (x: Tree): Tree[] => (x.t === op ? x.c : [x]);
      pool.push({ t: op, c: [...flat(a), ...flat(b)] } as Tree);
    }
    return pool[0]!;
  });

describe('schematic = network', () => {
  it('the network from the v1 bug report is drawn correctly', () => {
    // (((C1 — ((C3 — C7) ∥ C5) — C8) ∥ C2) — (C4 ∥ C6)), 958 nF.
    const values = [500e-9, 500e-9, 32e-6, 32e-6, 5e-6, 5e-6, 40e-6, 40e-6];
    const L = (k: number): Tree => ({ t: 'leaf', k: k - 1 });
    const tree: Tree = {
      t: 'series',
      c: [
        {
          t: 'parallel',
          c: [{ t: 'series', c: [L(1), { t: 'parallel', c: [{ t: 'series', c: [L(3), L(7)] }, L(5)] }, L(8)] }, L(2)],
        },
        { t: 'parallel', c: [L(4), L(6)] },
      ],
    };
    checkTree(tree, values, []);
    const v = evalTree(tree, (k) => values[k]!, new Map());
    expect(Math.round(v * 1e9)).toBe(958);
  });

  it('random series-parallel networks', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 9 }).chain((n) => fc.tuple(spTree(n), fc.array(fc.integer({ min: 1, max: 99 }), { minLength: n, maxLength: n }))),
        ([tree, vals]) => checkTree(tree, vals, []),
      ),
      { numRuns: 300 },
    );
  });

  it('every core, with leaves and with sub-networks on its edges', () => {
    for (const core of engineCores(9)) {
      const m = core.edges.length;
      const leaves: Tree = { t: 'core', core: core.id, c: core.edges.map((_, k) => ({ t: 'leaf', k })) };
      checkTree(leaves, Array.from({ length: m }, (_, k) => k + 1), [core]);
      // First edge holds a parallel pair (drawn as a box N1).
      const withSub: Tree = {
        t: 'series',
        c: [
          { t: 'core', core: core.id, c: [{ t: 'parallel', c: [{ t: 'leaf', k: 0 }, { t: 'leaf', k: m }] }, ...core.edges.slice(1).map((_, k) => ({ t: 'leaf', k: k + 1 }) as Tree)] },
          { t: 'leaf', k: m + 1 },
        ],
      };
      checkTree(withSub, Array.from({ length: m + 2 }, (_, k) => 2 * k + 3), [core]);
    }
  });
});
