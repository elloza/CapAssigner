//! Value dynamic programme over states, with meet-in-the-middle at the root.
//!
//! For every state `S` (a multiset of parts, or a part count) the engine stores the
//! sorted set `V(S)` of *distinct* equivalent capacitances reachable by networks
//! that use exactly the parts of `S`, each value with one back-pointer (a
//! witness network). `V(S)` is the union over unordered splits `S = L ⊎ R` of
//! `{a + b, ab/(a + b) : a ∈ V(L), b ∈ V(R)}` plus, optionally, the values of
//! non-series-parallel cores whose edges are filled from a decomposition of `S`.
//!
//! **Trimming.** Values closer than a relative factor `1 + eps` are merged. Series,
//! parallel and any core are monotone and 1-homogeneous in their inputs, hence
//! non-expansive in log-space: if every input is within factor `e^δ` of the
//! original, so is the output. By induction the best kept value is within
//! `(depth · eps)` (relative, first order) of the true optimum; the engine
//! reports the realised `eps` so the UI can state the guarantee.
//!
//! **Root.** The state being queried is never materialised. For each split and
//! each `a ∈ V(L)` (the smaller side) the partner value that hits the target
//! exactly is solved for and found in `V(R)` by binary search; neighbours are
//! scanned while they can still enter the top-K.

use crate::cores::Core;
use crate::laplace;
use crate::num::Num;
use crate::space::Space;

pub const LEAF: u8 = 0;
pub const SERIES: u8 = 1;
pub const PARALLEL: u8 = 2;
pub const CORE: u8 = 3;

/// A value with its back-pointer.
/// * `LEAF`: `a` = class.
/// * `SERIES`/`PARALLEL`: `a` = left state, `b` = index in `V(left)`,
///   `c` = index in `V(right)`; right state = complement of left.
/// * `CORE`: `a` = core index, `b` = offset of its parts in the arena.
#[derive(Clone, Copy, Debug)]
pub struct Entry<T> {
    pub v: T,
    pub kind: u8,
    pub a: u32,
    pub b: u32,
    pub c: u32,
}

#[derive(Clone, Debug)]
pub struct Params {
    /// Relative merge threshold; `0` means exact equality.
    pub eps: f64,
    /// Cap on `|V(S)|`; 0 derives it from `max_entries` (unlimited if that is
    /// `usize::MAX`). A state above its cap is coarsened on a log grid.
    pub max_per_state: usize,
    /// Include cores with at most this many edges (0 = series-parallel only).
    pub max_core_edges: usize,
    /// Budget of stored values across all states.
    pub max_entries: usize,
    /// Most core evaluations per state; beyond it the state's cores are
    /// skipped and the search is no longer exhaustive.
    pub max_core_work: u64,
}

impl Default for Params {
    fn default() -> Self {
        Params {
            eps: 0.0,
            max_per_state: 0,
            max_core_edges: 0,
            max_entries: usize::MAX,
            max_core_work: u64::MAX,
        }
    }
}

#[derive(Clone, Debug, Default)]
pub struct Stats {
    pub states_built: usize,
    pub entries: usize,
    pub candidates: u64,
    /// Largest relative merge distance actually applied (>= `Params::eps`).
    pub eps_used: f64,
    /// Some state was coarsened beyond `Params::eps` by `max_per_state`.
    pub coarsened: bool,
}

#[derive(Clone, Debug, PartialEq)]
pub enum Net {
    Leaf(usize),
    Series(Vec<Net>),
    Parallel(Vec<Net>),
    Core { core: usize, parts: Vec<Net> },
}

impl Net {
    pub fn parts(&self) -> usize {
        match self {
            Net::Leaf(_) => 1,
            Net::Series(c) | Net::Parallel(c) | Net::Core { parts: c, .. } => {
                c.iter().map(Net::parts).sum()
            }
        }
    }
}

#[derive(Clone, Debug)]
pub struct Cand<T> {
    pub v: T,
    pub err: f64,
    pub state: usize,
    pub size: usize,
    pub e: Entry<T>,
    /// Parts of a root-level core (root entries are not in the arena).
    pub parts: Vec<(u32, u32)>,
}

/// The K best candidates by relative error, without duplicate values.
pub struct TopK<T> {
    pub k: usize,
    pub items: Vec<Cand<T>>,
}

impl<T: Num> TopK<T> {
    pub fn new(k: usize) -> Self {
        TopK {
            k: k.max(1),
            items: Vec::new(),
        }
    }

    pub fn worst(&self) -> f64 {
        if self.items.len() < self.k {
            f64::INFINITY
        } else {
            self.items.last().map_or(f64::INFINITY, |c| c.err)
        }
    }

    /// Could a candidate with this error enter? Ties are admitted so that the
    /// final order (error, then value) does not depend on the visiting order.
    pub fn wants(&self, err: f64) -> bool {
        err <= self.worst()
    }

    pub fn offer(&mut self, c: Cand<T>) {
        if !self.wants(c.err) {
            return;
        }
        let x = c.v.to_f64();
        if let Some(pos) = self
            .items
            .iter()
            .position(|o| (o.v.to_f64() - x).abs() <= 1e-12 * x.abs().max(o.v.to_f64().abs()))
        {
            // Same value: keep the network with fewer parts, then the simpler kind.
            let o = &self.items[pos];
            if (c.size, c.e.kind) >= (o.size, o.e.kind) {
                return;
            }
            self.items.remove(pos);
        }
        let at = self
            .items
            .partition_point(|o| o.err < c.err || (o.err == c.err && o.v <= c.v));
        self.items.insert(at, c);
        self.items.truncate(self.k);
    }
}

pub struct Engine<'c, T: Num, S: Space> {
    pub space: S,
    classes: Vec<T>,
    sets: Vec<Option<Vec<Entry<T>>>>,
    arena: Vec<(u32, u32)>,
    cores: Vec<&'c Core>,
    pub p: Params,
    pub stats: Stats,
    progress: Option<Box<dyn FnMut(f64) + 'c>>,
    /// Some state skipped its cores because of `max_core_work`.
    cores_skipped: std::cell::Cell<bool>,
}

fn combine<T: Num>(kind: u8, x: T, y: T) -> T {
    if kind == SERIES {
        x.series(y)
    } else {
        x.parallel(y)
    }
}

/// Candidates buffered before being sorted into a state's value set.
const CHUNK: usize = 1 << 20;
/// Use the sort-free grid path when a state's candidates exceed its cap by
/// more than this factor.
const GRID_FACTOR: u64 = 8;
/// Never coarsen a state below this many values.
const MIN_STATE_CAP: usize = 256;

fn by_value<T: Num>(x: &Entry<T>, y: &Entry<T>) -> std::cmp::Ordering {
    x.v.partial_cmp(&y.v)
        .expect("finite values")
        .then(x.kind.cmp(&y.kind))
}

/// Keep the first of every run of values within a relative `eps` of it.
fn dedupe<T: Num>(sorted: impl IntoIterator<Item = Entry<T>>, eps: f64) -> Vec<Entry<T>> {
    let mut kept: Vec<Entry<T>> = Vec::new();
    for c in sorted {
        match kept.last() {
            Some(k) if T::close(k.v, c.v, eps) => {}
            _ => kept.push(c),
        }
    }
    kept
}

/// Keep one value per bucket of a logarithmic grid of width `g`. Buckets of
/// width `2g` are unions of buckets of width `g`, so repeated coarsening never
/// moves a value further than the final `g` from its representative.
fn snap<T: Num>(v: Vec<Entry<T>>, g: f64) -> Vec<Entry<T>> {
    let mut kept: Vec<Entry<T>> = Vec::new();
    let mut last = i64::MIN;
    for e in v {
        let b = (e.v.to_f64().ln() / g).floor() as i64;
        if b != last {
            kept.push(e);
            last = b;
        }
    }
    kept
}

/// A logarithmic grid built on the IEEE-754 bit pattern: for positive doubles
/// `to_bits` is monotone and piecewise linear in `log2`, so a bucket spanning
/// `2^shift` units in the last place has relative width at most `2^(shift−52)`.
/// Buckets for `shift + 1` are unions of those for `shift`.
struct LogGrid {
    base: u64,
    shift: u32,
    n: usize,
}

impl LogGrid {
    fn new(lo: f64, hi: f64, cap: usize) -> LogGrid {
        let base = lo.to_bits();
        let span = hi.to_bits().saturating_sub(base);
        let mut shift = 0;
        while (span >> shift) >= cap.max(1) as u64 {
            shift += 1;
        }
        LogGrid {
            base,
            shift,
            n: (span >> shift) as usize + 1,
        }
    }

    fn len(&self) -> usize {
        self.n
    }

    fn bucket(&self, v: f64) -> usize {
        ((v.to_bits().saturating_sub(self.base) >> self.shift) as usize).min(self.n - 1)
    }

    fn eps(&self) -> f64 {
        if self.shift == 0 {
            0.0
        } else {
            (self.shift as f64 - 52.0).exp2()
        }
    }
}

/// Merge a new chunk of candidates into a state's sorted value set, then
/// coarsen on the log grid (`grid` only ever grows) until at most `cap` remain.
fn absorb<T: Num>(
    acc: Vec<Entry<T>>,
    chunk: &mut Vec<Entry<T>>,
    eps: f64,
    cap: usize,
    grid: &mut f64,
) -> Vec<Entry<T>> {
    chunk.sort_by(by_value);
    let mut merged = Vec::with_capacity(acc.len() + chunk.len());
    let (mut i, mut j) = (0, 0);
    while i < acc.len() && j < chunk.len() {
        if by_value(&acc[i], &chunk[j]).is_le() {
            merged.push(acc[i]);
            i += 1;
        } else {
            merged.push(chunk[j]);
            j += 1;
        }
    }
    merged.extend_from_slice(&acc[i..]);
    merged.extend_from_slice(&chunk[j..]);
    chunk.clear();
    let mut kept = dedupe(merged, eps);
    if *grid > 0.0 {
        kept = snap(kept, *grid);
    }
    while kept.len() > cap {
        let lo = kept[0].v.to_f64();
        let hi = kept[kept.len() - 1].v.to_f64();
        *grid = if *grid > 0.0 {
            *grid * 2.0
        } else {
            ((hi / lo).ln() / cap as f64).max(1e-9)
        };
        kept = snap(kept, *grid);
    }
    kept
}

/// Visit every tuple of indices `idx[k] < lens[k]`.
fn for_each_index_tuple(lens: &[usize], f: &mut dyn FnMut(&[usize])) {
    if lens.contains(&0) {
        return;
    }
    let mut idx = vec![0usize; lens.len()];
    loop {
        f(&idx);
        let mut k = 0;
        while k < idx.len() {
            idx[k] += 1;
            if idx[k] < lens[k] {
                break;
            }
            idx[k] = 0;
            k += 1;
        }
        if k == idx.len() {
            return;
        }
    }
}

impl<'c, T: Num, S: Space> Engine<'c, T, S> {
    pub fn new(space: S, classes: Vec<T>, cores: &'c [Core], p: Params) -> Self {
        let n = space.n_states();
        let cores = cores.iter().filter(|c| c.m() <= p.max_core_edges).collect();
        Engine {
            space,
            classes,
            sets: vec![None; n],
            arena: Vec::new(),
            cores,
            stats: Stats {
                eps_used: p.eps,
                ..Stats::default()
            },
            p,
            progress: None,
            cores_skipped: std::cell::Cell::new(false),
        }
    }

    /// `f(fraction)` is called after each state, with the fraction of the
    /// estimated work done (a state of size k is weighted 5^k, which tracks how
    /// its candidate count grows).
    pub fn on_progress(&mut self, f: impl FnMut(f64) + 'c) {
        self.progress = Some(Box::new(f));
    }

    pub fn set(&self, s: usize) -> Option<&[Entry<T>]> {
        self.sets[s].as_deref()
    }

    pub fn class_value(&self, class: usize) -> T {
        self.classes[class]
    }

    /// Materialise every state for which `root(s)` is false, smallest first.
    pub fn build_all(&mut self, root: &dyn Fn(usize) -> bool) -> Result<(), String> {
        let n = self.space.n_states();
        let mut order: Vec<usize> = (0..n).filter(|&s| !root(s)).collect();
        order.sort_by_key(|&s| self.space.size(s));
        let total = order.len();
        let weight = |s: usize| 5f64.powi(self.space.size(s) as i32);
        let weights: Vec<f64> = order.iter().map(|&s| weight(s)).collect();
        // The root queries run after this loop; count them so progress does
        // not reach 100 % before they start.
        let root_weight: f64 = (0..n).filter(|&s| root(s)).map(weight).sum();
        let total_weight: f64 = weights.iter().sum::<f64>() + root_weight;
        let mut done_weight = 0.0;
        for (done, (s, w)) in order.into_iter().zip(weights).enumerate() {
            let cap = self.state_cap(total - done);
            self.build(s, cap)?;
            done_weight += w;
            if let Some(cb) = self.progress.as_mut() {
                cb(done_weight / total_weight);
            }
        }
        Ok(())
    }

    /// Size cap for the next state: explicit, or an even share of what is left
    /// of the budget (states are built smallest first, so the big ones at the
    /// end get most of it).
    fn state_cap(&self, remaining: usize) -> usize {
        if self.p.max_per_state > 0 {
            return self.p.max_per_state;
        }
        if self.p.max_entries == usize::MAX {
            return usize::MAX;
        }
        let left = self.p.max_entries.saturating_sub(self.stats.entries);
        (left / remaining.max(1)).max(MIN_STATE_CAP)
    }

    /// True when every network was considered: no state was coarsened, no
    /// merge beyond `eps`, and no state skipped its cores.
    pub fn exhaustive(&self) -> bool {
        !self.stats.coarsened && !self.cores_skipped.get()
    }

    fn core_work(&self, s: usize) -> u64 {
        let size = self.space.size(s);
        let mut work = 0u64;
        for core in self.cores.iter().filter(|c| c.m() <= size) {
            self.space.for_each_composition(s, core.m(), &mut |comp| {
                let p = comp.iter().fold(1u64, |acc, &t| {
                    acc.saturating_mul(self.sets[t].as_deref().map_or(0, <[_]>::len) as u64)
                });
                work = work.saturating_add(p);
            });
        }
        work
    }

    fn core_candidates(&self, s: usize, mut emit: impl FnMut(T, usize, &[(u32, u32)])) {
        let size = self.space.size(s);
        if self.cores.iter().all(|c| c.m() > size) {
            return;
        }
        if self.p.max_core_work < u64::MAX && self.core_work(s) > self.p.max_core_work {
            self.cores_skipped.set(true);
            return;
        }
        let mut w: Vec<T> = Vec::new();
        let mut parts: Vec<(u32, u32)> = Vec::new();
        for (ci, core) in self.cores.iter().enumerate() {
            let m = core.m();
            if m > size {
                continue;
            }
            self.space.for_each_composition(s, m, &mut |comp| {
                let sets: Vec<&[Entry<T>]> = comp
                    .iter()
                    .map(|&t| self.sets[t].as_deref().expect("sub-state built"))
                    .collect();
                let lens: Vec<usize> = sets.iter().map(|v| v.len()).collect();
                for_each_index_tuple(&lens, &mut |idx| {
                    w.clear();
                    parts.clear();
                    for k in 0..m {
                        w.push(sets[k][idx[k]].v);
                        parts.push((comp[k] as u32, idx[k] as u32));
                    }
                    let v = laplace::ceq(core.nv, 0, 1, &core.edges, &w);
                    emit(v, ci, &parts);
                });
            });
        }
    }

    fn build(&mut self, s: usize, cap: usize) -> Result<(), String> {
        let mut acc: Vec<Entry<T>> = Vec::new();
        let mut chunk: Vec<Entry<T>> = Vec::new();
        let mut local: Vec<(u32, u32)> = Vec::new();
        let mut grid = 0.0f64;
        let mut produced = 0u64;
        let eps = self.p.eps;
        if self.space.size(s) == 1 {
            for cl in self.space.leaf_classes(s) {
                chunk.push(Entry {
                    v: self.classes[cl],
                    kind: LEAF,
                    a: cl as u32,
                    b: 0,
                    c: 0,
                });
            }
        } else {
            let mut splits = Vec::new();
            self.space
                .for_each_split(s, &mut |l, r| splits.push((l, r)));
            let len = |t: usize| self.sets[t].as_deref().map_or(0, <[_]>::len) as u64;
            let estimate: u64 = splits.iter().map(|&(l, r)| 2 * len(l) * len(r)).sum();
            if cap < usize::MAX && estimate > GRID_FACTOR * cap as u64 {
                return self.build_grid(s, &splits, cap);
            }
            for (l, r) in splits {
                let lv = self.sets[l].as_deref().expect("left built");
                let rv = self.sets[r].as_deref().expect("right built");
                for (i, x) in lv.iter().enumerate() {
                    let j0 = if l == r { i } else { 0 };
                    for (j, y) in rv.iter().enumerate().skip(j0) {
                        for kind in [SERIES, PARALLEL] {
                            let v = combine(kind, x.v, y.v);
                            chunk.push(Entry {
                                v,
                                kind,
                                a: l as u32,
                                b: i as u32,
                                c: j as u32,
                            });
                        }
                    }
                    if chunk.len() >= CHUNK {
                        produced += chunk.len() as u64;
                        acc = absorb(acc, &mut chunk, eps, cap, &mut grid);
                    }
                }
            }
            self.core_candidates(s, |v, ci, parts| {
                chunk.push(Entry {
                    v,
                    kind: CORE,
                    a: ci as u32,
                    b: local.len() as u32,
                    c: 0,
                });
                local.extend_from_slice(parts);
                if chunk.len() >= CHUNK {
                    produced += chunk.len() as u64;
                    acc = absorb(std::mem::take(&mut acc), &mut chunk, eps, cap, &mut grid);
                }
            });
        }
        produced += chunk.len() as u64;
        let kept = absorb(acc, &mut chunk, eps, cap, &mut grid);
        self.finish_state(s, kept, &local, grid, produced)
    }

    /// Move a state's kept core parts into the arena and account for it.
    fn finish_state(
        &mut self,
        s: usize,
        mut kept: Vec<Entry<T>>,
        local: &[(u32, u32)],
        grid: f64,
        produced: u64,
    ) -> Result<(), String> {
        for e in kept.iter_mut().filter(|e| e.kind == CORE) {
            let m = self.cores[e.a as usize].m();
            let off = e.b as usize;
            e.b = self.arena.len() as u32;
            self.arena.extend_from_slice(&local[off..off + m]);
        }
        if grid > 0.0 {
            self.stats.coarsened = true;
            self.stats.eps_used = self.stats.eps_used.max(self.p.eps + grid);
        }
        self.stats.candidates += produced;
        self.stats.entries += kept.len();
        self.stats.states_built += 1;
        self.sets[s] = Some(kept);
        if self.stats.entries > self.p.max_entries {
            return Err(format!(
                "search space exceeds the budget of {} stored values",
                self.p.max_entries
            ));
        }
        Ok(())
    }

    /// Build a state known to exceed its cap without sorting: every candidate
    /// goes straight into a bucket of a monotone logarithmic grid spanning the
    /// state's exact range [series of all parts, parallel of all parts], and
    /// the first value of each bucket is kept.
    fn build_grid(
        &mut self,
        s: usize,
        splits: &[(usize, usize)],
        cap: usize,
    ) -> Result<(), String> {
        let mut lo = f64::INFINITY;
        let mut hi = 0.0f64;
        for &(l, r) in splits {
            let (lv, rv) = (
                self.sets[l].as_deref().unwrap(),
                self.sets[r].as_deref().unwrap(),
            );
            lo = lo.min(lv[0].v.series(rv[0].v).to_f64());
            hi = hi.max(lv[lv.len() - 1].v.parallel(rv[rv.len() - 1].v).to_f64());
        }
        let grid = LogGrid::new(lo, hi, cap);
        let mut buckets: Vec<Option<Entry<T>>> = vec![None; grid.len()];
        let mut local: Vec<(u32, u32)> = Vec::new();
        let mut produced = 0u64;
        for &(l, r) in splits {
            let lv = self.sets[l].as_deref().expect("left built");
            let rv = self.sets[r].as_deref().expect("right built");
            for (i, x) in lv.iter().enumerate() {
                let j0 = if l == r { i } else { 0 };
                for (j, y) in rv.iter().enumerate().skip(j0) {
                    for kind in [SERIES, PARALLEL] {
                        let v = combine(kind, x.v, y.v);
                        let slot = &mut buckets[grid.bucket(v.to_f64())];
                        if slot.is_none() {
                            *slot = Some(Entry {
                                v,
                                kind,
                                a: l as u32,
                                b: i as u32,
                                c: j as u32,
                            });
                        }
                    }
                }
                produced += 2 * (rv.len() - j0) as u64;
            }
        }
        self.core_candidates(s, |v, ci, parts| {
            produced += 1;
            let slot = &mut buckets[grid.bucket(v.to_f64())];
            if slot.is_none() {
                *slot = Some(Entry {
                    v,
                    kind: CORE,
                    a: ci as u32,
                    b: local.len() as u32,
                    c: 0,
                });
                local.extend_from_slice(parts);
            }
        });
        let kept: Vec<Entry<T>> = buckets.into_iter().flatten().collect();
        self.finish_state(s, kept, &local, grid.eps(), produced)
    }

    fn rel_err(v: T, target: f64) -> f64 {
        ((v.to_f64() - target) / target).abs()
    }

    /// Collect the best networks for state `s` into `top`.
    pub fn query(&self, s: usize, target: T, top: &mut TopK<T>) {
        let tf = target.to_f64();
        let size = self.space.size(s);
        if let Some(set) = self.sets[s].as_deref() {
            let pos = set.partition_point(|e| e.v < target);
            let offer = |j: usize, top: &mut TopK<T>| -> bool {
                let e = set[j];
                let err = Self::rel_err(e.v, tf);
                if !top.wants(err) {
                    return false;
                }
                top.offer(Cand {
                    v: e.v,
                    err,
                    state: s,
                    size,
                    e,
                    parts: Vec::new(),
                });
                true
            };
            for j in (0..pos).rev() {
                if !offer(j, top) {
                    break;
                }
            }
            for j in pos..set.len() {
                if !offer(j, top) {
                    break;
                }
            }
            return;
        }

        if size == 1 {
            for cl in self.space.leaf_classes(s) {
                let v = self.classes[cl];
                let e = Entry {
                    v,
                    kind: LEAF,
                    a: cl as u32,
                    b: 0,
                    c: 0,
                };
                top.offer(Cand {
                    v,
                    err: Self::rel_err(v, tf),
                    state: s,
                    size,
                    e,
                    parts: Vec::new(),
                });
            }
            return;
        }
        let mut splits = Vec::new();
        self.space
            .for_each_split(s, &mut |l, r| splits.push((l, r)));
        let z = T::zero();
        for (l, r) in splits {
            let lv = self.sets[l].as_deref().expect("left built");
            let rv = self.sets[r].as_deref().expect("right built");
            let swapped = lv.len() > rv.len();
            let (small, big) = if swapped { (rv, lv) } else { (lv, rv) };
            for (i, x) in small.iter().enumerate() {
                for kind in [SERIES, PARALLEL] {
                    // Partner value y* with x ⊕ y* = target.
                    let pos = if kind == PARALLEL {
                        let y = target.sub(x.v);
                        if y > z {
                            big.partition_point(|e| e.v < y)
                        } else {
                            0
                        }
                    } else if x.v > target {
                        let y = x.v.mul(target).div(x.v.sub(target));
                        big.partition_point(|e| e.v < y)
                    } else {
                        big.len()
                    };
                    let offer = |j: usize, top: &mut TopK<T>| -> bool {
                        let v = combine(kind, x.v, big[j].v);
                        let err = Self::rel_err(v, tf);
                        if !top.wants(err) {
                            return false;
                        }
                        let (bi, ci) = if swapped { (j, i) } else { (i, j) };
                        let e = Entry {
                            v,
                            kind,
                            a: l as u32,
                            b: bi as u32,
                            c: ci as u32,
                        };
                        top.offer(Cand {
                            v,
                            err,
                            state: s,
                            size,
                            e,
                            parts: Vec::new(),
                        });
                        true
                    };
                    for j in (0..pos).rev() {
                        if !offer(j, top) {
                            break;
                        }
                    }
                    for j in pos..big.len() {
                        if !offer(j, top) {
                            break;
                        }
                    }
                }
            }
        }

        self.core_candidates(s, |v, ci, parts| {
            let err = Self::rel_err(v, tf);
            if top.wants(err) {
                let e = Entry {
                    v,
                    kind: CORE,
                    a: ci as u32,
                    b: 0,
                    c: 0,
                };
                top.offer(Cand {
                    v,
                    err,
                    state: s,
                    size,
                    e,
                    parts: parts.to_vec(),
                });
            }
        });
    }

    fn net_of(&self, s: usize, e: &Entry<T>, root_parts: Option<&[(u32, u32)]>) -> Net {
        match e.kind {
            LEAF => Net::Leaf(e.a as usize),
            SERIES | PARALLEL => {
                let l = e.a as usize;
                let r = self.space.complement(s, l);
                let le = self.sets[l].as_deref().expect("built")[e.b as usize];
                let re = self.sets[r].as_deref().expect("built")[e.c as usize];
                let mut kids = Vec::new();
                for child in [self.net_of(l, &le, None), self.net_of(r, &re, None)] {
                    match (e.kind, child) {
                        (SERIES, Net::Series(c)) | (PARALLEL, Net::Parallel(c)) => kids.extend(c),
                        (_, c) => kids.push(c),
                    }
                }
                if e.kind == SERIES {
                    Net::Series(kids)
                } else {
                    Net::Parallel(kids)
                }
            }
            _ => {
                let core = self.cores[e.a as usize];
                let parts = match root_parts {
                    Some(p) if !p.is_empty() => p.to_vec(),
                    _ => self.arena[e.b as usize..e.b as usize + core.m()].to_vec(),
                };
                let parts = parts
                    .into_iter()
                    .map(|(t, i)| {
                        let t = t as usize;
                        let pe = self.sets[t].as_deref().expect("built")[i as usize];
                        self.net_of(t, &pe, None)
                    })
                    .collect();
                // Engine cores are a size-prefix of the catalog, so indices coincide.
                Net::Core {
                    core: e.a as usize,
                    parts,
                }
            }
        }
    }

    pub fn network(&self, c: &Cand<T>) -> Net {
        self.net_of(c.state, &c.e, Some(&c.parts))
    }
}

/// Evaluate a network tree given the class values (used by tests and the API
/// to double-check reconstructions).
pub fn eval<T: Num>(net: &Net, classes: &[T], cores: &[Core]) -> T {
    match net {
        Net::Leaf(c) => classes[*c],
        Net::Series(k) => k
            .iter()
            .map(|n| eval(n, classes, cores))
            .reduce(|a, b| a.series(b))
            .expect("non-empty"),
        Net::Parallel(k) => k
            .iter()
            .map(|n| eval(n, classes, cores))
            .reduce(|a, b| a.parallel(b))
            .expect("non-empty"),
        Net::Core { core, parts } => {
            let c = &cores[*core];
            let w: Vec<T> = parts.iter().map(|n| eval(n, classes, cores)).collect();
            laplace::ceq(c.nv, 0, 1, &c.edges, &w)
        }
    }
}
