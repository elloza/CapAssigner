//! Exact rational numbers on `i128`, used as the verification number type.
//!
//! Every value produced by a capacitor network with rational component values is
//! rational (Kirchhoff's laws are linear with rational coefficients), so running
//! the engine over `Q` gives exact results; the OEIS counting tests rely on it.

use std::cmp::Ordering;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub struct Q {
    n: i128,
    d: i128,
}

fn gcd(mut a: i128, mut b: i128) -> i128 {
    a = a.abs();
    b = b.abs();
    while b != 0 {
        let t = a % b;
        a = b;
        b = t;
    }
    a
}

fn mul(a: i128, b: i128) -> i128 {
    a.checked_mul(b).expect("rational overflow")
}

// Inherent arithmetic mirrors `Num` so the engine never needs operator traits.
#[allow(clippy::should_implement_trait)]
impl Q {
    pub fn new(n: i128, d: i128) -> Q {
        assert!(d != 0, "zero denominator");
        let g = gcd(n, d).max(1);
        let s = if d < 0 { -1 } else { 1 };
        Q {
            n: s * n / g,
            d: s * d / g,
        }
    }

    pub fn int(n: i128) -> Q {
        Q { n, d: 1 }
    }

    pub fn num(self) -> i128 {
        self.n
    }

    pub fn den(self) -> i128 {
        self.d
    }

    pub fn add(self, o: Q) -> Q {
        let g = gcd(self.d, o.d).max(1);
        let d = mul(self.d / g, o.d);
        let n = mul(self.n, o.d / g)
            .checked_add(mul(o.n, self.d / g))
            .expect("rational overflow");
        Q::new(n, d)
    }

    pub fn sub(self, o: Q) -> Q {
        self.add(Q { n: -o.n, d: o.d })
    }

    pub fn mul(self, o: Q) -> Q {
        let g1 = gcd(self.n, o.d).max(1);
        let g2 = gcd(o.n, self.d).max(1);
        Q::new(mul(self.n / g1, o.n / g2), mul(self.d / g2, o.d / g1))
    }

    pub fn div(self, o: Q) -> Q {
        assert!(o.n != 0, "division by zero");
        self.mul(Q::new(o.d, o.n))
    }

    pub fn to_f64(self) -> f64 {
        self.n as f64 / self.d as f64
    }
}

impl PartialOrd for Q {
    fn partial_cmp(&self, o: &Q) -> Option<Ordering> {
        Some(self.cmp(o))
    }
}

impl Ord for Q {
    fn cmp(&self, o: &Q) -> Ordering {
        mul(self.n, o.d).cmp(&mul(o.n, self.d))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_sign_and_gcd() {
        assert_eq!(Q::new(2, -4), Q::new(-1, 2));
        assert_eq!(Q::new(6, 9).num(), 2);
        assert_eq!(Q::new(6, 9).den(), 3);
    }

    #[test]
    fn arithmetic() {
        let a = Q::new(1, 2);
        let b = Q::new(1, 3);
        assert_eq!(a.add(b), Q::new(5, 6));
        assert_eq!(a.sub(b), Q::new(1, 6));
        assert_eq!(a.mul(b), Q::new(1, 6));
        assert_eq!(a.div(b), Q::new(3, 2));
        assert!(b < a);
    }
}
