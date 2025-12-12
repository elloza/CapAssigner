"""Regression tests for PDF reference exercises.

This module validates the SP Tree exhaustive solver against two reference
exercises from 'Obtener asociación condensadores 2.pdf' (2 pages). These tests
ensure that the solver correctly finds equivalent capacitances for known
reference cases.

Reference Exercises:
- Exercise 01: C1=15µF, C2=3µF, C3=6µF, C4=20µF; target Ceq≈5.96µF
- Exercise 02: C1=2µF, C2=8µF, C3=7µF, C4=4µF; target Ceq≈9.73µF

Tests verify:
1. Explicit topology Ceq calculation (validates mathematical correctness)
   - Manually construct series-parallel topologies
   - Validate that calculate_sp_ceq() produces correct results
   
2. Exhaustive search finds matching solutions (validates search algorithm)
   - Use find_best_sp_solutions() to search all SP topologies
   - Validate that at least one solution matches expected Ceq within tolerance

Test data uses SI units (Farads) exclusively to prevent unit conversion errors.
All capacitor values and expected results are documented with µF equivalents
in inline comments.

Performance: Tests complete within 10 seconds (FR-006, SC-003) for N=4
capacitors per exercise.

Constitutional Compliance:
    - Principle I (Scientific Accuracy): Validate algorithmic correctness
    - Principle IV (Modular Architecture): Test core algorithms independently
    - Principle V (Performance Awareness): Tests complete within 10 seconds
"""

from __future__ import annotations
import pytest
from capassigner.core.sp_enumeration import find_best_sp_solutions
from capassigner.core.sp_structures import (
    Leaf, Series, Parallel, calculate_sp_ceq
)
from tests.unit.test_fixtures import ToleranceLevel


# =============================================================================
# Validation Helper Functions (Phase 5: T018)
# =============================================================================

def validate_reference_exercise(exercise: dict) -> None:
    """Validate reference exercise data integrity (FR-004: SI units).
    
    Checks:
    - All capacitor values are positive
    - All capacitor values are in realistic range (1e-12 F to 1 F)
    - Expected Ceq is positive
    - Number of capacitors matches number of labels
    
    Args:
        exercise: Dictionary containing exercise data
        
    Raises:
        AssertionError: If validation fails
    """
    caps = exercise["capacitors"]
    labels = exercise["labels"]
    expected_ceq = exercise["expected_ceq_F"]
    
    # Validate positive values
    assert all(c > 0 for c in caps), (
        f"{exercise['id']}: All capacitors must be positive"
    )
    
    # Validate realistic range (1 pF to 1 F)
    assert all(1e-12 <= c <= 1.0 for c in caps), (
        f"{exercise['id']}: Capacitors must be in realistic range [1e-12, 1.0] F"
    )
    
    # Validate data integrity
    assert len(caps) == len(labels), (
        f"{exercise['id']}: Number of capacitors ({len(caps)}) must match labels ({len(labels)})"
    )
    
    assert expected_ceq > 0, (
        f"{exercise['id']}: Expected Ceq must be positive"
    )
    
    assert len(caps) > 0, (
        f"{exercise['id']}: Must have at least one capacitor"
    )


# =============================================================================
# Test Data Constants (Phase 1: T002, T003)
# =============================================================================

# Exercise 01: C1=15µF, C2=3µF, C3=6µF, C4=20µF; target Ceq≈5.96µF
EXERCISE_01 = {
    "id": "pdf2p_association_01",
    "title": "C1=15µF, C2=3µF, C3=6µF, C4=20µF; target Ceq≈5.96µF",
    "capacitors": [
        1.5e-05,  # C1 = 15 µF → 1.5e-05 F
        3e-06,    # C2 = 3 µF → 3e-06 F
        6e-06,    # C3 = 6 µF → 6e-06 F
        2e-05     # C4 = 20 µF → 2e-05 F
    ],
    "labels": ["C1", "C2", "C3", "C4"],
    "expected_ceq_F": 5.964912280701754e-06,  # ≈5.96 µF in Farads
    "terminals": {"pos": "a", "neg": "b"}
}

# Exercise 02: C1=2µF, C2=8µF, C3=7µF, C4=4µF; target Ceq≈9.73µF
EXERCISE_02 = {
    "id": "pdf2p_association_02",
    "title": "C1=2µF, C2=8µF, C3=7µF, C4=4µF; target Ceq≈9.73µF",
    "capacitors": [
        2e-06,    # C1 = 2 µF → 2e-06 F
        8e-06,    # C2 = 8 µF → 8e-06 F
        7e-06,    # C3 = 7 µF → 7e-06 F
        4e-06     # C4 = 4 µF → 4e-06 F
    ],
    "labels": ["C1", "C2", "C3", "C4"],
    "expected_ceq_F": 9.733333333333334e-06,  # ≈9.73 µF in Farads
    "terminals": {"pos": "A", "neg": "B"}
}

# Validate exercises at module load time (Phase 5: T019)
validate_reference_exercise(EXERCISE_01)
validate_reference_exercise(EXERCISE_02)


# =============================================================================
# Test Classes (Phase 2: T004, T005 | Phase 6: T020)
# =============================================================================

@pytest.mark.timeout(10)  # FR-006, SC-003: Must complete within 10 seconds
class TestExplicitTopologyValidation:
    """Test Ceq calculation for explicit circuit topologies.
    
    These tests validate that calculate_sp_ceq() produces correct results
    for manually constructed series-parallel topologies, independent of
    the search algorithm.
    """
    
    def test_exercise_01_explicit_topology(self):
        """Validate Ceq calculation for Exercise 01 explicit topology.
        
        Exercise 01: C1=15µF, C2=3µF, C3=6µF, C4=20µF; target Ceq≈5.96µF
        
        Topology determined: C4 in series with (C3 || (C1 in series C2))
        Calculation:
        - C1 in series C2 = 1/(1/15 + 1/3) = 2.5µF
        - C3 || 2.5 = 6 + 2.5 = 8.5µF
        - C4 in series 8.5 = 1/(1/20 + 1/8.5) ≈ 5.965µF
        """
        # Extract capacitor values
        caps = EXERCISE_01["capacitors"]
        
        # Construct topology: C4 in series with (C3 || (C1 in series C2))
        topology = Series(
            left=Leaf(capacitor_index=3, value=caps[3]),  # C4 = 20µF
            right=Parallel(
                left=Leaf(capacitor_index=2, value=caps[2]),  # C3 = 6µF
                right=Series(
                    left=Leaf(capacitor_index=0, value=caps[0]),  # C1 = 15µF
                    right=Leaf(capacitor_index=1, value=caps[1])  # C2 = 3µF
                )
            )
        )
        
        # Calculate equivalent capacitance
        observed_ceq = calculate_sp_ceq(topology)
        expected_ceq = EXERCISE_01["expected_ceq_F"]
        
        # Validate within exact tolerance
        if expected_ceq != 0:
            rel_error = abs((observed_ceq - expected_ceq) / expected_ceq)
        else:
            rel_error = abs(observed_ceq)
        
        assert rel_error < ToleranceLevel.EXACT, (
            f"Exercise 01 explicit topology: "
            f"observed={observed_ceq:.6e} F, expected={expected_ceq:.6e} F, "
            f"rel_error={rel_error:.2e} (topology: C4 in series (C3 || (C1 in series C2)))"
        )
    
    def test_exercise_02_explicit_topology(self):
        """Validate Ceq calculation for Exercise 02 explicit topology.
        
        Exercise 02: C1=2µF, C2=8µF, C3=7µF, C4=4µF; target Ceq≈9.73µF
        
        Topology determined: C1 || C4 || (C2 in series C3)
        Calculation:
        - C2 in series C3 = 1/(1/8 + 1/7) = 3.733µF
        - C1 || C4 || 3.733 = 2 + 4 + 3.733 = 9.733µF
        """
        # Extract capacitor values
        caps = EXERCISE_02["capacitors"]
        
        # Construct topology: C1 || C4 || (C2 in series C3)
        topology = Parallel(
            left=Parallel(
                left=Leaf(capacitor_index=0, value=caps[0]),  # C1 = 2µF
                right=Leaf(capacitor_index=3, value=caps[3])  # C4 = 4µF
            ),
            right=Series(
                left=Leaf(capacitor_index=1, value=caps[1]),  # C2 = 8µF
                right=Leaf(capacitor_index=2, value=caps[2])  # C3 = 7µF
            )
        )
        
        # Calculate equivalent capacitance
        observed_ceq = calculate_sp_ceq(topology)
        expected_ceq = EXERCISE_02["expected_ceq_F"]
        
        # Validate within exact tolerance
        if expected_ceq != 0:
            rel_error = abs((observed_ceq - expected_ceq) / expected_ceq)
        else:
            rel_error = abs(observed_ceq)
        
        assert rel_error < ToleranceLevel.EXACT, (
            f"Exercise 02 explicit topology: "
            f"observed={observed_ceq:.6e} F, expected={expected_ceq:.6e} F, "
            f"rel_error={rel_error:.2e} (topology: C1 || C4 || (C2 in series C3))"
        )


@pytest.mark.timeout(10)  # FR-006, SC-003: Must complete within 10 seconds
class TestExhaustiveSearchValidation:
    """Test that exhaustive search finds matching solutions.
    
    These tests validate that find_best_sp_solutions() can find topologies
    whose equivalent capacitance matches the expected value for reference
    exercises with known correct results.
    """
    
    def test_exercise_01_exhaustive_search(self):
        """Validate exhaustive search finds solution for Exercise 01.
        
        Exercise 01: C1=15µF, C2=3µF, C3=6µF, C4=20µF; target Ceq≈5.96µF
        
        The exhaustive search should find at least one series-parallel topology
        whose equivalent capacitance matches the expected value within tolerance.
        """
        # Extract test data
        capacitors = EXERCISE_01["capacitors"]
        expected_ceq = EXERCISE_01["expected_ceq_F"]
        exercise_id = EXERCISE_01["id"]
        
        # Run exhaustive search with tight tolerance
        # tolerance: 0.01% = 0.01 as percentage tolerance
        solutions = find_best_sp_solutions(
            capacitors=capacitors,
            target=expected_ceq,
            tolerance=0.01,  # 0.01% tolerance
            top_k=100
        )
        
        # Verify at least one solution was found
        assert len(solutions) > 0, (
            f"Exercise {exercise_id}: Exhaustive search found no solutions "
            f"within 0.01% tolerance for target Ceq={expected_ceq:.6e} F"
        )
        
        # Verify best solution matches expected Ceq within exact tolerance
        best_solution = solutions[0]
        observed_ceq = best_solution.ceq
        
        if expected_ceq != 0:
            rel_error = abs((observed_ceq - expected_ceq) / expected_ceq)
        else:
            rel_error = abs(observed_ceq)
        
        assert rel_error < ToleranceLevel.EXACT, (
            f"Exercise {exercise_id}: Exhaustive search best solution - "
            f"observed={observed_ceq:.6e} F, expected={expected_ceq:.6e} F, "
            f"rel_error={rel_error:.2e}, found {len(solutions)} solutions"
        )
    
    def test_exercise_02_exhaustive_search(self):
        """Validate exhaustive search finds solution for Exercise 02.
        
        Exercise 02: C1=2µF, C2=8µF, C3=7µF, C4=4µF; target Ceq≈9.73µF
        
        The exhaustive search should find at least one series-parallel topology
        whose equivalent capacitance matches the expected value within tolerance.
        """
        # Extract test data
        capacitors = EXERCISE_02["capacitors"]
        expected_ceq = EXERCISE_02["expected_ceq_F"]
        exercise_id = EXERCISE_02["id"]
        
        # Run exhaustive search with tight tolerance
        # tolerance: 0.01% = 0.01 as percentage tolerance
        solutions = find_best_sp_solutions(
            capacitors=capacitors,
            target=expected_ceq,
            tolerance=0.01,  # 0.01% tolerance
            top_k=100
        )
        
        # Verify at least one solution was found
        assert len(solutions) > 0, (
            f"Exercise {exercise_id}: Exhaustive search found no solutions "
            f"within 0.01% tolerance for target Ceq={expected_ceq:.6e} F"
        )
        
        # Verify best solution matches expected Ceq within exact tolerance
        best_solution = solutions[0]
        observed_ceq = best_solution.ceq
        
        if expected_ceq != 0:
            rel_error = abs((observed_ceq - expected_ceq) / expected_ceq)
        else:
            rel_error = abs(observed_ceq)
        
        assert rel_error < ToleranceLevel.EXACT, (
            f"Exercise {exercise_id}: Exhaustive search best solution - "
            f"observed={observed_ceq:.6e} F, expected={expected_ceq:.6e} F, "
            f"rel_error={rel_error:.2e}, found {len(solutions)} solutions"
        )
