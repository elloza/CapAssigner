# Tasks: SP Graph Exhaustive

**Branch**: `005-sp-graph-exhaustive` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup
*Project initialization and file creation*

- [ ] T001 Create `capassigner/core/sp_graph_exhaustive.py`
- [ ] T002 Create `tests/unit/test_sp_graph_exhaustive.py`

## Phase 2: Foundational (Fix SP Tree Bug)
*Critical fix for existing SP Tree enumeration to ensure fair comparison*

- [ ] T003 Create reproduction test case for Classroom Problem in `tests/unit/test_sp_enumeration.py`
- [ ] T004 Fix `enumerate_sp_topologies` in `capassigner/core/sp_enumeration.py` to use `itertools.combinations` for full partitioning
- [ ] T005 Verify SP Tree fix passes reproduction test case

## Phase 3: User Story 1 - SP Graph Exhaustive Method
*Core algorithm implementation*

- [ ] T006 [US1] Implement `generate_topologies` in `capassigner/core/sp_graph_exhaustive.py` (Graph enumeration)
- [ ] T007 [US1] Implement `is_sp_reducible` in `capassigner/core/sp_graph_exhaustive.py` (Iterative reduction)
- [ ] T008 [US1] Implement `solve` in `capassigner/core/sp_graph_exhaustive.py` (Main solver logic)
- [ ] T009 [US1] Implement unit tests for SP Graph Exhaustive in `tests/unit/test_sp_graph_exhaustive.py`
- [ ] T010 [US1] Verify Classroom Problem [3,2,3,1]pF -> 1pF is solved exactly by SP Graph method

## Phase 4: User Story 2 - UI Method Selection Clarity
*UI updates for method selection and guidance*

- [ ] T011 [US2] Update `capassigner/ui/tooltips.py` with descriptions for all 3 methods
- [ ] T012 [US2] Update `capassigner/ui/pages.py` to add "SP Graph Exhaustive" to method selector
- [ ] T013 [US2] Implement suggestion logic in `capassigner/ui/pages.py` (suggest other methods if error > 5%)

## Phase 5: User Story 3 - Documentation
*Educational content and documentation*

- [ ] T014 [US3] Update `capassigner/ui/theory.py` with SP Graph theory and method comparison table
- [ ] T015 [US3] Update `README.md` with method comparison and feature description

## Final Phase: Polish & Cross-Cutting
*Validation and cleanup*

- [ ] T016 Run full test suite to ensure no regressions
- [ ] T017 Verify performance constraints (N=6 < 30s) for both methods

## Dependencies

- Phase 2 (SP Tree Fix) is independent of Phase 3 (SP Graph Impl) but both are needed for final comparison.
- Phase 4 (UI) depends on Phase 3.
- Phase 5 (Docs) can be done in parallel with Phase 4.

## Implementation Strategy

1. **Fix the Bug First**: Ensure the baseline (SP Tree) is correct.
2. **Implement Core Algorithm**: Build the graph enumeration and reduction logic.
3. **Integrate UI**: Expose the new method to the user.
4. **Document**: Explain the differences.
