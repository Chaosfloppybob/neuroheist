import { useState } from 'react'
import ScanUpload from "./components/ScanUpload";


import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className = "glass panel">
      
       <h1>Brain scan analysis</h1>
      <p>some of the stuff</p>
      <ScanUpload onResult={(data) => console.log("Backend returned:", data)} />
    </div>

  );
}

export default App
