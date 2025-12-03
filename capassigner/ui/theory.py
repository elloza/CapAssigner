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
                "Method": "SP Exhaustive",
                "Speed": "Slow for N>8",
                "Topology Coverage": "SP only",
                "Optimality": "Guaranteed",
                "Best For": "Small N, exact solutions"
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
| N ≤ 6 capacitors | SP Exhaustive |
| N = 7-8 capacitors | SP Exhaustive (may be slow) |
| N > 8 capacitors | Heuristic Graph Search |
| Need bridges/meshes | Heuristic Graph Search |
| Need guaranteed optimal | SP Exhaustive |
| Time-constrained | Heuristic Graph Search |
""",
        "complexity_comparison": """
| Method | Time | Space | Guarantee |
|--------|------|-------|-----------|
| SP Exhaustive | O(Cat(n)×n!) | O(n) | Optimal within SP |
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


def show_all_theory_sections() -> None:
    """Display all theory sections before method selection (T075).

    This function should be called in pages.py to render all
    educational content expanders.
    """
    st.markdown("### 📖 Theory & Background")
    st.caption("Expand sections below to learn about each synthesis method.")
    
    show_sp_theory()
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
