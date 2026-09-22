//! Catalog of non-series-parallel "cores".
//!
//! Every two-terminal network in which each capacitor carries charge is 2-connected
//! once the virtual edge A–B is added. Its SPQR decomposition rooted at that edge
//! has only three kinds of nodes: series (S), parallel (P) and *rigid* (R). An R
//! node is a 3-connected simple graph; removing the virtual edge leaves a
//! two-terminal "core" whose edges are filled with smaller two-terminal networks.
//! The Wheatstone bridge (K4 minus an edge) is the smallest core.
//!
//! This module enumerates, by brute force with canonical labeling, every
//! 3-connected graph with at most `MAX_GRAPH_EDGES` edges (these need at most 6
//! vertices, because 3-connectivity forces minimum degree 3) and derives the
//! cores up to isomorphism that fixes the terminal pair.

use std::sync::OnceLock;

/// Largest 3-connected graph considered; cores have one edge fewer.
pub const MAX_GRAPH_EDGES: usize = 10;
/// Largest core size, i.e. the network is complete for up to this many parts.
pub const MAX_CORE_EDGES: usize = MAX_GRAPH_EDGES - 1;
const MAX_VERTS: usize = 6;

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Core {
    /// Number of vertices; terminals are always vertex 0 (A) and 1 (B).
    pub nv: usize,
    pub edges: Vec<(usize, usize)>,
}

impl Core {
    pub fn m(&self) -> usize {
        self.edges.len()
    }
}

fn pair_index(i: usize, j: usize) -> usize {
    let (i, j) = if i < j { (i, j) } else { (j, i) };
    // Row-major upper triangle for MAX_VERTS vertices.
    i * (2 * MAX_VERTS - i - 1) / 2 + (j - i - 1)
}

fn pairs(v: usize) -> Vec<(usize, usize)> {
    let mut out = Vec::new();
    for i in 0..v {
        for j in i + 1..v {
            out.push((i, j));
        }
    }
    out
}

fn edges_of(mask: u32) -> Vec<(usize, usize)> {
    pairs(MAX_VERTS)
        .into_iter()
        .filter(|&(i, j)| mask >> pair_index(i, j) & 1 == 1)
        .collect()
}

fn permutations(v: usize) -> Vec<Vec<usize>> {
    fn rec(cur: &mut Vec<usize>, used: &mut [bool], v: usize, out: &mut Vec<Vec<usize>>) {
        if cur.len() == v {
            out.push(cur.clone());
            return;
        }
        for x in 0..v {
            if !used[x] {
                used[x] = true;
                cur.push(x);
                rec(cur, used, v, out);
                cur.pop();
                used[x] = false;
            }
        }
    }
    let mut out = Vec::new();
    rec(&mut Vec::new(), &mut vec![false; v], v, &mut out);
    out
}

fn relabel(mask: u32, p: &[usize]) -> u32 {
    edges_of(mask)
        .into_iter()
        .fold(0, |m, (i, j)| m | 1 << pair_index(p[i], p[j]))
}

fn connected_without(adj: &[u32], v: usize, removed: u32) -> bool {
    let alive = ((1u32 << v) - 1) & !removed;
    if alive == 0 {
        return true;
    }
    let start = alive.trailing_zeros() as usize;
    let mut seen = 1u32 << start;
    let mut stack = vec![start];
    while let Some(x) = stack.pop() {
        let mut nb = adj[x] & alive & !seen;
        while nb != 0 {
            let y = nb.trailing_zeros() as usize;
            nb &= nb - 1;
            seen |= 1 << y;
            stack.push(y);
        }
    }
    seen == alive
}

fn is_three_connected(mask: u32, v: usize) -> bool {
    if v < 4 {
        return false;
    }
    let mut adj = vec![0u32; v];
    for (i, j) in edges_of(mask) {
        adj[i] |= 1 << j;
        adj[j] |= 1 << i;
    }
    if adj.iter().any(|a| a.count_ones() < 3) {
        return false;
    }
    for x in 0..v {
        for y in x..v {
            if !connected_without(&adj, v, 1 << x | 1 << y) {
                return false;
            }
        }
    }
    true
}

/// Canonical masks of all 3-connected graphs with `v` vertices and at most
/// `max_e` edges, up to isomorphism.
pub fn three_connected_graphs(v: usize, max_e: usize) -> Vec<u32> {
    let all = pairs(v);
    let perms = permutations(v);
    let mut found: Vec<u32> = Vec::new();
    let min_e = (3 * v).div_ceil(2);
    for e in min_e..=max_e.min(all.len()) {
        for_each_combination(all.len(), e, &mut |idx| {
            let mask = idx
                .iter()
                .fold(0u32, |m, &k| m | 1 << pair_index(all[k].0, all[k].1));
            if !is_three_connected(mask, v) {
                return;
            }
            let canon = perms.iter().map(|p| relabel(mask, p)).min().unwrap();
            if !found.contains(&canon) {
                found.push(canon);
            }
        });
    }
    found
}

fn for_each_combination(n: usize, k: usize, f: &mut dyn FnMut(&[usize])) {
    fn rec(start: usize, n: usize, k: usize, cur: &mut Vec<usize>, f: &mut dyn FnMut(&[usize])) {
        if cur.len() == k {
            f(cur);
            return;
        }
        for x in start..n {
            if n - x < k - cur.len() {
                break;
            }
            cur.push(x);
            rec(x + 1, n, k, cur, f);
            cur.pop();
        }
    }
    rec(0, n, k, &mut Vec::new(), f);
}

fn build_cores() -> Vec<Core> {
    let mut out: Vec<(usize, u32, Core)> = Vec::new();
    for v in 4..=MAX_VERTS {
        let perms = permutations(v);
        for g in three_connected_graphs(v, MAX_GRAPH_EDGES) {
            for (u, w) in edges_of(g) {
                let core = g & !(1 << pair_index(u, w));
                let canon = perms
                    .iter()
                    .filter(|p| (p[u] == 0 && p[w] == 1) || (p[u] == 1 && p[w] == 0))
                    .map(|p| relabel(core, p))
                    .min()
                    .unwrap();
                if !out.iter().any(|(nv, c, _)| *nv == v && *c == canon) {
                    let edges = edges_of(canon);
                    out.push((v, canon, Core { nv: v, edges }));
                }
            }
        }
    }
    out.sort_by_key(|(nv, c, core)| (core.m(), *nv, *c));
    out.into_iter().map(|(_, _, c)| c).collect()
}

/// All cores with at most `MAX_CORE_EDGES` edges, sorted by edge count.
pub fn all_cores() -> &'static [Core] {
    static CORES: OnceLock<Vec<Core>> = OnceLock::new();
    CORES.get_or_init(build_cores)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_three_connected_graphs() {
        // K4 is the only one on 4 vertices; W4, K5−e and K5 on 5 vertices;
        // the prism and K3,3 are the only cubic ones on 6 vertices.
        assert_eq!(three_connected_graphs(4, 10).len(), 1);
        assert_eq!(three_connected_graphs(5, 10).len(), 3);
        assert_eq!(three_connected_graphs(6, 9).len(), 2);
    }

    #[test]
    fn wheatstone_bridge_is_the_unique_smallest_core() {
        let cores = all_cores();
        let five: Vec<_> = cores.iter().filter(|c| c.m() == 5).collect();
        assert_eq!(five.len(), 1);
        assert!(cores.iter().all(|c| c.m() >= 5));
        // W4 minus a spoke and W4 minus a rim edge.
        assert_eq!(cores.iter().filter(|c| c.m() == 7).count(), 2);
    }

    #[test]
    fn cores_have_terminals_and_fit_the_reducer() {
        for c in all_cores() {
            assert!(c.nv <= crate::laplace::MAX_V);
            assert!(!c.edges.contains(&(0, 1)), "terminal edge must be removed");
            assert!(c.m() <= MAX_CORE_EDGES);
        }
    }
}
