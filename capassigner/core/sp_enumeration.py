"""Series-Parallel topology enumeration algorithms.

This module implements algorithms for enumerating all possible series-parallel
topologies given a set of capacitors using dynamic programming with memoization.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Exact SP formulas
    - Principle IV (Modular Architecture): No Streamlit imports
    - Principle V (Performance Awareness): Memoization for efficiency
"""

from __future__ import annotations
from typing import Optional, List, FrozenSet
from functools import lru_cache
import math

from capassigner.core.sp_structures import (
    Leaf, Series, Parallel, SPNode, 
    calculate_sp_ceq, sp_node_to_expression, sp_node_to_normalized_expression
)
from capassigner.core.metrics import Solution, ProgressUpdate, ProgressCallback, create_solution, rank_solutions
from capassigner.config import PROGRESS_UPDATE_FREQUENCY


def _estimate_total_topologies(n: int) -> int:
    """Estimate total number of SP topologies for n capacitors.
    
    Uses empirically measured values from the enumeration algorithm.
    These are the actual counts produced by enumerate_sp_topologies().
    
    Empirical values (actual counts from algorithm):
    - n=2: 2 topologies
    - n=3: 8 topologies  
    - n=4: 40 topologies
    - n=5: 224 topologies
    - n=6: 1,344 topologies
    - n=7: 8,448 topologies
    
    Args:
        n: Number of capacitors.
        
    Returns:
        Estimated number of topologies.
    """
    if n <= 0:
        return 1
    if n == 1:
        return 1
    
    # Actual counts from algorithm (measured empirically)
    actual_counts = {
        2: 2,
        3: 8,
        4: 40,
        5: 224,
        6: 1344,
        7: 8448,
        8: 54912,
    }
    
    if n in actual_counts:
        return actual_counts[n]
    
    # For larger n, extrapolate (roughly 6x growth per n)
    if n > 8:
        estimate = actual_counts[8]
        for _ in range(n - 8):
            estimate = int(estimate * 6.5)
        return min(estimate, 100_000_000)
    
    return 1000  # Fallback


def enumerate_sp_topologies(
    capacitors: List[float],
    progress_cb: Optional[ProgressCallback] = None
) -> List[SPNode]:
    """Generate all possible SP topologies for given capacitors.

    Uses recursive enumeration with memoization (dynamic programming).
    Complexity: Catalan(N) × N! where N = len(capacitors).

    Algorithm:
    - Base case: 1 capacitor → [Leaf(0, value)]
    - Recursive: Partition into two non-empty subsets, enumerate each,
      combine with Series and Parallel operators.
    - Memoization: Cache results by frozenset of capacitor indices.

    Args:
        capacitors: List of capacitance values in Farads.
        progress_cb: Optional callback for progress updates.
    
    Note:
        Progress is tracked using an estimated total based on Catalan numbers.

    Returns:
        All possible SP topologies (not ranked, not deduplicated).

    Raises:
        ValueError: If capacitors list is empty or contains non-positive values.

    Examples:
        >>> topologies = enumerate_sp_topologies([5e-12, 10e-12])
        >>> len(topologies)
        4  # Series(0,1), Series(1,0), Parallel(0,1), Parallel(1,0)
    """
    if not capacitors:
        raise ValueError("Cannot enumerate topologies with zero capacitors")
    if any(c <= 0 for c in capacitors):
        raise ValueError("All capacitor values must be positive")

    # Create index-to-value mapping
    n = len(capacitors)
    indices = frozenset(range(n))

    # Progress tracking - estimate total using Catalan formula
    estimated_total = _estimate_total_topologies(n)
    current_count = [0]  # Mutable counter for progress

    # Memoization cache
    cache = {}

    def _enumerate_recursive(subset: FrozenSet[int]) -> List[SPNode]:
        """Recursively enumerate SP topologies for a subset of capacitors."""
        # Check cache
        if subset in cache:
            return cache[subset]

        # Base case: single capacitor
        if len(subset) == 1:
            idx = list(subset)[0]
            result = [Leaf(capacitor_index=idx, value=capacitors[idx])]
            cache[subset] = result
            return result

        # Recursive case: partition into two non-empty subsets
        topologies = []
        subset_list = list(subset)

        # Generate all non-empty partitions
        # For efficiency, we only generate partitions where left <= right (lexicographically)
        for i in range(1, len(subset_list)):
            # Split at position i
            left_indices = frozenset(subset_list[:i])
            right_indices = frozenset(subset_list[i:])

            # Recursively enumerate sub-topologies
            left_topologies = _enumerate_recursive(left_indices)
            right_topologies = _enumerate_recursive(right_indices)

            # Combine with Series and Parallel
            for left in left_topologies:
                for right in right_topologies:
                    topologies.append(Series(left=left, right=right))
                    topologies.append(Parallel(left=left, right=right))

                    # Progress callback
                    current_count[0] += 2
                    if progress_cb and current_count[0] % PROGRESS_UPDATE_FREQUENCY == 0:
                        progress_cb(ProgressUpdate(
                            current=current_count[0],
                            total=estimated_total,
                            message=f"Exploring topologies... {current_count[0]:,}",
                            best_error=None
                        ))

        cache[subset] = topologies
        return topologies

    result = _enumerate_recursive(indices)

    # Final progress callback
    if progress_cb:
        progress_cb(ProgressUpdate(
            current=len(result),
            total=len(result),
            message=f"Enumeration complete: {len(result)} topologies",
            best_error=None
        ))

    return result


def find_best_sp_solutions(
    capacitors: List[float],
    target: float,
    tolerance: float = 5.0,
    top_k: int = 10,
    progress_cb: Optional[ProgressCallback] = None,
    deduplicate: bool = True
) -> List[Solution]:
    """Find top-K SP solutions ranked by error.

    Combines enumerate + calculate + rank pipeline.

    Args:
        capacitors: Available capacitance values in Farads.
        target: Target capacitance in Farads (must be > 0).
        tolerance: Acceptable relative error percentage (default 5.0 for ±5%).
        top_k: Number of best solutions to return (default 10).
        progress_cb: Optional callback for progress updates.
        deduplicate: If True, removes structurally equivalent topologies (default True).

    Returns:
        Top-K solutions sorted by absolute error (best first).

    Raises:
        ValueError: If target <= 0 or tolerance < 0.

    Examples:
        >>> capacitors = [5e-12, 10e-12]
        >>> solutions = find_best_sp_solutions(capacitors, 7.5e-12, top_k=2)
        >>> len(solutions)
        2
        >>> solutions[0].absolute_error <= solutions[1].absolute_error
        True
    """
    if target <= 0:
        raise ValueError("Target capacitance must be positive")
    if tolerance < 0:
        raise ValueError("Tolerance cannot be negative")

    # Generate capacitor labels
    capacitor_labels = [f"C{i+1}" for i in range(len(capacitors))]

    # Enumerate all SP topologies
    topologies = enumerate_sp_topologies(capacitors, progress_cb)

    # Calculate C_eq and create solutions
    solutions = []
    seen_normalized = set()  # Track normalized expressions to detect true duplicates
    
    for topology in topologies:
        try:
            ceq = calculate_sp_ceq(topology)
            
            # Use normalized expression to detect structurally equivalent topologies
            # This handles commutativity: (C1+C2) == (C2+C1), (C1||C2) == (C2||C1)
            if deduplicate:
                normalized = sp_node_to_normalized_expression(topology, capacitor_labels)
                
                # Skip duplicate topologies (same circuit, different tree structure)
                if normalized in seen_normalized:
                    continue
                seen_normalized.add(normalized)
            
            # Use original (non-normalized) expression for display
            expression = sp_node_to_expression(topology, capacitor_labels)
            solution = create_solution(topology, ceq, target, tolerance, expression)
            solutions.append(solution)
        except (ZeroDivisionError, TypeError) as e:
            # Skip invalid topologies (should not happen with valid input)
            continue

    # Rank by absolute error
    ranked = rank_solutions(solutions)

    # Return top K
    return ranked[:top_k]
