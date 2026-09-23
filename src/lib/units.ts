// Parsing and formatting of capacitance values.
//
// Accepted forms (all case-sensitive only where it matters):
//   5.2pF  5.2 pF  5.2p  5,2pF  4p7 / 4n7 / 2u2 (RKM code)  10fF  2.2µF 2.2uF  1mF  0.5F
//   1e-11  1.2E-12  1.2*10^-12  1.2×10^-12   → farads (exponent notation)
//   1.5e3pF                                   → exponent with a prefix
//   170/71pF                                  → exact fraction
//   5.2                                       → the chosen default unit
//   0.0000000000052                           → farads (a bare number below
//                                               1e-3 is read in farads, as in v1)
// A bare "f" suffix is femto (as in SPICE); "F" alone is farads.

import { Frac } from './exact';

export type Prefix = 'f' | 'p' | 'n' | 'µ' | 'm' | '';

export const PREFIX_EXP: Record<Prefix, number> = { f: -15, p: -12, n: -9, µ: -6, m: -3, '': 0 };
export const UNITS: Prefix[] = ['f', 'p', 'n', 'µ', 'm', ''];

export interface Parsed {
  /** Value in farads as a double. */
  farads: number;
  /** The same value, exact, from the decimal text. */
  exact: Frac;
  /** Canonical display string. */
  text: string;
}

export type ParseResult = { ok: true; value: Parsed } | { ok: false; error: ParseError };

export type ParseError =
  | { code: 'empty' }
  | { code: 'syntax'; input: string }
  | { code: 'nonpositive'; input: string };

const PREFIX_ALIASES: Record<string, Prefix> = {
  f: 'f',
  p: 'p',
  P: 'p',
  n: 'n',
  N: 'n',
  u: 'µ',
  U: 'µ',
  µ: 'µ',
  μ: 'µ', // Greek mu, which many keyboards produce instead of the micro sign
  m: 'm',
};

function scaled(mantissa: string, exp: number): Frac {
  const base = Frac.fromDecimal(mantissa);
  return exp >= 0
    ? base.mul(new Frac(10n ** BigInt(exp)))
    : base.div(new Frac(10n ** BigInt(-exp)));
}

function done(exact: Frac, input: string): ParseResult {
  if (exact.cmp(Frac.ZERO) <= 0) return { ok: false, error: { code: 'nonpositive', input } };
  const farads = exact.toNumber();
  return { ok: true, value: { farads, exact, text: formatCapacitance(farads) } };
}

export function parseCapacitance(raw: string, defaultUnit: Prefix = 'p'): ParseResult {
  const input = raw.trim();
  if (input === '') return { ok: false, error: { code: 'empty' } };
  const s = input.replace(/\s+/g, '').replace(/(\d),(\d)/g, '$1.$2');
  const num = '([+-]?(?:\\d+\\.?\\d*|\\.\\d+))';

  // Exponent notation: always farads.
  let m = new RegExp(`^${num}[eE]([+-]?\\d+)F?$`).exec(s);
  if (m) return done(scaled(m[1]!, Number(m[2])), input);
  m = new RegExp(`^${num}[*x×·]10\\^([+-]?\\d+)F?$`).exec(s);
  if (m) return done(scaled(m[1]!, Number(m[2])), input);

  // Exact fraction: 170/71pF.
  m = /^(\d+(?:\.\d+)?)\/(\d+(?:\.\d+)?)([fpPnNuUµμm]?)F?$/.exec(s);
  if (m) {
    const den = Frac.fromDecimal(m[2]!);
    if (den.isZero()) return { ok: false, error: { code: 'syntax', input } };
    const prefix = m[3] === '' ? defaultUnit : PREFIX_ALIASES[m[3]!]!;
    return done(scaled(m[1]!, PREFIX_EXP[prefix]).div(den), input);
  }

  // RKM code: 4p7 = 4.7p.
  m = /^(\d+)([fpnuUµμm])(\d+)F?$/.exec(s);
  if (m) {
    const prefix = PREFIX_ALIASES[m[2]!]!;
    return done(scaled(`${m[1]}.${m[3]}`, PREFIX_EXP[prefix]), input);
  }

  // Exponent with a prefix: 1.5e3pF.
  m = new RegExp(`^${num}[eE]([+-]?\\d+)([fpPnNuUµμm])F?$`).exec(s);
  if (m) {
    const prefix = PREFIX_ALIASES[m[3]!]!;
    return done(scaled(m[1]!, Number(m[2]) + PREFIX_EXP[prefix]), input);
  }

  // Number with optional prefix and optional F.
  m = new RegExp(`^${num}([fpPnNuUµμm]?)([Ff]?)$`).exec(s);
  if (m) {
    const [, mant, pre, unit] = m as unknown as [string, string, string, string];
    let prefix: Prefix;
    // A tiny bare number is almost surely already in farads (v1 behaviour).
    if (pre === '' && unit === '' && Number(mant) !== 0 && Math.abs(Number(mant)) < 1e-3) prefix = '';
    else if (pre === '' && unit === '') prefix = defaultUnit;
    else if (pre === '' && unit === 'F') prefix = '';
    else if (pre === '' && unit === 'f') prefix = 'f';
    else if (pre === 'f' && unit !== '') prefix = 'f';
    else prefix = PREFIX_ALIASES[pre]!;
    return done(scaled(mant, PREFIX_EXP[prefix]), input);
  }
  return { ok: false, error: { code: 'syntax', input } };
}

/**
 * Split a list typed by the user. Separators: whitespace, ';', newlines, and
 * commas that are not decimal commas (a comma between two digits is decimal).
 */
export function splitList(text: string): string[] {
  return text
    .split(/[\s;]+/)
    .flatMap((tok) => {
      // "1,2,3" is a list; "4,7" (a single comma between digits) is a decimal.
      const decimal = /^[^,]*\d,\d[^,]*$/.test(tok);
      return decimal ? [tok] : tok.split(',');
    })
    .filter((t) => t !== '');
}

/** Merge "5.2 pF" typed with a space back into one token. */
export function tokenize(text: string): string[] {
  const out: string[] = [];
  for (const t of splitList(text)) {
    if (/^[fpPnNuUµμm]?F?$/.test(t) && t !== '' && out.length > 0 && /\d$/.test(out[out.length - 1]!)) {
      out[out.length - 1] += t;
    } else out.push(t);
  }
  return out;
}

export function parseList(
  text: string,
  defaultUnit: Prefix = 'p',
): { values: Parsed[]; errors: ParseError[] } {
  const values: Parsed[] = [];
  const errors: ParseError[] = [];
  for (const tok of tokenize(text)) {
    const r = parseCapacitance(tok, defaultUnit);
    if (r.ok) values.push(r.value);
    else errors.push(r.error);
  }
  return { values, errors };
}

let decimalComma = false;

/** Display numbers with a decimal comma (Spanish) instead of a point. */
export function setDecimalComma(on: boolean): void {
  decimalComma = on;
}

/** Localise the decimal separator of an already formatted number. */
export function localNumber(s: string): string {
  return decimalComma ? s.replace(/(\d)\.(\d)/g, '$1,$2') : s;
}

/** Choose the prefix that puts the mantissa in [1, 1000). */
export function bestPrefix(farads: number): Prefix {
  const a = Math.abs(farads);
  for (const p of UNITS) {
    if (a < 10 ** (PREFIX_EXP[p] + 3) * (1 - 5e-13)) return p;
  }
  return '';
}

export function formatCapacitance(farads: number, digits = 4): string {
  if (farads === 0) return '0 F';
  if (!Number.isFinite(farads)) return String(farads);
  let p = bestPrefix(farads);
  let mant = Number((farads / 10 ** PREFIX_EXP[p]).toPrecision(digits));
  // Rounding may carry into the next prefix (999.99 pF → 1000 pF → 1 nF).
  const next = UNITS[UNITS.indexOf(p) + 1];
  if (Math.abs(mant) >= 1000 && next !== undefined) {
    mant = Number((farads / 10 ** PREFIX_EXP[next]).toPrecision(digits));
    p = next;
  }
  return localNumber(`${mant} ${p}F`);
}

export function formatPercent(rel: number, digits = 3): string {
  const pct = rel * 100;
  // Differences below 1e-12 are float round-off of an exact match.
  if (Math.abs(rel) < 1e-12) return '0 %';
  const a = Math.abs(pct);
  const s = a >= 0.01 ? pct.toFixed(digits) : pct.toExponential(2);
  return localNumber(`${pct > 0 ? '+' : ''}${s} %`);
}
