"""Educational content and theory sections.

This module provides theory explanations, formulas, and educational content
for each synthesis method (SP exhaustive, heuristics, graph-based).

Displays content using st.latex for formulas and st.expander for
collapsible theory sections.

Constitutional Compliance:
    - Principle II (UX First): Clear educational content
    - Principle V (Extensibility): Modular theory content functions
"""

from typing import Any, Dict, List
import streamlit as st


def get_sp_theory_content() -> Dict[str, Any]:
    """Get theory content for Series-Parallel networks (T071).

    Returns:
        Dictionary with keys:
            - title: Section title
            - explanation: Detailed explanation text
            - formulas: List of (latex_string, description) tuples
            - when_to_use: When to use this method
            - complexity: Time/space complexity description
    """
    return {
        "title": "Series-Parallel (SP) Networks",
        "explanation": """
**Series-Parallel networks** are the most common type of capacitor configurations.
They can be fully described by binary trees where:

- **Series connection**: Capacitors in series have their reciprocal capacitances added
- **Parallel connection**: Capacitors in parallel have their capacitances directly summed

These networks are "well-structured" and can be recursively decomposed into simpler
sub-networks. The SP Exhaustive method enumerates all possible binary tree topologies
that combine the input capacitors.
""",
        "formulas": [
            (r"C_{series} = \frac{1}{\frac{1}{C_1} + \frac{1}{C_2} + \cdots + \frac{1}{C_n}}", 
             "Series combination formula"),
            (r"C_{parallel} = C_1 + C_2 + \cdots + C_n", 
             "Parallel combination formula"),
            (r"T(n) = \text{Cat}(n-1) \times n!", 
             "Number of SP topologies for n capacitors (Catalan number × permutations)"),
        ],
        "when_to_use": """
✅ Use SP Exhaustive when:
- You have **N ≤ 8** capacitors
- You want **guaranteed optimal** solutions
- Your circuit must use standard series/parallel connections
- You need **exact enumeration** of all possibilities
""",
        "complexity": """
**Time Complexity**: O(Cat(n) × n!)
- Cat(n) ≈ 4ⁿ / (n^1.5 × √π)
- For n=8: ~264,600 topologies

**Space Complexity**: O(n) for tree depth

The algorithm uses **memoization** to avoid recomputing equivalent subtrees.
"""
    }


def get_sp_graph_theory_content() -> Dict[str, Any]:
    """Get theory content for SP Graph Exhaustive method."""
    return {
        "title": "SP Graph Exhaustive",
        "explanation": """
**SP Graph Exhaustive** extends the Series-Parallel concept to general graphs.
Unlike the Tree method which builds circuits from the bottom up, this method:
1. Enumerates all connected **multigraph topologies** with N edges.
2. Assigns capacitors to edges.
3. Checks if the resulting graph is **SP-reducible** using iterative reduction rules.

This allows finding solutions that have **internal nodes** (bridge-like structures)
which are still SP-reducible but cannot be represented as simple binary trees.

**Example**: The "Classroom Problem"
A circuit with 4 capacitors can form a structure with internal nodes C and D
that reduces to a single equivalent capacitance, even if it's not a simple ladder.
""",
        "formulas": [
            (r"V \in [2, N+1]", "Number of nodes ranges from 2 (all parallel) to N+1 (all series)"),
            (r"C_{parallel} = \sum C_i", "Parallel reduction rule (edges between same nodes)"),
            (r"C_{series} = (1/C_1 + 1/C_2)^{-1}", "Series reduction rule (degree-2 internal node)"),
        ],
        "when_to_use": """
✅ Use SP Graph Exhaustive when:
- You have **N ≤ 6** capacitors
- You suspect the solution requires **internal nodes** (bridges)
- SP Tree method fails to find an exact solution
- You still want a guaranteed SP-reducible circuit
""",
        "complexity": """
**Time Complexity**: High (Exponential)
- Enumerates all multigraphs + all permutations of capacitors.
- Much slower than SP Tree for N > 6.

**Space Complexity**: O(N + E) for graph storage.
"""
    }


def get_laplacian_theory_content() -> Dict[str, Any]:
    """Get theory content for Laplacian/graph-based analysis (T072).

    Returns:
        Dictionary with theory content for the Laplacian nodal analysis method.
    """
    return {
        "title": "Laplacian Nodal Analysis",
        "explanation": """
**Graph-based analysis** uses nodal admittance matrices to compute the equivalent
capacitance of arbitrary network topologies, including **non-SP configurations**
like Wheatstone bridges and delta-wye networks.

The method models the capacitor network as a graph where:
- **Nodes**: Connection points (terminals A, B, and internal nodes)
- **Edges**: Capacitors with their capacitance values

Using Laplacian (nodal) analysis, we apply boundary conditions:
- Terminal A is set to voltage V_A = 1
- Terminal B is set to voltage V_B = 0 (ground)

The current flowing into terminal A equals the equivalent capacitance (in s-domain).
""",
        "formulas": [
            (r"\mathbf{Y} = s \cdot \mathbf{C}", 
             "Admittance matrix (Y = s×C for capacitors)"),
            (r"\mathbf{Y} \cdot \mathbf{V} = \mathbf{I}", 
             "Nodal equation (Kirchhoff's current law)"),
            (r"V_A = 1, \quad V_B = 0", 
             "Boundary conditions at terminals"),
            (r"C_{eq} = I_A = \sum_j Y_{A,j} \cdot V_j", 
             "Equivalent capacitance equals current at terminal A"),
            (r"\mathbf{C} = \begin{bmatrix} \sum C_j & -C_{1,2} & \cdots \\ -C_{1,2} & \sum C_k & \cdots \\ \vdots & \vdots & \ddots \end{bmatrix}", 
             "Laplacian matrix structure"),
        ],
        "when_to_use": """
✅ Use Laplacian analysis when:
- Working with **non-SP topologies** (bridges, meshes, delta/wye)
- Analyzing **arbitrary graph structures**
- You need to compute C_eq for **given topologies**
- Handling networks with **internal nodes**
""",
        "complexity": """
**Time Complexity**: O(n³) for matrix inversion
- Uses LU decomposition or pseudo-inverse for singular matrices

**Space Complexity**: O(n²) for the admittance matrix

Very efficient for evaluating single topologies, but not for enumeration.
"""
    }


def get_heuristic_theory_content() -> Dict[str, Any]:
    """Get theory content for heuristic random graph search (T073).

    Returns:
        Dictionary with theory content for the heuristic search method.
    """
    return {
        "title": "Heuristic Graph Search",
        "explanation": """
**Heuristic search** explores the space of arbitrary graph topologies using random
generation and evaluation. Unlike SP Exhaustive, it can discover **non-SP solutions**
that may achieve better matches to the target capacitance.

The algorithm:
1. **Generates random graphs** connecting capacitors to nodes
2. **Evaluates** each topology using Laplacian analysis
3. **Tracks** the top-k best solutions found
4. Repeats for a specified number of iterations

The search uses **deterministic seeding** for reproducibility: given the same
seed, iterations, and capacitors, you will get identical results.
""",
        "formulas": [
            (r"N_{topologies} = O\left( n^{(n+k)} \right)", 
             "Approximate topology space size (n edges, k internal nodes)"),
            (r"P_{success} = 1 - (1 - p_{good})^{iterations}", 
             "Probability of finding a good solution"),
            (r"C_{eq}^{graph} = \text{Laplacian}(G, \{C_i\})", 
             "Graph evaluation using nodal analysis"),
        ],
        "when_to_use": """
✅ Use Heuristic Search when:
- You have **N > 8** capacitors
- SP Exhaustive is **too slow** or times out
- You want to explore **non-SP topologies** (bridges, meshes)
- You're willing to trade **guaranteed optimality** for **speed**
- You want **reproducible** random exploration (set a seed)
""",
        "complexity": """
**Time Complexity**: O(iterations × n³)
- Each iteration: O(n³) for Laplacian evaluation
- Typical: 1000-10000 iterations

**Space Complexity**: O(n² + k) for graph + top-k solutions

The **iterations** parameter controls exploration depth. More iterations
increase the probability of finding optimal or near-optimal solutions.
"""
    }


def get_enumeration_theory_content() -> Dict[str, Any]:
    """Get theory content for topology enumeration and Catalan numbers.

    Returns:
        Dictionary with keys:
            - title: Section title
            - explanation: Detailed explanation text
            - formulas: List of (latex_string, description) tuples
            - empirical_data: Table of empirical topology counts
            - references: Academic references
    """
    return {
        "title": "Topology Enumeration & Catalan Numbers",
        "explanation": """
**Series-Parallel topology enumeration** is closely related to the **Catalan numbers**,
a famous sequence in combinatorics that counts various recursive structures.

The number of distinct SP topologies for *n* capacitors depends on:

1. **The number of binary tree structures**: Related to the (n-1)th Catalan number
2. **The permutations of capacitors**: How capacitors are assigned to leaf nodes

The **Catalan numbers** (OEIS A000108) count, among many things:
- The number of **full binary trees** with n+1 leaves
- The number of ways to **parenthesize** n+1 factors
- The number of **Dyck words** of length 2n
- The number of ways to **triangulate** a convex polygon with n+2 sides

These structures are isomorphic to Series-Parallel trees, where each internal
node represents either a series or parallel operation.

The sequence was discovered by **Minggatu** in the 1730s and later studied by
**Eugène Charles Catalan** (1814-1894).
""",
        "formulas": [
            (r"C_n = \frac{1}{n+1} \binom{2n}{n} = \frac{(2n)!}{(n+1)! \cdot n!}",
             "Catalan number formula (closed form)"),
            (r"C_0 = 1, \quad C_{n+1} = \sum_{i=0}^{n} C_i \cdot C_{n-i}",
             "Recurrence relation for Catalan numbers"),
            (r"C_n \sim \frac{4^n}{n^{3/2} \sqrt{\pi}}",
             "Asymptotic growth (Stirling's approximation)"),
            (r"T(n) = C_{n-1} \times n! \times 2^{n-1}",
             "Upper bound for SP topologies (tree structures × permutations × operations)"),
        ],
        "catalan_sequence": [
            (0, 1), (1, 1), (2, 2), (3, 5), (4, 14), (5, 42), (6, 132), (7, 429), (8, 1430)
        ],
        "empirical_data": [
            {"n": 2, "Topologies": 2, "Formula Estimate": "C₁ × 2! = 2"},
            {"n": 3, "Topologies": 8, "Formula Estimate": "C₂ × 3! × 2 = 24 (upper bound)"},
            {"n": 4, "Topologies": 40, "Formula Estimate": "5 × 24 × 4 = 480 (upper bound)"},
            {"n": 5, "Topologies": 224, "Formula Estimate": "14 × 120 × 8 = 13,440 (upper bound)"},
            {"n": 6, "Topologies": 1344, "Formula Estimate": "42 × 720 × 16 = 483,840 (upper bound)"},
            {"n": 7, "Topologies": 8448, "Formula Estimate": "132 × 5040 × 32 (upper bound)"},
            {"n": 8, "Topologies": 54912, "Formula Estimate": "429 × 40320 × 64 (upper bound)"},
        ],
        "empirical_explanation": """
### Why Empirical Values?

The actual number of **distinct** SP topologies is **less** than the theoretical upper bound
because:

1. **Symmetry**: Series and parallel operations are commutative: S(A,B) = S(B,A)
2. **Memoization**: Equivalent subtrees are counted only once
3. **Equivalence classes**: Many different trees compute the same capacitance

The empirical values in CapAssigner are **exact counts** obtained by running the
enumeration algorithm and counting unique topologies. These values enable accurate
progress bar estimation during exhaustive search.

| n Capacitors | Actual Topologies | Growth Factor |
|--------------|-------------------|---------------|
| 2 | 2 | - |
| 3 | 8 | ×4 |
| 4 | 40 | ×5 |
| 5 | 224 | ×5.6 |
| 6 | 1,344 | ×6 |
| 7 | 8,448 | ×6.3 |
| 8 | 54,912 | ×6.5 |

The growth factor approaches 6-7× per additional capacitor, which is consistent with
combinatorial analysis of labeled binary trees.
""",
        "references": """
### Academic References

1. **Richard P. Stanley** (2015). *Catalan Numbers*. Cambridge University Press.
   - Comprehensive reference covering 200+ interpretations of Catalan numbers.

2. **OEIS A000108** - The On-Line Encyclopedia of Integer Sequences.
   - URL: [oeis.org/A000108](https://oeis.org/A000108)
   - The definitive reference for Catalan number sequence and properties.

3. **Duffin, R. J.** (1965). "Topology of series-parallel networks".
   *Journal of Mathematical Analysis and Applications*, 10(2), 303-318.
   - Foundational paper on series-parallel graph theory.

4. **Eppstein, D.** (1992). "Parallel recognition of series-parallel graphs".
   *Information and Computation*, 98(1), 41-55.
   - Efficient algorithms for SP graph recognition.

5. **Wikipedia contributors**. "Catalan number" and "Series-parallel graph".
   *Wikipedia, The Free Encyclopedia*.
   - Accessible introductions to these concepts.
"""
    }


def get_method_comparison_content() -> Dict[str, Any]:
    """Get method comparison content (T074).

    Returns:
        Dictionary with comparison table data and recommendations.
    """
    return {
        "title": "Method Comparison",
        "comparison_table": [
            {
                "Method": "SP Tree Exhaustive",
                "Speed": "Fast (N≤8)",
                "Topology Coverage": "SP Trees",
                "Optimality": "Guaranteed (Tree)",
                "Best For": "Standard SP circuits"
            },
            {
                "Method": "SP Graph Exhaustive",
                "Speed": "Slow (N≤6)",
                "Topology Coverage": "SP Graphs (w/ bridges)",
                "Optimality": "Guaranteed (SP)",
                "Best For": "Complex SP circuits"
            },
            {
                "Method": "Heuristic Graph",
                "Speed": "Configurable",
                "Topology Coverage": "All (SP + non-SP)",
                "Optimality": "Probabilistic",
                "Best For": "Large N, exploration"
            },
        ],
        "recommendations": """
### Choosing the Right Method

| Scenario | Recommended Method |
|----------|-------------------|
| N ≤ 6 capacitors | SP Graph Exhaustive |
| N = 7-8 capacitors | SP Tree Exhaustive |
| N > 8 capacitors | Heuristic Graph Search |
| Need bridges (SP-reducible) | SP Graph Exhaustive |
| Need non-SP bridges | Heuristic Graph Search |
| Need guaranteed optimal | SP Tree/Graph Exhaustive |
""",
        "complexity_comparison": """
| Method | Time | Space | Guarantee |
|--------|------|-------|-----------|
| SP Tree Exhaustive | O(Cat(n)×n!) | O(n) | Optimal within SP Tree |
| SP Graph Exhaustive | O(Exp(n)) | O(n+e) | Optimal within SP Graph |
| Heuristic Graph | O(iter×n³) | O(n²) | Best-effort |
"""
    }


def show_sp_theory() -> None:
    """Display theory section for Series-Parallel networks (T075).

    Renders the SP theory content in a Streamlit expander with
    LaTeX formulas and explanations.
    """
    content = get_sp_theory_content()
    
    with st.expander(f"📚 {content['title']}", expanded=False):
        st.markdown(content['explanation'])
        
        st.markdown("### Key Formulas")
        for latex, description in content['formulas']:
            st.latex(latex)
            st.caption(description)
        
        st.markdown("### When to Use")
        st.markdown(content['when_to_use'])
        
        st.markdown("### Complexity")
        st.markdown(content['complexity'])


def show_sp_graph_theory() -> None:
    """Display theory section for SP Graph Exhaustive method."""
    content = get_sp_graph_theory_content()
    
    with st.expander(f"📚 {content['title']}", expanded=False):
        st.markdown(content['explanation'])
        
        st.markdown("### Key Formulas")
        for latex, description in content['formulas']:
            st.latex(latex)
            st.caption(description)
        
        st.markdown("### When to Use")
        st.markdown(content['when_to_use'])
        
        st.markdown("### Complexity")
        st.markdown(content['complexity'])


def show_graph_theory() -> None:
    """Display theory section for graph-based (Laplacian) analysis (T075).

    Renders the Laplacian theory content explaining nodal analysis,
    admittance matrices, and boundary conditions.
    """
    content = get_laplacian_theory_content()
    
    with st.expander(f"📚 {content['title']}", expanded=False):
        st.markdown(content['explanation'])
        
        st.markdown("### Key Formulas")
        for latex, description in content['formulas']:
            st.latex(latex)
            st.caption(description)
        
        st.markdown("### When to Use")
        st.markdown(content['when_to_use'])
        
        st.markdown("### Complexity")
        st.markdown(content['complexity'])


def show_heuristic_theory() -> None:
    """Display theory section for heuristic search methods (T075).

    Renders the heuristic theory content explaining random exploration,
    deterministic seeding, and probabilistic guarantees.
    """
    content = get_heuristic_theory_content()
    
    with st.expander(f"📚 {content['title']}", expanded=False):
        st.markdown(content['explanation'])
        
        st.markdown("### Key Formulas")
        for latex, description in content['formulas']:
            st.latex(latex)
            st.caption(description)
        
        st.markdown("### When to Use")
        st.markdown(content['when_to_use'])
        
        st.markdown("### Complexity")
        st.markdown(content['complexity'])


def show_enumeration_theory() -> None:
    """Display theory section for topology enumeration and Catalan numbers.

    Renders educational content about how SP topology enumeration works,
    the connection to Catalan numbers, and academic references.
    """
    import pandas as pd
    
    content = get_enumeration_theory_content()
    
    with st.expander(f"🔢 {content['title']}", expanded=False):
        st.markdown(content['explanation'])
        
        st.markdown("### Key Formulas")
        for latex, description in content['formulas']:
            st.latex(latex)
            st.caption(description)
        
        # Catalan sequence display
        st.markdown("### Catalan Number Sequence")
        catalan_str = ", ".join([f"C({n})={c}" for n, c in content['catalan_sequence']])
        st.code(catalan_str, language=None)
        
        # Empirical data table
        st.markdown("### Empirical Topology Counts")
        st.markdown("*Actual counts from exhaustive enumeration in CapAssigner:*")
        df = pd.DataFrame(content['empirical_data'])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Explanation of empirical values
        st.markdown(content['empirical_explanation'])
        
        # Academic references
        st.markdown(content['references'])


def show_method_comparison() -> None:
    """Display method comparison section (T078).

    Renders a comparison table and recommendations for choosing
    between synthesis methods.
    """
    import pandas as pd
    
    content = get_method_comparison_content()
    
    with st.expander(f"🔄 {content['title']}", expanded=False):
        # Display comparison table
        df = pd.DataFrame(content['comparison_table'])
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Display recommendations
        st.markdown(content['recommendations'])
        
        # Display complexity comparison
        st.markdown("### Complexity Comparison")
        st.markdown(content['complexity_comparison'])


def get_sp_vs_graph_limitations_content() -> Dict[str, Any]:
    """Get detailed content explaining SP algorithm limitations and when graph methods are needed.

    Returns:
        Dictionary with comprehensive explanation of SP vs Graph topologies,
        including the classroom 4-capacitor example that cannot be solved by SP enumeration.
    """
    return {
        "title": "⚠️ SP Algorithm Limitations: When Pure SP is Not Enough",
        "introduction": """
**CRITICAL UNDERSTANDING**: Not all capacitor networks can be represented as pure Series-Parallel (SP) topologies!

The SP enumeration algorithm in CapAssigner is designed to generate **binary tree structures**
where each capacitor appears **exactly once** in the tree. This works perfectly for many
practical circuits, but it has a fundamental limitation: **it cannot generate graph topologies
with internal nodes** where the same capacitor value needs to appear multiple times.
""",
        "sp_tree_structure": """
### What is a Series-Parallel Tree?

An SP tree is a **binary tree** where:
- **Leaf nodes**: Individual capacitors (each capacitor index appears once)
- **Internal nodes**: Series (S) or Parallel (P) operations
- **Structure**: Recursive decomposition into smaller sub-networks

**Example SP Tree for 3 capacitors:**
```
      S (Series)
     / \\
    C1  P (Parallel)
       / \\
      C2  C3
```
This represents: C1 in series with (C2 || C3)

**Calculation**: 
- C2 || C3 = C2 + C3
- C1 in series with (C2 + C3) = 1/(1/C1 + 1/(C2+C3))

**Key constraint**: Each capacitor index (C1, C2, C3) appears **exactly once** in the tree.
""",
        "graph_topology_structure": """
### What is a General Graph Topology?

A graph topology allows:
- **Multiple internal nodes**: Not just terminals A and B, but also nodes C, D, E, etc.
- **Capacitor reuse**: The **same capacitor value** can appear on multiple edges
- **Arbitrary connectivity**: Not limited to binary tree decomposition
- **Bridge circuits**: Networks that cannot be simplified to SP form (e.g., Wheatstone bridge)

**Example Graph Topology (Classroom 4-capacitor problem):**
```
Terminal A ----[C2=3pF]---- Node C ----[C2=3pF]---- Node D ----[C2=3pF]---- Terminal B
                              |                        |
                              |                        |
                           [C1=2pF]                 [C4=1pF]
                              |                        |
                              +--------[Bridge]--------+
```

In this topology:
- **C2 (3pF) appears THREE times**: A→C, C→D, D→B (using the same 3pF value repeatedly)
- **Internal nodes C and D** exist between the terminals
- The structure forms a **bridge network** with C1 and C4 connecting across the main path

**Why this works**: The 3pF capacitor value from the original 4-capacitor set {2pF, 3pF, 3pF, 1pF}
is used to create three parallel paths in the network topology, which the graph-based Laplacian
method can model correctly.
""",
        "classroom_example": """
### Case Study: The Classroom 4-Capacitor Problem

**Given capacitors**: C₁=2pF, C₂=3pF, C₃=3pF, C₄=1pF  
**Target**: C_eq = 1.0pF **EXACT**

#### Why SP Enumeration Fails

The SP enumeration algorithm generates **40 distinct topologies** for 4 capacitors.
However, **NONE** of these topologies produce C_eq = 1.0pF.

**Best SP result**: C_eq = 0.923pF (error = 7.69%)

**Why?** The correct topology requires:
1. **Internal nodes** (C and D) between terminals A and B
2. **Reusing the 3pF value** three times in the circuit
3. A **bridge configuration** that cannot be decomposed into pure series/parallel

#### The Correct Graph Topology

The textbook solution uses this topology:
```
A ----[3pF]---- C ----[2pF || 1pF]---- D ----[3pF]---- B
                 \\                      /
                  \\---- [loop] -------/
```

Breaking down the calculation:
1. **Parallel combination at C-D**: 2pF || 1pF = (2×1)/(2+1) = 0.667pF
2. **Effective path A→C→D→B**: 3pF in series with 0.667pF in series with 3pF
3. **Using Laplacian nodal analysis** with the explicit graph structure: C_eq = **1.0pF EXACT**

This topology **cannot be represented as an SP tree** because:
- The 3pF value appears twice (A→C and D→B edges)
- Internal nodes C and D are required
- The parallel combination 2pF||1pF is embedded within a larger series chain

#### Verification

**SP Enumeration Result**: 40 topologies generated, C_eq range = [0.462pF, 9.0pF], NO solution = 1.0pF  
**Graph Laplacian Result**: Given explicit topology, C_eq = 1.0pF ✅

**Conclusion**: The classroom problem is **not an SP enumeration bug** — it's a fundamental
limitation of the SP algorithm design. The correct solution requires graph topology with
internal nodes.
""",
        "when_sp_fails": """
### When Does SP Enumeration Fail?

SP enumeration **cannot find exact solutions** for:

1. **Bridge Circuits** (Wheatstone bridge configurations)
   - Example: Diamond-shaped 4-capacitor network with cross-connection

2. **Topologies requiring internal nodes**
   - When terminals A and B are not directly connected through binary tree operations
   - Networks with junction points beyond A and B

3. **Circuits requiring capacitor value reuse**
   - When the same capacitor value needs to appear on multiple edges
   - The classroom example: 3pF used three times in the topology

4. **Delta (Δ) or Wye (Y) configurations**
   - Three-terminal networks that don't reduce to SP form
   - Require delta-wye transformation or nodal analysis

5. **Mesh networks**
   - Multiple closed loops that cannot be broken down into series/parallel
""",
        "solution_strategy": """
### Recommended Solution Strategy

When SP enumeration doesn't find an acceptable solution:

#### Step 1: Verify if SP solution exists
- Check if your target circuit has bridge structures
- Look for internal nodes in the desired topology
- Determine if capacitor values need to be reused

#### Step 2: Use Graph-Based Methods
If your problem requires non-SP topology:

**Option A: Explicit Topology Specification**
- Use the `calculate_graph_ceq()` function directly
- Manually specify the graph structure with NetworkX
- Define nodes and edges with capacitor values
- Get exact C_eq using Laplacian nodal analysis

**Option B: Heuristic Graph Search**
- Use `find_best_heuristic_solutions()` to randomly generate graph topologies
- Set high iteration count (10,000+) for thorough exploration
- The algorithm will generate graphs with internal nodes and arbitrary connectivity
- Trade guaranteed optimality for ability to explore non-SP space

#### Step 3: Interpret Results
- **SP result with error < 1%**: Acceptable approximation using standard SP topology
- **SP result with error > 5%**: Strong indicator that non-SP topology needed
- **Graph/heuristic finds exact solution**: Confirms non-SP requirement

#### Example: Solving the Classroom Problem

```python
import networkx as nx
from capassigner.core.graphs import calculate_graph_ceq

# Define the graph topology with internal nodes
G = nx.Graph()
G.add_edge('A', 'C', capacitance=3e-12)  # 3pF from A to C
G.add_edge('C', 'D', capacitance=3e-12)  # 3pF from C to D (reusing 3pF value)
G.add_edge('D', 'B', capacitance=3e-12)  # 3pF from D to B (reusing again)
G.add_edge('C', 'D', capacitance=0.667e-12)  # Parallel 2pF||1pF = 0.667pF

# Calculate equivalent capacitance
ceq, warning = calculate_graph_ceq(G, terminal_a='A', terminal_b='B')
print(f"C_eq = {ceq*1e12:.3f} pF")  # Output: C_eq = 1.000 pF
```
""",
        "algorithm_flowchart": """
### Decision Flowchart: Which Algorithm to Use?

```
START: Need to find C_eq for capacitor network
  |
  ├─ Do you have a specific topology in mind?
  |    |
  |    ├─ YES → Does it have internal nodes or bridges?
  |    |         |
  |    |         ├─ YES → Use calculate_graph_ceq() with explicit topology
  |    |         └─ NO  → Use SP enumeration (will find it quickly)
  |    |
  |    └─ NO  → Need to search for topology
  |              |
  |              ├─ N ≤ 8 capacitors?
  |              |    |
  |              |    ├─ YES → Try SP enumeration first
  |              |    |         |
  |              |    |         ├─ Result error < 1%? → DONE (use SP result)
  |              |    |         └─ Result error > 5%? → Try heuristic search
  |              |    |
  |              |    └─ NO  → N > 8, use heuristic search
  |              |
  |              └─ Heuristic Search Configuration:
  |                   - iterations: 10,000+ for thorough exploration
  |                   - internal_nodes: 0-3 (allows graph topologies)
  |                   - seed: set for reproducibility
```
""",
        "key_takeaways": """
### Key Takeaways

1. **SP enumeration is NOT broken** — it works exactly as designed for SP tree topologies

2. **Not all circuits are SP topologies** — bridge circuits and networks with internal nodes
   require graph-based methods

3. **High error (>5%) is a red flag** — indicates your problem may require non-SP topology

4. **Graph methods are more general** — they can handle ANY topology, including SP,
   but are slower for enumeration (use for evaluation only)

5. **Heuristic search explores both** — generates random graphs including non-SP topologies,
   good for discovering unexpected solutions

6. **Classroom example is pedagogically important** — demonstrates the difference between
   SP trees and general graph topologies in circuit design

7. **Tool selection matters** — using the wrong algorithm for your problem type wastes time
   or produces suboptimal results
"""
    }


def show_sp_vs_graph_limitations() -> None:
    """Display comprehensive explanation of SP algorithm limitations (NEW).

    Renders detailed educational content explaining:
    - Difference between SP trees and general graph topologies
    - Why SP enumeration cannot solve certain problems (e.g., classroom example)
    - When to use graph-based methods instead
    - Decision flowchart for algorithm selection
    - Worked example with the classroom 4-capacitor problem
    """
    content = get_sp_vs_graph_limitations_content()
    
    with st.expander(f"{content['title']}", expanded=False):
        st.markdown(content['introduction'])
        
        st.markdown(content['sp_tree_structure'])
        
        st.markdown(content['graph_topology_structure'])
        
        st.markdown("---")
        st.markdown(content['classroom_example'])
        
        st.markdown("---")
        st.markdown(content['when_sp_fails'])
        
        st.markdown("---")
        st.markdown(content['solution_strategy'])
        
        st.markdown("---")
        st.markdown(content['algorithm_flowchart'])
        
        st.markdown("---")
        st.info(content['key_takeaways'])


def show_all_theory_sections() -> None:
    """Display all theory sections before method selection (T075).

    This function should be called in pages.py to render all
    educational content expanders.
    """
    st.markdown("### 📖 Theory & Background")
    st.caption("Expand sections below to learn about each synthesis method.")
    
    # Show comprehensive SP limitations first (most important for users)
    show_sp_vs_graph_limitations()
    
    # Then show individual method theories
    show_sp_theory()
    show_sp_graph_theory()
    show_graph_theory()
    show_heuristic_theory()
    show_enumeration_theory()
    show_method_comparison()


def show_formula(formula: str, description: str) -> None:
    """Display a formula with LaTeX rendering and description (T076).

    Args:
        formula: LaTeX formula string (without $$ delimiters).
        description: Plain text description of the formula.
    """
    st.latex(formula)
    st.caption(description)
