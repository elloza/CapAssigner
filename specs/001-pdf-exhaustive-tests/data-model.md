# Data Model: PDF Exhaustive Regression Tests

**Feature Branch**: `001-pdf-exhaustive-tests`  
**Date**: 2025-12-12  
**Phase**: 1 (Design)

## Overview

This document defines the data entities and structures for the PDF reference exercise validation tests. Since this is a testing feature, the data model focuses on test data structures rather than production data entities.

## Core Entities

### ReferenceExercise

Represents a single PDF reference exercise with known expected results.

**Attributes**:
- `id` (str): Unique identifier (e.g., "pdf2p_association_01")
- `title` (str): Human-readable description (e.g., "C1=15uF, C2=3uF, C3=6uF, C4=20uF; target Ceq≈5.96uF")
- `capacitors` (List[float]): Capacitor values in Farads (SI units)
- `capacitor_labels` (List[str]): Human-readable labels (e.g., ["C1", "C2", "C3", "C4"])
- `expected_ceq_F` (float): Analytical expected equivalent capacitance in Farads
- `terminals` (dict): Terminal identifiers (e.g., {"pos": "a", "neg": "b"})

**Validation Rules**:
- All capacitor values must be positive (> 0)
- All capacitor values must be in realistic range (1e-12 F to 1 F)
- `expected_ceq_F` must be positive
- Number of capacitors must equal number of labels
- Capacitor list must not be empty

**Example**:
```python
ReferenceExercise(
    id="pdf2p_association_01",
    title="C1=15uF, C2=3uF, C3=6uF, C4=20uF; target Ceq≈5.96uF",
    capacitors=[1.5e-05, 3e-06, 6e-06, 2e-05],
    capacitor_labels=["C1", "C2", "C3", "C4"],
    expected_ceq_F=5.964912280701754e-06,
    terminals={"pos": "a", "neg": "b"}
)
```

### ExplicitTopology

Represents a manually constructed series-parallel topology for validation.

**Attributes**:
- `exercise_id` (str): Reference to parent ReferenceExercise
- `topology` (SPNode): Manually constructed SP tree (Leaf, Series, or Parallel)
- `description` (str): Human-readable description of topology structure

**Purpose**:
- Validates that `calculate_sp_ceq()` produces correct results for known topologies
- Provides ground truth independent of search algorithm

**Example**:
```python
ExplicitTopology(
    exercise_id="pdf2p_association_01",
    topology=Series(
        left=Parallel(
            left=Leaf(capacitor_index=0, value=1.5e-05),  # C1
            right=Leaf(capacitor_index=1, value=3e-06)    # C2
        ),
        right=Parallel(
            left=Leaf(capacitor_index=2, value=6e-06),    # C3
            right=Leaf(capacitor_index=3, value=2e-05)    # C4
        )
    ),
    description="(C1||C2) in series with (C3||C4)"
)
```

### TestResult

Represents the outcome of a validation test.

**Attributes**:
- `exercise_id` (str): Reference to ReferenceExercise
- `test_type` (str): "explicit_topology" or "exhaustive_search"
- `success` (bool): Whether test passed
- `observed_ceq_F` (Optional[float]): Computed equivalent capacitance
- `expected_ceq_F` (float): Expected equivalent capacitance
- `relative_error` (Optional[float]): Relative error if applicable
- `failure_message` (Optional[str]): Detailed error message if failed

**Purpose**:
- Captures test execution results for reporting
- Provides structured data for test assertions

## Relationships

```text
ReferenceExercise (1) ──> (0..1) ExplicitTopology
    │
    └──> (1..*) TestResult

SPNode (existing core entity)
    ├── Leaf
    ├── Series
    └── Parallel
```

## State Transitions

### Test Execution Flow

```text
1. Test Setup
   ├── Load ReferenceExercise data
   └── Construct ExplicitTopology (if applicable)

2. Explicit Topology Test
   ├── Call calculate_sp_ceq(topology)
   ├── Compare to expected_ceq_F
   └── Create TestResult

3. Exhaustive Search Test
   ├── Call find_best_sp_solutions(capacitors, target=expected_ceq_F)
   ├── Check if any solution matches within tolerance
   └── Create TestResult

4. Test Teardown
   └── Assert all TestResults indicate success
```

## Data Validation

### Input Validation

Tests must validate that ReferenceExercise data meets requirements:

```python
def validate_reference_exercise(exercise: ReferenceExercise) -> None:
    """Validate reference exercise data integrity."""
    # FR-004: Must use SI units (Farads)
    assert all(c > 0 for c in exercise.capacitors), "All capacitors must be positive"
    assert all(1e-12 <= c <= 1 for c in exercise.capacitors), "Capacitors must be in realistic range"
    
    # Data integrity
    assert len(exercise.capacitors) == len(exercise.capacitor_labels), "Labels must match capacitors"
    assert exercise.expected_ceq_F > 0, "Expected Ceq must be positive"
    assert len(exercise.capacitors) > 0, "Must have at least one capacitor"
```

### Tolerance Validation

Tests use `ToleranceLevel.EXACT` (1e-10 relative error):

```python
def validate_ceq_match(observed: float, expected: float, exercise_id: str) -> None:
    """Validate equivalent capacitance matches expected value."""
    if expected != 0:
        rel_error = abs((observed - expected) / expected)
    else:
        rel_error = abs(observed)
    
    assert rel_error < ToleranceLevel.EXACT, (
        f"Exercise {exercise_id}: Ceq mismatch - "
        f"observed={observed:.6e} F, expected={expected:.6e} F, "
        f"rel_error={rel_error:.2e}"
    )
```

## Test Data Constants

### Exercise 01 Data

```python
EXERCISE_01 = ReferenceExercise(
    id="pdf2p_association_01",
    title="C1=15uF, C2=3uF, C3=6uF, C4=20uF; target Ceq≈5.96uF",
    capacitors=[
        1.5e-05,  # C1 = 15 µF
        3e-06,    # C2 = 3 µF
        6e-06,    # C3 = 6 µF
        2e-05     # C4 = 20 µF
    ],
    capacitor_labels=["C1", "C2", "C3", "C4"],
    expected_ceq_F=5.964912280701754e-06,  # ≈5.96 µF
    terminals={"pos": "a", "neg": "b"}
)
```

### Exercise 02 Data

```python
EXERCISE_02 = ReferenceExercise(
    id="pdf2p_association_02",
    title="C1=2uF, C2=8uF, C3=7uF, C4=4uF; target Ceq≈9.73uF",
    capacitors=[
        2e-06,    # C1 = 2 µF
        8e-06,    # C2 = 8 µF
        7e-06,    # C3 = 7 µF
        4e-06     # C4 = 4 µF
    ],
    capacitor_labels=["C1", "C2", "C3", "C4"],
    expected_ceq_F=9.733333333333334e-06,  # ≈9.73 µF
    terminals={"pos": "A", "neg": "B"}
)
```

## Dependencies

This data model depends on existing core entities:
- `SPNode` (Union[Leaf, Series, Parallel]) from `capassigner/core/sp_structures.py`
- `calculate_sp_ceq()` from `capassigner/core/sp_structures.py`
- `find_best_sp_solutions()` from `capassigner/core/sp_enumeration.py`
- `ToleranceLevel.EXACT` from `tests/unit/test_fixtures.py`

## Notes

- This is test infrastructure, not production data
- No database or persistence required
- Data is embedded directly in test file for simplicity
- If more exercises are added later, consider moving to fixtures or JSON file
