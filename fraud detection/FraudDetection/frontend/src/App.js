import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);
      setResult(response.data);
      setError("");
    } catch (error) {
      console.error("Error uploading file:", error);
      setError("Failed to upload file");
    }
  };

  return (
    <div className="App">
      <h1>Fraud Detection</h1>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUpload}>Upload</button>

      {error && <p className="error">{error}</p>}

      {result && (
        <div>
          <h2>Results:</h2>
          <ul>
            {result.map((item, index) => (
              <li key={index}>
                Transaction {item.transaction}: {item.fraud ? "Fraud" : "Legit"}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;
