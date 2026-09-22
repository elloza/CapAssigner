# Tasks: PDF Exhaustive Regression Tests

**Feature**: `001-pdf-exhaustive-tests`  
**Input**: Design documents from `/specs/001-pdf-exhaustive-tests/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `- [ ] [ID] [P?] [Story?] Description`

- **Checkbox**: `- [ ]` (required at start of every task)
- **[ID]**: Task identifier (T001, T002, etc.)
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- **Description**: Clear action with exact file path

## Path Conventions

This is a single project with tests at: `tests/unit/test_pdf_exhaustive.py`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create test file structure and setup basic test infrastructure

- [X] T001 Create test file tests/unit/test_pdf_exhaustive.py with module docstring and imports
- [X] T002 [P] Define EXERCISE_01 test data constant with capacitor values and expected Ceq in tests/unit/test_pdf_exhaustive.py
- [X] T003 [P] Define EXERCISE_02 test data constant with capacitor values and expected Ceq in tests/unit/test_pdf_exhaustive.py

**Checkpoint**: Test file exists with all necessary imports and test data constants

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core test infrastructure that MUST be complete before user stories can be implemented

- [X] T004 Create TestExplicitTopologyValidation test class in tests/unit/test_pdf_exhaustive.py
- [X] T005 Create TestExhaustiveSearchValidation test class in tests/unit/test_pdf_exhaustive.py

**Checkpoint**: Test class structure ready for test method implementation

---

## Phase 3: User Story 2 - Validate computed Ceq for fixed topologies (Priority: P2)

**Goal**: Validate that the equivalent-capacitance calculation matches the analytical answer for explicit circuit topologies, independent of the search algorithm

**Independent Test**: Run `pytest tests/unit/test_pdf_exhaustive.py::TestExplicitTopologyValidation -v` to verify explicit topology tests pass

**Why P2 before P1**: Implementing explicit topology tests first establishes that `calculate_sp_ceq()` is correct before testing the search algorithm

### Implementation for User Story 2

- [X] T006 [P] [US2] Determine valid SP topology for Exercise 01 that achieves target Ceq (document in test comment)
- [X] T007 [P] [US2] Determine valid SP topology for Exercise 02 that achieves target Ceq (document in test comment)
- [X] T008 [US2] Implement test_exercise_01_explicit_topology method in tests/unit/test_pdf_exhaustive.py
- [X] T009 [US2] Implement test_exercise_02_explicit_topology method in tests/unit/test_pdf_exhaustive.py
- [X] T010 [US2] Add clear assertion messages with exercise ID and observed vs expected values for explicit topology tests

**Checkpoint**: Running explicit topology tests verifies `calculate_sp_ceq()` produces correct results for both exercises

---

## Phase 4: User Story 1 - Validate SP exhaustive on reference examples (Priority: P1) 🎯 MVP

**Goal**: Validate that the exhaustive solver can reach the known target equivalent capacitance for reference exercises with known correct results

**Independent Test**: Run `pytest tests/unit/test_pdf_exhaustive.py::TestExhaustiveSearchValidation -v` to verify exhaustive search finds matching solutions

### Implementation for User Story 1

- [X] T011 [US1] Implement test_exercise_01_exhaustive_search method in tests/unit/test_pdf_exhaustive.py
- [X] T012 [US1] Implement test_exercise_02_exhaustive_search method in tests/unit/test_pdf_exhaustive.py
- [X] T013 [US1] Add assertion to verify at least one solution is found for each exercise
- [X] T014 [US1] Add assertion to verify best solution matches expected Ceq within ToleranceLevel.EXACT
- [X] T015 [US1] Add clear assertion messages with exercise ID and observed vs expected values for exhaustive search tests

**Checkpoint**: Running exhaustive search tests verifies `find_best_sp_solutions()` finds correct solutions for both exercises

---

## Phase 5: User Story 3 - Prevent unit mistakes in test inputs (Priority: P3)

**Goal**: Ensure tests clearly use SI units (Farads) and validate that values are in realistic ranges to prevent common unit mistakes

**Independent Test**: Run `pytest tests/unit/test_pdf_exhaustive.py -v` to verify all tests pass with correct unit handling

### Implementation for User Story 3

- [X] T016 [P] [US3] Add inline comments documenting unit conversions in EXERCISE_01 data (e.g., "# C1 = 15 µF → 1.5e-05 F")
- [X] T017 [P] [US3] Add inline comments documenting unit conversions in EXERCISE_02 data (e.g., "# C1 = 2 µF → 2e-06 F")
- [X] T018 [US3] Add validation helper function validate_reference_exercise in tests/unit/test_pdf_exhaustive.py to check capacitor values are positive and in realistic range
- [X] T019 [US3] Call validate_reference_exercise for both exercises in test setup or at module level

**Checkpoint**: All tests include clear unit documentation and validate input data ranges

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements and validation

- [X] T020 [P] Add pytest.mark.timeout(10) decorator to test classes to enforce performance requirement
- [X] T021 [P] Add module-level docstring explaining test purpose and reference to PDF source
- [X] T022 Run full test suite with pytest tests/unit/test_pdf_exhaustive.py -v to verify all 4 tests pass
- [X] T023 Run pytest tests/unit/ -v to verify no regressions in existing tests
- [X] T024 Verify test execution time is under 10 seconds as required by FR-006 and SC-003
- [X] T025 [P] Add code comments explaining topology construction choices for explicit tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Story 2 (Phase 3)**: Depends on Foundational (Phase 2) - Validates math correctness FIRST
- **User Story 1 (Phase 4)**: Depends on Foundational (Phase 2) and ideally US2 - Validates search algorithm
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Can run in parallel with US1/US2
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 2 (P2)**: Should be implemented FIRST to validate `calculate_sp_ceq()` correctness
- **User Story 1 (P1)**: Should be implemented SECOND to validate `find_best_sp_solutions()` search
- **User Story 3 (P3)**: Can be implemented in parallel with US1/US2 (adds documentation and validation)

**Rationale for order**: Implementing explicit topology tests (US2) first establishes that the math is correct before testing whether the search algorithm (US1) can find solutions. This provides better failure attribution.

### Within Each User Story

- **US2**: Topology determination (T006-T007) before test implementation (T008-T010)
- **US1**: Test implementation (T011-T012) before assertions (T013-T015)
- **US3**: Comments and validation can be added independently

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (define different exercise data constants)
- **Phase 3 (US2)**: T006 and T007 can run in parallel (determine topologies for different exercises)
- **Phase 5 (US3)**: T016 and T017 can run in parallel (document different exercises)
- **Phase 6**: T020, T021, and T025 can run in parallel (different types of improvements)
- **Across User Stories**: US3 tasks can proceed in parallel with US1/US2 once Phase 2 is complete

---

## Parallel Example: User Story 2

If you have team capacity, these tasks can proceed simultaneously after Phase 2:

```bash
# Developer A: Exercise 01 explicit topology
git checkout -b feature/us2-exercise01
# Work on T006 (determine topology) and T008 (implement test)

# Developer B: Exercise 02 explicit topology
git checkout -b feature/us2-exercise02
# Work on T007 (determine topology) and T009 (implement test)

# Merge both when complete
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

For immediate value delivery, prioritize in this order:

1. **Phase 1-2**: Setup and foundational structure (T001-T005)
2. **Phase 3 (US2)**: Explicit topology validation for Exercise 01 only (T006, T008, T010)
3. **Phase 4 (US1)**: Exhaustive search validation for Exercise 01 only (T011, T013-T015)

This provides a working test for one complete exercise and validates both the math and search algorithm.

### Full Implementation

For complete feature delivery:

1. Complete all tasks for Exercise 01 (US1 + US2)
2. Extend to Exercise 02 (complete remaining US1 + US2 tasks)
3. Add unit documentation and validation (US3)
4. Polish and performance validation (Phase 6)

### Incremental Delivery

Each user story delivers independent value:

- **US2 complete**: Validates that `calculate_sp_ceq()` is mathematically correct for explicit topologies
- **US1 complete**: Validates that `find_best_sp_solutions()` can find solutions (depends on US2 being correct)
- **US3 complete**: Adds documentation and safety checks to prevent unit mistakes

---

## Test Execution

### Run individual user story tests:

```powershell
# Activate environment (REQUIRED)
conda activate .\.conda

# User Story 2: Explicit topology tests
pytest tests/unit/test_pdf_exhaustive.py::TestExplicitTopologyValidation -v

# User Story 1: Exhaustive search tests
pytest tests/unit/test_pdf_exhaustive.py::TestExhaustiveSearchValidation -v

# All tests for this feature
pytest tests/unit/test_pdf_exhaustive.py -v

# With detailed output
pytest tests/unit/test_pdf_exhaustive.py -v -s
```

### Expected Results

- ✅ 4 tests pass (2 explicit topology + 2 exhaustive search)
- ✅ Tests complete in <10 seconds total (SC-003)
- ✅ Clear pass/fail messages with exercise ID and values (FR-005, SC-004)
- ✅ No regressions in existing test suite

### Troubleshooting

**If T008/T009 fails (explicit topology)**:
- Verify topology construction matches analytical solution
- Check capacitor index mappings are correct
- Try alternative topology combinations
- Confirm expected Ceq value from spec is correct

**If T011/T012 fails (exhaustive search)**:
- Verify T008/T009 pass first (math must be correct)
- Check tolerance_pct parameter (may need to increase slightly)
- Verify capacitor values match exercise definitions exactly
- Confirm expected Ceq is achievable with SP topology

**If tests timeout**:
- Should not happen for N=4 capacitors
- Verify memoization in `enumerate_sp_topologies()` is working
- Check for infinite loops in test logic

---

## Success Criteria Validation

After implementation, verify these success criteria:

- ✅ **SC-001**: Both exercises pass for both explicit topology and exhaustive search tests
- ✅ **SC-002**: Observed Ceq matches expected within ToleranceLevel.EXACT (1e-10) for all tests
- ✅ **SC-003**: Tests complete in under 10 seconds
- ✅ **SC-004**: Failure messages clearly indicate whether issue is in Ceq calculation or exhaustive search

---

## References

- Feature spec: [spec.md](spec.md)
- Implementation plan: [plan.md](plan.md)
- Data model: [data-model.md](data-model.md)
- Research decisions: [research.md](research.md)
- Quick start guide: [quickstart.md](quickstart.md)
- Test contracts: [contracts/test-contracts.yaml](contracts/test-contracts.yaml)
- Existing test patterns: `tests/unit/test_sp_enumeration.py`
- Tolerance definitions: `tests/unit/test_fixtures.py`
