# Quickstart: PDF Exhaustive Regression Tests

**Feature Branch**: `001-pdf-exhaustive-tests`  
**Date**: 2025-12-12  
**Estimated Implementation Time**: 2-3 hours

## Overview

Add automated regression tests for two PDF reference exercises to validate the SP Tree exhaustive solver. Tests ensure the solver finds correct equivalent capacitances for known reference cases.

## Prerequisites

- Active conda environment: `.conda/` (see constitution)
- Existing dependencies already installed (pytest, numpy)
- Basic understanding of series/parallel capacitor formulas

## Quick Setup

```powershell
# 1. Activate conda environment (REQUIRED)
conda activate .\.conda

# 2. Verify current tests pass
pytest tests/unit/ -v

# 3. Create feature branch (if not already on it)
git checkout -b 001-pdf-exhaustive-tests
```

## Implementation Steps

### Step 1: Create Test File (30 minutes)

Create `tests/unit/test_pdf_exhaustive.py`:

```python
"""Regression tests for PDF reference exercises.

Validates:
1. Explicit topology Ceq calculation
2. Exhaustive search finds matching solutions

Test data from 'Obtener asociación condensadores 2.pdf'.
"""

import pytest
from capassigner.core.sp_enumeration import find_best_sp_solutions
from capassigner.core.sp_structures import (
    Leaf, Series, Parallel, calculate_sp_ceq
)
from tests.unit.test_fixtures import ToleranceLevel

# Test data constants
EXERCISE_01 = {
    "id": "pdf2p_association_01",
    "capacitors": [1.5e-05, 3e-06, 6e-06, 2e-05],  # C1, C2, C3, C4
    "labels": ["C1", "C2", "C3", "C4"],
    "expected_ceq_F": 5.964912280701754e-06
}

EXERCISE_02 = {
    "id": "pdf2p_association_02",
    "capacitors": [2e-06, 8e-06, 7e-06, 4e-06],  # C1, C2, C3, C4
    "labels": ["C1", "C2", "C3", "C4"],
    "expected_ceq_F": 9.733333333333334e-06
}


class TestExplicitTopologyValidation:
    """Test Ceq calculation for explicit circuit topologies."""
    
    # TODO: Implement test_exercise_01_explicit_topology()
    # TODO: Implement test_exercise_02_explicit_topology()


class TestExhaustiveSearchValidation:
    """Test that exhaustive search finds matching solutions."""
    
    # TODO: Implement test_exercise_01_exhaustive_search()
    # TODO: Implement test_exercise_02_exhaustive_search()
```

### Step 2: Implement Explicit Topology Tests (45 minutes)

For each exercise, determine a valid SP topology and test it:

```python
def test_exercise_01_explicit_topology(self):
    """Validate Ceq calculation for Exercise 01 explicit topology."""
    # TODO: Construct explicit topology
    # Example: Series(Parallel(C1, C2), Parallel(C3, C4))
    topology = Series(
        left=Parallel(
            left=Leaf(capacitor_index=0, value=1.5e-05),
            right=Leaf(capacitor_index=1, value=3e-06)
        ),
        right=Parallel(
            left=Leaf(capacitor_index=2, value=6e-06),
            right=Leaf(capacitor_index=3, value=2e-05)
        )
    )
    
    observed_ceq = calculate_sp_ceq(topology)
    expected_ceq = EXERCISE_01["expected_ceq_F"]
    
    rel_error = abs((observed_ceq - expected_ceq) / expected_ceq)
    assert rel_error < ToleranceLevel.EXACT, (
        f"Exercise 01 explicit topology: "
        f"observed={observed_ceq:.6e}, expected={expected_ceq:.6e}, "
        f"rel_error={rel_error:.2e}"
    )
```

**Key tasks**:
1. Determine valid topology for each exercise (may require trial and error)
2. Construct topology using Leaf, Series, Parallel
3. Call `calculate_sp_ceq()` and assert against expected value
4. Use clear error messages with exercise ID and values

### Step 3: Implement Exhaustive Search Tests (45 minutes)

For each exercise, validate that `find_best_sp_solutions()` finds a matching solution:

```python
def test_exercise_01_exhaustive_search(self):
    """Validate exhaustive search finds solution for Exercise 01."""
    capacitors = EXERCISE_01["capacitors"]
    expected_ceq = EXERCISE_01["expected_ceq_F"]
    
    # Run exhaustive search with tight tolerance
    solutions = find_best_sp_solutions(
        capacitors=capacitors,
        target_ceq=expected_ceq,
        tolerance_pct=0.01,  # 0.01% tolerance
        max_solutions=100
    )
    
    # Check if any solution matches
    assert len(solutions) > 0, (
        f"Exercise 01 exhaustive search found no solutions within tolerance"
    )
    
    # Verify best solution is within tolerance
    best_solution = solutions[0]
    rel_error = abs((best_solution.ceq - expected_ceq) / expected_ceq)
    assert rel_error < ToleranceLevel.EXACT, (
        f"Exercise 01 exhaustive search best solution: "
        f"observed={best_solution.ceq:.6e}, expected={expected_ceq:.6e}, "
        f"rel_error={rel_error:.2e}"
    )
```

**Key tasks**:
1. Call `find_best_sp_solutions()` with exercise data
2. Assert that at least one solution is found
3. Verify best solution matches expected Ceq within tolerance
4. Use clear error messages

### Step 4: Add Performance Validation (15 minutes)

Add timeout decorator to ensure tests complete quickly:

```python
@pytest.mark.timeout(10)  # Maximum 10 seconds per test
class TestExhaustiveSearchValidation:
    # ... existing tests
```

### Step 5: Run and Debug (30 minutes)

```powershell
# Run new tests only
pytest tests/unit/test_pdf_exhaustive.py -v

# Run with detailed output
pytest tests/unit/test_pdf_exhaustive.py -v -s

# Run all unit tests to check for regressions
pytest tests/unit/ -v
```

**Expected results**:
- 4 tests pass (2 explicit topology, 2 exhaustive search)
- Tests complete in <10 seconds total
- Clear pass/fail messages

**If tests fail**:
1. Check explicit topology construction (verify manual topology is correct)
2. Check tolerance level (should be ToleranceLevel.EXACT)
3. Verify unit conversions (all values in Farads)
4. Check if exhaustive search needs higher tolerance_pct parameter

## Verification Checklist

- [ ] All 4 tests pass
- [ ] Tests complete in <10 seconds
- [ ] Failure messages include exercise ID and observed/expected values
- [ ] Tests use SI units (Farads) consistently
- [ ] Tests are deterministic (no randomness)
- [ ] Code follows existing test patterns from `test_sp_enumeration.py`

## Common Issues

### Issue: Explicit topology test fails

**Symptom**: Large relative error (>1e-6)

**Solution**: 
- Verify topology structure matches analytical solution
- Try different topology combinations
- Check capacitor index mappings

### Issue: Exhaustive search finds no solutions

**Symptom**: `len(solutions) == 0`

**Solution**:
- Increase `tolerance_pct` parameter (try 1.0% instead of 0.01%)
- Verify capacitor values are correct
- Check if expected Ceq is achievable with SP topology

### Issue: Tests timeout

**Symptom**: pytest timeout after 10 seconds

**Solution**:
- Should not happen for N=4 capacitors
- Check for infinite loops in code
- Verify memoization is working

## Next Steps

After implementation:
1. Run full test suite: `pytest tests/ -v`
2. Update documentation if needed
3. Commit with clear message: "Add PDF exhaustive regression tests (exercises 01-02)"
4. Create PR referencing this spec

## Development Tips

1. **Start with one exercise**: Implement and debug Exercise 01 completely before moving to Exercise 02
2. **Use existing tests as reference**: Copy patterns from `test_sp_enumeration.py`
3. **Test incrementally**: Run tests after each function implementation
4. **Document topologies**: Add comments explaining why a specific topology was chosen

## References

- Feature spec: [spec.md](spec.md)
- Data model: [data-model.md](data-model.md)
- Test contracts: [contracts/test-contracts.yaml](contracts/test-contracts.yaml)
- Research decisions: [research.md](research.md)
- Existing test patterns: `tests/unit/test_sp_enumeration.py`
- Tolerance definitions: `tests/unit/test_fixtures.py`
