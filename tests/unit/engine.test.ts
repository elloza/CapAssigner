// The compiled WASM engine, cross-checked by the independent TS oracle.

import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { cores, solve } from './wasm-engine';
import { verifySolution } from '../../src/lib/verify';
import { Frac } from '../../src/lib/exact';
import { parseCapacitance } from '../../src/lib/units';
import type { SolveRequest, SolveResponse } from '../../src/lib/types';
import golden from '../fixtures/golden_v1.json';

function exactOf(v: number): Frac {
  return Frac.fromNumber(v);
}

/** Every solution passes the oracle and uses its parts legally. */
function checkResponse(req: SolveRequest, res: SolveResponse, exactVals?: Frac[]): void {
  const target = exactOf(req.target);
  for (const s of res.solutions) {
    const leafExact = (k: number) => {
      const leaf = s.leaves[k]!;
      return exactVals && leaf.index !== null ? exactVals[leaf.index]! : exactOf(leaf.value);
    };
    const v = verifySolution(s, res.cores, target, leafExact);
    expect(v.problems).toEqual([]);
    if (req.mode === 'all') {
      const used = s.leaves.map((l) => l.index!).sort((a, b) => a - b);
      expect(used).toEqual(req.values.map((_, i) => i));
      s.leaves.forEach((l) => expect(l.value).toBe(req.values[l.index!]));
    } else {
      expect(s.parts).toBeLessThanOrEqual(req.maxParts ?? 4);
      expect(s.parts).toBeGreaterThanOrEqual(req.minParts ?? 1);
      for (const l of s.leaves) expect(req.values).toContain(l.value);
      if (req.stock) {
        const used = new Map<number, number>();
        for (const l of s.leaves) used.set(l.value, (used.get(l.value) ?? 0) + 1);
        for (const [val, n] of used) {
          const avail = req.values.reduce((acc, x, i) => acc + (x === val ? req.stock![i]! : 0), 0);
          expect(n).toBeLessThanOrEqual(avail);
        }
      }
    }
  }
  const errs = res.solutions.map((s) => Math.abs(s.relError));
  expect([...errs].sort((a, b) => a - b)).toEqual(errs);
}

describe('WASM engine', () => {
  it('ships the core catalog', () => {
    const all = cores(9);
    expect(all.filter((c) => c.edges.length === 5)).toHaveLength(1);
    expect(all.every((c) => c.nv <= 6)).toBe(true);
  });

  it('solves the classroom problem exactly, verified with exact arithmetic', () => {
    const texts = ['3pF', '2pF', '3pF', '1pF'];
    const parsed = texts.map((t) => {
      const r = parseCapacitance(t);
      if (!r.ok) throw new Error(t);
      return r.value;
    });
    const req: SolveRequest = { mode: 'all', values: parsed.map((p) => p.farads), target: 1e-12, topK: 5 };
    const res = solve(req);
    checkResponse(req, res, parsed.map((p) => p.exact));
    const best = res.solutions[0]!;
    const target = (parseCapacitance('1pF') as { ok: true; value: { exact: Frac } }).value.exact;
    const v = verifySolution(best, res.cores, target, (k) => parsed[best.leaves[k]!.index!]!.exact);
    expect(v.exact!.eq(target)).toBe(true);
    expect(res.stats.exhaustive).toBe(true);
  });

  it('the balanced bridge reaches C from five equal parts', () => {
    const req: SolveRequest = { mode: 'all', values: Array(5).fill(10e-9), target: 10e-9, maxCoreEdges: 5 };
    const res = solve(req);
    checkResponse(req, res);
    expect(Math.abs(res.solutions[0]!.relError)).toBeLessThan(1e-12);
    expect(res.solutions[0]!.tree.t).toBe('core');
  });

  it.each(golden.cases.map((c) => [c.id, c] as const))('matches or beats v1 on %s', (_, c) => {
    const req: SolveRequest = { mode: 'all', values: c.capacitors, target: c.target, topK: 3, maxCoreEdges: 7 };
    const res = solve(req);
    checkResponse(req, res);
    expect(Math.abs(res.solutions[0]!.relError)).toBeLessThanOrEqual(c.v1_best_rel_error + 1e-12);
  });

  it('random use-all problems: every result is physically verified', () => {
    fc.assert(
      fc.property(
        fc.array(fc.integer({ min: 1, max: 100 }), { minLength: 1, maxLength: 7 }),
        fc.integer({ min: 1, max: 400 }),
        fc.constantFrom(0, 5, 7),
        (caps, t, cores) => {
          const req: SolveRequest = {
            mode: 'all',
            values: caps.map((c) => c * 1e-12),
            target: t * 1e-12 / 4,
            topK: 8,
            maxCoreEdges: cores,
          };
          checkResponse(req, solve(req));
        },
      ),
      { numRuns: 60 },
    );
  });

  it('random inventory problems respect parts and stock', () => {
    fc.assert(
      fc.property(
        fc.uniqueArray(fc.integer({ min: 1, max: 60 }), { minLength: 1, maxLength: 6 }),
        fc.integer({ min: 1, max: 500 }),
        fc.integer({ min: 1, max: 4 }),
        fc.boolean(),
        fc.array(fc.integer({ min: 0, max: 3 }), { minLength: 6, maxLength: 6 }),
        (vals, t, k, limited, stock) => {
          const req: SolveRequest = {
            mode: 'inventory',
            values: vals.map((v) => v * 1e-9),
            target: (t * 1e-9) / 7,
            maxParts: k,
            topK: 6,
            stock: limited ? stock.slice(0, vals.length) : null,
          };
          const res = solve(req);
          checkResponse(req, res);
        },
      ),
      { numRuns: 60 },
    );
  });

  it('rejects invalid requests with a message', () => {
    expect(() => solve({ mode: 'all', values: [], target: 1 })).toThrow(/no capacitor/);
    expect(() => solve({ mode: 'all', values: [1], target: -1 })).toThrow(/target/);
  });
});

describe('bridge-5 golden case', () => {
  it('reaches 170/71 pF exactly with a bridge; series-parallel stops at 43/18 pF', () => {
    const vals = [1, 2, 3, 4, 5].map((v) => Frac.int(v).div(Frac.int(10 ** 12)));
    const target = new Frac(170n, 71n * 10n ** 12n);
    const base: SolveRequest = { mode: 'all', values: vals.map((v) => v.toNumber()), target: target.toNumber(), topK: 3 };
    for (const [cores, expected] of [
      [0, new Frac(43n, 18n * 10n ** 12n)],
      [5, target],
    ] as const) {
      const res = solve({ ...base, maxCoreEdges: cores });
      const best = res.solutions[0]!;
      const v = verifySolution(best, res.cores, target, (k) => vals[best.leaves[k]!.index!]!);
      expect(v.problems).toEqual([]);
      expect(v.exact!.eq(expected)).toBe(true);
    }
  });
});
