//! Equivalent capacitance of an arbitrary two-terminal network by Kron reduction.
//!
//! The nodal equations of a capacitor network are `L·V = Q`, with `L` the
//! capacitance-weighted graph Laplacian. Eliminating every internal node (the
//! Schur complement onto the terminals, a.k.a. Kron reduction) leaves a 2×2
//! Laplacian whose off-diagonal entry is `−C_eq`. Elimination keeps the matrix a
//! Laplacian (non-positive off-diagonals, positive pivots), so no pivoting is
//! needed and the same code is exact over rationals.

use crate::num::Num;

/// Maximum number of vertices supported by the stack-allocated reduction.
pub const MAX_V: usize = 8;

/// `C_eq` between `a` and `b` for a graph with `nv` vertices, `edges[i]` carrying
/// capacitance `w[i]`. Isolated internal nodes contribute nothing.
pub fn ceq<T: Num>(nv: usize, a: usize, b: usize, edges: &[(usize, usize)], w: &[T]) -> T {
    assert!(nv <= MAX_V && a < nv && b < nv && a != b);
    assert_eq!(edges.len(), w.len());
    let z = T::zero();
    let mut l = [[z; MAX_V]; MAX_V];
    for (&(u, v), &c) in edges.iter().zip(w) {
        if u == v {
            continue;
        }
        l[u][u] = l[u][u].add(c);
        l[v][v] = l[v][v].add(c);
        l[u][v] = l[u][v].sub(c);
        l[v][u] = l[v][u].sub(c);
    }
    let mut alive = [false; MAX_V];
    alive[..nv].fill(true);
    for k in 0..nv {
        if k == a || k == b {
            continue;
        }
        alive[k] = false;
        let p = l[k][k];
        if p <= z {
            continue;
        }
        for i in 0..nv {
            if !alive[i] || l[i][k] == z {
                continue;
            }
            let f = l[i][k].div(p);
            for j in 0..nv {
                if alive[j] && l[k][j] != z {
                    l[i][j] = l[i][j].sub(f.mul(l[k][j]));
                }
            }
        }
    }
    z.sub(l[a][b])
}

/// Same reduction for graphs of any size (heap-allocated, `O(nv³)`), used to
/// double-check reconstructed networks.
pub fn ceq_graph(nv: usize, a: usize, b: usize, edges: &[(usize, usize, f64)]) -> f64 {
    let mut l = vec![vec![0.0f64; nv]; nv];
    for &(u, v, c) in edges {
        if u != v {
            l[u][u] += c;
            l[v][v] += c;
            l[u][v] -= c;
            l[v][u] -= c;
        }
    }
    let mut alive = vec![true; nv];
    for k in 0..nv {
        if k == a || k == b {
            continue;
        }
        alive[k] = false;
        let p = l[k][k];
        if p <= 0.0 {
            continue;
        }
        for i in 0..nv {
            if !alive[i] || l[i][k] == 0.0 {
                continue;
            }
            let f = l[i][k] / p;
            for j in 0..nv {
                if alive[j] && l[k][j] != 0.0 {
                    l[i][j] -= f * l[k][j];
                }
            }
        }
    }
    -l[a][b]
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::rational::Q;

    #[test]
    fn series_and_parallel() {
        let s = ceq(3, 0, 1, &[(0, 2), (2, 1)], &[Q::int(2), Q::int(2)]);
        assert_eq!(s, Q::int(1));
        let p = ceq(2, 0, 1, &[(0, 1), (0, 1)], &[Q::int(2), Q::int(3)]);
        assert_eq!(p, Q::int(5));
    }

    #[test]
    fn unit_wheatstone_bridge_is_one() {
        // A=0, B=1, internal 2,3; the bridge element is 2-3.
        let e = [(0, 2), (0, 3), (2, 1), (3, 1), (2, 3)];
        assert_eq!(ceq(4, 0, 1, &e, &[Q::int(1); 5]), Q::int(1));
    }

    #[test]
    fn unbalanced_bridge_closed_form() {
        // Arms c1 (A-x), c2 (A-y), c3 (x-B), c4 (y-B), bridge c5 (x-y).
        let c = [1.0, 2.0, 3.0, 4.0, 5.0];
        let e = [(0, 2), (0, 3), (2, 1), (3, 1), (2, 3)];
        let got = ceq(4, 0, 1, &e, &c);
        let [c1, c2, c3, c4, c5] = c;
        let num = c1 * c2 * (c3 + c4) + c3 * c4 * (c1 + c2) + c5 * (c1 + c2) * (c3 + c4);
        let den = (c1 + c3) * (c2 + c4) + c5 * (c1 + c2 + c3 + c4);
        assert!((got - num / den).abs() < 1e-12);
    }

    #[test]
    fn disconnected_terminal_gives_zero() {
        assert_eq!(ceq(3, 0, 1, &[(0, 2)], &[1.0]), 0.0);
    }
}
