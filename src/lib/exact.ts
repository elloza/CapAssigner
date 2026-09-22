// Exact rational arithmetic on BigInt, used to verify networks independently
// of the floating-point engine. Values are built from the decimal *text* the
// user typed, so "4.7pF" is exactly 47/10 · 10^-12 and never a rounded double.

function gcd(a: bigint, b: bigint): bigint {
  if (a < 0n) a = -a;
  if (b < 0n) b = -b;
  while (b !== 0n) [a, b] = [b, a % b];
  return a;
}

export class Frac {
  readonly n: bigint;
  readonly d: bigint;

  constructor(n: bigint, d: bigint = 1n) {
    if (d === 0n) throw new RangeError('zero denominator');
    if (d < 0n) {
      n = -n;
      d = -d;
    }
    const g = gcd(n, d) || 1n;
    this.n = n / g;
    this.d = d / g;
  }

  static readonly ZERO = new Frac(0n);
  static readonly ONE = new Frac(1n);

  static int(v: number | bigint): Frac {
    return new Frac(BigInt(v));
  }

  /** Parse a plain decimal string such as "-12.500e-3" exactly. */
  static fromDecimal(text: string): Frac {
    const m = /^([+-]?)(\d*)(?:\.(\d*))?(?:[eE]([+-]?\d+))?$/.exec(text.trim());
    if (!m || (m[2] === '' && (m[3] ?? '') === '')) throw new SyntaxError(`not a decimal: ${text}`);
    const int = m[2] ?? '';
    const frac = m[3] ?? '';
    const exp = Number(m[4] ?? '0') - frac.length;
    let n = BigInt((int + frac).replace(/^0+(?=\d)/, '') || '0');
    if (m[1] === '-') n = -n;
    return exp >= 0 ? new Frac(n * 10n ** BigInt(exp)) : new Frac(n, 10n ** BigInt(-exp));
  }

  /** Exact value of a finite double (every double is a dyadic rational). */
  static fromNumber(x: number): Frac {
    if (!Number.isFinite(x)) throw new RangeError('non-finite');
    if (Number.isInteger(x)) return new Frac(BigInt(x));
    let d = 1n;
    while (!Number.isInteger(x)) {
      x *= 2;
      d *= 2n;
    }
    return new Frac(BigInt(x), d);
  }

  add(o: Frac): Frac {
    return new Frac(this.n * o.d + o.n * this.d, this.d * o.d);
  }
  sub(o: Frac): Frac {
    return new Frac(this.n * o.d - o.n * this.d, this.d * o.d);
  }
  mul(o: Frac): Frac {
    return new Frac(this.n * o.n, this.d * o.d);
  }
  div(o: Frac): Frac {
    if (o.n === 0n) throw new RangeError('division by zero');
    return new Frac(this.n * o.d, this.d * o.n);
  }
  neg(): Frac {
    return new Frac(-this.n, this.d);
  }
  cmp(o: Frac): number {
    const l = this.n * o.d;
    const r = o.n * this.d;
    return l < r ? -1 : l > r ? 1 : 0;
  }
  eq(o: Frac): boolean {
    return this.n === o.n && this.d === o.d;
  }
  isZero(): boolean {
    return this.n === 0n;
  }

  /** Correctly rounded enough for display and float comparisons. */
  toNumber(): number {
    const neg = this.n < 0n;
    const n = neg ? -this.n : this.n;
    // Scale so the quotient keeps ~20 significant digits.
    const shift = BigInt(Math.max(0, 64 - (n.toString(2).length - this.d.toString(2).length)));
    const q = Number((n << shift) / this.d);
    // Divide in two steps so 2^shift never overflows for tiny values.
    const half = Math.min(Number(shift), 1000);
    const v = q / 2 ** half / 2 ** (Number(shift) - half);
    return neg ? -v : v;
  }

  toString(): string {
    return this.d === 1n ? `${this.n}` : `${this.n}/${this.d}`;
  }
}

export function series(a: Frac, b: Frac): Frac {
  return a.mul(b).div(a.add(b));
}

export function parallel(a: Frac, b: Frac): Frac {
  return a.add(b);
}
