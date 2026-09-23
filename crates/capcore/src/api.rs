//! JSON-facing solver: request validation, mode dispatch and result shaping.
//! Values cross the boundary in farads; internally they are normalised so the
//! target is 1, which keeps relative precision independent of the unit scale.

use serde::{Deserialize, Serialize};

use crate::cores::{all_cores, Core, MAX_CORE_EDGES};
use crate::engine::{eval, Engine, Net, Params, TopK};
use crate::laplace::ceq_graph;
use crate::space::{MultisetSpace, SizeSpace, Space, MAX_CLASSES, MAX_COUNT};

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum Mode {
    /// Every listed capacitor is used exactly once.
    All,
    /// Choose between `min_parts` and `max_parts` parts from an inventory.
    Inventory,
}

#[derive(Clone, Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct Request {
    pub mode: Mode,
    pub values: Vec<f64>,
    pub target: f64,
    /// Inventory stock per value (`None` = unlimited).
    #[serde(default)]
    pub stock: Option<Vec<u32>>,
    #[serde(default = "default_max_parts")]
    pub max_parts: usize,
    #[serde(default = "default_min_parts")]
    pub min_parts: usize,
    #[serde(default = "default_top_k")]
    pub top_k: usize,
    /// Largest non-series-parallel core to consider (0 = series-parallel only).
    #[serde(default)]
    pub max_core_edges: usize,
    #[serde(default = "default_budget")]
    pub max_entries: usize,
}

fn default_max_parts() -> usize {
    4
}
fn default_min_parts() -> usize {
    1
}
fn default_top_k() -> usize {
    20
}
fn default_budget() -> usize {
    6_000_000
}

/// Limits enforced on requests coming from the UI.
pub const MAX_ALL_PARTS: usize = 12;
pub const MAX_INVENTORY_PARTS: usize = 10;
/// Largest "use all" problem for which non-series-parallel networks are explored.
pub const MAX_CORE_PARTS: usize = 8;
/// Core evaluations for a whole search (a few seconds in the browser).
pub const MAX_CORE_WORK: u64 = 40_000_000;
/// Float values closer than this are the same value.
pub const FLOAT_EPS: f64 = 1e-12;

#[derive(Clone, Debug, Serialize, PartialEq)]
#[serde(tag = "t", rename_all = "lowercase")]
pub enum Tree {
    Leaf { k: usize },
    Series { c: Vec<Tree> },
    Parallel { c: Vec<Tree> },
    Core { core: usize, c: Vec<Tree> },
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct LeafOut {
    pub class: usize,
    pub value: f64,
    /// Position in the request's `values` (mode `all` only).
    pub index: Option<usize>,
}

#[derive(Clone, Debug, Serialize)]
pub struct GraphOut {
    pub nodes: usize,
    pub a: usize,
    pub b: usize,
    /// `[u, v, leaf]` triples.
    pub edges: Vec<[usize; 3]>,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Solution {
    pub value: f64,
    /// Signed relative error `(value − target) / target`.
    pub rel_error: f64,
    pub parts: usize,
    pub tree: Tree,
    pub leaves: Vec<LeafOut>,
    pub graph: GraphOut,
}

#[derive(Clone, Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct StatsOut {
    pub states: usize,
    pub entries: usize,
    pub candidates: u64,
    pub eps_used: f64,
    /// Every network was considered (up to float rounding).
    pub exhaustive: bool,
    /// Every enabled non-series-parallel core was explored. When false the
    /// bound only covers the networks that do not use the skipped cores.
    pub cores_complete: bool,
    /// Proven bound: the true optimum's relative error is at most this much
    /// better than the best reported one.
    pub bound_rel: f64,
}

#[derive(Clone, Debug, Serialize)]
pub struct CoreOut {
    pub id: usize,
    pub nv: usize,
    pub edges: Vec<[usize; 2]>,
}

#[derive(Clone, Debug, Serialize)]
pub struct Response {
    pub solutions: Vec<Solution>,
    pub stats: StatsOut,
    pub cores: Vec<CoreOut>,
}

fn validate(req: &Request) -> Result<(), String> {
    if !(req.target.is_finite() && req.target > 0.0) {
        return Err("target must be a positive number".into());
    }
    if req.values.is_empty() {
        return Err("no capacitor values".into());
    }
    if req.values.iter().any(|v| !(v.is_finite() && *v > 0.0)) {
        return Err("capacitor values must be positive numbers".into());
    }
    // Values are normalised by the target; keep the ratios far from the f64
    // limits so no value underflows, overflows or becomes subnormal (the log
    // grid bound assumes normal doubles).
    if req
        .values
        .iter()
        .any(|v| !(1e-150..=1e150).contains(&(v / req.target)))
    {
        return Err("values and target differ by more than 150 orders of magnitude".into());
    }
    if req.top_k == 0 || req.top_k > 1000 {
        return Err("topK must be between 1 and 1000".into());
    }
    match req.mode {
        Mode::All if req.values.len() > MAX_ALL_PARTS => Err(format!(
            "at most {MAX_ALL_PARTS} capacitors in 'use all' mode"
        )),
        Mode::Inventory if req.max_parts == 0 || req.max_parts > MAX_INVENTORY_PARTS => Err(
            format!("maxParts must be between 1 and {MAX_INVENTORY_PARTS}"),
        ),
        Mode::Inventory if req.min_parts == 0 || req.min_parts > req.max_parts => {
            Err("minParts must be between 1 and maxParts".into())
        }
        Mode::Inventory => match &req.stock {
            Some(s) if s.len() != req.values.len() => {
                Err("stock must have one entry per value".into())
            }
            _ => Ok(()),
        },
        Mode::All => Ok(()),
    }
}

/// Distinct values (exact float equality) with the input positions of each.
fn classes_of(values: &[f64]) -> (Vec<f64>, Vec<Vec<usize>>) {
    let mut classes: Vec<f64> = Vec::new();
    let mut members: Vec<Vec<usize>> = Vec::new();
    for (i, &v) in values.iter().enumerate() {
        match classes.iter().position(|&c| c == v) {
            Some(k) => members[k].push(i),
            None => {
                classes.push(v);
                members.push(vec![i]);
            }
        }
    }
    (classes, members)
}

struct Shaper<'a> {
    classes: &'a [f64],
    members: Option<Vec<Vec<usize>>>,
    cursor: Vec<usize>,
    leaves: Vec<LeafOut>,
    edges: Vec<[usize; 3]>,
    nodes: usize,
    cores: &'a [Core],
}

impl Shaper<'_> {
    fn tree(&mut self, net: &Net) -> Tree {
        match net {
            Net::Leaf(c) => {
                let index = self.members.as_ref().map(|m| {
                    let i = m[*c][self.cursor[*c]];
                    self.cursor[*c] += 1;
                    i
                });
                self.leaves.push(LeafOut {
                    class: *c,
                    value: self.classes[*c],
                    index,
                });
                Tree::Leaf {
                    k: self.leaves.len() - 1,
                }
            }
            Net::Series(k) => Tree::Series {
                c: k.iter().map(|n| self.tree(n)).collect(),
            },
            Net::Parallel(k) => Tree::Parallel {
                c: k.iter().map(|n| self.tree(n)).collect(),
            },
            Net::Core { core, parts } => Tree::Core {
                core: *core,
                c: parts.iter().map(|n| self.tree(n)).collect(),
            },
        }
    }

    fn new_node(&mut self) -> usize {
        self.nodes += 1;
        self.nodes - 1
    }

    fn flatten(&mut self, t: &Tree, u: usize, v: usize) {
        match t {
            Tree::Leaf { k } => self.edges.push([u, v, *k]),
            Tree::Parallel { c } => c.iter().for_each(|x| self.flatten(x, u, v)),
            Tree::Series { c } => {
                let mut prev = u;
                for (i, x) in c.iter().enumerate() {
                    let next = if i + 1 == c.len() { v } else { self.new_node() };
                    self.flatten(x, prev, next);
                    prev = next;
                }
            }
            Tree::Core { core, c } => {
                let k = &self.cores[*core];
                let mut map = vec![u, v];
                for _ in 2..k.nv {
                    let n = self.new_node();
                    map.push(n);
                }
                for (&(x, y), part) in k.edges.iter().zip(c) {
                    self.flatten(part, map[x], map[y]);
                }
            }
        }
    }
}

fn used_cores(t: &Tree, out: &mut Vec<usize>) {
    match t {
        Tree::Leaf { .. } => {}
        Tree::Series { c } | Tree::Parallel { c } => c.iter().for_each(|x| used_cores(x, out)),
        Tree::Core { core, c } => {
            if !out.contains(core) {
                out.push(*core);
            }
            c.iter().for_each(|x| used_cores(x, out));
        }
    }
}

/// Problem data shared by both modes: normalised and raw class values.
struct Ctx<'a> {
    classes: &'a [f64],
    raw: &'a [f64],
    members: Option<Vec<Vec<usize>>>,
    target: f64,
    depth: usize,
}

fn run<S: Space>(
    mut eng: Engine<'_, f64, S>,
    roots: &[usize],
    queries: &[usize],
    top_k: usize,
    ctx: Ctx<'_>,
) -> Result<Response, String> {
    let Ctx {
        classes,
        raw,
        members,
        target,
        depth,
    } = ctx;
    eng.build_all(&|s| roots.contains(&s))?;
    let mut top = TopK::new(top_k);
    for &s in queries {
        eng.query(s, 1.0, &mut top);
    }
    let cores = all_cores();
    let mut solutions = Vec::new();
    let mut core_ids = Vec::new();
    for c in &top.items {
        let net = eng.network(c);
        let mut sh = Shaper {
            classes,
            cursor: vec![0; classes.len()],
            members: members.clone(),
            leaves: Vec::new(),
            edges: Vec::new(),
            nodes: 2,
            cores,
        };
        let tree = sh.tree(&net);
        sh.flatten(&tree, 0, 1);
        // Self-check: the tree and the flattened graph agree with the DP value.
        let by_tree = eval(&net, classes, cores);
        let wedges: Vec<(usize, usize, f64)> = sh
            .edges
            .iter()
            .map(|&[u, v, k]| (u, v, classes[sh.leaves[k].class]))
            .collect();
        let by_graph = ceq_graph(sh.nodes, 0, 1, &wedges);
        let tol = 1e-9 * c.v.abs().max(1e-300);
        if (by_tree - c.v).abs() > tol || (by_graph - c.v).abs() > tol {
            return Err(format!(
                "internal consistency check failed: dp={} tree={} graph={}",
                c.v, by_tree, by_graph
            ));
        }
        used_cores(&tree, &mut core_ids);
        // Report the part values exactly as given, not re-scaled.
        let leaves = sh
            .leaves
            .into_iter()
            .map(|l| LeafOut {
                value: raw[l.class],
                ..l
            })
            .collect();
        solutions.push(Solution {
            value: c.v * target,
            rel_error: c.v - 1.0,
            parts: net.parts(),
            tree,
            leaves,
            graph: GraphOut {
                nodes: sh.nodes,
                a: 0,
                b: 1,
                edges: sh.edges,
            },
        });
    }
    core_ids.sort();
    let st = &eng.stats;
    Ok(Response {
        solutions,
        stats: StatsOut {
            states: st.states_built,
            entries: st.entries,
            candidates: st.candidates,
            eps_used: eng.eps_bound(),
            exhaustive: eng.exhaustive(),
            cores_complete: eng.cores_complete(),
            // Proven bound: ε_opt ≥ ε_found − (e^{(n−1)ε} − 1)(1 + ε_opt), and
            // ε_opt ≤ ε_found, so (1 + ε_found) makes it safe to display.
            bound_rel: (eng.eps_bound() * depth.saturating_sub(1) as f64).exp_m1()
                * (1.0 + top.items.first().map_or(0.0, |c| c.err)),
        },
        cores: core_ids
            .into_iter()
            .map(|id| CoreOut {
                id,
                nv: cores[id].nv,
                edges: cores[id].edges.iter().map(|&(u, v)| [u, v]).collect(),
            })
            .collect(),
    })
}

/// Solve a request. `progress(fraction)` reports the share of the estimated work done.
pub fn solve(req: &Request, progress: &mut dyn FnMut(f64)) -> Result<Response, String> {
    validate(req)?;
    let target = req.target;
    let params = Params {
        eps: FLOAT_EPS,
        max_per_state: 0,
        // Beyond MAX_CORE_PARTS distinct-ish parts the non-series-parallel
        // search space (millions of core decompositions) is out of reach.
        max_core_edges: if req.mode == Mode::All && req.values.len() > MAX_CORE_PARTS {
            0
        } else {
            req.max_core_edges.min(MAX_CORE_EDGES)
        },
        max_entries: req.max_entries,
        max_core_work: MAX_CORE_WORK,
    };
    let cores = all_cores();
    match req.mode {
        Mode::All => {
            let (classes, members) = classes_of(&req.values);
            let norm: Vec<f64> = classes.iter().map(|c| c / target).collect();
            let counts: Vec<u8> = members.iter().map(|m| m.len() as u8).collect();
            let n = req.values.len();
            let space = MultisetSpace::new(&counts, n);
            let full = space.id(MultisetSpace::pack(&counts)).expect("full state");
            let mut eng = Engine::new(space, norm.clone(), cores, params);
            eng.on_progress(&mut *progress);
            let ctx = Ctx {
                classes: &norm,
                raw: &classes,
                members: Some(members),
                target,
                depth: n,
            };
            run(eng, &[full], &[full], req.top_k, ctx)
        }
        Mode::Inventory => {
            let (classes, members) = classes_of(&req.values);
            let norm: Vec<f64> = classes.iter().map(|c| c / target).collect();
            let k = req.max_parts;
            let stock: Option<Vec<usize>> = req.stock.as_ref().map(|s| {
                members
                    .iter()
                    .map(|m| m.iter().map(|&i| s[i] as usize).sum())
                    .collect()
            });
            let limited = stock.as_ref().is_some_and(|s| s.iter().any(|&c| c < k));
            if limited {
                let stock = stock.expect("limited implies stock");
                if classes.len() > MAX_CLASSES {
                    return Err(format!(
                        "at most {MAX_CLASSES} distinct values with limited stock"
                    ));
                }
                let uni: Vec<u8> = stock
                    .iter()
                    .map(|&c| c.min(k).min(MAX_COUNT as usize) as u8)
                    .collect();
                let space = MultisetSpace::new(&uni, k);
                let roots: Vec<usize> = (0..space.n_states())
                    .filter(|&s| space.size(s) == k)
                    .collect();
                let queries: Vec<usize> = (0..space.n_states())
                    .filter(|&s| space.size(s) >= req.min_parts)
                    .collect();
                let mut eng = Engine::new(space, norm.clone(), cores, params);
                eng.on_progress(&mut *progress);
                let ctx = Ctx {
                    classes: &norm,
                    raw: &classes,
                    members: None,
                    target,
                    depth: k,
                };
                run(eng, &roots, &queries, req.top_k, ctx)
            } else {
                let space = SizeSpace {
                    kmax: k,
                    nclass: classes.len(),
                };
                let queries: Vec<usize> = (req.min_parts - 1..k).collect();
                let mut eng = Engine::new(space, norm.clone(), cores, params);
                eng.on_progress(&mut *progress);
                let ctx = Ctx {
                    classes: &norm,
                    raw: &classes,
                    members: None,
                    target,
                    depth: k,
                };
                run(eng, &[k - 1], &queries, req.top_k, ctx)
            }
        }
    }
}

pub fn cores_out(max_edges: usize) -> Vec<CoreOut> {
    all_cores()
        .iter()
        .enumerate()
        .filter(|(_, c)| c.m() <= max_edges)
        .map(|(id, c)| CoreOut {
            id,
            nv: c.nv,
            edges: c.edges.iter().map(|&(u, v)| [u, v]).collect(),
        })
        .collect()
}
