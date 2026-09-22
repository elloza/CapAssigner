//! Number abstraction so the engine runs on `f64` (production) and on exact
//! rationals (verification) with the same code.

use crate::rational::Q;

pub trait Num: Copy + PartialOrd + std::fmt::Debug + 'static {
    fn zero() -> Self;
    fn add(self, o: Self) -> Self;
    fn sub(self, o: Self) -> Self;
    fn mul(self, o: Self) -> Self;
    fn div(self, o: Self) -> Self;
    fn to_f64(self) -> f64;
    /// `b` (>= `a`) is indistinguishable from `a`: exact equality when `eps == 0`,
    /// otherwise within a relative factor `1 + eps`.
    fn close(a: Self, b: Self, eps: f64) -> bool;

    /// Capacitors in parallel add.
    fn parallel(self, o: Self) -> Self {
        self.add(o)
    }

    /// Capacitors in series: C1·C2 / (C1 + C2).
    fn series(self, o: Self) -> Self {
        self.mul(o).div(self.add(o))
    }
}

impl Num for f64 {
    fn zero() -> Self {
        0.0
    }
    fn add(self, o: Self) -> Self {
        self + o
    }
    fn sub(self, o: Self) -> Self {
        self - o
    }
    fn mul(self, o: Self) -> Self {
        self * o
    }
    fn div(self, o: Self) -> Self {
        self / o
    }
    fn to_f64(self) -> f64 {
        self
    }
    fn close(a: Self, b: Self, eps: f64) -> bool {
        b <= a * (1.0 + eps)
    }
}

impl Num for Q {
    fn zero() -> Self {
        Q::int(0)
    }
    fn add(self, o: Self) -> Self {
        Q::add(self, o)
    }
    fn sub(self, o: Self) -> Self {
        Q::sub(self, o)
    }
    fn mul(self, o: Self) -> Self {
        Q::mul(self, o)
    }
    fn div(self, o: Self) -> Self {
        Q::div(self, o)
    }
    fn to_f64(self) -> f64 {
        Q::to_f64(self)
    }
    fn close(a: Self, b: Self, eps: f64) -> bool {
        if eps == 0.0 {
            a == b
        } else {
            b.to_f64() <= a.to_f64() * (1.0 + eps)
        }
    }
}
