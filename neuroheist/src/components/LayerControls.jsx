import "./LayerControls.css";

const LAYER_INFO = {
  brain: { label: "Brain", color: "#d4d4d8" },
  tumor: { label: "Tumor", color: "#ef4444" },
};

export default function LayerControls({ layers, onChange, hasTumor }) {
  // Update one property of one layer, e.g. update("brain", { opacity: 0.5 })
  function update(key, changes) {
    onChange({ ...layers, [key]: { ...layers[key], ...changes } });
  }

  // One-click "glass brain" look: see-through brain, solid tumor
  function showTumorInside() {
    onChange({
      brain: { visible: true, opacity: 0.3 },
      tumor: { visible: true, opacity: 1 },
    });
  }

  const keys = hasTumor ? ["brain", "tumor"] : ["brain"];

  return (
    <div className="layers">
      <h2>Layers</h2>

      {keys.map((key) => {
        const layer = layers[key];
        const info = LAYER_INFO[key];
        const percent = Math.round(layer.opacity * 100);

        return (
          <div key={key} className={`layer${layer.visible ? "" : " is-hidden"}`}>
            <div className="layer__header">
              <span className="layer__swatch" style={{ background: info.color }} />
              <span className="layer__name">{info.label}</span>

              {/* A real checkbox, styled to look like a switch */}
              <label className="layer__toggle">
                <input
                  type="checkbox"
                  checked={layer.visible}
                  onChange={(e) => update(key, { visible: e.target.checked })}
                  aria-label={`Show ${info.label.toLowerCase()}`}
                />
                <span className="layer__switch" />
              </label>
            </div>

            <div className="layer__slider-row">
              <input
                className="layer__slider"
                type="range"
                min="0"
                max="100"
                value={percent}
                disabled={!layer.visible}
                onChange={(e) => update(key, { opacity: Number(e.target.value) / 100 })}
                aria-label={`${info.label} opacity`}
              />
              <span className="layer__value">{percent}%</span>
            </div>
          </div>
        );
      })}

      {hasTumor ? (
        <button type="button" className="layers__preset" onClick={showTumorInside}>
          See-through brain
        </button>
      ) : (
        <p className="layers__note">No tumor regions detected.</p>
      )}
    </div>
  );
}
