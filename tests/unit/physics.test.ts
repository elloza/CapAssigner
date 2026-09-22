// Physics consistency of the independent oracle on random networks.

import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { analyze, ceqExact, type WEdge } from '../../src/lib/physics';
import { Frac, parallel, series } from '../../src/lib/exact';

/** Random connected network: a random spanning tree over n nodes plus extra edges. */
const network = fc
  .integer({ min: 2, max: 7 })
  .chain((n) =>
    fc.record({
      n: fc.constant(n),
      tree: fc.array(fc.nat(), { minLength: n - 1, maxLength: n - 1 }),
      extra: fc.array(fc.tuple(fc.nat(n - 1), fc.nat(n - 1)), { maxLength: 8 }),
      caps: fc.array(fc.integer({ min: 1, max: 50 }), { minLength: n - 1 + 8, maxLength: n - 1 + 8 }),
    }),
  )
  .map(({ n, tree, extra, caps }) => {
    const pairs: [number, number][] = [];
    for (let i = 1; i < n; i++) pairs.push([tree[i - 1]! % i, i]);
    for (const [u, v] of extra) if (u !== v) pairs.push([u, v]);
    const edges: WEdge<number>[] = pairs.map(([u, v], i) => ({ u, v, c: caps[i]! }));
    return { n, edges };
  });

const rel = (a: number, b: number) => Math.abs(a - b) / Math.max(Math.abs(a), Math.abs(b), 1e-300);

describe('nodal oracle', () => {
  it('series and parallel formulas', () => {
    expect(analyze(3, 0, 1, [{ u: 0, v: 2, c: 2 }, { u: 2, v: 1, c: 2 }]).ceq).toBeCloseTo(1, 14);
    expect(analyze(2, 0, 1, [{ u: 0, v: 1, c: 2 }, { u: 0, v: 1, c: 3 }]).ceq).toBe(5);
  });

  it('Wheatstone bridge: balanced middle element carries no charge', () => {
    // A=0, B=1, x=2, y=3; ratios 1:2 on both sides.
    const e = [
      { u: 0, v: 2, c: 2 },
      { u: 2, v: 1, c: 4 },
      { u: 0, v: 3, c: 3 },
      { u: 3, v: 1, c: 6 },
      { u: 2, v: 3, c: 17 },
    ];
    const r = analyze(4, 0, 1, e);
    expect(Math.abs(r.charges[4]!)).toBeLessThan(1e-12);
    expect(r.ceq).toBeCloseTo(2 * 4 / 6 + 3 * 6 / 9, 12);
  });

  it('Y–Δ transformation preserves C_eq', () => {
    fc.assert(
      fc.property(fc.array(fc.integer({ min: 1, max: 30 }), { minLength: 5, maxLength: 5 }), ([a, b, c, x, y]) => {
        // Star (capacitances a,b,c from centre 3 to nodes 0,1,2) → delta.
        const s = a! + b! + c!;
        const star = [
          { u: 3, v: 0, c: a! },
          { u: 3, v: 1, c: b! },
          { u: 3, v: 2, c: c! },
          { u: 0, v: 2, c: x! },
          { u: 2, v: 1, c: y! },
        ];
        const delta = [
          { u: 0, v: 1, c: (a! * b!) / s },
          { u: 1, v: 2, c: (b! * c!) / s },
          { u: 0, v: 2, c: (a! * c!) / s },
          { u: 0, v: 2, c: x! },
          { u: 2, v: 1, c: y! },
        ];
        return rel(analyze(4, 0, 1, star).ceq, analyze(3, 0, 1, delta).ceq) < 1e-12;
      }),
    );
  });

  it('energy balance and charge conservation', () => {
    fc.assert(
      fc.property(network, ({ n, edges }) => {
        const r = analyze(n, 0, 1, edges);
        return rel(2 * r.energy, r.ceq) < 1e-10 && r.residual < 1e-10;
      }),
    );
  });

  it('bounds: series of all ≤ C_eq ≤ sum of all', () => {
    fc.assert(
      fc.property(network, ({ n, edges }) => {
        const c = analyze(n, 0, 1, edges).ceq;
        const lo = 1 / edges.reduce((s, e) => s + 1 / e.c, 0);
        const hi = edges.reduce((s, e) => s + e.c, 0);
        return c >= lo * (1 - 1e-12) && c <= hi * (1 + 1e-12);
      }),
    );
  });

  it('reciprocity: swapping the terminals changes nothing', () => {
    fc.assert(
      fc.property(network, ({ n, edges }) => rel(analyze(n, 0, 1, edges).ceq, analyze(n, 1, 0, edges).ceq) < 1e-10),
    );
  });

  it('homogeneity and Rayleigh monotonicity', () => {
    fc.assert(
      fc.property(network, fc.integer({ min: 2, max: 9 }), fc.nat(), ({ n, edges }, k, pick) => {
        const base = analyze(n, 0, 1, edges).ceq;
        const scaled = analyze(n, 0, 1, edges.map((e) => ({ ...e, c: e.c * k }))).ceq;
        const i = pick % edges.length;
        const bumped = analyze(n, 0, 1, edges.map((e, j) => (j === i ? { ...e, c: e.c + 1 } : e))).ceq;
        return rel(scaled, k * base) < 1e-10 && bumped >= base * (1 - 1e-12);
      }),
    );
  });

  it('sensitivity: dC_eq/dc_e = Δv_e²', () => {
    fc.assert(
      fc.property(network, fc.nat(), ({ n, edges }, pick) => {
        const i = pick % edges.length;
        const r = analyze(n, 0, 1, edges);
        const h = 1e-6 * edges[i]!.c;
        const up = analyze(n, 0, 1, edges.map((e, j) => (j === i ? { ...e, c: e.c + h } : e))).ceq;
        const numeric = (up - r.ceq) / h;
        return Math.abs(numeric - r.voltages[i]! ** 2) < 1e-4;
      }),
    );
  });

  it('exact solver agrees with floating point', () => {
    fc.assert(
      fc.property(network, ({ n, edges }) => {
        const exact = ceqExact(n, 0, 1, edges.map((e) => ({ ...e, c: Frac.int(e.c) })));
        return rel(exact.toNumber(), analyze(n, 0, 1, edges).ceq) < 1e-12;
      }),
    );
  });

  it('exact series/parallel on the classroom problem', () => {
    const [c1, c2, c3, c4] = [3, 2, 3, 1].map((x) => Frac.int(x));
    const v = series(series(c1!, parallel(c2!, c4!)), c3!);
    expect(v.eq(Frac.int(1))).toBe(true);
  });

  it('disconnected terminal gives zero', () => {
    expect(analyze(3, 0, 1, [{ u: 0, v: 2, c: 1 }]).ceq).toBe(0);
  });
});

describe('Frac', () => {
  it('parses decimals exactly', () => {
    expect(Frac.fromDecimal('0.1').eq(new Frac(1n, 10n))).toBe(true);
    expect(Frac.fromDecimal('-12.500e-3').eq(new Frac(-1n, 80n))).toBe(true);
    expect(Frac.fromDecimal('3e2').eq(Frac.int(300))).toBe(true);
    expect(() => Frac.fromDecimal('.')).toThrow();
  });

  it('fromNumber is exact and toNumber round-trips', () => {
    fc.assert(
      fc.property(fc.double({ min: -1e6, max: 1e6, noNaN: true }), (x) => Frac.fromNumber(x).toNumber() === x),
    );
  });

  it('field laws', () => {
    const q = fc.tuple(fc.integer({ min: -50, max: 50 }), fc.integer({ min: 1, max: 50 })).map(([n, d]) => new Frac(BigInt(n), BigInt(d)));
    fc.assert(
      fc.property(q, q, q, (a, b, c) => {
        return a.add(b).mul(c).eq(a.mul(c).add(b.mul(c))) && a.sub(b).add(b).eq(a);
      }),
    );
  });
});
