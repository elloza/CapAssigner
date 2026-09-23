// Independent circuit oracle: nodal analysis of an arbitrary capacitor network.
//
// With terminal A at 1 V and B at 0 V, the internal node potentials solve
// L_II·v_I = −L_IA (Kirchhoff's charge law for initially neutral nodes). Then
//   C_eq = Q_A = Σ_{edges at A} c·(1 − v_j)
// and energy conservation requires ½·C_eq = ½·Σ c·(Δv)². This file shares no
// code with the Rust engine, so it serves as the referee in the tests and in
// the UI's "verified" badge.

import { Frac } from './exact';
import type { Core, Graph, Tree } from './types';

export interface WEdge<T> {
  u: number;
  v: number;
  c: T;
}

export interface Analysis {
  ceq: number;
  /** Node potentials for 1 V across A–B. */
  potentials: number[];
  /** Per edge: voltage across it (fraction of the applied voltage). */
  voltages: number[];
  /** Per edge: charge for 1 V applied (farads · volts). */
  charges: number[];
  /** Stored energy for 1 V applied, ½·Σ c·Δv². */
  energy: number;
  /** Largest charge imbalance at an internal node divided by what is allowed:
   *  1e-9·C_eq plus the rounding of the potentials (~ε) amplified by the
   *  node's capacitances. Charge is conserved when this is ≤ 1. */
  residual: number;
}

function reachable(n: number, edges: WEdge<unknown>[], from: number[]): boolean[] {
  const adj: number[][] = Array.from({ length: n }, () => []);
  for (const e of edges) {
    adj[e.u]!.push(e.v);
    adj[e.v]!.push(e.u);
  }
  const seen = new Array<boolean>(n).fill(false);
  const stack = [...from];
  for (const s of from) seen[s] = true;
  while (stack.length) {
    const x = stack.pop()!;
    for (const y of adj[x]!) {
      if (!seen[y]) {
        seen[y] = true;
        stack.push(y);
      }
    }
  }
  return seen;
}

interface Field<T> {
  zero: T;
  one: T;
  add(a: T, b: T): T;
  sub(a: T, b: T): T;
  mul(a: T, b: T): T;
  div(a: T, b: T): T;
  isZero(a: T): boolean;
  abs(a: T): number;
}

const F64: Field<number> = {
  zero: 0,
  one: 1,
  add: (a, b) => a + b,
  sub: (a, b) => a - b,
  mul: (a, b) => a * b,
  div: (a, b) => a / b,
  isZero: (a) => a === 0,
  abs: (a) => Math.abs(a),
};

const FRAC: Field<Frac> = {
  zero: Frac.ZERO,
  one: Frac.ONE,
  add: (a, b) => a.add(b),
  sub: (a, b) => a.sub(b),
  mul: (a, b) => a.mul(b),
  div: (a, b) => a.div(b),
  isZero: (a) => a.isZero(),
  abs: (a) => Math.abs(a.toNumber()),
};

/** Solve M·x = r by Gaussian elimination with partial pivoting. */
function solveLinear<T>(F: Field<T>, M: T[][], r: T[]): T[] {
  const n = r.length;
  for (let k = 0; k < n; k++) {
    let p = k;
    for (let i = k + 1; i < n; i++) if (F.abs(M[i]![k]!) > F.abs(M[p]![k]!)) p = i;
    if (F.isZero(M[p]![k]!)) throw new Error('singular nodal matrix');
    [M[k], M[p]] = [M[p]!, M[k]!];
    [r[k], r[p]] = [r[p]!, r[k]!];
    for (let i = k + 1; i < n; i++) {
      const f = F.div(M[i]![k]!, M[k]![k]!);
      if (F.isZero(f)) continue;
      for (let j = k; j < n; j++) M[i]![j] = F.sub(M[i]![j]!, F.mul(f, M[k]![j]!));
      r[i] = F.sub(r[i]!, F.mul(f, r[k]!));
    }
  }
  const x = new Array<T>(n).fill(F.zero);
  for (let i = n - 1; i >= 0; i--) {
    let s: T = r[i]!;
    for (let j = i + 1; j < n; j++) s = F.sub(s, F.mul(M[i]![j]!, x[j]!));
    x[i] = F.div(s, M[i]![i]!);
  }
  return x;
}

/** Node potentials with V_A = 1, V_B = 0. Nodes cut off from both terminals float at 0. */
function potentials<T>(F: Field<T>, n: number, a: number, b: number, edges: WEdge<T>[]): T[] {
  const live = reachable(n, edges, [a, b]);
  const internal: number[] = [];
  for (let i = 0; i < n; i++) if (i !== a && i !== b && live[i]) internal.push(i);
  const pos = new Map(internal.map((node, i) => [node, i]));
  const M = internal.map(() => internal.map(() => F.zero));
  const r = internal.map(() => F.zero);
  for (const { u, v, c } of edges) {
    if (u === v) continue;
    for (const [x, y] of [
      [u, v],
      [v, u],
    ] as const) {
      const i = pos.get(x);
      if (i === undefined) continue;
      M[i]![i] = F.add(M[i]![i]!, c);
      const j = pos.get(y);
      if (j !== undefined) M[i]![j] = F.sub(M[i]![j]!, c);
      else if (y === a) r[i] = F.add(r[i]!, c);
    }
  }
  const vi = internal.length ? solveLinear(F, M, r) : [];
  const out = new Array<T>(n).fill(F.zero);
  out[a] = F.one;
  internal.forEach((node, i) => (out[node] = vi[i]!));
  return out;
}

function terminalCharge<T>(F: Field<T>, a: number, pot: T[], edges: WEdge<T>[]): T {
  let q = F.zero;
  for (const { u, v, c } of edges) {
    if (u === a && v !== a) q = F.add(q, F.mul(c, F.sub(F.one, pot[v]!)));
    else if (v === a && u !== a) q = F.add(q, F.mul(c, F.sub(F.one, pot[u]!)));
  }
  return q;
}

/**
 * Floating-point nodal analysis in GTH form (Grassmann–Taksar–Heyman): only the
 * couplings g_ij ≥ 0 are kept, eliminating node k adds g_ik·g_kj/Σg_k to the
 * others, and afterwards each eliminated node's potential is the weighted mean
 * of its neighbours at elimination time. No subtraction anywhere, so values
 * spanning many decades (10 nF next to 55 F) stay accurate to rounding.
 */
function gth(n: number, a: number, b: number, edges: WEdge<number>[]): { ceq: number; pot: number[] } {
  const g = Array.from({ length: n }, () => new Array<number>(n).fill(0));
  for (const { u, v, c } of edges) {
    if (u === v) continue;
    g[u]![v]! += c;
    g[v]![u]! += c;
  }
  const live = reachable(n, edges, [a, b]);
  const alive = live.slice();
  const order: { k: number; row: number[]; p: number }[] = [];
  for (let k = 0; k < n; k++) {
    if (k === a || k === b || !live[k]) continue;
    alive[k] = false;
    let p = 0;
    for (let j = 0; j < n; j++) if (alive[j]) p += g[k]![j]!;
    order.push({ k, row: g[k]!.map((x, j) => (alive[j] ? x : 0)), p });
    if (p <= 0) continue;
    for (let i = 0; i < n; i++) {
      if (!alive[i] || g[i]![k]! <= 0) continue;
      const f = g[i]![k]! / p;
      for (let j = 0; j < n; j++) if (alive[j] && j !== i && g[k]![j]! > 0) g[i]![j]! += f * g[k]![j]!;
    }
  }
  const pot = new Array<number>(n).fill(0);
  pot[a] = 1;
  for (let t = order.length - 1; t >= 0; t--) {
    const { k, row, p } = order[t]!;
    if (p > 0) pot[k] = row.reduce((s, x, j) => s + x * pot[j]!, 0) / p;
  }
  return { ceq: g[a]![b]!, pot };
}

export function analyze(n: number, a: number, b: number, edges: WEdge<number>[]): Analysis {
  const { ceq, pot } = gth(n, a, b, edges);
  const voltages = edges.map((e) => pot[e.u]! - pot[e.v]!);
  const charges = edges.map((e, i) => e.c * voltages[i]!);
  const energy = 0.5 * edges.reduce((s, e, i) => s + e.c * voltages[i]! ** 2, 0);
  // Charge balance at internal nodes. Each potential is known to a few ε, which
  // a capacitance c turns into an absolute charge error of about c·ε: with
  // 55 F next to 10 nF that is far above 1e-9·C_eq, and is not a violation.
  const net = new Array<number>(n).fill(0);
  const capSum = new Array<number>(n).fill(0);
  edges.forEach((e, i) => {
    net[e.u]! += charges[i]!;
    net[e.v]! -= charges[i]!;
    capSum[e.u]! += e.c;
    capSum[e.v]! += e.c;
  });
  let residual = 0;
  const live = reachable(n, edges, [a, b]);
  for (let i = 0; i < n; i++) {
    if (i === a || i === b || !live[i]) continue;
    const allowed = 1e-9 * ceq + 16 * Number.EPSILON * capSum[i]!;
    residual = Math.max(residual, Math.abs(net[i]!) / allowed);
  }
  return { ceq, potentials: pot, voltages, charges, energy, residual };
}

export function ceqExact(n: number, a: number, b: number, edges: WEdge<Frac>[]): Frac {
  return terminalCharge(FRAC, a, potentials(FRAC, n, a, b, edges), edges);
}

/** Weighted edges of an engine graph given the value of each leaf. */
export function graphEdges<T>(g: Graph, leafValue: (k: number) => T): WEdge<T>[] {
  return g.edges.map(([u, v, k]) => ({ u, v, c: leafValue(k) }));
}

/** Evaluate a network tree structurally (series/parallel formulas, cores by nodal analysis). */
export function evalTree(t: Tree, leaf: (k: number) => number, cores: Map<number, Core>): number {
  switch (t.t) {
    case 'leaf':
      return leaf(t.k);
    case 'series':
      return 1 / t.c.reduce((s, x) => s + 1 / evalTree(x, leaf, cores), 0);
    case 'parallel':
      return t.c.reduce((s, x) => s + evalTree(x, leaf, cores), 0);
    case 'core': {
      const core = cores.get(t.core);
      if (!core) throw new Error(`unknown core ${t.core}`);
      const edges = core.edges.map(([u, v], i) => ({ u, v, c: evalTree(t.c[i]!, leaf, cores) }));
      return analyze(core.nv, 0, 1, edges).ceq;
    }
  }
}

/**
 * Guaranteed C_eq interval when every part may deviate by ±tol (relative).
 * C_eq is monotone in each capacitance and 1-homogeneous, so the extremes are
 * reached with all parts at their lower or all at their upper limits.
 */
export function toleranceInterval(ceq: number, tol: number): [number, number] {
  return [ceq * (1 - tol), ceq * (1 + tol)];
}
