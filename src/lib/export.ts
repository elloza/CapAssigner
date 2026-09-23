// Text representations of a solution: formula, SPICE netlist, CircuiTikZ.

import type { Diagram, Drawing, Pt } from './render/layout';
import type { Core, Solution, Tree } from './types';

export type LeafName = (leaf: number) => string;

/** Human formula: "∥" for parallel, "—" for series, cores by name. */
export function formula(t: Tree, name: LeafName, coreName: (id: number) => string): string {
  const go = (x: Tree, parent: Tree['t'] | null): string => {
    switch (x.t) {
      case 'leaf':
        return name(x.k);
      case 'series':
      case 'parallel': {
        const s = x.c.map((c) => go(c, x.t)).join(x.t === 'series' ? ' — ' : ' ∥ ');
        return parent === null || parent === 'core' ? s : `(${s})`;
      }
      case 'core':
        return `${coreName(x.core)}[${x.c.map((c) => go(c, 'core')).join(', ')}]`;
    }
  };
  return go(t, null);
}

/** LaTeX for KaTeX, with the same operators as `formula`. */
export function formulaTex(t: Tree, name: LeafName, coreName: (id: number) => string): string {
  const go = (x: Tree): string => {
    switch (x.t) {
      case 'leaf':
        return name(x.k).replace(/^C(\d+)$/, 'C_{$1}');
      case 'parallel':
        return `\\left(${x.c.map(go).join(' \\parallel ')}\\right)`;
      case 'series':
        return `\\left(${x.c.map(go).join(' \\mathbin{\\text{—}} ')}\\right)`;
      case 'core':
        return `\\text{${coreName(x.core)}}\\!\\left[${x.c.map(go).join(',\\,')}\\right]`;
    }
  };
  return go(t);
}

function spiceValue(f: number): string {
  const units: [number, string][] = [
    [1e-15, 'f'],
    [1e-12, 'p'],
    [1e-9, 'n'],
    [1e-6, 'u'],
    [1e-3, 'm'],
    [1, ''],
  ];
  let best = units[0]!;
  for (const u of units) if (f >= u[0] * 0.9999999) best = u;
  return `${Number((f / best[0]).toPrecision(12))}${best[1]}`;
}

/** SPICE netlist: node 1 is A, node 0 (ground) is B. */
export function spice(sol: Solution, name: LeafName, title: string): string {
  const g = sol.graph;
  const node = (i: number) => (i === g.b ? '0' : i === g.a ? '1' : String(i + 1));
  const lines = [`* ${title}`, `* C_eq = ${sol.value.toExponential(9)} F between nodes 1 (A) and 0 (B)`];
  // SPICE capacitor names must start with C; keep the user's label as a comment.
  g.edges.forEach(([u, v, k], i) => {
    const label = name(k);
    const id = /^C\d+$/.test(label) ? label : `C${i + 1}`;
    const note = id === label ? '' : ` ; ${label}`;
    lines.push(`${id} ${node(u)} ${node(v)} ${spiceValue(sol.leaves[k]!.value)}${note}`);
  });
  lines.push('* Check: .ac or .op with a source between 1 and 0', '.end');
  return lines.join('\n');
}

function tikzDrawing(d: Drawing, name: LeafName, value: (k: number) => string): string {
  const s = 1 / 40;
  const p = ([x, y]: Pt) => `(${(x * s).toFixed(3)},${(-y * s).toFixed(3)})`;
  const out: string[] = [];
  for (const q of d.prims) {
    switch (q.t) {
      case 'wire':
        out.push(`  \\draw ${q.pts.map(p).join(' -- ')};`);
        break;
      case 'cap': {
        const n = name(q.leaf).replace(/^C(\d+)$/, 'C_{$1}');
        out.push(`  \\draw ${p(q.from)} to[C, l=$${n}$, a={${value(q.leaf).replace('µ', '$\\mu$')}}] ${p(q.to)};`);
        break;
      }
      case 'box':
        out.push(`  \\draw ${p(q.from)} to[generic, l=$${q.label}$] ${p(q.to)};`);
        break;
      case 'dot':
        out.push(`  \\fill ${p(q.at)} circle (1.5pt);`);
        break;
      case 'term':
        out.push(`  \\draw ${p(q.at)} node[ocirc, label=above:$${q.name}$] {};`);
        break;
    }
  }
  return out.join('\n');
}

/** Standalone CircuiTikZ document for the diagram. */
export function circuitikz(diagram: Diagram, name: LeafName, value: (k: number) => string): string {
  const pics = [
    `\\begin{circuitikz}[european]\n${tikzDrawing(diagram.main, name, value)}\n\\end{circuitikz}`,
    ...diagram.subs.map(
      (s) =>
        `\n\\medskip\\noindent $${s.label}$:\\par\n\\begin{circuitikz}[european]\n${tikzDrawing(s.drawing, name, value)}\n\\end{circuitikz}`,
    ),
  ];
  return [
    '\\documentclass[border=4pt]{standalone}',
    '\\usepackage{circuitikz}',
    '\\begin{document}',
    '\\begin{minipage}{\\linewidth}',
    ...pics,
    '\\end{minipage}',
    '\\end{document}',
  ].join('\n');
}

export function coreLabel(core: Core | undefined, lang: 'es' | 'en'): string {
  if (!core) return 'R';
  if (core.edges.length === 5) return lang === 'es' ? 'Puente' : 'Bridge';
  return `R${core.edges.length}·${core.id}`;
}
