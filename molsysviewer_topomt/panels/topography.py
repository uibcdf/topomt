"""TopoMT Topography panel widget — summary view with render trigger."""

from __future__ import annotations

from typing import Any

from molsysviewer import AddonPanelWidget

from ..runtime import ensure_runtime, record_event


_ESM = """
export function render({ model, el }) {
  let state = {
    n_features: 0,
    feature_counts: {},
    tag_prefix: "topomt-pocket",
    status: "idle",
    error: null,
  };

  el.innerHTML = `
    <div class="tmt-panel">
      <div class="tmt-summary" id="tmt-summary">
        <span class="tmt-empty">No topography loaded.</span>
      </div>
      <button class="tmt-btn tmt-btn--primary" id="tmt-render">Render Pockets</button>
      <button class="tmt-btn tmt-btn--secondary" id="tmt-clear">Clear</button>
      <div class="tmt-status" id="tmt-status"></div>
    </div>
  `;

  const summaryEl = el.querySelector("#tmt-summary");
  const renderBtn = el.querySelector("#tmt-render");
  const clearBtn  = el.querySelector("#tmt-clear");
  const statusEl  = el.querySelector("#tmt-status");

  function buildSummaryHtml(counts) {
    const entries = Object.entries(counts);
    if (entries.length === 0) return '<span class="tmt-empty">No features.</span>';
    return entries.map(([t, n]) =>
      `<div class="tmt-row"><span class="tmt-kind">${t}</span><span class="tmt-count">${n}</span></div>`
    ).join("");
  }

  function applyState(s) {
    state = { ...state, ...s };
    summaryEl.innerHTML =
      state.n_features > 0
        ? buildSummaryHtml(state.feature_counts)
        : '<span class="tmt-empty">No topography loaded.</span>';

    renderBtn.disabled = state.status === "rendering" || state.n_features === 0;
    renderBtn.textContent = state.status === "rendering" ? "Rendering…" : "Render Pockets";

    if (state.status === "done") {
      statusEl.textContent = "Rendered.";
      statusEl.className = "tmt-status tmt-status--ok";
    } else if (state.status === "error" && state.error) {
      statusEl.textContent = "Error: " + state.error;
      statusEl.className = "tmt-status tmt-status--error";
    } else if (state.status === "rendering") {
      statusEl.textContent = "Rendering…";
      statusEl.className = "tmt-status tmt-status--busy";
    } else {
      statusEl.textContent = "";
      statusEl.className = "tmt-status";
    }
  }

  renderBtn.addEventListener("click", () => {
    model.send({ type: "action", id: "render_pockets", payload: {} });
  });

  clearBtn.addEventListener("click", () => {
    model.send({ type: "action", id: "clear_pockets", payload: {} });
  });

  model.on("msg:custom", (msg) => {
    if (msg?.type === "state") applyState(msg.state);
  });

  model.send({ type: "query", id: "viewer.context" });
  applyState(state);
}
"""

_CSS = """
.tmt-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  font-size: 13px;
  font-family: sans-serif;
}
.tmt-summary {
  min-height: 36px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.tmt-empty {
  font-size: 11px;
  opacity: 0.5;
  font-style: italic;
}
.tmt-row {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}
.tmt-kind {
  text-transform: capitalize;
  opacity: 0.8;
}
.tmt-count {
  font-weight: 600;
}
.tmt-btn {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
}
.tmt-btn--primary {
  background: #3a7bd5;
  color: #fff;
}
.tmt-btn--secondary {
  background: transparent;
  border: 1px solid #555;
  color: inherit;
}
.tmt-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.tmt-status {
  font-size: 11px;
  min-height: 16px;
}
.tmt-status--ok    { color: #4caf50; }
.tmt-status--error { color: #f44336; }
.tmt-status--busy  { opacity: 0.7; }
"""


class TopoMTTopographyPanel(AddonPanelWidget):
    _esm: str = _ESM
    _css: str = _CSS

    def on_mount(self, view: Any) -> None:
        runtime = ensure_runtime(view)
        self.push_state(self._build_state(runtime))

    def handle_action(self, view: Any, action_id: str, payload: dict) -> None:
        runtime = ensure_runtime(view)

        if action_id == "render_pockets":
            if runtime.topography is None:
                self.push_state({**self._build_state(runtime), "status": "error", "error": "No topography attached."})
                return
            self.push_state({**self._build_state(runtime), "status": "rendering"})
            try:
                from ..render import render_topography_pockets
                result = render_topography_pockets(
                    view, runtime.topography, tag_prefix=runtime.tag_prefix, skip_digestion=True
                )
                record_event(view, "panel_render_pockets", n_rendered=result["n_rendered"])
                self.push_state({**self._build_state(runtime), "status": "done"})
            except Exception as exc:
                self.push_state({**self._build_state(runtime), "status": "error", "error": str(exc)})

        elif action_id == "clear_pockets":
            try:
                view.shapes.clear(tag_prefix=runtime.tag_prefix, skip_digestion=True)
            except Exception:
                pass
            record_event(view, "panel_clear_pockets")
            self.push_state({**self._build_state(runtime), "status": "idle"})

    @staticmethod
    def _build_state(runtime: Any) -> dict:
        from ..payloads import topography_payload
        if runtime.topography is not None:
            try:
                payload = topography_payload(runtime.topography)
                return {
                    "n_features": payload["n_features"],
                    "feature_counts": payload["feature_counts"],
                    "tag_prefix": runtime.tag_prefix,
                    "status": "idle",
                    "error": None,
                }
            except Exception:
                pass
        return {
            "n_features": 0,
            "feature_counts": {},
            "tag_prefix": runtime.tag_prefix,
            "status": "idle",
            "error": None,
        }
