// Shapes exchanged with the WASM engine (see crates/capcore/src/api.rs).

export type Mode = 'all' | 'inventory';

export interface SolveRequest {
  mode: Mode;
  /** Farads. */
  values: number[];
  target: number;
  stock?: number[] | null;
  maxParts?: number;
  minParts?: number;
  topK?: number;
  /** 0 = series-parallel only; 5 adds bridges; up to 9 = every network. */
  maxCoreEdges?: number;
  maxEntries?: number;
}

export type Tree =
  | { t: 'leaf'; k: number }
  | { t: 'series'; c: Tree[] }
  | { t: 'parallel'; c: Tree[] }
  | { t: 'core'; core: number; c: Tree[] };

export interface Leaf {
  class: number;
  value: number;
  /** Index in the request's `values` (mode `all`). */
  index: number | null;
}

export interface Graph {
  nodes: number;
  a: number;
  b: number;
  /** [u, v, leaf] */
  edges: [number, number, number][];
}

export interface Solution {
  value: number;
  relError: number;
  parts: number;
  tree: Tree;
  leaves: Leaf[];
  graph: Graph;
}

export interface Core {
  id: number;
  nv: number;
  edges: [number, number][];
}

export interface SolveStats {
  states: number;
  entries: number;
  candidates: number;
  epsUsed: number;
  exhaustive: boolean;
  /** Every enabled non-series-parallel core was explored. */
  coresComplete: boolean;
  boundRel: number;
}

export interface SolveResponse {
  solutions: Solution[];
  stats: SolveStats;
  cores: Core[];
}
