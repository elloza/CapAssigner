// IEC 60063 preferred number series.

export type Series = 'E3' | 'E6' | 'E12' | 'E24' | 'E48' | 'E96';

const E24 = [
  1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6,
  6.2, 6.8, 7.5, 8.2, 9.1,
];

/** Mantissas in [1, 10) of a series. */
export function mantissas(s: Series): number[] {
  switch (s) {
    case 'E3':
      return E24.filter((_, i) => i % 8 === 0);
    case 'E6':
      return E24.filter((_, i) => i % 4 === 0);
    case 'E12':
      return E24.filter((_, i) => i % 2 === 0);
    case 'E24':
      return E24;
    case 'E48':
    case 'E96': {
      // E48 and E96 are exactly 10^(i/N) rounded to three significant figures.
      const n = s === 'E48' ? 48 : 96;
      return Array.from({ length: n }, (_, i) => Math.round(100 * 10 ** (i / n)) / 100);
    }
  }
}

/** Values of a series as text with unit, e.g. "4.7nF", over decades [from, to). */
export function seriesValues(s: Series, fromExp: number, toExp: number): string[] {
  const out: string[] = [];
  const prefixes: [number, string][] = [
    [-15, 'f'],
    [-12, 'p'],
    [-9, 'n'],
    [-6, 'µ'],
    [-3, 'm'],
    [0, ''],
  ];
  for (let e = fromExp; e < toExp; e++) {
    const [base, pre] = prefixes.filter(([b]) => b <= e).at(-1)!;
    const scale = 10 ** (e - base);
    for (const m of mantissas(s)) out.push(`${Number((m * scale).toPrecision(3))}${pre}F`);
  }
  return out;
}
