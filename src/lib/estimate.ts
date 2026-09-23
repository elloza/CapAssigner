// Rough running-time model for a request, calibrated on the native timing
// surveys in crates/capcore/tests/api.rs (see docs/approaches.md) and scaled
// for WebAssembly in a browser worker.

import type { SolveRequest } from './types';

/** Measured browser/native slowdown of the WASM build. */
const WASM_FACTOR = 2;

export interface Estimate {
  /** Expected wall time in seconds. */
  seconds: number;
  /** The search is expected to be exhaustive (no coarsening). */
  exhaustive: boolean;
}

/** log-log interpolation in a sorted table of (x, seconds). */
function interp(table: [number, number][], x: number): number {
  if (x <= table[0]![0]) return table[0]![1];
  for (let i = 1; i < table.length; i++) {
    const [x1, y1] = table[i]!;
    const [x0, y0] = table[i - 1]!;
    if (x <= x1) {
      const t = (x - x0) / (x1 - x0);
      return Math.exp(Math.log(y0) + t * (Math.log(y1) - Math.log(y0)));
    }
  }
  return table[table.length - 1]![1];
}

// Series-parallel "use all" times (s, native) by effective number of distinct parts.
const SP_ALL: [number, number][] = [
  [4, 0.001],
  [6, 0.005],
  [7, 0.03],
  [8, 0.2],
  [9, 3],
  [10, 2.5],
  [11, 4.7],
  [12, 25],
];

// Extra factor when non-series-parallel cores are enabled.
const CORES_ALL: [number, number][] = [
  [6, 1.5],
  [7, 2],
  [8, 3.5],
  [9, 2.8],
];

function counts(values: number[]): number[] {
  const m = new Map<number, number>();
  for (const v of values) m.set(v, (m.get(v) ?? 0) + 1);
  return [...m.values()];
}

export function estimate(req: SolveRequest): Estimate {
  const cores = (req.maxCoreEdges ?? 0) > 0;
  if (req.mode === 'all') {
    // Equal values collapse states: 2^n_eff = Π(count + 1).
    const nEff = Math.log2(counts(req.values).reduce((p, c) => p * (c + 1), 1));
    let s = interp(SP_ALL, nEff);
    if (cores && req.values.length <= 8) s *= interp(CORES_ALL, nEff);
    return { seconds: s * WASM_FACTOR, exhaustive: nEff <= 8.5 };
  }
  const k = req.maxParts ?? 4;
  const m = counts(req.values).length;
  let s: number;
  if (k <= 3) s = 0.01;
  else if (k === 4) s = 0.02 * Math.max(1, (m / 48) ** 3);
  else if (k === 5) s = 0.1 * Math.max(1, (m / 24) ** 1.5);
  else s = 0.3 * Math.max(0.2, (m / 24) ** 2.2);
  if (cores && k >= 5 && m <= 24) s *= 3;
  return { seconds: s * WASM_FACTOR, exhaustive: k <= 4 || (k === 5 && m <= 24) };
}
