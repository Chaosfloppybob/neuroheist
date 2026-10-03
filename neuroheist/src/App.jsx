import { useState } from "react";
import ScanUpload from "./components/ScanUpload";
import ResultsView from "./components/ResultsView";
import "./App.css";

function App() {
  // null = no scan analyzed yet (show upload); anything else = show results
  const [result, setResult] = useState(null);

  return (
    <div className="app">
      {result === null ? (
        <div className="glass panel">
          <h1>Brain scan analysis</h1>
          <p className="subtitle">
            Upload an MRI scan to detect and visualize tumor regions in 3D.
          </p>
          {/* When the upload finishes, its data is stored here and the screen switches */}
          <ScanUpload onResult={setResult} />
        </div>
      ) : (
        <ResultsView result={result} onNewScan={() => setResult(null)} />
      )}
    </div>
  );
}

export default App;
