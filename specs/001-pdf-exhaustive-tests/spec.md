# Feature Specification: PDF Exhaustive Regression Tests

**Feature Branch**: `001-pdf-exhaustive-tests`  
**Created**: 2025-12-12  
**Status**: Draft  
**Input**: Add automated regression tests from two PDF example circuits; current “SP Tree Exhaustive” does not find the expected equivalent capacitance for these cases.

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Validate SP exhaustive on reference examples (Priority: P1)

As a developer validating the solver, I want the automated test suite to include reference exercises with known correct results so that solver regressions are caught immediately.

**Why this priority**: The exhaustive method is used to validate correctness; if it fails on simple, known examples, it undermines confidence in results and blocks further development.

**Independent Test**: Running the unit tests should verify that the exhaustive solver can reach the known target equivalent capacitance for each reference exercise.

**Acceptance Scenarios**:

1. **Given** the capacitor inventory and the target equivalent capacitance for exercise 1 (in SI units), **When** the SP Tree exhaustive search runs, **Then** it returns at least one solution whose equivalent capacitance matches the target within the required tolerance.
2. **Given** the capacitor inventory and the target equivalent capacitance for exercise 2 (in SI units), **When** the SP Tree exhaustive search runs, **Then** it returns at least one solution whose equivalent capacitance matches the target within the required tolerance.

---

### User Story 2 - Validate computed Ceq for fixed topologies (Priority: P2)

As a developer, I want the test suite to validate that the equivalent-capacitance calculation matches the analytical answer for the same exercises, independent of the search algorithm.

**Why this priority**: This separates “search can’t find it” from “math evaluation is wrong,” which speeds up debugging and prevents false conclusions.

**Independent Test**: Unit tests compute $C_{eq}$ for an explicitly defined circuit and compare to the analytical expected value.

**Acceptance Scenarios**:

1. **Given** an explicit series/parallel structure corresponding to exercise 1, **When** the equivalent capacitance is computed, **Then** it matches the analytical expected value within tolerance.
2. **Given** an explicit node/connection description corresponding to exercise 2, **When** the equivalent capacitance is computed, **Then** it matches the analytical expected value within tolerance.

---

---

### User Story 3 - Prevent unit mistakes in test inputs (Priority: P3)

As a developer, I want tests to clearly use SI units (Farads) for both inputs and expected values so that common unit mistakes (e.g., treating µF as F) are avoided.

**Why this priority**: The most common reason for “solver fails” is unit mismatch; the tests should make the unit expectations explicit.

**Independent Test**: Tests and test data declare units explicitly and include a sanity check that values are in a realistic range.

**Acceptance Scenarios**:

1. **Given** the reference exercise definitions, **When** the tests run, **Then** they validate that all capacitor values and expected results are in Farads and within a reasonable numeric range for the exercises.

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Unit mismatch: inputs accidentally provided in µF without conversion to Farads.
- Duplicate values: repeated capacitor values should not cause incorrect rejection or missed solutions.
- Order invariance: shuffling the capacitor list should not change whether a valid solution exists.
- Tight tolerance: solver should still succeed with a low-decimal tolerance for these small cases.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The automated test suite MUST include two reference exercises with a defined capacitor inventory and an analytical expected equivalent capacitance.
- **FR-002**: For each exercise, the test suite MUST validate equivalent capacitance computation for an explicit circuit topology (independent of any search algorithm).
- **FR-003**: For each exercise, the SP Tree exhaustive search MUST be validated to find a circuit whose equivalent capacitance matches the analytical expected value within tolerance.
- **FR-004**: All reference exercise definitions MUST use SI units (Farads) for both capacitor values and expected equivalent capacitance.
- **FR-005**: The reference exercise tests MUST be deterministic (no randomness) and MUST fail with a clear assertion message indicating which exercise failed and what value was observed vs expected.
- **FR-006**: The tests MUST complete within a reasonable runtime for a local developer workflow for these small exercises (4 capacitors each).

### Key Entities *(include if feature involves data)*

- **Reference Exercise**: A named example containing capacitor inventory, terminals, and expected equivalent capacitance.
- **Capacitor**: A component with a numeric capacitance value in Farads.
- **Expected Result**: The analytical equivalent capacitance value (Farads) used for validation.

## Assumptions & Dependencies

- The reference exercises use exactly the listed capacitors (no extra components) and all values are provided in SI units (Farads).
- The exhaustive method is expected to find a matching series/parallel arrangement for these exercises because the intended solutions are series/parallel-reducible.
- The acceptance tolerance is “low decimals” meaning the solver output matches the analytical expected value within a small numeric tolerance appropriate to the µF scale.
- The automated tests run in a typical local developer environment and should not require manual interaction.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: Running the full automated test suite reports both reference exercises as passing for both “explicit topology Ceq validation” and “SP Tree exhaustive search validation.”
- **SC-002**: For each reference exercise, the observed equivalent capacitance from the solver is within the defined tolerance of the analytical expected value.
- **SC-003**: The reference exercise tests complete in under 10 seconds on a typical developer machine.
- **SC-004**: Failures (if any) clearly indicate whether the issue is in “Ceq calculation” vs “exhaustive search did not find the solution.”

## Reference Exercise Definitions

The following two exercises define the required inventories, terminals, and expected results (values in Farads):

```json
{
  "schema_version": "1.0",
  "units": "farad",
  "notes": "Tests extracted from 'Obtener asociación condensadores 2.pdf' (2 pages). Values in SI. expected_ceq computed analytically.",
  "tests": [
    {
      "id": "pdf2p_association_01",
      "title": "C1=15uF, C2=3uF, C3=6uF, C4=20uF; target Ceq≈5.96uF",
      "terminals": { "pos": "a", "neg": "b" },
      "capacitors": [
        { "name": "C1", "value_F": 1.5e-05 },
        { "name": "C2", "value_F": 3e-06 },
        { "name": "C3", "value_F": 6e-06 },
        { "name": "C4", "value_F": 2e-05 }
      ],
      "expected": { "ceq_F": 5.964912280701754e-06 }
    },
    {
      "id": "pdf2p_association_02",
      "title": "C1=2uF, C2=8uF, C3=7uF, C4=4uF; target Ceq≈9.73uF",
      "terminals": { "pos": "A", "neg": "B" },
      "capacitors": [
        { "name": "C1", "value_F": 2e-06 },
        { "name": "C2", "value_F": 8e-06 },
        { "name": "C3", "value_F": 7e-06 },
        { "name": "C4", "value_F": 4e-06 }
      ],
      "expected": { "ceq_F": 9.733333333333334e-06 }
    }
  ]
}
```
