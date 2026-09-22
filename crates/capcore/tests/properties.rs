//! Physical and algorithmic consistency properties of the engine.

use std::collections::BTreeSet;

use capcore::cores::all_cores;
use capcore::engine::{eval, Engine, Net, Params, TopK};
use capcore::laplace::{ceq, ceq_graph};
use capcore::num::Num;
use capcore::rational::Q;
use capcore::space::{MultisetSpace, SizeSpace};
use proptest::prelude::*;

/// Independent brute force: every series-parallel value over the exact subset
/// `mask`, by plain recursion over all splits (no multiset symmetry, no trimming).
fn naive_sp(vals: &[Q], mask: u32) -> BTreeSet<Q> {
    let mut out = BTreeSet::new();
    if mask.count_ones() == 1 {
        out.insert(vals[mask.trailing_zeros() as usize]);
        return out;
    }
    let low = mask.isolate_lowest_one();
    let mut sub = (mask - 1) & mask;
    while sub > 0 {
        if sub & low != 0 {
            let l = naive_sp(vals, sub);
            let r = naive_sp(vals, mask & !sub);
            for &a in &l {
                for &b in &r {
                    out.insert(a.series(b));
                    out.insert(a.parallel(b));
                }
            }
        }
        sub = (sub - 1) & mask;
    }
    out
}

fn classes(vals: &[i64]) -> (Vec<Q>, Vec<u8>) {
    let mut cls: Vec<i64> = Vec::new();
    let mut cnt: Vec<u8> = Vec::new();
    for &v in vals {
        match cls.iter().position(|&c| c == v) {
            Some(k) => cnt[k] += 1,
            None => {
                cls.push(v);
                cnt.push(1);
            }
        }
    }
    (cls.into_iter().map(|v| Q::int(v as i128)).collect(), cnt)
}

fn engine_full_set(vals: &[i64], max_core_edges: usize) -> Vec<Q> {
    let (cls, cnt) = classes(vals);
    let space = MultisetSpace::new(&cnt, vals.len());
    let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
    let params = Params {
        max_core_edges,
        ..Params::default()
    };
    let mut eng = Engine::new(space, cls, all_cores(), params);
    eng.build_all(&|_| false).unwrap();
    eng.set(full).unwrap().iter().map(|e| e.v).collect()
}

fn dual(net: &Net) -> Net {
    match net {
        Net::Leaf(c) => Net::Leaf(*c),
        Net::Series(k) => Net::Parallel(k.iter().map(dual).collect()),
        Net::Parallel(k) => Net::Series(k.iter().map(dual).collect()),
        Net::Core { .. } => unreachable!("only series-parallel networks have this dual"),
    }
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]

    /// The multiset DP equals the naive subset recursion exactly.
    #[test]
    fn dp_matches_naive_enumeration(vals in prop::collection::vec(1i64..6, 1..6)) {
        let qs: Vec<Q> = vals.iter().map(|&v| Q::int(v as i128)).collect();
        let naive: Vec<Q> = naive_sp(&qs, (1u32 << vals.len()) - 1).into_iter().collect();
        prop_assert_eq!(engine_full_set(&vals, 0), naive);
    }

    /// Series of all ≤ C_eq ≤ parallel of all, for every network (bridges included).
    #[test]
    fn bounds(vals in prop::collection::vec(1i64..20, 1..7)) {
        let qs: Vec<Q> = vals.iter().map(|&v| Q::int(v as i128)).collect();
        let lo = qs.iter().copied().reduce(|a, b| a.series(b)).unwrap();
        let hi = qs.iter().copied().reduce(|a, b| a.parallel(b)).unwrap();
        let set = engine_full_set(&vals, 9);
        prop_assert_eq!(*set.first().unwrap(), lo);
        prop_assert_eq!(*set.last().unwrap(), hi);
    }

    /// C_eq(k·C) = k·C_eq(C): the value set scales linearly.
    #[test]
    fn homogeneity(vals in prop::collection::vec(1i64..8, 1..6), k in 2i64..5) {
        let scaled: Vec<i64> = vals.iter().map(|v| v * k).collect();
        let a: Vec<Q> = engine_full_set(&vals, 5).into_iter().map(|v| v.mul(Q::int(k as i128))).collect();
        prop_assert_eq!(engine_full_set(&scaled, 5), a);
    }

    /// Relabelling the parts changes nothing.
    #[test]
    fn permutation_invariance(mut vals in prop::collection::vec(1i64..9, 1..6), seed in any::<u64>()) {
        let before = engine_full_set(&vals, 5);
        let n = vals.len();
        for i in (1..n).rev() {
            vals.swap(i, (seed as usize).wrapping_mul(i + 7) % (i + 1));
        }
        prop_assert_eq!(engine_full_set(&vals, 5), before);
    }

    /// Rayleigh monotonicity: raising any capacitance never lowers C_eq.
    #[test]
    fn rayleigh_monotonicity(w in prop::collection::vec(1i64..30, 9), bump in 1i64..10, which in 0usize..9) {
        for core in all_cores() {
            let m = core.m();
            let base: Vec<Q> = w[..m].iter().map(|&x| Q::int(x as i128)).collect();
            let mut up = base.clone();
            up[which % m] = up[which % m].add(Q::int(bump as i128));
            prop_assert!(ceq(core.nv, 0, 1, &core.edges, &up) >= ceq(core.nv, 0, 1, &core.edges, &base));
        }
    }

    /// Series-parallel duality: swapping series and parallel and inverting every
    /// value inverts C_eq (capacitance ↔ elastance).
    #[test]
    fn series_parallel_duality(vals in prop::collection::vec(1i64..9, 2..6), pick in any::<prop::sample::Index>()) {
        let (cls, cnt) = classes(&vals);
        let space = MultisetSpace::new(&cnt, vals.len());
        let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
        let mut eng = Engine::new(space, cls.clone(), all_cores(), Params::default());
        eng.build_all(&|s| s == full).unwrap();
        let mut top = TopK::new(50);
        eng.query(full, Q::int(3), &mut top);
        let c = &top.items[pick.index(top.items.len())];
        let net = eng.network(c);
        let inv: Vec<Q> = cls.iter().map(|q| Q::int(1).div(*q)).collect();
        prop_assert_eq!(eval(&dual(&net), &inv, all_cores()), Q::int(1).div(c.v));
    }

    /// Meet-in-the-middle at the root finds exactly the best values of the fully
    /// materialised root set, and reconstructed networks evaluate to their value.
    #[test]
    fn root_query_matches_materialised(vals in prop::collection::vec(1i64..12, 2..7), t_num in 1i64..60, t_den in 1i64..10) {
        let (cls, cnt) = classes(&vals);
        let n = vals.len();
        let target = Q::new(t_num as i128, t_den as i128);
        let mk = || {
            let space = MultisetSpace::new(&cnt, n);
            Engine::new(space, cls.clone(), all_cores(), Params { max_core_edges: 7, ..Params::default() })
        };
        let full = MultisetSpace::new(&cnt, n).id(MultisetSpace::pack(&cnt)).unwrap();
        let mut lazy = mk();
        lazy.build_all(&|s| s == full).unwrap();
        let mut a = TopK::new(8);
        lazy.query(full, target, &mut a);
        let mut eager = mk();
        eager.build_all(&|_| false).unwrap();
        let mut b = TopK::new(8);
        eager.query(full, target, &mut b);
        let va: Vec<Q> = a.items.iter().map(|c| c.v).collect();
        let vb: Vec<Q> = b.items.iter().map(|c| c.v).collect();
        prop_assert_eq!(&va, &vb);
        for c in &a.items {
            let net = lazy.network(c);
            prop_assert_eq!(net.parts(), n);
            prop_assert_eq!(eval(&net, &cls, all_cores()), c.v);
        }
    }

    /// Coarsening keeps its promise: the best error found with a tiny per-state
    /// cap is within the reported bound of the exact optimum.
    #[test]
    fn coarsening_bound_holds(vals in prop::collection::vec(1.0f64..100.0, 5..8), t in 1.0f64..50.0) {
        let n = vals.len();
        let cnt = vec![1u8; n];
        let run = |cap: usize| {
            let space = MultisetSpace::new(&cnt, n);
            let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
            let p = Params { eps: 1e-12, max_per_state: cap, ..Params::default() };
            let mut eng = Engine::new(space, vals.clone(), all_cores(), p);
            eng.build_all(&|s| s == full).unwrap();
            let mut top = TopK::new(1);
            eng.query(full, t, &mut top);
            (top.items[0].err, eng.stats.eps_used)
        };
        let (exact, _) = run(0);
        let (approx, eps) = run(40);
        let bound = (eps * (n - 1) as f64).exp_m1() * (1.0 + exact) + 1e-12;
        prop_assert!(approx <= exact + bound, "approx {} exact {} bound {}", approx, exact, bound);
    }
}

#[test]
fn inventory_size_space_matches_brute_force() {
    // E6 decade: best networks of up to 3 parts with unlimited repetition.
    let e6 = [1.0, 1.5, 2.2, 3.3, 4.7, 6.8];
    let target = 5.123;
    let mut brute: Vec<f64> = Vec::new();
    for &a in &e6 {
        brute.push(a);
        for &b in &e6 {
            brute.push(a.series(b));
            brute.push(a.parallel(b));
            for &c in &e6 {
                for x in [a.series(b), a.parallel(b)] {
                    brute.push(x.series(c));
                    brute.push(x.parallel(c));
                }
            }
        }
    }
    let best = brute
        .iter()
        .map(|v| ((v - target) / target).abs())
        .fold(f64::INFINITY, f64::min);
    let space = SizeSpace {
        kmax: 3,
        nclass: e6.len(),
    };
    let mut eng = Engine::new(
        space,
        e6.to_vec(),
        all_cores(),
        Params {
            eps: 1e-12,
            ..Params::default()
        },
    );
    eng.build_all(&|s| s == 2).unwrap();
    let mut top = TopK::new(5);
    for s in 0..3 {
        eng.query(s, target, &mut top);
    }
    assert!((top.items[0].err - best).abs() < 1e-12);
    for c in &top.items {
        assert!(eng.network(c).parts() <= 3);
        assert!((eval(&eng.network(c), &e6, all_cores()) - c.v).abs() < 1e-12);
    }
}

#[test]
fn every_core_network_evaluates_like_its_flat_graph() {
    // Fill each core with parts 1..m and compare the reducer with the dense solver.
    for core in all_cores() {
        let w: Vec<f64> = (1..=core.m()).map(|x| x as f64).collect();
        let edges: Vec<(usize, usize, f64)> = core
            .edges
            .iter()
            .zip(&w)
            .map(|(&(u, v), &c)| (u, v, c))
            .collect();
        let a = ceq(core.nv, 0, 1, &core.edges, &w);
        let b = ceq_graph(core.nv, 0, 1, &edges);
        assert!((a - b).abs() < 1e-12 * a);
    }
}
