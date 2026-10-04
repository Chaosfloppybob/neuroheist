import { useState } from "react";
import BrainViewer from "./BrainViewer";
import TreatmentPanel from "./TreatmentPanel";
import "./ResultsView.css";

export default function ResultsView({ result, file, onNewScan }) {
  // Holds { reductionPercent, summary, sources } after a treatment is simulated
  const [treatmentResult, setTreatmentResult] = useState(null);

  return (
    <div className="results">
      <header className="results__header">
        <h1>Scan results</h1>
        {/* Reuses your upload button styles */}
        <button className="upload__button" onClick={onNewScan}>
          New scan
        </button>
      </header>

      <div className="results__grid">
        {/* Left column: tumor region toggles + opacity slider */}
        <aside className="glass results__controls">
          <h2>Layers</h2>
          <p>Layer controls go here</p>
        </aside>

        {/* Center column: the 3D viewer */}
        <div className="glass results__viewer">
          {/* reductionPercent isn't used by the viewer yet; it's for the shrink slider later */}
          <BrainViewer
            file={file}
            maskUrl={result?.maskUrl}
            reductionPercent={treatmentResult?.reductionPercent}
          />
        </div>

        {/* Right column: stats on top, treatment simulation below */}
        <div className="results__side">
          <section className="glass results__stats">
            <h2>Findings</h2>
            {/* Temporary: shows the raw backend data so you can see its shape */}
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </section>

          <section className="glass results__chat">
            <TreatmentPanel scanResult={result} onResult={setTreatmentResult} />
          </section>
        </div>
      </div>
    </div>
  );
}
