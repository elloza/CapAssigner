// Primitives → SVG markup. Colours come from CSS custom properties so the
// same markup works in light and dark themes (and falls back to black when
// exported standalone).

import type { Drawing, Prim, Pt } from './layout';

export interface LeafLabel {
  name: string;
  value: string;
}

const PLATE_GAP = 7;
const PLATE_LEN = 24;

function esc(s: string): string {
  return s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]!);
}

function capacitor(from: Pt, to: Pt, label: LeafLabel, highlight: boolean): string {
  const [x1, y1] = from;
  const [x2, y2] = to;
  const len = Math.hypot(x2 - x1, y2 - y1);
  const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
  const mx = (x1 + x2) / 2;
  const my = (y1 + y2) / 2;
  const half = len / 2;
  // Keep labels upright: put them above horizontal parts, beside steep ones.
  const upright = Math.abs(ang) > 90 ? ang + 180 : ang;
  const cls = highlight ? 'cap hl' : 'cap';
  return `<g class="${cls}" transform="translate(${mx} ${my}) rotate(${ang})">
<line x1="${-half}" y1="0" x2="${-PLATE_GAP / 2}" y2="0"/>
<line x1="${PLATE_GAP / 2}" y1="0" x2="${half}" y2="0"/>
<line class="plate" x1="${-PLATE_GAP / 2}" y1="${-PLATE_LEN / 2}" x2="${-PLATE_GAP / 2}" y2="${PLATE_LEN / 2}"/>
<line class="plate" x1="${PLATE_GAP / 2}" y1="${-PLATE_LEN / 2}" x2="${PLATE_GAP / 2}" y2="${PLATE_LEN / 2}"/>
<g transform="rotate(${upright - ang})">
<text class="name" x="0" y="-17" text-anchor="middle">${esc(label.name)}</text>
<text class="val" x="0" y="26" text-anchor="middle">${esc(label.value)}</text>
</g></g>`;
}

function box(from: Pt, to: Pt, label: string): string {
  const [x1, y1] = from;
  const [x2, y2] = to;
  const ang = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
  const half = Math.hypot(x2 - x1, y2 - y1) / 2;
  const upright = Math.abs(ang) > 90 ? ang + 180 : ang;
  return `<g class="sub" transform="translate(${(x1 + x2) / 2} ${(y1 + y2) / 2}) rotate(${ang})">
<line x1="${-half}" y1="0" x2="-18" y2="0"/><line x1="18" y1="0" x2="${half}" y2="0"/>
<rect x="-18" y="-10" width="36" height="20" rx="4"/>
<text transform="rotate(${upright - ang})" x="0" y="4" text-anchor="middle">${esc(label)}</text></g>`;
}

function prim(p: Prim, labels: (leaf: number) => LeafLabel, hl: number | null): string {
  switch (p.t) {
    case 'wire':
      return `<polyline class="wire" points="${p.pts.map((q) => q.join(',')).join(' ')}"/>`;
    case 'cap':
      return capacitor(p.from, p.to, labels(p.leaf), hl === p.leaf);
    case 'box':
      return box(p.from, p.to, p.label);
    case 'dot':
      return `<circle class="dot" cx="${p.at[0]}" cy="${p.at[1]}" r="3"/>`;
    case 'term':
      return `<g class="term"><circle cx="${p.at[0]}" cy="${p.at[1]}" r="5"/><text x="${p.at[0]}" y="${p.at[1] - 11}" text-anchor="middle">${p.name}</text></g>`;
  }
}

const STYLE = `<style>
.wire,.cap line,.sub line{stroke:var(--ink,#111);stroke-width:1.6;fill:none;stroke-linecap:round}
.cap .plate{stroke-width:3}
.cap.hl line{stroke:var(--accent,#c2410c)}
.cap text,.sub text,.term text{font:12px system-ui,sans-serif;fill:var(--ink,#111)}
.cap .val{fill:var(--muted,#555);font-size:11px}
.sub rect{fill:var(--paper,#fff);stroke:var(--accent,#c2410c);stroke-width:1.6}
.dot{fill:var(--ink,#111)}
.term circle{fill:var(--paper,#fff);stroke:var(--ink,#111);stroke-width:1.6}
.term text{font-weight:600}
</style>`;

export function toSvg(
  d: Drawing,
  labels: (leaf: number) => LeafLabel,
  opts: { highlight?: number | null; title?: string } = {},
): string {
  const body = d.prims.map((p) => prim(p, labels, opts.highlight ?? null)).join('\n');
  const title = opts.title ? `<title>${esc(opts.title)}</title>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d.width} ${d.height}" width="${d.width}" height="${d.height}" role="img">${title}${STYLE}${body}</svg>`;
}
