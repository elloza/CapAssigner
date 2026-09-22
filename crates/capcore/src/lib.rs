//! CapAssigner core: synthesis of capacitor networks with a target equivalent
//! capacitance. Compiled to WebAssembly for the browser; also a normal Rust
//! library so the whole engine is tested natively.

pub mod api;
pub mod cores;
pub mod engine;
pub mod laplace;
pub mod num;
pub mod rational;
pub mod space;

use wasm_bindgen::prelude::*;

/// Solve a JSON request (see [`api::Request`]) and return a JSON response.
/// `progress(done, total)` is invoked while the value sets are built.
#[wasm_bindgen(js_name = solve)]
pub fn solve_json(request: &str, progress: Option<js_sys::Function>) -> Result<String, JsValue> {
    let req: api::Request = serde_json::from_str(request)
        .map_err(|e| JsValue::from_str(&format!("bad request: {e}")))?;
    let mut report = |done: usize, total: usize| {
        if let Some(f) = &progress {
            let _ = f.call2(
                &JsValue::NULL,
                &JsValue::from_f64(done as f64),
                &JsValue::from_f64(total as f64),
            );
        }
    };
    let res = api::solve(&req, &mut report).map_err(|e| JsValue::from_str(&e))?;
    serde_json::to_string(&res).map_err(|e| JsValue::from_str(&e.to_string()))
}

/// The catalog of non-series-parallel cores with at most `max_edges` edges.
#[wasm_bindgen(js_name = cores)]
pub fn cores_json(max_edges: usize) -> String {
    serde_json::to_string(&api::cores_out(max_edges)).expect("serializable")
}

#[wasm_bindgen]
pub fn version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}
