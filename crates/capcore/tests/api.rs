//! End-to-end tests of the JSON-facing solver, including the v1 golden fixtures.

use capcore::api::{solve, Mode, Request, Response, Tree};
use serde_json::Value;

fn req(mode: Mode, values: &[f64], target: f64) -> Request {
    Request {
        mode,
        values: values.to_vec(),
        target,
        stock: None,
        max_parts: 4,
        min_parts: 1,
        top_k: 10,
        max_core_edges: 0,
        max_entries: 6_000_000,
    }
}

fn run(r: &Request) -> Response {
    solve(r, &mut |_| {}).expect("solve")
}

fn count_leaves(t: &Tree) -> usize {
    match t {
        Tree::Leaf { .. } => 1,
        Tree::Series { c } | Tree::Parallel { c } | Tree::Core { c, .. } => {
            c.iter().map(count_leaves).sum()
        }
    }
}

#[test]
fn classroom_problem_is_solved_exactly() {
    // v1 regression: 3, 2, 3, 1 pF → 1 pF needs (C2 ∥ C4) in series with C1 and C3.
    let res = run(&req(Mode::All, &[3e-12, 2e-12, 3e-12, 1e-12], 1e-12));
    let best = &res.solutions[0];
    assert!(best.rel_error.abs() < 1e-12);
    assert!(res.stats.exhaustive);
    let mut idx: Vec<usize> = best.leaves.iter().map(|l| l.index.unwrap()).collect();
    idx.sort();
    assert_eq!(idx, vec![0, 1, 2, 3], "every capacitor used exactly once");
}

#[test]
fn bridge_beats_series_parallel_for_five_equal() {
    // Five equal capacitors cannot give C with series-parallel, but a balanced
    // Wheatstone bridge does.
    let mut r = req(Mode::All, &[8e-12; 5], 8e-12);
    let sp = run(&r);
    assert!(sp.solutions[0].rel_error.abs() > 0.1);
    r.max_core_edges = 5;
    let all = run(&r);
    assert!(all.solutions[0].rel_error.abs() < 1e-12);
    assert!(matches!(all.solutions[0].tree, Tree::Core { .. }));
    assert_eq!(all.cores.len(), 1);
    assert_eq!(all.cores[0].edges.len(), 5);
}

#[test]
fn golden_v1_fixtures_are_matched_or_beaten() {
    let raw = include_str!("../../../tests/fixtures/golden_v1.json");
    let golden: Value = serde_json::from_str(raw).unwrap();
    for case in golden["cases"].as_array().unwrap() {
        let caps: Vec<f64> = case["capacitors"]
            .as_array()
            .unwrap()
            .iter()
            .map(|v| v.as_f64().unwrap())
            .collect();
        let target = case["target"].as_f64().unwrap();
        let v1 = case["v1_best_rel_error"].as_f64().unwrap();
        let res = run(&req(Mode::All, &caps, target));
        let best = res.solutions[0].rel_error.abs();
        assert!(
            best <= v1 + 1e-12,
            "{}: v2 {best:e} worse than v1 {v1:e}",
            case["id"]
        );
        assert!(res.stats.exhaustive, "{} should be exhaustive", case["id"]);
    }
}

#[test]
fn solutions_are_sorted_distinct_and_consistent() {
    let caps = [1.5e-12, 2.7e-12, 3.3e-12, 4.7e-12, 5.6e-12, 6.8e-12];
    let mut r = req(Mode::All, &caps, 3.1e-12);
    r.top_k = 50;
    r.max_core_edges = 7;
    let res = run(&r);
    assert_eq!(res.solutions.len(), 50);
    for w in res.solutions.windows(2) {
        assert!(w[0].rel_error.abs() <= w[1].rel_error.abs());
        assert!((w[0].value - w[1].value).abs() > 1e-24);
    }
    for s in &res.solutions {
        assert_eq!(s.parts, 6);
        assert_eq!(count_leaves(&s.tree), 6);
        assert_eq!(s.graph.edges.len(), 6);
        assert!(((s.value - 3.1e-12) / 3.1e-12 - s.rel_error).abs() < 1e-9);
    }
}

#[test]
fn inventory_unlimited_e12() {
    let e12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2];
    let decade: Vec<f64> = e12.iter().flat_map(|v| [v * 1e-12, v * 1e-11]).collect();
    let mut r = req(Mode::Inventory, &decade, 7.77e-12);
    r.max_parts = 3;
    let res = run(&r);
    let best = &res.solutions[0];
    assert!(best.parts <= 3);
    assert!(best.rel_error.abs() < 2e-3, "{}", best.rel_error);
    assert!(best.leaves.iter().all(|l| l.index.is_none()));
}

#[test]
fn inventory_prefers_fewer_parts_for_equal_values() {
    // 10 pF exists as a single part; a 2-part network with the same value must
    // not displace it.
    let mut r = req(Mode::Inventory, &[10e-12, 20e-12], 10e-12);
    r.max_parts = 3;
    let res = run(&r);
    assert_eq!(res.solutions[0].parts, 1);
}

#[test]
fn inventory_limited_stock_is_respected() {
    let mut r = req(Mode::Inventory, &[1e-12, 5e-12], 3e-12);
    r.max_parts = 4;
    r.stock = Some(vec![4, 0]);
    let res = run(&r);
    for s in &res.solutions {
        assert!(s.leaves.iter().all(|l| l.value == 1e-12));
    }
    // 3 pF = three 1 pF in parallel.
    assert!(res.solutions[0].rel_error.abs() < 1e-12);
    assert_eq!(res.solutions[0].parts, 3);
}

#[test]
fn large_problem_is_coarsened_with_a_bound() {
    let caps: Vec<f64> = (1..=10).map(|k| (k as f64).sqrt() * 1e-12).collect();
    let mut r = req(Mode::All, &caps, 2.345e-12);
    r.max_entries = 400_000;
    r.top_k = 5;
    let res = run(&r);
    assert!(!res.stats.exhaustive);
    // Worst-case bound for a deliberately tiny budget; the actual error is far smaller.
    assert!(res.stats.bound_rel > 0.0 && res.stats.bound_rel < 0.1);
    assert!(res.solutions[0].rel_error.abs() < 1e-4);
    assert!(res.stats.entries <= 400_000);
}

#[test]
fn invalid_requests_are_rejected() {
    let bad = [
        req(Mode::All, &[], 1.0),
        req(Mode::All, &[1.0, -2.0], 1.0),
        req(Mode::All, &[1.0], 0.0),
        req(Mode::All, &[1.0; 13], 1.0),
        Request {
            max_parts: 0,
            ..req(Mode::Inventory, &[1.0], 1.0)
        },
        Request {
            stock: Some(vec![1, 2]),
            ..req(Mode::Inventory, &[1.0], 1.0)
        },
        Request {
            top_k: 0,
            ..req(Mode::All, &[1.0], 1.0)
        },
        // Ratios that would underflow after normalisation (external audit).
        req(Mode::All, &[1e-200, 1.0], 1e150),
    ];
    for r in &bad {
        assert!(solve(r, &mut |_| {}).is_err(), "{r:?}");
    }
}

#[test]
fn deterministic_output() {
    let r = Request {
        max_core_edges: 7,
        ..req(Mode::All, &[1e-6, 2.2e-6, 4.7e-6, 10e-6, 22e-6], 5e-6)
    };
    let a = serde_json::to_string(&run(&r)).unwrap();
    let b = serde_json::to_string(&run(&r)).unwrap();
    assert_eq!(a, b);
}

/// Timing survey used to choose UI limits: `cargo test --release -- --ignored --nocapture`.
#[test]
#[ignore]
fn timing_survey() {
    let var = |k: &str, d: usize| {
        std::env::var(k)
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(d)
    };
    for n in var("TIMING_FROM", 8)..=var("TIMING_TO", 12) {
        for cores in [0, var("TIMING_CORES", 7)] {
            let caps: Vec<f64> = (1..=n).map(|k| (k as f64 + 0.37).sqrt() * 1e-12).collect();
            let r = Request {
                max_core_edges: cores,
                top_k: 20,
                ..req(Mode::All, &caps, 2.345e-12)
            };
            let t = std::time::Instant::now();
            let res = run(&r);
            eprintln!(
                "n={n:2} cores={cores} {:>8.2}s exhaustive={} bound={:.2e} best={:.2e} entries={} cands={}",
                t.elapsed().as_secs_f64(),
                res.stats.exhaustive,
                res.stats.bound_rel,
                res.solutions[0].rel_error.abs(),
                res.stats.entries,
                res.stats.candidates
            );
        }
    }
}

/// Inventory timing survey: `cargo test --release --test api inventory_timing -- --ignored --nocapture`.
#[test]
#[ignore]
fn inventory_timing_survey() {
    let e24 = [
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
        5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
    ];
    let var = |k: &str, d: usize| {
        std::env::var(k)
            .ok()
            .and_then(|v| v.parse().ok())
            .unwrap_or(d)
    };
    let budget = var("TIMING_BUDGET", 6_000_000);
    let kmax = var("TIMING_K", 8);
    for (name, step) in [("E6", 4), ("E12", 2), ("E24", 1)] {
        for decades in [2, 4] {
            let vals: Vec<f64> = (0..decades)
                .flat_map(|d| {
                    e24.iter()
                        .step_by(step)
                        .map(move |m| m * 10f64.powi(d) * 1e-12)
                })
                .collect();
            for k in [3, 4, 5, 6, 8].into_iter().filter(|&k| k <= kmax) {
                for cores in [0, 9] {
                    let r = Request {
                        max_parts: k,
                        max_core_edges: cores,
                        max_entries: budget,
                        ..req(Mode::Inventory, &vals, 3.1416e-11)
                    };
                    let t = std::time::Instant::now();
                    let res = run(&r);
                    eprintln!(
                        "{name} m={:3} K={k} cores={cores} {:>7.2}s exh={} best={:.1e}",
                        vals.len(),
                        t.elapsed().as_secs_f64(),
                        res.stats.exhaustive,
                        res.solutions[0].rel_error.abs()
                    );
                }
            }
        }
    }
}

/// Regression for C1 (docs/REVISION.md): when the core work guard fires, the
/// non-series-parallel networks must still be explored and the reported bound
/// must cover them. Target = exact value of a network containing a bridge.
#[test]
fn bridge_targets_stay_within_the_reported_bound_under_the_work_guard() {
    use capcore::laplace::ceq;
    let bridge = |c: [f64; 5]| ceq(4, 0, 1, &[(0, 2), (0, 3), (2, 1), (3, 1), (2, 3)], &c);
    let series = |a: f64, b: f64| a * b / (a + b);

    // "Use all", 9 distinct parts: bridge(1..5) in series with (6 ∥ 7) and 8, parallel with 9.
    let caps: Vec<f64> = (1..=9).map(|k| k as f64 * 1.37e-12).collect();
    let c = |k: usize| caps[k - 1];
    let target = series(
        series(bridge([c(1), c(2), c(3), c(4), c(5)]), c(6) + c(7)),
        c(8),
    ) + c(9);
    let r = Request {
        max_core_edges: 9,
        top_k: 3,
        ..req(Mode::All, &caps, target)
    };
    let res = run(&r);
    let best = res.solutions[0].rel_error.abs();
    assert!(
        best <= res.stats.bound_rel + 1e-12,
        "use-all: best {best:e} outside bound {:e}",
        res.stats.bound_rel
    );

    // Inventory: 48 E24 values, up to 6 parts; target = a bridge of E24 values
    // in series with one more part (not reachable in series-parallel).
    let e24 = [
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
        5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
    ];
    let vals: Vec<f64> = e24.iter().flat_map(|v| [v * 1e-12, v * 1e-11]).collect();
    let target = series(
        bridge([1.1e-12, 3.6e-12, 2.4e-12, 7.5e-12, 5.1e-12]),
        9.1e-11,
    );
    let r = Request {
        max_core_edges: 9,
        max_parts: 6,
        max_entries: 1_000_000,
        top_k: 3,
        ..req(Mode::Inventory, &vals, target)
    };
    let res = run(&r);
    let best = res.solutions[0].rel_error.abs();
    // Either every core was explored and the bound covers the bridge, or the
    // skipped cores are reported and nothing claims to be exhaustive.
    if res.stats.cores_complete {
        assert!(
            best <= res.stats.bound_rel + 1e-12,
            "inventory: best {best:e} outside bound"
        );
    } else {
        assert!(!res.stats.exhaustive);
    }
}

/// Cost survey of "all networks" with 9 parts: `cargo test --release --test api core9 -- --ignored --nocapture`.
#[test]
#[ignore]
fn core9_survey() {
    for (label, caps) in [
        (
            "9 distinct",
            (1..=9)
                .map(|k| (k as f64 + 0.37).sqrt() * 1e-12)
                .collect::<Vec<_>>(),
        ),
        (
            "9 with a pair",
            (1..=9)
                .map(|k| ((k.min(8)) as f64 + 0.37).sqrt() * 1e-12)
                .collect(),
        ),
        (
            "8 distinct",
            (1..=8).map(|k| (k as f64 + 0.37).sqrt() * 1e-12).collect(),
        ),
    ] {
        let t = std::time::Instant::now();
        let res = run(&Request {
            max_core_edges: 9,
            top_k: 5,
            ..req(Mode::All, &caps, 2.345e-12)
        });
        eprintln!(
            "core9 {label}: {:.2}s exhaustive={} bound={:.2e} best={:.2e}",
            t.elapsed().as_secs_f64(),
            res.stats.exhaustive,
            res.stats.bound_rel,
            res.solutions[0].rel_error.abs()
        );
    }
}
