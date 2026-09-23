// Input sanity checks shown before searching.

import { describe, expect, it } from 'vitest';
import { buildRequest, DEFAULT_FORM, sanityChecks } from '../../src/lib/form';

const codes = (...args: Parameters<typeof sanityChecks>) => sanityChecks(...args).map((c) => c.code);

describe('sanityChecks', () => {
  it('a normal classroom problem raises nothing', () => {
    expect(codes('all', [3e-12, 2e-12, 3e-12, 1e-12], 1e-12, 3, false)).toEqual([]);
  });

  it('flags targets outside [all in series, all in parallel]', () => {
    // 1 and 2 pF: series 2/3 pF, parallel 3 pF.
    expect(codes('all', [1e-12, 2e-12], 0.5e-12, 3, false)).toEqual(['unreachableLow']);
    expect(codes('all', [1e-12, 2e-12], 4e-12, 3, false)).toEqual(['unreachableHigh']);
    expect(codes('all', [1e-12, 2e-12], 3e-12, 3, false)).toEqual([]);
    // Inventory with K = 3 parts from {1, 2} pF: range [1/3, 6] pF.
    expect(codes('inventory', [1e-12, 2e-12], 7e-12, 3, false)).toEqual(['unreachableHigh']);
    expect(codes('inventory', [1e-12, 2e-12], 0.4e-12, 3, false)).toEqual([]);
  });

  it('flags unit slips: huge spread, tiny and huge parts', () => {
    // The user report: 10 nF next to 55.4 F.
    const c = codes('all', [10e-9, 55.4, 3], 10.4e-9, 3, false);
    expect(c).toContain('spread');
    expect(c).toContain('huge');
    expect(codes('all', [0.01e-12, 1e-12], 0.5e-12, 3, false)).toContain('tiny');
  });

  it('blocks what the engine cannot take', () => {
    expect(codes('all', [1e-200, 1e-12], 1e-12, 3, false)).toContain('ratio');
    const many = Array.from({ length: 40 }, (_, i) => (i + 1) * 1e-12);
    expect(codes('inventory', many, 5e-12, 3, true)).toContain('classes');
    expect(codes('inventory', many, 5e-12, 3, false)).not.toContain('classes');
  });

  it('a blocking check disables the search, a warning does not', () => {
    const warn = buildRequest({ ...DEFAULT_FORM, caps: '1pF 2pF', target: '10pF' });
    expect(warn.checks.map((c) => c.code)).toEqual(['unreachableHigh']);
    expect(warn.req).not.toBeNull();
    const many = Array.from({ length: 40 }, (_, i) => `${i + 1}pF×2`).join(' ');
    const block = buildRequest({ ...DEFAULT_FORM, mode: 'inventory', source: 'custom', inventory: many, target: '5pF' });
    expect(block.req).toBeNull();
  });
});
