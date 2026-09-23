//! Formal-review diagnostics. Each test checks one claim made in the theory
//! page or the code comments, against an independent computation.
//!
//! Run: `cargo test --release --test review -- --nocapture --test-threads=1`

use std::collections::BTreeSet;

use capcore::cores::all_cores;
use capcore::engine::{Engine, Params, TopK};
use capcore::laplace::ceq;
use capcore::num::Num;
use capcore::rational::Q;
use capcore::space::{MultisetSpace, SizeSpace};

/// Tiny deterministic generator so the diagnostics are reproducible.
struct Lcg(u64);
impl Lcg {
    fn next(&mut self) -> f64 {
        self.0 = self
            .0
            .wrapping_mul(6364136223846793005)
            .wrapping_add(1442695040888963407);
        (self.0 >> 11) as f64 / (1u64 << 53) as f64
    }
}

// ---------------------------------------------------------------------------
// D1 — completeness for DISTINCT values against brute force over all graphs.
// ---------------------------------------------------------------------------

fn connected(nv: usize, edges: &[(usize, usize)], alive: &[bool]) -> bool {
    let start = match (0..nv).find(|&i| alive[i]) {
        Some(s) => s,
        None => return true,
    };
    let mut seen = vec![false; nv];
    let mut stack = vec![start];
    seen[start] = true;
    while let Some(x) = stack.pop() {
        for &(u, v) in edges {
            for (a, b) in [(u, v), (v, u)] {
                if a == x && alive[b] && !seen[b] {
                    seen[b] = true;
                    stack.push(b);
                }
            }
        }
    }
    (0..nv).all(|i| !alive[i] || seen[i])
}

/// Every edge lies on a simple A–B path  ⟺  G + AB is 2-connected.
fn admissible(nv: usize, edges: &[(usize, usize)]) -> bool {
    let mut h = edges.to_vec();
    h.push((0, 1));
    let alive = vec![true; nv];
    if !connected(nv, &h, &alive) {
        return false;
    }
    if nv >= 3 {
        for x in 0..nv {
            let mut a = alive.clone();
            a[x] = false;
            let hx: Vec<_> = h
                .iter()
                .copied()
                .filter(|&(u, v)| u != x && v != x)
                .collect();
            if !connected(nv, &hx, &a) {
                return false;
            }
        }
    }
    true
}

/// All values of admissible two-terminal networks where part i is edge i.
/// Internal vertices are labelled by first appearance (symmetry breaking).
fn brute_all(vals: &[Q]) -> BTreeSet<Q> {
    fn rec(i: usize, vals: &[Q], k: usize, edges: &mut Vec<(usize, usize)>, out: &mut BTreeSet<Q>) {
        let n = vals.len();
        if i == n {
            let nv = 2 + k;
            if admissible(nv, edges) {
                out.insert(ceq(nv, 0, 1, edges, vals));
            }
            return;
        }
        let max_v = (2 + k + 2).min(n + 1);
        for u in 0..max_v {
            for v in u + 1..max_v {
                // A new vertex 2+k+1 may only appear together with 2+k.
                let uses_new2 = v == 2 + k + 1;
                if uses_new2 && u != 2 + k {
                    continue;
                }
                let new_k = if v >= 2 + k { v - 1 } else { k };
                edges.push((u, v));
                rec(i + 1, vals, new_k.max(k), edges, out);
                edges.pop();
            }
        }
    }
    let mut out = BTreeSet::new();
    rec(0, vals, 0, &mut Vec::new(), &mut out);
    out
}

fn engine_all(vals: &[Q], max_core_edges: usize) -> BTreeSet<Q> {
    let n = vals.len();
    let cnt = vec![1u8; n];
    let space = MultisetSpace::new(&cnt, n);
    let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
    let p = Params {
        max_core_edges,
        ..Params::default()
    };
    let mut eng = Engine::new(space, vals.to_vec(), all_cores(), p);
    eng.build_all(&|_| false).unwrap();
    eng.set(full).unwrap().iter().map(|e| e.v).collect()
}

#[test]
fn d1_all_networks_distinct_values_match_brute_force() {
    let primes = [2i128, 3, 5, 7, 11, 13];
    for n in 2..=6 {
        let vals: Vec<Q> = primes[..n].iter().map(|&p| Q::int(p)).collect();
        let t = std::time::Instant::now();
        let brute = brute_all(&vals);
        let eng = engine_all(&vals, 9);
        let sp = engine_all(&vals, 0);
        eprintln!(
            "D1 n={n}: brute={} engine(all)={} engine(SP)={} missing={} extra={} ({:.1}s)",
            brute.len(),
            eng.len(),
            sp.len(),
            brute.difference(&eng).count(),
            eng.difference(&brute).count(),
            t.elapsed().as_secs_f64()
        );
        assert_eq!(brute, eng, "n = {n}");
    }
}

// ---------------------------------------------------------------------------
// D2 — are non-SP cores silently skipped by the work guard?
// ---------------------------------------------------------------------------

/// Diagnostic behind finding C1 of docs/REVISION.md: prints whether the
/// non-series-parallel work guard fires. Not an assertion (yet).
#[test]
#[ignore]
fn d2_core_work_guard() {
    // "use all" with distinct values, as the API configures it.
    for n in 7..=9 {
        let vals: Vec<f64> = (1..=n).map(|k| (k as f64 + 0.37).sqrt()).collect();
        let cnt = vec![1u8; n];
        let space = MultisetSpace::new(&cnt, n);
        let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
        let p = Params {
            eps: 1e-12,
            max_core_edges: 9,
            max_entries: 6_000_000,
            max_core_work: 20_000_000,
            ..Params::default()
        };
        let mut eng = Engine::new(space, vals, all_cores(), p);
        eng.build_all(&|s| s == full).unwrap();
        let mut top = TopK::new(5);
        eng.query(full, 1.2345, &mut top);
        eprintln!(
            "D2 all n={n}: coarsened={} cores_skipped={}",
            eng.stats.coarsened,
            eng.cores_skipped()
        );
    }
    // Inventory (unlimited E-series), as the UI configures it.
    let e24 = [
        1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
        5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
    ];
    for (m_label, vals) in [
        (
            "E12x2",
            e24.iter()
                .step_by(2)
                .flat_map(|v| [*v, v * 10.0])
                .collect::<Vec<f64>>(),
        ),
        ("E24x2", e24.iter().flat_map(|v| [*v, v * 10.0]).collect()),
        (
            "E24x4",
            e24.iter()
                .flat_map(|v| [*v, v * 10.0, v * 100.0, v * 1000.0])
                .collect(),
        ),
    ] {
        for k in [5usize, 6] {
            let space = SizeSpace {
                kmax: k,
                nclass: vals.len(),
            };
            let p = Params {
                eps: 1e-12,
                max_core_edges: 9,
                max_entries: 1_000_000,
                max_core_work: 20_000_000,
                ..Params::default()
            };
            let mut eng = Engine::new(space, vals.clone(), all_cores(), p);
            eng.build_all(&|s| s == k - 1).unwrap();
            let mut top = TopK::new(5);
            for s in 0..k {
                eng.query(s, 31.416, &mut top);
            }
            eprintln!(
                "D2 inventory {m_label} (m={}) K={k}: coarsened={} cores_skipped={}",
                vals.len(),
                eng.stats.coarsened,
                eng.cores_skipped()
            );
        }
    }
}

// ---------------------------------------------------------------------------
// D3 — does the "guaranteed bound" hold when states are coarsened?
// ---------------------------------------------------------------------------

fn best(vals: &[f64], target: f64, cap: usize) -> (f64, f64) {
    best_with(vals, target, cap, 0)
}

fn best_with(vals: &[f64], target: f64, cap: usize, cores: usize) -> (f64, f64) {
    let n = vals.len();
    let cnt = vec![1u8; n];
    let space = MultisetSpace::new(&cnt, n);
    let full = space.id(MultisetSpace::pack(&cnt)).unwrap();
    let p = Params {
        eps: 1e-12,
        max_per_state: cap,
        max_core_edges: cores,
        ..Params::default()
    };
    let mut eng = Engine::new(space, vals.to_vec(), all_cores(), p);
    eng.build_all(&|s| s == full).unwrap();
    let mut top = TopK::new(1);
    eng.query(full, target, &mut top);
    (top.items[0].err, eng.stats.eps_used)
}

#[test]
fn d3_coarsening_bound() {
    let mut rng = Lcg(7);
    let (mut cases, mut viol_full, mut viol_ui, mut worst_ratio) = (0, 0, 0, 0.0f64);
    for _ in 0..300 {
        let n = 6 + (rng.next() * 3.0) as usize; // 6..8
        let vals: Vec<f64> = (0..n).map(|_| 1.0 + 99.0 * rng.next()).collect();
        let target = 1.0 + 60.0 * rng.next();
        let (exact, _) = best(&vals, target, 0);
        for cap in [8usize, 20, 60] {
            let (approx, eps) = best(&vals, target, cap);
            let b = (eps * (n - 1) as f64).exp_m1();
            let full = exact + b * (1.0 + exact) + 1e-12;
            let ui = exact + b + 1e-12;
            cases += 1;
            if approx > full {
                viol_full += 1;
            }
            if approx > ui {
                viol_ui += 1;
            }
            if b > 0.0 {
                worst_ratio = worst_ratio.max((approx - exact) / b);
            }
        }
    }
    eprintln!(
        "D3 {cases} coarsened runs: violations of the proven bound = {viol_full}, of the UI bound (no (1+ε) factor) = {viol_ui}; worst (found − optimum)/bound = {worst_ratio:.3}"
    );
    assert_eq!(viol_full, 0);
}

// ---------------------------------------------------------------------------
// D4 — numerical accuracy of the f64 Kron reduction with large value spreads.
// ---------------------------------------------------------------------------

#[test]
fn d4_numerics_wide_spread() {
    let mut rng = Lcg(11);
    let mut worst = 0.0f64;
    let mut checked = 0;
    for core in all_cores() {
        for _ in 0..200 {
            let decades = if core.nv <= 4 { 8.0 } else { 3.5 };
            let w: Vec<i128> = (0..core.m())
                .map(|_| 10f64.powf(rng.next() * decades).round().max(1.0) as i128)
                .collect();
            let wf: Vec<f64> = w.iter().map(|&x| x as f64).collect();
            let wq: Vec<Q> = w.iter().map(|&x| Q::int(x)).collect();
            let exact = std::panic::catch_unwind(|| ceq(core.nv, 0, 1, &core.edges, &wq));
            if let Ok(q) = exact {
                let f = ceq(core.nv, 0, 1, &core.edges, &wf);
                worst = worst.max(((f - q.to_f64()) / q.to_f64()).abs());
                checked += 1;
            }
        }
    }
    eprintln!("D4 {checked} core evaluations with spreads up to 1e8: worst relative error f64 vs exact = {worst:.2e}");
    assert!(worst < 1e-9);
}

// ---------------------------------------------------------------------------
// D5 — limited stock: engine value sets vs brute force over sub-multisets.
// ---------------------------------------------------------------------------

fn naive_sp(vals: &[Q]) -> BTreeSet<Q> {
    fn go(vals: &[Q], mask: u32) -> BTreeSet<Q> {
        let mut out = BTreeSet::new();
        if mask.count_ones() == 1 {
            out.insert(vals[mask.trailing_zeros() as usize]);
            return out;
        }
        let low = mask.isolate_lowest_one();
        let mut sub = (mask - 1) & mask;
        while sub > 0 {
            if sub & low != 0 {
                let l = go(vals, sub);
                let r = go(vals, mask & !sub);
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
    go(vals, (1u32 << vals.len()) - 1)
}

#[test]
fn d5_limited_stock_matches_brute_force() {
    let classes = [Q::int(2), Q::int(3), Q::int(7)];
    let mut rng = Lcg(3);
    for _ in 0..40 {
        let stock: Vec<u8> = (0..3).map(|_| (rng.next() * 4.0) as u8).collect();
        let k = 1 + (rng.next() * 5.0) as usize; // 1..5
        let uni: Vec<u8> = stock.iter().map(|&c| c.min(k as u8)).collect();
        if uni.iter().all(|&c| c == 0) {
            continue;
        }
        let space = MultisetSpace::new(&uni, k);
        let n_states = capcore::space::Space::n_states(&space);
        let p = Params {
            max_core_edges: 9,
            ..Params::default()
        };
        let mut eng = Engine::new(space, classes.to_vec(), all_cores(), p);
        eng.build_all(&|_| false).unwrap();
        let mut got = BTreeSet::new();
        for s in 0..n_states {
            got.extend(eng.set(s).unwrap().iter().map(|e| e.v));
        }
        let mut want = BTreeSet::new();
        let mut counts = [0u8; 3];
        loop {
            let size: usize = counts.iter().map(|&c| c as usize).sum();
            if size >= 1 && size <= k {
                let list: Vec<Q> = counts
                    .iter()
                    .zip(&classes)
                    .flat_map(|(&c, &v)| std::iter::repeat_n(v, c as usize))
                    .collect();
                if list.len() >= 5 {
                    want.extend(brute_all(&list));
                } else {
                    want.extend(naive_sp(&list));
                }
            }
            let mut i = 0;
            while i < 3 {
                counts[i] += 1;
                if counts[i] <= uni[i] {
                    break;
                }
                counts[i] = 0;
                i += 1;
            }
            if i == 3 {
                break;
            }
        }
        assert_eq!(got, want, "stock {stock:?} K={k}");
    }
    eprintln!("D5 limited stock: 40 random drawers match brute force (SP + bridges)");
}

#[test]
fn d3b_coarsening_bound_with_cores() {
    let mut rng = Lcg(19);
    let (mut cases, mut viol, mut worst_ratio) = (0, 0, 0.0f64);
    for _ in 0..150 {
        let n = 6 + (rng.next() * 2.0) as usize; // 6..7
        let vals: Vec<f64> = (0..n).map(|_| 10f64.powf(3.0 * rng.next())).collect();
        let target = 10f64.powf(2.0 * rng.next());
        let (exact, _) = best_with(&vals, target, 0, 9);
        for cap in [4usize, 10, 30] {
            let (approx, eps) = best_with(&vals, target, cap, 9);
            let b = (eps * (n - 1) as f64).exp_m1();
            cases += 1;
            if approx > exact + b * (1.0 + exact) + 1e-12 {
                viol += 1;
            }
            if b > 0.0 {
                worst_ratio = worst_ratio.max((approx - exact) / b);
            }
        }
    }
    eprintln!("D3b {cases} coarsened runs with cores: bound violations = {viol}; worst (found − optimum)/bound = {worst_ratio:.3}");
    assert_eq!(viol, 0);
}
