import { describe, expect, it } from 'vitest';
import fc from 'fast-check';
import { formatCapacitance, parseCapacitance, parseList, splitList, type Prefix } from '../../src/lib/units';
import { Frac } from '../../src/lib/exact';

function farads(s: string, unit: Prefix = 'p'): number {
  const r = parseCapacitance(s, unit);
  if (!r.ok) throw new Error(`failed: ${s}`);
  return r.value.farads;
}

describe('parseCapacitance', () => {
  // Cases carried over from v1 (legacy/tests/unit/test_parsing.py).
  it.each([
    ['5.2pF', 5.2e-12],
    ['1nF', 1e-9],
    ['2.7µF', 2.7e-6],
    ['2.7uF', 2.7e-6],
    ['1mF', 1e-3],
    ['0.5F', 0.5],
    ['1e-11', 1e-11],
    ['1.2e-12', 1.2e-12],
    ['5E-10', 5e-10],
    ['1*10^-11', 1e-11],
    ['1.2 * 10 ^ -12', 1.2e-12],
  ])('v1 format %s', (s, v) => {
    expect(farads(s)).toBeCloseTo(v, 25);
    expect(Math.abs(farads(s) - v) / v).toBeLessThan(1e-15);
  });

  it.each([
    ['5.2 pF', 5.2e-12],
    ['5,2pF', 5.2e-12],
    ['4p7', 4.7e-12],
    ['4n7', 4.7e-9],
    ['2u2', 2.2e-6],
    ['10fF', 10e-15],
    ['10f', 10e-15],
    ['3.3n', 3.3e-9],
    ['2.2μF', 2.2e-6],
    ['1.2×10^-12', 1.2e-12],
    ['47pf', 47e-12],
  ])('v2 format %s', (s, v) => {
    expect(Math.abs(farads(s) - v) / v).toBeLessThan(1e-15);
  });

  it('exact fractions', () => {
    const r = parseCapacitance('170/71pF');
    expect(r.ok && r.value.exact.eq(new Frac(170n, 71n * 10n ** 12n))).toBe(true);
    expect(parseCapacitance('1/0pF').ok).toBe(false);
  });

  it('tiny bare numbers are farads, as in v1 (review A2)', () => {
    expect(farads('0.0000000000052')).toBeCloseTo(5.2e-12, 25);
    expect(farads('0.0005')).toBeCloseTo(5e-4, 15);
  });

  it('exponent with a prefix (review M3)', () => {
    expect(farads('1.5e3pF')).toBeCloseTo(1.5e-9, 20);
    expect(farads('2e-1n')).toBeCloseTo(2e-10, 22);
  });

  it('bare numbers use the default unit', () => {
    expect(farads('5.2', 'p')).toBeCloseTo(5.2e-12, 25);
    expect(farads('5.2', 'n')).toBeCloseTo(5.2e-9, 22);
    expect(farads('5.2', '')).toBe(5.2);
  });

  it('keeps the exact decimal value', () => {
    const r = parseCapacitance('4.7pF');
    expect(r.ok && r.value.exact.eq(new Frac(47n, 10n ** 13n))).toBe(true);
  });

  it.each(['', 'abc', '5xF', '--5pF', '1e', 'pF'])('rejects %j', (s) => {
    expect(parseCapacitance(s).ok).toBe(false);
  });

  it.each(['0pF', '-5pF', '0'])('rejects non-positive %s', (s) => {
    const r = parseCapacitance(s);
    expect(!r.ok && r.error.code).toBe('nonpositive');
  });

  it('round-trips formatted values', () => {
    fc.assert(
      fc.property(fc.double({ min: 1e-15, max: 1, noNaN: true }), (v) => {
        const text = formatCapacitance(v, 12);
        const back = farads(text.replace(' ', ''));
        return Math.abs(back - v) / v < 1e-10;
      }),
    );
  });
});

describe('lists', () => {
  it('splits on whitespace, semicolons and non-decimal commas', () => {
    expect(splitList('1pF, 2pF;3pF\n4,7pF 5pF,6pF')).toEqual(['1pF', '2pF', '3pF', '4,7pF', '5pF', '6pF']);
  });

  it('a token with several commas is a list, one comma between digits a decimal', () => {
    expect(parseList('1,2,3').values.map((v) => v.farads)).toEqual([1e-12, 2e-12, 3e-12]);
    expect(parseList('1,5 2,2').values.map((v) => v.farads)).toEqual([1.5e-12, 2.2e-12]);
  });

  it('joins a unit typed after a space', () => {
    const { values, errors } = parseList('5.2 pF 3 nF 10');
    expect(errors).toEqual([]);
    expect(values.map((v) => v.farads)).toEqual([5.2e-12, 3e-9, 10e-12]);
  });

  it('reports bad tokens', () => {
    const { values, errors } = parseList('1pF foo 2pF');
    expect(values).toHaveLength(2);
    expect(errors).toEqual([{ code: 'syntax', input: 'foo' }]);
  });
});

describe('formatCapacitance', () => {
  it.each([
    [5.2e-12, '5.2 pF'],
    [1.5e-9, '1.5 nF'],
    [2.7e-6, '2.7 µF'],
    [1e-3, '1 mF'],
    [1, '1 F'],
    [999.99e-12, '1 nF'],
    [15e-15, '15 fF'],
  ])('%s → %s', (v, s) => {
    expect(formatCapacitance(v)).toBe(s);
  });
});
