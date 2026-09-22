# Approaches to capacitor-network synthesis

Problem: given a multiset of capacitances and a target C\*, find two-terminal networks minimising |C_eq − C\*| / C\*. Variants: *all* parts used once, *subset* of a finite inventory, or *catalogue* with reusable values.

Physics: with V_A = 1, V_B = 0, the internal potentials solve L_II v_I = −L_IA, and C_eq = Q_A is the Schur complement of the capacitance-weighted Laplacian onto the terminals. This is the same quantity as the effective conductance of a resistor network with conductances c_e.

## What v2 implements

| Method | Status | Notes |
|---|---|---|
| Value DP over part multisets | **Implemented** (`crates/capcore/src/engine.rs`) | Stores distinct values per state with one witness each. Equal values share a class, so 2^n states collapse to Π(count+1). |
| Meet in the middle at the root | **Implemented** | The root state is never materialised. |
| SPQR cores (bridges and all 3-connected skeletons) | **Implemented** (`cores.rs`) | Complete for ≤ 9 parts (validated against OEIS A337517); in the app, exhaustive up to 8 distinct parts before the memory budget forces coarsening. |
| Log-grid pruning with a proven bound | **Implemented** | Sort-free bucketing on the IEEE-754 bit pattern once a state exceeds its memory share. |
| Exact rational verification | **Implemented** (Rust `Q` for tests, TS `Frac` in the app) | Values come from the decimal text, never from rounded doubles. |
| Tolerance interval | **Implemented** | Monotone and 1-homogeneous, so a uniform ±δ gives exactly [(1−δ)C, (1+δ)C]. |
| MILP (placement × potentials, exact linearisation of binary·continuous) | Not implemented | Would give certifiable general optima with extra constraints (cost, voltage). Needs a fixed number of node slots and symmetry breaking. `highs-js` could run it in a worker. The core DP already covers ≤ 8 distinct parts exhaustively. |
| ALNS with exact DP/MILP repair | Not implemented | The natural route beyond 12 parts or with side constraints. Use the sensitivity Δv² to choose what to destroy. |
| Robust optimisation (heterogeneous tolerances) | Not implemented | Two copies of the network (all-lower / all-upper) suffice by monotonicity. |
| Learned generators (LLM/RL) | Out of scope | Evaluation here is cheap and exact, and search dominates on quality. |
| WebGPU / Pyodide | Rejected | Branchy combinatorics with ≤ 6-node matrices, and a heavy runtime for no gain. |

## Measured behaviour (native, release; WASM is roughly 1–2× slower)

| n distinct parts | SP only | All networks |
|---|---|---|
| 8 | 0.2 s, exhaustive | 0.7 s, exhaustive |
| 9 | 3 s, bound 0.02 % | 8 s, bound 0.05 % |
| 10 | 2.4 s, bound 0.2 % (best error 4e-9) | cores disabled in the UI |
| 12 | 25 s, bound 4 % (best error 1e-9) | — |

The bound is a worst case. In practice the best error found is many orders of magnitude smaller.

## Toward a publication (from the external research review)

A defensible paper would be framed around a benchmark (*CapBench*: exact, scale and robust families, with targets stored as exact rationals) and would compare:

- the tree enumeration of v1 against the value DP,
- the value DP against the multiset DP,
- the SP optimum against the general optimum (the "SP gap"; the {1,…,5} pF → 170/71 pF bridge is a minimal example),
- MILP and ALNS at scale.

Every reported circuit would pass the independent rational verifier. The v2 engine already provides the exact SP/general ground truth up to 9 parts and a verified browser artefact.

## References

- F. Dörfler, F. Bullo, *Kron Reduction of Graphs with Applications to Electrical Networks*, IEEE TCAS-I 60(1), 2013.
- J. Hopcroft, R. Tarjan, *Dividing a graph into triconnected components*, SIAM J. Comput. 2(3), 1973.
- S. Khan, *The bounds of the set of equivalent resistances of n equal resistors…*, arXiv:1004.3346.
- O. Ibarra, C. Kim, *Fast approximation algorithms for the knapsack and sum of subset problems*, J. ACM 22(4), 1975.
- T. Chan, Z. Liang, M. Sozio, *Network design for s-t effective resistance*, 2019.
- E. Weissler et al., *Enumeration of all superconducting circuits up to 5 nodes*, arXiv:2410.18497.
- OEIS A048211, A174283, A337517, A006351.
