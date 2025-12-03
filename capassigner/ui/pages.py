"""Main UI pages and layouts.

This module contains the primary Streamlit UI components for rendering
the main application pages, including input widgets, method selection,
and results display.

Constitutional Compliance:
    - Principle II (UX First): Clear, responsive UI with progress feedback
    - Principle III (Robust Input): Comprehensive input validation
    - Principle IV (Modular Architecture): UI logic separate from core
"""

from __future__ import annotations
import streamlit as st
from typing import List, Optional
import pandas as pd


def _rerun() -> None:
    """Compatible rerun for different Streamlit versions.
    
    st.rerun() was introduced in Streamlit 1.27.0.
    Earlier versions use st.experimental_rerun().
    """
    if hasattr(st, 'rerun'):
        st.rerun()
    else:
        st.experimental_rerun()


from capassigner.config import (
    DEFAULT_TOLERANCE,
    MAX_SP_EXHAUSTIVE_N,
    DEFAULT_HEURISTIC_ITERS,
    DEFAULT_MAX_INTERNAL_NODES,
    E12_SERIES,
    E24_SERIES,
    E48_SERIES,
    E96_SERIES,
)
from capassigner.core.sp_enumeration import find_best_sp_solutions
from capassigner.core.heuristics import heuristic_search
from capassigner.core.metrics import ProgressUpdate, Solution
from capassigner.core.parsing import parse_capacitance, format_capacitance
from capassigner.core.graphs import GraphTopology
from capassigner.ui.plots import render_sp_circuit, render_graph_network, generate_latex_code
from capassigner.ui.theory import (
    show_all_theory_sections,
    show_sp_theory,
    show_graph_theory,
    show_heuristic_theory,
    show_method_comparison,
    get_sp_theory_content,
    get_laplacian_theory_content,
    get_heuristic_theory_content,
    get_method_comparison_content,
)
from capassigner.ui.tooltips import (
    TOOLTIP_CAP_TARGET,
    TOOLTIP_CAP_LIST,
    TOOLTIP_TOLERANCE,
    TOOLTIP_METHOD_SP_EXHAUSTIVE,
    TOOLTIP_METHOD_HEURISTIC,
    TOOLTIP_HEURISTIC_ITERS,
    TOOLTIP_HEURISTIC_INTERNAL,
    TOOLTIP_SEED,
)

# E-Series descriptions for the UI
E_SERIES_DESCRIPTIONS = {
    "E12": """**E12 Series** (±10% tolerance)
    
The E12 series contains **12 values per decade** and is used for components with 
±10% tolerance. These are the most common and affordable capacitor values.

Values per decade: 1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2

**Use case**: General-purpose circuits where precision is not critical.""",

    "E24": """**E24 Series** (±5% tolerance)

The E24 series contains **24 values per decade** and is used for ±5% tolerance 
components. Provides better resolution than E12 while still being widely available.

Values per decade: 1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 
3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1

**Use case**: Audio, signal processing, and general analog circuits.""",

    "E48": """**E48 Series** (±2% tolerance)

The E48 series contains **48 values per decade** and is used for precision ±2% 
tolerance components. Less commonly stocked but provides finer value selection.

**Use case**: Precision analog circuits, active filters, instrumentation.""",

    "E96": """**E96 Series** (±1% tolerance)

The E96 series contains **96 values per decade** and is used for high-precision 
±1% tolerance components. Provides the finest resolution for precision applications.

**Use case**: Precision instrumentation, measurement equipment, calibration circuits."""
}


def _initialize_session_state() -> None:
    """Initialize session state with default values (T090, T095, T098).

    Sets up default values for:
    - solutions: List of found solutions (None initially)
    - computing: Whether computation is in progress
    - last_method: Last used synthesis method
    - last_tolerance: Last used tolerance value
    - capacitors_text: Text content of capacitor inventory
    - current_page: Current navigation page
    - capacitor_rows: List of individual capacitor input rows
    """
    defaults = {
        'solutions': None,
        'computing': False,
        'last_method': "SP Exhaustive",
        'last_tolerance': DEFAULT_TOLERANCE,
        'capacitors_text': "1pF\n2pF\n5pF",
        'current_page': "🔬 Calculator",
        'capacitor_rows': ["1pF", "2pF", "5pF"],
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def render_placeholder_page() -> None:
    """Render placeholder welcome page for the application.

    Displays a simple welcome message to verify Streamlit is working
    correctly. This will be replaced with the full UI in future features.
    """
    st.title("Welcome to CapAssigner - Capacitor Network Synthesis")
    st.write("""
    This is a placeholder page to verify the application scaffolding.

    CapAssigner helps you design capacitor networks by finding optimal
    topologies that match your target capacitance.

    Future features will include:
    - Capacitor list editor
    - Method selection (SP exhaustive, heuristics, etc.)
    - Results visualization with SchemDraw and NetworkX
    - Theory sections with educational content
    """)
    st.info("🚧 Application under development - full features coming soon!")


def render_main_page() -> None:
    """Render the main application page with navigation menu.

    Provides a sidebar menu to navigate between:
    - Calculator: Main capacitor network synthesis tool
    - Theory: Educational content about synthesis methods
    """
    # Initialize session state
    _initialize_session_state()

    # Sidebar navigation menu
    with st.sidebar:
        st.title("🔌 CapAssigner")
        st.markdown("---")
        
        # Navigation menu
        page = st.radio(
            "Navigation",
            ["🔬 Calculator", "📚 Theory"],
            index=0 if st.session_state.current_page == "🔬 Calculator" else 1,
            key="nav_radio"
        )
        st.session_state.current_page = page
        
        st.markdown("---")

    # Render the selected page
    if page == "🔬 Calculator":
        _render_calculator_page()
    else:
        _render_theory_page()


def _render_theory_page() -> None:
    """Render the dedicated theory page with all educational content."""
    st.title("📚 Capacitor Network Theory")
    st.write("Learn about the different methods for synthesizing capacitor networks.")
    
    st.markdown("---")
    
    # Introduction
    st.header("Introduction")
    st.markdown("""
    CapAssigner uses advanced algorithms to find optimal capacitor network topologies
    that match a target capacitance. Understanding the underlying theory helps you
    choose the right method and interpret the results.
    
    **Key concepts covered:**
    - Series-Parallel (SP) network theory
    - Laplacian nodal analysis for arbitrary graphs
    - Heuristic search strategies
    - Method selection guidelines
    """)
    
    st.markdown("---")
    
    # SP Theory Section
    st.header("1. Series-Parallel Networks")
    content = get_sp_theory_content()
    st.markdown(content['explanation'])
    
    st.subheader("Key Formulas")
    for latex, description in content['formulas']:
        st.latex(latex)
        st.caption(description)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("When to Use")
        st.markdown(content['when_to_use'])
    with col2:
        st.subheader("Complexity")
        st.markdown(content['complexity'])
    
    st.markdown("---")
    
    # Laplacian Theory Section
    st.header("2. Laplacian Nodal Analysis")
    content = get_laplacian_theory_content()
    st.markdown(content['explanation'])
    
    st.subheader("Key Formulas")
    for latex, description in content['formulas']:
        st.latex(latex)
        st.caption(description)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("When to Use")
        st.markdown(content['when_to_use'])
    with col2:
        st.subheader("Complexity")
        st.markdown(content['complexity'])
    
    st.markdown("---")
    
    # Heuristic Theory Section
    st.header("3. Heuristic Graph Search")
    content = get_heuristic_theory_content()
    st.markdown(content['explanation'])
    
    st.subheader("Key Formulas")
    for latex, description in content['formulas']:
        st.latex(latex)
        st.caption(description)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("When to Use")
        st.markdown(content['when_to_use'])
    with col2:
        st.subheader("Complexity")
        st.markdown(content['complexity'])
    
    st.markdown("---")
    
    # Method Comparison Section
    st.header("4. Method Comparison")
    content = get_method_comparison_content()
    
    # Display comparison table
    df = pd.DataFrame(content['comparison_table'])
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Display recommendations
    st.subheader("Choosing the Right Method")
    st.markdown(content['recommendations'])
    
    # Display complexity comparison
    st.subheader("Complexity Comparison")
    st.markdown(content['complexity_comparison'])


def _render_calculator_page() -> None:
    """Render the calculator page with full capacitor network synthesis functionality.

    Provides UI for:
    - Target capacitance input
    - Capacitor inventory management
    - Method selection (SP Exhaustive, Heuristic Graph Search)
    - Results display with circuit diagrams
    - Progress tracking for long computations
    """
    st.title("🔬 Capacitor Network Calculator")
    st.write("Find optimal capacitor network topologies to match your target capacitance.")

    # Sidebar: Input parameters
    with st.sidebar:
        st.header("Input Parameters")

        # Target capacitance input (T051: use tooltip)
        target_input = st.text_input(
            "Target Capacitance",
            value="3.1pF",
            help=TOOLTIP_CAP_TARGET,
            key="target_input_field"
        )

        # Tolerance input (T079: use tooltip)
        tolerance = st.number_input(
            "Tolerance (%)",
            min_value=0.0,
            max_value=100.0,
            value=DEFAULT_TOLERANCE,
            step=0.1,
            help=TOOLTIP_TOLERANCE,
            key="tolerance_input"
        )

        # Capacitor inventory (T091-T097)
        st.subheader("Capacitor Inventory")
        
        # E-series info expander
        with st.expander("ℹ️ About E-Series", expanded=False):
            st.markdown("""
The **E-series** are internationally standardized sets of preferred 
capacitor/resistor values. Each series provides a specific number of 
values per decade (10× range), spaced for optimal coverage within the 
tolerance grade:
            """)
            for series_name, description in E_SERIES_DESCRIPTIONS.items():
                st.markdown(description)
                st.markdown("---")

        # E-series preset buttons (T094)
        st.caption("Load preset E-series values:")
        preset_cols = st.columns(4)
        with preset_cols[0]:
            if st.button("E12", key="load_e12", help="Load E12 series (±10% tolerance, 12 values/decade)"):
                st.session_state.capacitor_rows = [f"{v*10}pF" for v in E12_SERIES]
                st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
                _rerun()
        with preset_cols[1]:
            if st.button("E24", key="load_e24", help="Load E24 series (±5% tolerance, 24 values/decade)"):
                st.session_state.capacitor_rows = [f"{v*10}pF" for v in E24_SERIES]
                st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
                _rerun()
        with preset_cols[2]:
            if st.button("E48", key="load_e48", help="Load E48 series (±2% tolerance, 48 values/decade)"):
                st.session_state.capacitor_rows = [f"{v*10:.1f}pF" for v in E48_SERIES]
                st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
                _rerun()
        with preset_cols[3]:
            if st.button("E96", key="load_e96", help="Load E96 series (±1% tolerance, 96 values/decade)"):
                st.session_state.capacitor_rows = [f"{v*10:.2f}pF" for v in E96_SERIES]
                st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
                _rerun()

        # Display individual capacitor input rows
        st.caption("Enter capacitor values (one per row):")
        
        # Render each capacitor row with a remove button
        rows_to_remove = []
        new_rows = []
        
        for i, row_value in enumerate(st.session_state.capacitor_rows):
            col1, col2 = st.columns([4, 1])
            with col1:
                new_value = st.text_input(
                    f"C{i+1}",
                    value=row_value,
                    key=f"cap_row_{i}",
                    label_visibility="collapsed"
                )
                new_rows.append(new_value)
            with col2:
                if st.button("❌", key=f"remove_row_{i}", help="Remove this capacitor"):
                    rows_to_remove.append(i)
        
        # Apply row updates
        st.session_state.capacitor_rows = new_rows
        
        # Remove marked rows
        if rows_to_remove:
            st.session_state.capacitor_rows = [
                r for i, r in enumerate(st.session_state.capacitor_rows) 
                if i not in rows_to_remove
            ]
            st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
            _rerun()

        # Add/Clear buttons (T092, T093)
        add_clear_cols = st.columns(2)
        with add_clear_cols[0]:
            if st.button("➕ Add Row", key="add_row", use_container_width=True):
                st.session_state.capacitor_rows.append("")
                st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)
                _rerun()
        with add_clear_cols[1]:
            if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
                st.session_state.capacitor_rows = []
                st.session_state.capacitors_text = ""
                _rerun()

        # Update capacitors_text from rows for parsing
        st.session_state.capacitors_text = "\n".join(st.session_state.capacitor_rows)

        st.markdown("---")

        # Method selection (T066)
        st.subheader("Method Selection")
        method = st.selectbox(
            "Synthesis Method",
            ["SP Exhaustive", "Heuristic Graph Search"],
            help=f"{TOOLTIP_METHOD_SP_EXHAUSTIVE}\n\n{TOOLTIP_METHOD_HEURISTIC}",
            key="method_select"
        )

        # Heuristic parameters (T067) - only show when Heuristic Graph Search selected
        if method == "Heuristic Graph Search":
            st.subheader("Heuristic Parameters")

            heuristic_iterations = st.number_input(
                "Iterations",
                min_value=100,
                max_value=10000,
                value=DEFAULT_HEURISTIC_ITERS,
                step=100,
                help=TOOLTIP_HEURISTIC_ITERS,
                key="heuristic_iterations"
            )

            max_internal_nodes = st.number_input(
                "Max Internal Nodes",
                min_value=0,
                max_value=5,
                value=DEFAULT_MAX_INTERNAL_NODES,
                step=1,
                help=TOOLTIP_HEURISTIC_INTERNAL,
                key="max_internal_nodes"
            )

            heuristic_seed = st.number_input(
                "Random Seed",
                min_value=0,
                max_value=999999,
                value=0,
                step=1,
                help=TOOLTIP_SEED,
                key="heuristic_seed"
            )
        else:
            # Default values when not using heuristic
            heuristic_iterations = DEFAULT_HEURISTIC_ITERS
            max_internal_nodes = DEFAULT_MAX_INTERNAL_NODES
            heuristic_seed = 0

        # Number of solutions to display
        top_k = st.number_input(
            "Solutions to Display",
            min_value=1,
            max_value=100,
            value=10,
            step=1,
            help="Number of best solutions to show",
            key="top_k_input"
        )

        # Find Solutions button
        find_button = st.button("🔍 Find Solutions", type="primary", use_container_width=True)

    # Main content area
    if find_button:
        # Parse inputs from the rows
        capacitors_input = st.session_state.capacitors_text
        target_value, capacitor_values = _parse_inputs(target_input, capacitors_input)

        if target_value is None or capacitor_values is None:
            st.error("Please correct input errors before proceeding.")
        else:
            n_caps = len(capacitor_values)
            
            # Show statistics panel before computation
            st.markdown("---")
            st.subheader("📊 Search Statistics")
            
            stats_cols = st.columns(3)
            with stats_cols[0]:
                st.metric("Capacitors", n_caps)
            with stats_cols[1]:
                if method == "SP Exhaustive":
                    # Calculate number of SP topologies: Catalan(n-1) * n!
                    from math import factorial
                    def catalan(n):
                        if n <= 1:
                            return 1
                        return factorial(2*n) // (factorial(n+1) * factorial(n))
                    
                    total_topologies = catalan(n_caps - 1) * factorial(n_caps) if n_caps > 0 else 0
                    st.metric("Total SP Topologies", f"{total_topologies:,}")
                else:
                    st.metric("Iterations", f"{heuristic_iterations:,}")
            with stats_cols[2]:
                # Calculate theoretical range
                min_cap = min(capacitor_values) if capacitor_values else 0
                max_cap = sum(capacitor_values) if capacitor_values else 0
                min_series = min_cap / n_caps if n_caps > 0 else 0
                st.metric(
                    "Achievable Range", 
                    f"{format_capacitance(min_series)} - {format_capacitance(max_cap)}"
                )
            
            # Check if target is achievable
            if target_value < min_series * 0.5 or target_value > max_cap * 1.5:
                st.warning(
                    f"⚠️ Target {format_capacitance(target_value)} may be difficult to achieve. "
                    f"Theoretical range with your capacitors: {format_capacitance(min_series)} to {format_capacitance(max_cap)}. "
                    f"Consider adding capacitors closer to the target value."
                )

            # Check for N > MAX_SP_EXHAUSTIVE_N warning (T031)
            if method == "SP Exhaustive" and n_caps > MAX_SP_EXHAUSTIVE_N:
                st.warning(
                    f"⚠️ You have {n_caps} capacitors. "
                    f"SP Exhaustive may be slow for N > {MAX_SP_EXHAUSTIVE_N}. "
                    f"Consider using Heuristic Graph Search for better performance."
                )

            st.markdown("---")
            
            # Create progress container in main area
            progress_container = st.container()
            with progress_container:
                st.subheader("🔄 Computing...")
                progress_bar = st.progress(0)
                progress_text = st.empty()
                stats_row = st.columns(3)
                with stats_row[0]:
                    current_metric = st.empty()
                with stats_row[1]:
                    best_error_metric = st.empty()
                with stats_row[2]:
                    within_tol_metric = st.empty()

            # Initialize counters for progress
            progress_data = {'within_tolerance_count': 0, 'best_error': float('inf')}

            # Define progress callback (T028)
            def on_progress(update: ProgressUpdate) -> None:
                """Update progress bar and status text."""
                progress = update.current / update.total if update.total > 0 else 0
                # Clamp progress to [0.0, 1.0] range to avoid Streamlit errors
                progress = max(0.0, min(1.0, progress))
                progress_bar.progress(progress)
                progress_text.markdown(f"**{update.message}**")
                current_metric.metric("Topologies Explored", f"{update.current:,}")
                
                if update.best_error is not None:
                    progress_data['best_error'] = min(progress_data['best_error'], update.best_error)
                    best_error_metric.metric("Best Error", format_capacitance(progress_data['best_error']))

            # Run computation (T068)
            try:
                if method == "SP Exhaustive":
                    solutions = find_best_sp_solutions(
                        capacitors=capacitor_values,
                        target=target_value,
                        tolerance=tolerance,
                        top_k=top_k,
                        progress_cb=on_progress
                    )
                else:  # Heuristic Graph Search
                    solutions = heuristic_search(
                        capacitors=capacitor_values,
                        target=target_value,
                        iterations=heuristic_iterations,
                        max_internal_nodes=max_internal_nodes,
                        seed=heuristic_seed,
                        tolerance=tolerance,
                        top_k=top_k,
                        progress_cb=on_progress
                    )

                st.session_state.solutions = solutions
                st.session_state.last_method = method
                st.session_state.last_tolerance = tolerance
                st.session_state.last_target = target_value
                st.session_state.last_n_caps = n_caps

                # Clear progress container
                progress_container.empty()

                # Display success message with statistics
                within_count = len([s for s in solutions if s.within_tolerance])
                
                if len(solutions) == 0:
                    st.error(
                        f"❌ No solutions found. This configuration may not have any valid topologies. "
                        f"Try adding more capacitors or adjusting the target value."
                    )
                elif within_count == 0:
                    st.warning(
                        f"⚠️ Found {len(solutions)} solutions, but **none within ±{tolerance}% tolerance**. "
                        f"Best solution has {solutions[0].relative_error:.2f}% error. "
                        f"Consider increasing tolerance or adding more capacitors."
                    )
                else:
                    st.success(
                        f"✅ Found {len(solutions)} solutions using {method}! "
                        f"**{within_count} within ±{tolerance}% tolerance**"
                    )
                    
                    # Show best solution summary
                    best = solutions[0]
                    st.info(
                        f"🏆 **Best solution**: {best.expression} = {format_capacitance(best.ceq)} "
                        f"(error: {best.relative_error:.3f}%)"
                    )

            except Exception as e:
                progress_container.empty()
                st.error(f"Error during computation: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                st.session_state.solutions = None

    # Display results if available (T029, T030)
    if st.session_state.solutions is not None:
        # Get tolerance from session state or use default
        display_tolerance = st.session_state.get('last_tolerance', DEFAULT_TOLERANCE)
        _display_results(
            st.session_state.solutions,
            st.session_state.last_method,
            display_tolerance
        )


def _parse_inputs(
    target_input: str,
    capacitors_input: str
) -> tuple[Optional[float], Optional[List[float]]]:
    """Parse target and capacitor inputs using robust parsing module.

    Args:
        target_input: Target capacitance string.
        capacitors_input: Capacitor values (newline or comma-separated).

    Returns:
        Tuple of (target_value, capacitor_values) or (None, None) if parsing fails.
    """
    # Parse target using new parsing module (T047)
    target_result = parse_capacitance(target_input)
    if not target_result.success:
        st.error(f"Invalid target capacitance: {target_result.error_message}")
        return None, None

    target_value = target_result.value

    # Parse capacitors
    raw_values = capacitors_input.replace(',', '\n').split('\n')
    capacitor_values = []

    for raw in raw_values:
        raw = raw.strip()
        if not raw:  # Skip empty lines
            continue

        result = parse_capacitance(raw)
        if not result.success:
            st.error(f"Invalid capacitor value '{raw}': {result.error_message}")
            return None, None

        capacitor_values.append(result.value)

    if not capacitor_values:
        st.error("Please enter at least one capacitor value.")
        return None, None

    return target_value, capacitor_values


def _display_results(
    solutions: List[Solution],
    method: str = "SP Exhaustive",
    tolerance: float = 5.0
) -> None:
    """Display results table and circuit diagrams (T029, T030, T068, T085-T087).

    Args:
        solutions: List of Solution objects to display.
        method: The synthesis method used ("SP Exhaustive" or "Heuristic Graph Search").
        tolerance: Tolerance percentage for the "no solutions" message.
    """
    from capassigner.core.metrics import filter_by_tolerance

    st.header("Results")

    if not solutions:
        st.info("No solutions found within tolerance.")
        return

    # Filter toggle (T086)
    show_only_within_tolerance = st.checkbox(
        "Show only within tolerance",
        value=False,
        help="When enabled, only solutions with relative error ≤ tolerance are shown.",
        key="filter_tolerance_toggle"
    )

    # Apply filter if enabled
    if show_only_within_tolerance:
        filtered_solutions = filter_by_tolerance(solutions)
    else:
        filtered_solutions = solutions

    # Handle empty results after filtering (T087)
    if not filtered_solutions:
        within_count = len([s for s in solutions if s.within_tolerance])
        st.warning(
            f"⚠️ No solutions within ±{tolerance}% tolerance.\n\n"
            f"**{len(solutions)}** solutions were found, but none meet the tolerance requirement.\n\n"
            "**Suggestions:**\n"
            "- Increase the tolerance percentage\n"
            "- Add more capacitors to the inventory\n"
            "- Try a different synthesis method\n\n"
            f"Disable the filter above to see all {len(solutions)} solutions."
        )
        return

    # Show filter status (T085, T086)
    within_count = len([s for s in filtered_solutions if s.within_tolerance])
    if show_only_within_tolerance:
        st.caption(f"Showing {len(filtered_solutions)} solutions within tolerance")
    else:
        st.caption(
            f"Showing {len(filtered_solutions)} solutions "
            f"({within_count} within tolerance)"
        )

    # Create results dataframe for table display (T048: use format_capacitance)
    results_data = []
    for i, sol in enumerate(filtered_solutions):
        results_data.append({
            "Rank": i + 1,
            "Topology": sol.expression,
            "C_eq": format_capacitance(sol.ceq),
            "Target": format_capacitance(sol.target),
            "Abs Error": format_capacitance(sol.absolute_error),
            "Rel Error (%)": f"{sol.relative_error:.2f}",
            "Within Tolerance": "✓" if sol.within_tolerance else "✗"
        })

    df = pd.DataFrame(results_data)

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    # Circuit diagram expansion (T030, T068)
    st.subheader("Circuit Diagrams")
    st.write("Click on a solution to view its circuit diagram:")

    # Show diagrams in expandable sections (T048: use format_capacitance)
    for i, sol in enumerate(filtered_solutions):
        with st.expander(f"Solution #{i+1}: {sol.expression} (C_eq = {format_capacitance(sol.ceq)})"):
            try:
                # Check if this is a graph topology or SP topology
                is_graph = sol.is_graph_topology()

                if is_graph:
                    # Render graph network diagram
                    fig = render_graph_network(sol.topology)
                    st.pyplot(fig)
                else:
                    # Render SP circuit diagram
                    capacitor_labels = _extract_capacitor_labels_from_solution(sol)
                    capacitor_values = _extract_capacitor_values_from_solution(sol)
                    fig = render_sp_circuit(sol.topology, capacitor_labels, capacitor_values)
                    st.pyplot(fig)

                # Display metrics (T048: use format_capacitance)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Equivalent Capacitance", format_capacitance(sol.ceq))
                with col2:
                    st.metric("Absolute Error", format_capacitance(sol.absolute_error))
                with col3:
                    st.metric("Relative Error", f"{sol.relative_error:.2f}%")

                # Show additional info for graph topologies
                if is_graph:
                    topology = sol.topology
                    st.info(
                        f"📊 Graph details: {topology.graph.number_of_nodes()} nodes, "
                        f"{topology.graph.number_of_edges()} edges, "
                        f"{len(topology.internal_nodes)} internal nodes"
                    )

                # LaTeX code generation
                st.markdown("---")
                st.markdown("##### 📝 LaTeX Code (CircuiTikZ)")
                show_latex = st.checkbox(
                    "Show LaTeX code", 
                    key=f"latex_toggle_{i}",
                    value=False
                )
                
                if show_latex:
                    try:
                        if is_graph:
                            latex_code = generate_latex_code(sol.topology)
                        else:
                            latex_code = generate_latex_code(
                                sol.topology, 
                                capacitor_labels, 
                                capacitor_values
                            )
                        
                        st.markdown("""
                        **Instructions:** Copy this code into a `.tex` file and compile with `pdflatex`.
                        
                        **Required packages:**
                        - `circuitikz` - Circuit drawing
                        - `siunitx` - SI units formatting
                        """)
                        
                        st.code(latex_code, language="latex")
                        
                        # Download button
                        st.download_button(
                            label="⬇️ Download .tex file",
                            data=latex_code,
                            file_name=f"circuit_solution_{i+1}.tex",
                            mime="text/x-tex"
                        )
                    except Exception as e:
                        st.error(f"Error generating LaTeX: {str(e)}")

            except Exception as e:
                st.error(f"Error rendering circuit diagram: {str(e)}")


def _extract_capacitor_labels_from_solution(sol: Solution) -> List[str]:
    """Extract capacitor labels from solution topology.

    Args:
        sol: Solution object.

    Returns:
        List of capacitor labels (e.g., ["C1", "C2", "C3"]).
    """
    # Extract capacitor indices from topology by walking the tree
    from capassigner.core.sp_structures import Leaf, Series, Parallel

    indices = set()

    def walk(node):
        if isinstance(node, Leaf):
            indices.add(node.capacitor_index)
        elif isinstance(node, (Series, Parallel)):
            walk(node.left)
            walk(node.right)

    walk(sol.topology)

    # Generate labels for all indices
    max_index = max(indices) if indices else 0
    return [f"C{i+1}" for i in range(max_index + 1)]


def _extract_capacitor_values_from_solution(sol: Solution) -> List[float]:
    """Extract capacitor values from solution topology.

    Args:
        sol: Solution object.

    Returns:
        List of capacitor values in Farads.
    """
    from capassigner.core.sp_structures import Leaf, Series, Parallel

    values_dict = {}

    def walk(node):
        if isinstance(node, Leaf):
            values_dict[node.capacitor_index] = node.value
        elif isinstance(node, (Series, Parallel)):
            walk(node.left)
            walk(node.right)

    walk(sol.topology)

    # Return values in index order
    max_index = max(values_dict.keys()) if values_dict else 0
    return [values_dict.get(i, 0.0) for i in range(max_index + 1)]
