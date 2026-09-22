"""Export v1 results as golden fixtures for the v2 cross-implementation tests.

Runs the v1 SP tree enumerator on every exercise known to the v1 test-suite
(classroom problem, the two PDF reference exercises and the regression cases)
and writes ``tests/fixtures/golden_v1.json`` at the repository root. v2 must
find a best error that is never worse than v1's for any of these cases.

Usage (from ``legacy/``)::

    python scripts/export_golden.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

LEGACY = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LEGACY))

from capassigner.core.sp_enumeration import find_best_sp_solutions  # noqa: E402
from tests.unit import test_fixtures as fx  # noqa: E402
from tests.unit.test_pdf_exhaustive import EXERCISE_01, EXERCISE_02  # noqa: E402


def cases() -> list[dict]:
    out = [
        {
            "id": "classroom_4cap",
            "capacitors": [3e-12, 2e-12, 3e-12, 1e-12],
            "target": 1e-12,
            "source": "v1 tests/unit/test_sp_enumeration_classroom.py",
        }
    ]
    for ex in (EXERCISE_01, EXERCISE_02):
        out.append(
            {
                "id": ex["id"],
                "capacitors": ex["capacitors"],
                "target": ex["expected_ceq_F"],
                "source": "v1 tests/unit/test_pdf_exhaustive.py",
            }
        )
    for group in (
        fx.SIMPLE_REGRESSION_CASES,
        fx.MEDIUM_REGRESSION_CASES,
        fx.COMPLEX_REGRESSION_CASES,
        fx.EDGE_REGRESSION_CASES,
    ):
        for c in group:
            out.append(
                {
                    "id": c["name"],
                    "capacitors": c["capacitors"],
                    "target": c["target_ceq"],
                    "source": "v1 tests/unit/test_fixtures.py",
                }
            )
    return out


def main() -> None:
    results = []
    for case in cases():
        best = find_best_sp_solutions(case["capacitors"], case["target"], top_k=1)[0]
        results.append(
            {
                **case,
                "v1_best_ceq": best.ceq,
                "v1_best_rel_error": abs(best.ceq - case["target"]) / case["target"],
                "v1_expression": best.expression,
            }
        )
        print(f"{case['id']:<40} n={len(case['capacitors'])} rel_err={results[-1]['v1_best_rel_error']:.3e}")
    dest = LEGACY.parent / "tests" / "fixtures" / "golden_v1.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"generator": "legacy/scripts/export_golden.py", "cases": results}, indent=2))
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
