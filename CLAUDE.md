# CapAssigner Development Guidelines

v2 is a static web app (GitHub Pages): a Rust engine compiled to WebAssembly plus a Svelte 5 / TypeScript UI. v1 (Python/Streamlit) lives in `legacy/` and is only used to generate golden fixtures.

## Layout
```
crates/capcore/     Rust engine: engine.rs (value DP, MITM root, log-grid pruning), cores.rs (3-connected cores),
                    space.rs (multiset/size state spaces), laplace.rs (Kron reduction), rational.rs, api.rs (JSON), lib.rs (wasm-bindgen)
src/                Svelte app; src/lib/physics.ts + exact.ts are the independent oracle (must not share code with Rust)
src/workers/        solver.worker.ts runs the WASM engine
tests/unit/         Vitest (units, physics properties, WASM cross-checks); tests/e2e/ Playwright
tests/fixtures/     golden_v1.json (regenerate: cd legacy && python scripts/export_golden.py)
legacy/             v1, unchanged
```

## Commands
- `npm run wasm` builds `src/wasm/pkg` (needs `~/.cargo/bin` on PATH); `npm run build`, `npm run dev`
- `npm test` (Vitest), `npm run check` (svelte-check), `npm run build && npm run e2e` (Playwright)
- `cargo test --workspace --release`, `cargo clippy --workspace --all-targets -- -D warnings`, `cargo fmt --all`
- Timing survey: `cargo test --release --test api timing -- --ignored --nocapture`

## Rules
- Values cross the WASM boundary in farads; the engine normalises by the target. Leaf values must round-trip bit-exactly (serde_json `float_roundtrip`).
- Never prune by closeness to the target inside the DP; only log-grid coarsening, which carries a proven bound (`stats.boundRel`).
- Any engine change must keep the OEIS tests (`crates/capcore/tests/oeis.rs`) and the golden/oracle tests green.
