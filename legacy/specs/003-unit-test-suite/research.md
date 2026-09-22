# Research: Comprehensive Unit Test Suite for Circuit Algorithms

**Feature**: Comprehensive Unit Test Suite
**Date**: 2025-12-12
**Purpose**: Document best practices and technical decisions for implementing comprehensive unit testing and fixing the 4-capacitor bug

---

## 1. Root Cause Analysis: 4-Capacitor Bug

**Research Question**: Why does the algorithm return 7.69% error for a 4-capacitor example with a known exact solution?

### Decision: Systematic Component Testing Approach

**Rationale**:
- The bug could be in SP enumeration (not generating all topologies), C_eq calculation (math errors), or solution filtering (discarding correct solutions)
- Need to isolate which component fails by testing each in isolation
- Start with validating that enumeration generates expected number of topologies
- Then validate each topology's C_eq calculation matches hand-calculated values
- Finally validate ranking and filtering logic

**Testing Strategy**:
1. Verify topology count for N=4 matches theoretical value (40 topologies expected)
2. Hand-calculate C_eq for the known exact solution topology
3. Verify that exact solution appears in enumerated topologies
4. Verify that exact solution ranks first (lowest error)
5. If any step fails, isolate and fix that specific component

**Alternatives Considered**:
- **Rewriting algorithms from scratch**: Rejected - too risky, better to fix incrementally with tests
- **Property-based testing (Hypothesis)**: Deferred - good for future but requires more setup time
- **Mathematical proof verification**: Supplement only - practical testing needed first

**References**:
- Series-Parallel Networks: "The Art of Computer Programming" Vol 4, Knuth
- Test-Driven Development: Beck, Kent. "Test Driven Development: By Example"

---

## 2. Floating-Point Precision Tolerances

**Research Question**: What epsilon tolerances should be used for different types of assertions?

### Decision: Tiered Tolerance Strategy

**Rationale**:
- IEEE 754 double precision has ~15-17 decimal digits of precision
- Accumulated floating-point errors depend on operation complexity
- Need different thresholds for "exact" vs "approximate" solutions

**Tolerance Levels**:
- **Exact solutions**: 1e-10 relative error (clarified in spec)
  - Use for known mathematical identities
  - Use when comparing SP topology calculations to hand-calculated values
  - Example: `assert abs((actual - expected) / expected) < 1e-10`

- **Approximate solutions (heuristic search)**: 1e-6 relative error
  - Use for random algorithm outputs where some variance expected
  - Still tight enough to catch significant errors
  - Example: `assert abs((actual - expected) / expected) < 1e-6`

- **User-facing tolerance**: User-specified percentage (e.g., 5%)
  - Use for acceptance criteria visible to end users
  - Example: `assert abs(actual - expected) / expected < tolerance / 100`

**Implementation**:
```python
import math

def assert_exact_match(actual, expected, description=""):
    """Assert values match within exact solution tolerance."""
    rel_error = abs((actual - expected) / expected) if expected != 0 else abs(actual)
    assert rel_error < 1e-10, f"{description}: rel_error={rel_error}, actual={actual}, expected={expected}"

def assert_approximate_match(actual, expected, description=""):
    """Assert values match within approximate solution tolerance."""
    rel_error = abs((actual - expected) / expected) if expected != 0 else abs(actual)
    assert rel_error < 1e-6, f"{description}: rel_error={rel_error}, actual={actual}, expected={expected}"
```

**Alternatives Considered**:
- **Use `math.isclose()`**: Adopted for convenience where appropriate
- **Absolute error only**: Rejected - doesn't scale across capacitance magnitudes (pF to µF)
- **Single tolerance for everything**: Rejected - too loose for exact solutions, too tight for heuristics

---

## 3. Test Fixture Design Pattern

**Research Question**: How should shared test data (capacitor sets, known solutions) be organized?

### Decision: pytest Fixtures with conftest.py + Dedicated Fixture Module

**Rationale**:
- pytest fixtures provide clean dependency injection
- conftest.py makes fixtures available to all tests automatically
- Dedicated module (`test_fixtures.py`) for complex fixture data keeps conftest.py clean
- Enables reuse without global variables or imports

**Fixture Categories**:
1. **Simple capacitor sets**: Basic inputs for unit tests
2. **Known solutions**: Classroom examples with verified answers
3. **Edge cases**: Empty lists, single capacitor, extreme values
4. **Performance fixtures**: Large capacitor sets for timing tests

**Implementation Pattern**:
```python
# conftest.py (lightweight, auto-discovered)
import pytest
from tests.unit.test_fixtures import KNOWN_SOLUTIONS

@pytest.fixture
def simple_caps():
    """Simple 2-3 capacitor set for quick tests."""
    return [5e-12, 10e-12]

@pytest.fixture
def classroom_4cap():
    """The 4-capacitor example from bug report."""
    return KNOWN_SOLUTIONS["classroom_4cap"]

# test_fixtures.py (data repository)
KNOWN_SOLUTIONS = {
    "classroom_4cap": {
        "capacitors": [1e-12, 2e-12, 5e-12, 10e-12],
        "target": 3.33e-12,
        "exact_topology": "((C1||C2)||C3)||C4",  # Example
        "expected_ceq": 3.33e-12,
        "source": "Professor classroom example Dec 2025"
    },
    # Add more as identified
}
```

**Alternatives Considered**:
- **JSON/YAML test data files**: Deferred - overkill for initial 20 test cases, can add later
- **Global variables**: Rejected - poor practice, harder to modify per-test
- **Each test creates own data**: Rejected - duplication, maintenance burden

---

## 4. Regression Test Organization

**Research Question**: How should 20+ regression test cases be organized for maintainability?

### Decision: Parameterized Tests with Named Test Cases

**Rationale**:
- pytest's `@pytest.mark.parametrize` enables testing multiple inputs with single test function
- Named test cases (via `ids` parameter) provide clear failure messages
- Easy to add new cases without writing new test functions
- Can mark subsets for selective execution

**Structure**:
```python
import pytest
from tests.unit.test_fixtures import REGRESSION_CASES

@pytest.mark.parametrize("case", REGRESSION_CASES, ids=lambda c: c["name"])
def test_sp_enumeration_regression(case):
    """Regression tests for SP enumeration finding known solutions."""
    capacitors = case["capacitors"]
    target = case["target_ceq"]
    expected_topology = case["expected_topology"]
    
    solutions = find_best_sp_solutions(capacitors, target, tolerance=1.0)
    
    # Verify expected solution appears in results
    assert any(
        sol.expression == expected_topology and sol.error_pct < 1.0
        for sol in solutions
    ), f"Expected topology {expected_topology} not found for {case['name']}"
```

**Test Case Categorization** (for 20+ cases):
- **Simple (N=2-3)**: 3 cases - verify basic series/parallel
- **Medium (N=4-6)**: 8 cases - diverse topologies including bug case
- **Complex (N=7-8)**: 4 cases - ensure enumeration scales
- **Edge cases**: 3 cases - single capacitor, identical values, extreme ratios
- **Known classroom examples**: 2 cases - professor-provided examples

**Alternatives Considered**:
- **Separate test function per case**: Rejected - 20+ functions too verbose
- **Test classes with methods**: Acceptable alternative, parametrize chosen for conciseness
- **Property-based testing**: Future enhancement, not replacement for regression tests

---

## 5. Algorithm Refactoring for Testability

**Research Question**: What refactoring patterns enable better unit testing without breaking UI?

### Decision: Dependency Injection + Pure Functions Where Possible

**Rationale**:
- Pure functions (no side effects, deterministic) are easiest to test
- Explicit parameters instead of implicit dependencies enable test mocking
- Can change internal signatures freely since UI layer can be updated

**Refactoring Patterns**:

1. **Extract randomness to parameters**:
```python
# Before: Hard to test deterministically
def generate_random_graph(capacitors, max_internal_nodes=2):
    rng = np.random.default_rng()  # Non-deterministic!
    # ...

# After: Testable with fixed seed
def generate_random_graph(capacitors, max_internal_nodes=2, seed=None, rng=None):
    if rng is None:
        rng = np.random.default_rng(seed)
    # ...
    
# Test usage:
def test_random_graph_determinism():
    caps = [5e-12, 10e-12]
    g1 = generate_random_graph(caps, seed=42)
    g2 = generate_random_graph(caps, seed=42)
    assert graphs_equal(g1, g2)  # Same seed => same graph
```

2. **Separate calculation from presentation**:
```python
# Before: Returns formatted string
def calculate_error(actual, target):
    error_pct = abs(actual - target) / target * 100
    return f"{error_pct:.2f}%"  # Hard to test numerically

# After: Separate concerns
def calculate_relative_error_pct(actual, target):
    """Pure calculation - returns float."""
    return abs(actual - target) / target * 100

def format_error(error_pct):
    """Formatting only - testable separately."""
    return f"{error_pct:.2f}%"
```

3. **Progress callbacks remain optional**:
```python
# Already done well in existing code
def enumerate_sp_topologies(
    capacitors: List[float],
    progress_callback: Optional[ProgressCallback] = None
) -> List[SPNode]:
    # UI provides callback, tests pass None
    if progress_callback:
        progress_callback(...)
```

**UI Update Strategy** (if breaking changes needed):
- Document all signature changes in migration notes
- Update UI imports and calls in same feature branch
- Add deprecation warnings if gradual migration preferred (optional)

**Alternatives Considered**:
- **Wrapper functions for backward compatibility**: Rejected - adds complexity without benefit
- **Global configuration object**: Rejected - harder to test, violates constitution
- **Dependency injection framework**: Overkill for current scale

---

## 6. Test Execution Performance Optimization

**Research Question**: How to keep test execution under 30 seconds with 20+ comprehensive cases?

### Decision: Multi-Layer Strategy

**Rationale**:
- Some tests are inherently slow (N=8 enumeration)
- Need balance between comprehensiveness and speed
- pytest supports parallel execution and selective running

**Optimization Techniques**:

1. **Test markers for selective execution**:
```python
@pytest.mark.fast
def test_series_formula():
    # Runs in milliseconds
    pass

@pytest.mark.slow
def test_n8_enumeration():
    # Runs in seconds
    pass

# Run only fast tests during TDD:
# pytest -m fast

# Run full suite before commit:
# pytest -m "fast or slow"
```

2. **Smaller test inputs where possible**:
- Use N=2-3 for unit tests of formulas
- Use N=4-5 for integration tests
- Use N=7-8 only for specific performance/scalability tests

3. **Memoization cache warming**:
- SP enumeration uses `@lru_cache`
- First test with N=5 warms cache for subsequent N≤5 tests
- Organize tests to leverage cache

4. **pytest-xdist for parallel execution** (optional):
```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

**Time Budget Allocation** (30s total):
- **Unit tests** (< 10s): Fast formula/calculation tests
  - 50+ assertions running in < 100ms each
- **Regression tests** (< 20s): Known solution validation
  - 20+ test cases, average 1s each
  - Most with N=4-6 (fast), few with N=7-8 (slow)
- **Buffer**: Allow 10-20% variance for CI environment

**Alternatives Considered**:
- **Skip slow tests by default**: Rejected - defeats purpose of regression testing
- **Reduce test coverage**: Rejected - 20+ cases is minimum for confidence
- **Optimize algorithms**: Out of scope for this feature (but may result from debugging)

---

## 7. Test Documentation and Maintenance

**Research Question**: How should tests be documented for future maintainability?

### Decision: Self-Documenting Test Structure + Inline Comments

**Rationale**:
- Clear test names explain intent
- Docstrings provide context for why test exists
- Inline comments explain expected values and formulas

**Documentation Standards**:

```python
class TestSeriesParallelFormulas:
    """Validate series and parallel capacitance formulas against mathematical theory.
    
    Constitutional Compliance: Principle IV (Algorithmic Correctness)
    
    References:
        - Series: C_eq = 1 / (1/C1 + 1/C2 + ... + 1/Cn)
        - Parallel: C_eq = C1 + C2 + ... + Cn
    """
    
    def test_series_equal_capacitors(self):
        """Test series of N equal capacitors: C_eq = C/N.
        
        Example: Two 10pF capacitors in series = 5pF
        Formula: 1/C_eq = 1/10pF + 1/10pF = 2/10pF => C_eq = 5pF
        """
        caps = [10e-12, 10e-12]
        expected = 5e-12  # 10pF / 2 capacitors
        
        topology = Series(Leaf(0, caps[0]), Leaf(1, caps[1]))
        actual = calculate_sp_ceq(topology)
        
        assert_exact_match(actual, expected, "Two 10pF caps in series")
```

**Test Naming Convention**:
- `test_<component>_<scenario>_<expected_outcome>`
- Examples:
  - `test_sp_enumeration_n4_generates_40_topologies`
  - `test_graph_ceq_disconnected_returns_zero`
  - `test_heuristic_search_deterministic_with_seed`

**Alternatives Considered**:
- **External documentation**: Too much context switching, gets out of sync
- **Minimal comments**: Rejected - harder for future maintainers to understand why test exists
- **Verbose docstrings on every test**: Middle ground chosen - docstrings on test classes and complex tests only

---

## 8. Error Handling and Invalid Input Testing

**Research Question**: How should tests validate error handling for edge cases?

### Decision: Explicit Exception Testing with pytest.raises

**Rationale**:
- Edge cases (empty lists, negative values, zero) should raise clear exceptions
- Tests should verify both that exception is raised AND that message is helpful
- Constitutional Principle III (Robust Input Parsing) applies to algorithms too

**Exception Testing Pattern**:
```python
def test_empty_capacitor_list_raises_error():
    """Test that empty capacitor list raises ValueError with clear message."""
    with pytest.raises(ValueError, match="Capacitor list cannot be empty"):
        enumerate_sp_topologies([])

def test_negative_capacitor_value_raises_error():
    """Test that negative capacitance raises ValueError."""
    with pytest.raises(ValueError, match="Capacitance must be positive"):
        enumerate_sp_topologies([5e-12, -10e-12])

def test_zero_capacitor_value_raises_error():
    """Test that zero capacitance raises ValueError."""
    with pytest.raises(ValueError, match="Capacitance must be positive"):
        enumerate_sp_topologies([5e-12, 0.0])
```

**Required Edge Cases** (from spec):
1. ✅ Empty capacitor list → ValueError
2. ✅ Zero value capacitor → ValueError  
3. ✅ Negative value capacitor → ValueError
4. Disconnected graph → C_eq = 0 (already handled)
5. Singular matrix in Laplacian → Use pseudo-inverse (already handled)
6. Target capacitance out of range → Return empty solutions (graceful)

**Alternatives Considered**:
- **Silent failures**: Rejected - violates fail-fast principle
- **Return None/null**: Rejected - exceptions are more Pythonic
- **Logging warnings only**: Rejected - invalid input should stop execution

---

## Summary of Technical Decisions

| # | Decision | Rationale | Impact |
|---|----------|-----------|--------|
| 1 | Systematic component testing | Isolate bug root cause | Guides test implementation order |
| 2 | Tiered tolerance strategy | Match precision to test type | Reliable assertions without false failures |
| 3 | Fixtures with conftest.py | Clean test data management | Reusable, maintainable test data |
| 4 | Parameterized regression tests | 20+ cases without duplication | Easy to add new regression cases |
| 5 | Dependency injection refactoring | Enable mocking and determinism | Testable algorithms, may require UI updates |
| 6 | Test markers + small inputs | Meet 30-second time budget | Fast TDD cycle, comprehensive CI |
| 7 | Self-documenting tests | Future maintainability | Clear intent and formulas in code |
| 8 | Explicit exception testing | Validate error handling | Robust edge case coverage |

**Next Steps**: Proceed to Phase 1 (Data Model & Contracts) to define test case structure and API contracts for algorithms.
