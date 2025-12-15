import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select an Excel file.");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);
      setResults(response.data);
      setError("");
    } catch (err) {
      setError(err.response?.data?.error || "Upload failed.");
      setResults([]);
    }
  };

  return (
    <div className="container">
      <header>
        <h1>💰 AML Fraud Detection System</h1>
        <p>Analyze transaction data for potential money laundering in seconds.</p>
      </header>

      <section className="upload">
        <input type="file" accept=".xlsx" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload & Analyze</button>
        {error && <p className="error">{error}</p>}
      </section>

      {results.length > 0 && (
        <section className="results">
          <h2>🔍 Analysis Results</h2>
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>From Bank</th>
                <th>To Bank</th>
                <th>Amount</th>
                <th>Currency</th>
                <th>Format</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {results.map((tx, i) => (
                <tr key={i} className={tx.fraud ? "fraud" : "legit"}>
                  <td>{tx.transaction}</td>
                  <td>{tx.from_bank}</td>
                  <td>{tx.to_bank}</td>
                  <td>${tx.amount?.toFixed(2)}</td>
                  <td>{tx.received_currency}</td>
                  <td>{tx.payment_format}</td>
                  <td>{tx.fraud ? "🚨 Fraudulent" : "✅ Legitimate"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}

export default App;
