"""Reproduction test for the Classroom Problem bug in SP Enumeration."""

import pytest
from capassigner.core.sp_enumeration import find_best_sp_solutions

def test_classroom_problem_reproduction():
    """
    Test the 'Classroom Problem' which failed in the original SP Tree implementation.
    
    Inputs: [3pF, 2pF, 3pF, 1pF]
    Target: 1.0pF
    
    The correct topology is SP-reducible:
    A-C1-C-(C2||C4)-D-C3-B
    Where C1=3, C2=2, C3=3, C4=1.
    C2||C4 = 3pF.
    Then Series(3, 3, 3) = 1pF.
    
    This requires the enumerator to find the partition that groups C2 and C4 together
    in parallel, and then puts that in series with C1 and C3.
    
    Original implementation failed because it only split lists linearly (prefix/suffix),
    so it couldn't group {C2, C4} if they weren't adjacent in the input list 
    (or if the recursive splits didn't allow it).
    """
    capacitors = [3e-12, 2e-12, 3e-12, 1e-12]
    target = 1.0e-12
    
    # We expect exact solution (error ~ 0)
    solutions = find_best_sp_solutions(capacitors, target, top_k=1)
    
    assert len(solutions) > 0
    best = solutions[0]
    
    # Check if we found the exact solution
    # Using a small epsilon for float comparison
    assert best.absolute_error < 1e-15, \
        f"Failed to find exact solution. Best found: {best.ceq} (Error: {best.absolute_error})"
