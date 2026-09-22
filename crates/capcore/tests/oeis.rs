//! Combinatorial ground truth: the number of distinct equivalent values of `n`
//! equal capacitors must match the published OEIS sequences exactly. Capacitors
//! and resistors share the same algebra (series ↔ parallel are swapped, which is
//! a bijection on value sets), so the resistor sequences apply.

use capcore::cores::all_cores;
use capcore::engine::{Engine, Params};
use capcore::rational::Q;
use capcore::space::MultisetSpace;

fn count_equal(n: usize, max_core_edges: usize) -> usize {
    let space = MultisetSpace::new(&[n as u8], n);
    let full = space.id(MultisetSpace::pack(&[n as u8])).unwrap();
    let params = Params {
        max_core_edges,
        ..Params::default()
    };
    let mut eng = Engine::new(space, vec![Q::int(1)], all_cores(), params);
    eng.build_all(&|_| false).unwrap();
    eng.set(full).unwrap().len()
}

#[test]
fn a048211_series_parallel_values() {
    // Number of distinct values from n equal elements, series-parallel only.
    let expected = [1, 2, 4, 9, 22, 53, 131, 337, 869, 2213, 5691, 14517];
    for (i, &e) in expected.iter().enumerate() {
        assert_eq!(count_equal(i + 1, 0), e, "n = {}", i + 1);
    }
}

#[test]
fn a174283_series_parallel_and_bridge_values() {
    // Adds the Wheatstone bridge (the only 5-edge core) recursively.
    let expected = [1, 2, 4, 9, 23, 57, 151, 415, 1157];
    for (i, &e) in expected.iter().enumerate() {
        assert_eq!(count_equal(i + 1, 5), e, "n = {}", i + 1);
    }
}

#[test]
fn a337517_all_networks_values() {
    // Every two-terminal network (all 3-connected cores).
    let expected = [1, 2, 4, 9, 23, 57, 151, 427, 1263];
    for (i, &e) in expected.iter().enumerate() {
        assert_eq!(count_equal(i + 1, 9), e, "n = {}", i + 1);
    }
}

#[test]
fn a006351_labeled_series_parallel_networks() {
    // With generic (algebraically independent) values, distinct series-parallel
    // networks give distinct values, so the value count equals the number of
    // series-parallel networks with n labeled edges.
    let expected = [1, 2, 8, 52, 472, 5504, 78416];
    let primes = [2.0f64, 3.0, 5.0, 7.0, 11.0, 13.0, 17.0];
    for (i, &e) in expected.iter().enumerate() {
        let n = i + 1;
        let counts = vec![1u8; n];
        let space = MultisetSpace::new(&counts, n);
        let full = space.id(MultisetSpace::pack(&counts)).unwrap();
        let vals: Vec<f64> = primes[..n].iter().map(|p| p.ln()).collect();
        let params = Params {
            eps: 1e-13,
            ..Params::default()
        };
        let mut eng = Engine::new(space, vals, all_cores(), params);
        eng.build_all(&|_| false).unwrap();
        assert_eq!(eng.set(full).unwrap().len(), e, "n = {n}");
    }
}

/// Golden case from the external research review: {1,2,3,4,5} → 170/71 needs a
/// bridge; the best series-parallel value is 43/18 (0.2288 % away).
#[test]
fn bridge_5_golden_sp_gap() {
    use capcore::engine::TopK;
    let vals: Vec<Q> = (1..=5).map(Q::int).collect();
    let target = Q::new(170, 71);
    let best = |max_core_edges: usize| {
        let cnt = [1u8; 5];
        let space = MultisetSpace::new(&cnt, 5);
        let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
        let params = Params {
            max_core_edges,
            ..Params::default()
        };
        let mut eng = Engine::new(space, vals.clone(), all_cores(), params);
        eng.build_all(&|s| s == full).unwrap();
        let mut top = TopK::new(1);
        eng.query(full, target, &mut top);
        top.items[0].v
    };
    assert_eq!(best(0), Q::new(43, 18));
    assert_eq!(best(5), target);
}
