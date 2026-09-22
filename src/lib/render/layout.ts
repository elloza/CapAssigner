// Schematic layout of a network tree as drawing primitives, shared by the SVG
// renderer and the CircuiTikZ exporter.
//
// Series blocks run left to right, parallel blocks stack between two rails, and
// a non-series-parallel core is drawn as its graph with A on the left and B on
// the right; a core edge that holds a whole sub-network is drawn as a labelled
// box and that sub-network is laid out separately.

import type { Core, Tree } from '../types';

export type Pt = [number, number];

export type Prim =
  | { t: 'wire'; pts: Pt[] }
  | { t: 'cap'; from: Pt; to: Pt; leaf: number }
  | { t: 'box'; from: Pt; to: Pt; label: string }
  | { t: 'dot'; at: Pt }
  | { t: 'term'; at: Pt; name: string };

export interface Drawing {
  width: number;
  height: number;
  prims: Prim[];
}

export interface Diagram {
  main: Drawing;
  /** Sub-networks referenced by boxes in core blocks, in label order. */
  subs: { label: string; drawing: Drawing }[];
}

const LEAF_W = 90;
const LEAF_H = 56;
const RAIL = 14;
const GAP = 8;
const CORE_W = 260;
const CORE_H = 200;
const LEAD = 26;

interface Block {
  w: number;
  h: number;
  /** Emit primitives with the block's top-left corner at (x, y). */
  draw(x: number, y: number, out: Prim[]): void;
}

function vertexPositions(core: Core): Pt[] {
  // x: the electrical potential of each vertex with unit edges (A = 0, B = 1),
  // so charge visibly flows left to right. y: a repulsion layout with x fixed,
  // started alternately above and below the A–B axis.
  const n = core.nv;
  const adj: number[][] = Array.from({ length: n }, () => []);
  for (const [u, v] of core.edges) {
    adj[u]!.push(v);
    adj[v]!.push(u);
  }
  const x: number[] = Array.from({ length: n }, (_, i) => (i === 1 ? 1 : i === 0 ? 0 : 0.5));
  for (let it = 0; it < 500; it++) {
    for (let i = 2; i < n; i++) x[i] = adj[i]!.reduce((s, j) => s + x[j]!, 0) / adj[i]!.length;
  }
  const y: number[] = Array.from({ length: n }, (_, i) => (i < 2 ? 0.5 : i % 2 === 0 ? 0.1 : 0.9));
  for (let it = 0; it < 300; it++) {
    for (let i = 2; i < n; i++) {
      let f = 0;
      for (let j = 0; j < n; j++) {
        if (j === i) continue;
        const dx = x[i]! - x[j]!;
        const dy = y[i]! - y[j]!;
        const d2 = dx * dx + dy * dy + 1e-4;
        f += (dy / d2) * 0.01;
      }
      for (const j of adj[i]!) f -= (y[i]! - y[j]!) * 0.02;
      y[i] = Math.min(1, Math.max(0, y[i]! + f));
    }
  }
  // Use the full height: stretch the internal vertices around the A–B axis.
  const spread = Math.max(...y.slice(2).map((v) => Math.abs(v - 0.5)));
  const k = spread > 1e-6 ? 0.5 / spread : 1;
  return x.map((xi, i) => [0.08 + 0.84 * xi, 0.5 + (y[i]! - 0.5) * k]);
}

export function layout(tree: Tree, cores: Core[]): Diagram {
  const coreById = new Map(cores.map((c) => [c.id, c]));
  const subs: { label: string; tree: Tree }[] = [];

  function block(t: Tree): Block {
    switch (t.t) {
      case 'leaf':
        return {
          w: LEAF_W,
          h: LEAF_H,
          draw: (x, y, out) => out.push({ t: 'cap', from: [x, y + LEAF_H / 2], to: [x + LEAF_W, y + LEAF_H / 2], leaf: t.k }),
        };
      case 'series': {
        const kids = t.c.map(block);
        const h = Math.max(...kids.map((b) => b.h));
        const w = kids.reduce((s, b) => s + b.w, 0);
        return {
          w,
          h,
          draw: (x, y, out) => {
            let cx = x;
            for (const b of kids) {
              b.draw(cx, y + (h - b.h) / 2, out);
              cx += b.w;
            }
          },
        };
      }
      case 'parallel': {
        const kids = t.c.map(block);
        const inner = Math.max(...kids.map((b) => b.w));
        const w = inner + 2 * RAIL + 2 * GAP;
        const h = kids.reduce((s, b) => s + b.h, 0) + GAP * (kids.length - 1);
        return {
          w,
          h,
          draw: (x, y, out) => {
            const mids: number[] = [];
            let cy = y;
            for (const b of kids) {
              const bx = x + RAIL + GAP + (inner - b.w) / 2;
              const my = cy + b.h / 2;
              mids.push(my);
              out.push({ t: 'wire', pts: [[x + RAIL, my], [bx, my]] });
              b.draw(bx, cy, out);
              out.push({ t: 'wire', pts: [[bx + b.w, my], [x + w - RAIL, my]] });
              cy += b.h + GAP;
            }
            const top = mids[0]!;
            const bot = mids[mids.length - 1]!;
            const mid = y + h / 2;
            out.push({ t: 'wire', pts: [[x + RAIL, top], [x + RAIL, bot]] });
            out.push({ t: 'wire', pts: [[x + w - RAIL, top], [x + w - RAIL, bot]] });
            out.push({ t: 'wire', pts: [[x, mid], [x + RAIL, mid]] });
            out.push({ t: 'wire', pts: [[x + w - RAIL, mid], [x + w, mid]] });
            for (const my of mids) {
              if (my !== top && my !== bot) {
                out.push({ t: 'dot', at: [x + RAIL, my] });
                out.push({ t: 'dot', at: [x + w - RAIL, my] });
              }
            }
            if (mid > top && mid < bot) {
              out.push({ t: 'dot', at: [x + RAIL, mid] });
              out.push({ t: 'dot', at: [x + w - RAIL, mid] });
            }
          },
        };
      }
      case 'core': {
        const core = coreById.get(t.core);
        if (!core) throw new Error(`unknown core ${t.core}`);
        const pos = vertexPositions(core);
        const w = CORE_W + 2 * LEAD;
        const h = CORE_H;
        const labels = t.c.map((child) => {
          if (child.t === 'leaf') return null;
          const label = `N${subs.length + 1}`;
          subs.push({ label, tree: child });
          return label;
        });
        return {
          w,
          h,
          draw: (x, y, out) => {
            const at = (i: number): Pt => [x + LEAD + pos[i]![0] * CORE_W, y + 12 + pos[i]![1] * (CORE_H - 24)];
            out.push({ t: 'wire', pts: [[x, y + h / 2], at(0)] });
            out.push({ t: 'wire', pts: [at(1), [x + w, y + h / 2]] });
            core.edges.forEach(([u, v], i) => {
              const child = t.c[i]!;
              const lab = labels[i];
              if (child.t === 'leaf') out.push({ t: 'cap', from: at(u), to: at(v), leaf: child.k });
              else out.push({ t: 'box', from: at(u), to: at(v), label: lab! });
            });
            for (let i = 0; i < core.nv; i++) out.push({ t: 'dot', at: at(i) });
          },
        };
      }
    }
  }

  function drawing(t: Tree): Drawing {
    const b = block(t);
    const pad = 36;
    const prims: Prim[] = [];
    const y0 = 16;
    prims.push({ t: 'wire', pts: [[pad - 20, y0 + b.h / 2], [pad, y0 + b.h / 2]] });
    b.draw(pad, y0, prims);
    prims.push({ t: 'wire', pts: [[pad + b.w, y0 + b.h / 2], [pad + b.w + 20, y0 + b.h / 2]] });
    prims.push({ t: 'term', at: [pad - 20, y0 + b.h / 2], name: 'A' });
    prims.push({ t: 'term', at: [pad + b.w + 20, y0 + b.h / 2], name: 'B' });
    return { width: b.w + 2 * pad, height: b.h + 2 * y0, prims };
  }

  const main = drawing(tree);
  const out: Diagram['subs'] = [];
  // Sub-networks can themselves contain cores (which append more subs).
  for (let i = 0; i < subs.length; i++) out.push({ label: subs[i]!.label, drawing: drawing(subs[i]!.tree) });
  return { main, subs: out };
}
