// Re-derive every reported network with the independent oracle, in floating
// point and exactly (from the decimal text the user typed).

import { Frac } from './exact';
import { analyze, ceqExact, evalTree, graphEdges, type Analysis } from './physics';
import type { Core, Solution } from './types';

export interface Verification {
  ok: boolean;
  analysis: Analysis;
  /** Exact C_eq in farads (null when the network is too large to check exactly). */
  exact: Frac | null;
  /** Exact signed relative error with respect to the exact target. */
  exactRelError: number | null;
  problems: string[];
}

const REL_TOL = 1e-9;
const EXACT_MAX_EDGES = 16;

/**
 * @param leafExact exact value of each leaf (by leaf number)
 */
export function verifySolution(
  sol: Solution,
  cores: Core[],
  target: Frac,
  leafExact: (k: number) => Frac,
): Verification {
  const problems: string[] = [];
  const g = sol.graph;
  const analysis = analyze(g.nodes, g.a, g.b, graphEdges(g, (k) => sol.leaves[k]!.value));
  const rel = (x: number) => Math.abs(x - sol.value) / sol.value;
  if (rel(analysis.ceq) > REL_TOL) problems.push(`nodal C_eq ${analysis.ceq} ≠ ${sol.value}`);
  const byTree = evalTree(sol.tree, (k) => sol.leaves[k]!.value, new Map(cores.map((c) => [c.id, c])));
  if (rel(byTree) > REL_TOL) problems.push(`structural C_eq ${byTree} ≠ ${sol.value}`);
  if (Math.abs(2 * analysis.energy - analysis.ceq) > REL_TOL * analysis.ceq)
    problems.push('energy balance violated');
  if (analysis.residual > 1) problems.push('charge conservation violated');
  if (g.edges.length !== sol.parts) problems.push('part count mismatch');

  let exact: Frac | null = null;
  let exactRelError: number | null = null;
  if (g.edges.length <= EXACT_MAX_EDGES) {
    exact = ceqExact(g.nodes, g.a, g.b, graphEdges(g, leafExact));
    exactRelError = exact.sub(target).div(target).toNumber();
    if (Math.abs(exact.toNumber() - sol.value) > REL_TOL * sol.value)
      problems.push(`exact C_eq ${exact.toNumber()} ≠ ${sol.value}`);
  }
  return { ok: problems.length === 0, analysis, exact, exactRelError, problems };
}
