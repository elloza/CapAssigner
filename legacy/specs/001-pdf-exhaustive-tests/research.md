# Research: PDF Exhaustive Regression Tests

**Feature Branch**: `001-pdf-exhaustive-tests`  
**Date**: 2025-12-12  
**Phase**: 0 (Research)

## Overview

This document resolves all technical unknowns identified during the planning phase. The feature adds automated regression tests for two PDF reference exercises to validate the SP Tree exhaustive solver.

## Research Tasks Completed

### 1. Test Framework Integration

**Decision**: Use pytest with existing test fixture infrastructure

**Rationale**: 
- Project already has comprehensive pytest test suite (tests/unit/, tests/contract/, tests/integration/)
- Existing test fixtures provide tolerance levels: `ToleranceLevel.EXACT` (1e-10) for exact SP calculations
- Test helpers like `assert_exact_match()` and `assert_approximate_match()` are already available
- Constitution requires pytest ≥5.0 (already installed)

**Alternatives considered**:
- **unittest framework**: Rejected because pytest is already the standard in this project
- **New test framework**: Rejected to maintain consistency with existing test suite

### 2. Tolerance Specification

**Decision**: Use `ToleranceLevel.EXACT` (1e-10 relative error) for both explicit topology tests and exhaustive search validation

**Rationale**:
- PDF exercises provide analytical expected values to high precision (e.g., 5.964912280701754e-06 F)
- Series/parallel formulas are exact mathematical operations (not approximate)
- `ToleranceLevel.EXACT` is specifically designed for "known mathematical identities" and "SP topology calculations compared to hand-calculated values" (per test_fixtures.py docstring)
- With 4 capacitors, numerical error accumulation is minimal

**Alternatives considered**:
- **ToleranceLevel.APPROXIMATE** (1e-6): Rejected because SP formulas are exact, not heuristic
- **Custom tolerance for µF scale**: Rejected because relative error tolerance is scale-invariant
- **Absolute tolerance**: Rejected because the project uses relative error consistently

### 3. Test Data Format

**Decision**: Define test data as Python dataclasses or dictionaries directly in test file

**Rationale**:
- JSON format in spec is for documentation clarity, but Python tests benefit from native data structures
- Easier to maintain and debug without external file dependencies
- Allows inline comments and type checking
- Test data is small (2 exercises, 4 capacitors each) - no need for external files

**Alternatives considered**:
- **JSON file**: Rejected for simplicity; no need for external file when data is small
- **YAML file**: Rejected for same reason; adds unnecessary dependency
- **Fixture conftest.py**: Rejected because these are feature-specific tests, not reusable fixtures

### 4. Test Structure

**Decision**: Create `tests/unit/test_pdf_exhaustive.py` with two test classes:
1. `TestExplicitTopologyValidation`: Validates equivalent capacitance calculation for explicitly defined circuits
2. `TestExhaustiveSearchValidation`: Validates that exhaustive search finds solutions matching expected Ceq

**Rationale**:
- Separates "math is correct" (explicit topology) from "search can find it" (exhaustive algorithm)
- Matches user story structure (P1: exhaustive validation, P2: explicit topology validation)
- Clear failure attribution: if explicit fails, formula is wrong; if only exhaustive fails, search algorithm is wrong
- Follows existing test patterns in `test_sp_enumeration.py`

**Alternatives considered**:
- **Single test function for both concerns**: Rejected because it mixes concerns and makes debugging harder
- **Separate test files**: Rejected because both test classes operate on same data and feature
- **Integration test location**: Rejected because these are unit tests of core algorithms

### 5. Exhaustive Search Invocation

**Decision**: Use `find_best_sp_solutions()` from `sp_enumeration.py` with target Ceq and tight tolerance

**Rationale**:
- `find_best_sp_solutions()` is the public API that combines enumeration + ranking + filtering
- It already supports target Ceq and tolerance percentage parameters
- Returns ranked solutions with error metrics
- Test validates the full workflow that end users experience

**Alternatives considered**:
- **enumerate_sp_topologies() directly**: Rejected because this is too low-level and doesn't rank or filter
- **Custom search logic in tests**: Rejected to avoid duplicating production code logic

### 6. Explicit Topology Construction

**Decision**: Manually construct SPNode trees using Leaf, Series, and Parallel dataclasses for each exercise's expected solution

**Rationale**:
- Provides ground truth for "given this exact topology, what is Ceq?"
- Tests `calculate_sp_ceq()` function in isolation
- Requires reverse-engineering the expected circuit from analytical Ceq, but this validates understanding of the problem

**Implementation approach**:
- For each exercise, determine one valid SP topology that achieves the target Ceq
- Construct the topology tree manually: `Series(Parallel(...), ...)`
- Call `calculate_sp_ceq()` and compare to expected value
- If analytical solution suggests a specific topology, document it in test comments

**Alternatives considered**:
- **Skip explicit topology tests**: Rejected because it's a requirement (FR-002, User Story 2)
- **Programmatic topology generation**: Rejected because test should be deterministic and explicit

### 7. Unit Handling and Validation

**Decision**: Test data uses SI units (Farads) with explicit scientific notation (e.g., `1.5e-05`)

**Rationale**:
- Constitution Principle III requires SI units in all calculations
- Scientific notation makes unit scale explicit (e.g., `1.5e-05` clearly means 15 µF in Farads)
- Python natively handles scientific notation
- Test assertions validate that values are in realistic ranges (1e-12 to 1e-3 F for practical capacitors)

**Validation approach**:
- Add sanity checks that capacitor values are positive and within realistic range
- Document conversion in test comments: "# C1=15uF → 1.5e-05 F"
- Assert expected Ceq values match spec exactly (no unit conversion errors)

**Alternatives considered**:
- **Parse from strings with units**: Rejected because tests should use native numeric types
- **Separate unit test for parsing**: Already covered by existing `test_parsing.py`

### 8. Performance Validation

**Decision**: Add timing assertions using pytest duration markers or custom timing logic

**Rationale**:
- Constitution specifies "SP Exhaustive (N=5) < 3 seconds"
- These tests use N=4, expected to complete in <1 second
- SC-003 requires tests complete in <10 seconds

**Implementation approach**:
- Use `pytest.mark.timeout(10)` to enforce maximum duration
- Optionally log actual duration for performance regression tracking
- No need for granular timing since N=4 is well within performance budget

**Alternatives considered**:
- **Custom timing decorator**: Rejected for simplicity; pytest timeout is sufficient
- **Performance profiling**: Rejected as out of scope; this is functional validation

## Best Practices Research

### pytest Best Practices for Scientific Computing

1. **Use descriptive test names**: `test_exercise_01_explicit_topology_ceq()` clearly indicates what is tested
2. **Parametrize when appropriate**: If more exercises are added, use `@pytest.mark.parametrize`
3. **Clear assertion messages**: Include actual vs expected values in failure messages
4. **Docstrings with formulas**: Document expected topologies using mathematical notation
5. **Fixture isolation**: Each test should be independent and not rely on shared state

### SP Topology Testing Patterns (from existing tests)

From `test_sp_enumeration.py`:
- Test known topology counts for small N
- Verify both series and parallel combinations are generated
- Check that Ceq calculations match hand-calculated values
- Use `calculate_sp_ceq()` for validation, not string representations

### Error Message Best Practices

From FR-005:
- Include exercise ID in failure message
- Report observed vs expected Ceq
- Indicate whether failure is in explicit topology or exhaustive search
- Example: `"Exercise 01: Explicit topology Ceq mismatch: observed=5.97e-06, expected=5.96e-06"`

## Remaining Unknowns

None. All technical decisions are resolved and ready for Phase 1 (Design).

## References

- Existing test fixtures: `tests/unit/test_fixtures.py`
- SP enumeration tests: `tests/unit/test_sp_enumeration.py`
- Tolerance specifications: `ToleranceLevel` class
- Constitution performance targets: Section "Performance Targets"
- Core algorithms: `capassigner/core/sp_enumeration.py`, `sp_structures.py`
