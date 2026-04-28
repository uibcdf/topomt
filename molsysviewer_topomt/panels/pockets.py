"""TopoMT Pockets panel widget — per-pocket list with show/hide controls."""

from __future__ import annotations

from typing import Any

from molsysviewer import AddonPanelWidget

from ..runtime import ensure_runtime, record_event


_ESM = """
export function render({ model, el }) {
  let state = {
    pockets: [],
    tag_prefix: "topomt-pocket",
    status: "idle",
    error: null,
  };

  el.innerHTML = `
    <div class="tmt-pockets-panel">
      <div class="tmt-pocket-list" id="tmt-pocket-list">
        <span class="tmt-empty">No pockets loaded.</span>
      </div>
      <div class="tmt-actions">
        <button class="tmt-btn tmt-btn--primary" id="tmt-show-all">Show All</button>
        <button class="tmt-btn tmt-btn--secondary" id="tmt-clear-all">Clear</button>
      </div>
      <div class="tmt-status" id="tmt-status"></div>
    </div>
  `;

  const listEl    = el.querySelector("#tmt-pocket-list");
  const showAllBtn = el.querySelector("#tmt-show-all");
  const clearBtn  = el.querySelector("#tmt-clear-all");
  const statusEl  = el.querySelector("#tmt-status");

  function buildPocketRow(p) {
    const scoreText = p.score !== null && p.score !== undefined ? p.score.toFixed(2) : "—";
    const row = document.createElement("div");
    row.className = "tmt-pocket-row";
    row.innerHTML = `
      <span class="tmt-pocket-id">${p.feature_id}</span>
      <span class="tmt-pocket-score">${scoreText}</span>
      <button class="tmt-btn tmt-btn--small" data-id="${p.feature_id}">Show</button>
    `;
    row.querySelector("button").addEventListener("click", () => {
      model.send({ type: "action", id: "show_pocket", payload: { feature_id: p.feature_id } });
    });
    return row;
  }

  function applyState(s) {
    state = { ...state, ...s };

    listEl.innerHTML = "";
    if (state.pockets.length === 0) {
      listEl.innerHTML = '<span class="tmt-empty">No pockets loaded.</span>';
    } else {
      state.pockets.forEach(p => listEl.appendChild(buildPocketRow(p)));
    }

    showAllBtn.disabled = state.status === "rendering" || state.pockets.length === 0;
    showAllBtn.textContent = state.status === "rendering" ? "Rendering…" : "Show All";

    if (state.status === "done") {
      statusEl.textContent = "Done.";
      statusEl.className = "tmt-status tmt-status--ok";
    } else if (state.status === "error" && state.error) {
      statusEl.textContent = "Error: " + state.error;
      statusEl.className = "tmt-status tmt-status--error";
    } else {
      statusEl.textContent = "";
      statusEl.className = "tmt-status";
    }
  }

  showAllBtn.addEventListener("click", () => {
    model.send({ type: "action", id: "show_all_pockets", payload: {} });
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
.tmt-pockets-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  font-size: 13px;
  font-family: sans-serif;
}
.tmt-pocket-list {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-height: 200px;
  overflow-y: auto;
}
.tmt-empty {
  font-size: 11px;
  opacity: 0.5;
  font-style: italic;
}
.tmt-pocket-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}
.tmt-pocket-id {
  flex: 1;
  font-family: monospace;
}
.tmt-pocket-score {
  width: 40px;
  text-align: right;
  opacity: 0.7;
}
.tmt-actions {
  display: flex;
  gap: 6px;
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
.tmt-btn--small {
  padding: 2px 7px;
  font-size: 11px;
  background: transparent;
  border: 1px solid #555;
  color: inherit;
  border-radius: 3px;
  cursor: pointer;
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
"""


class TopoMTPocketsPanel(AddonPanelWidget):
    _esm: str = _ESM
    _css: str = _CSS

    def on_mount(self, view: Any) -> None:
        runtime = ensure_runtime(view)
        self.push_state(self._build_state(runtime))

    def handle_action(self, view: Any, action_id: str, payload: dict) -> None:
        runtime = ensure_runtime(view)

        if action_id == "show_all_pockets":
            if runtime.topography is None:
                self.push_state({**self._build_state(runtime), "status": "error", "error": "No topography attached."})
                return
            self.push_state({**self._build_state(runtime), "status": "rendering"})
            try:
                from ..render import render_topography_pockets
                result = render_topography_pockets(
                    view, runtime.topography, tag_prefix=runtime.tag_prefix, skip_digestion=True
                )
                record_event(view, "panel_show_all_pockets", n_rendered=result["n_rendered"])
                self.push_state({**self._build_state(runtime), "status": "done"})
            except Exception as exc:
                self.push_state({**self._build_state(runtime), "status": "error", "error": str(exc)})

        elif action_id == "show_pocket":
            feature_id = payload.get("feature_id")
            if not feature_id or runtime.topography is None:
                return
            try:
                from ..integration import attach_features
                attach_features(
                    view, runtime.topography,
                    feature_ids=[feature_id],
                    enable_addon=False, render=True,
                    tag_prefix=runtime.tag_prefix,
                    skip_digestion=True,
                )
                record_event(view, "panel_show_pocket", feature_id=feature_id)
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
        pockets = []
        if runtime.topography is not None:
            try:
                from ..payloads import topography_payload
                payload = topography_payload(runtime.topography)
                pockets = [
                    {"feature_id": f["feature_id"], "score": f.get("score")}
                    for f in payload["features"]
                    if f.get("feature_type") == "pocket"
                ]
            except Exception:
                pass
        return {
            "pockets": pockets,
            "tag_prefix": runtime.tag_prefix,
            "status": "idle",
            "error": None,
        }
