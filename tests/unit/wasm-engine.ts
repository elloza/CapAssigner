// Load the compiled WASM engine synchronously in Node for tests.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { initSync, solve as rawSolve, cores as rawCores } from '../../src/wasm/pkg/capcore.js';
import type { Core, SolveRequest, SolveResponse } from '../../src/lib/types';

const wasm = readFileSync(
  fileURLToPath(new URL('../../src/wasm/pkg/capcore_bg.wasm', import.meta.url)),
);
initSync({ module: wasm });

export function solve(req: SolveRequest): SolveResponse {
  return JSON.parse(rawSolve(JSON.stringify(req))) as SolveResponse;
}

export function cores(maxEdges: number): Core[] {
  return JSON.parse(rawCores(maxEdges)) as Core[];
}
