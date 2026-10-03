import "./ResultsView.css";

export default function ResultsView({ result, onNewScan }) {
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
          <p>3D viewer goes here</p>
        </div>

        {/* Right column: stats on top, chat below */}
        <div className="results__side">
          <section className="glass results__stats">
            <h2>Findings</h2>
            {/* Temporary: shows the raw backend data so you can see its shape */}
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </section>

          <section className="glass results__chat">
            <h2>Ask about this scan</h2>
            <p>Chat goes here</p>
          </section>
        </div>
      </div>
    </div>
  );
}
