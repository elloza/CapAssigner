// Main-thread client for the solver worker, with cancellation.

import type { SolveRequest, SolveResponse } from './types';
import type { WorkerOut } from '../workers/solver.worker';

export interface SolveResult {
  res: SolveResponse;
  ms: number;
  /** Size of the WASM memory after the search (its peak so far). */
  memoryMB: number;
}

export class SolverClient {
  private worker: Worker | null = null;
  private seq = 0;
  private pending: { id: number; reject: (e: Error) => void } | null = null;

  private spawn(): Worker {
    this.worker ??= new Worker(new URL('../workers/solver.worker.ts', import.meta.url), {
      type: 'module',
    });
    return this.worker;
  }

  /** Start the worker early so the WASM module is compiled before the first search. */
  warmUp(): void {
    this.spawn();
  }

  run(req: SolveRequest, onProgress?: (fraction: number) => void): Promise<SolveResult> {
    this.cancel();
    const worker = this.spawn();
    const id = ++this.seq;
    return new Promise((resolve, reject) => {
      this.pending = { id, reject };
      worker.onmessage = (ev: MessageEvent<WorkerOut>) => {
        const m = ev.data;
        if (m.id !== id) return;
        if (m.type === 'progress') onProgress?.(m.fraction);
        else {
          this.pending = null;
          if (m.type === 'done') resolve({ res: m.res, ms: m.ms, memoryMB: m.memoryMB });
          else {
            // The worker closes itself after an error; spawn a new one next time.
            this.worker?.terminate();
            this.worker = null;
            reject(new Error(friendly(m.message)));
          }
        }
      };
      worker.onerror = (e) => {
        this.pending = null;
        this.worker?.terminate();
        this.worker = null;
        reject(new Error(e.message || 'worker crashed (out of memory?)'));
      };
      worker.postMessage({ id, req });
    });
  }

  /** Abort the running search, if any. */
  cancel(): void {
    if (!this.pending) return;
    this.pending.reject(new CancelledError());
    this.pending = null;
    this.worker?.terminate();
    this.worker = null;
  }
}

/** Engine traps are cryptic; the usual cause is running out of memory. */
function friendly(message: string): string {
  return /unreachable|memory|allocation|out of bounds/i.test(message) ? 'out of memory' : message;
}

export class CancelledError extends Error {
  constructor() {
    super('cancelled');
    this.name = 'CancelledError';
  }
}
