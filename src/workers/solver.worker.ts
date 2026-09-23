// Runs the WASM engine off the main thread. One request at a time; the page
// cancels a search by terminating this worker and starting a fresh one.

import init, { solve } from '../wasm/pkg/capcore.js';
import type { SolveRequest, SolveResponse } from '../lib/types';

export type WorkerIn = { id: number; req: SolveRequest };
export type WorkerOut =
  | { id: number; type: 'progress'; fraction: number }
  | { id: number; type: 'done'; res: SolveResponse; ms: number }
  | { id: number; type: 'error'; message: string };

const ready = init();

self.onmessage = async (ev: MessageEvent<WorkerIn>) => {
  const { id, req } = ev.data;
  const post = (m: WorkerOut) => self.postMessage(m);
  try {
    await ready;
    const t0 = performance.now();
    let last = 0;
    const out = solve(JSON.stringify(req), (fraction: number) => {
      const now = performance.now();
      if (now - last > 60 || fraction >= 1) {
        last = now;
        post({ id, type: 'progress', fraction });
      }
    });
    post({ id, type: 'done', res: JSON.parse(out) as SolveResponse, ms: performance.now() - t0 });
  } catch (e) {
    post({ id, type: 'error', message: e instanceof Error ? e.message : String(e) });
  }
};
