import { useEffect, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState("cust_001");
  const [prediction, setPrediction] = useState(null);

  useEffect(() => {
    fetch(`${API_BASE_URL}/recoveries/summary`)
      .then((response) => response.json())
      .then((data) => setSummary(data))
      .catch((error) => console.error("Summary fetch error:", error));

    fetch(`${API_BASE_URL}/customers`)
      .then((response) => response.json())
      .then((data) => setCustomers(data.customers || []))
      .catch((error) => console.error("Customers fetch error:", error));
  }, []);

  useEffect(() => {
    if (!selectedCustomerId) return;

    fetch(`${API_BASE_URL}/predict/${selectedCustomerId}`)
      .then((response) => response.json())
      .then((data) => setPrediction(data))
      .catch((error) => console.error("Prediction fetch error:", error));
  }, [selectedCustomerId]);

  return (
    <div className="app">
      <header className="hero">
        <p className="eyebrow">RevenueRecover AI</p>
        <h1>Failed Payment Recovery Dashboard</h1>
        <p className="subtitle">
          Monitor failed payments, view recovery predictions, and decide the next
          action from one place.
        </p>
      </header>

      <main className="dashboard">
        <section className="card">
          <h2>Recovery Summary</h2>
          {summary ? (
            <div className="stats">
              <div className="stat-box">
                <span>Total Failed Customers</span>
                <strong>{summary.total_failed_customers}</strong>
              </div>
              <div className="stat-box">
                <span>Total Failed Amount</span>
                <strong>₹{summary.total_failed_amount}</strong>
              </div>
              <div className="stat-box">
                <span>Likely Recoveries</span>
                <strong>{summary.likely_recoveries}</strong>
              </div>
              <div className="stat-box">
                <span>Possible Recoveries</span>
                <strong>{summary.possible_recoveries}</strong>
              </div>
              <div className="stat-box">
                <span>Unlikely Recoveries</span>
                <strong>{summary.unlikely_recoveries}</strong>
              </div>
            </div>
          ) : (
            <p>Loading summary...</p>
          )}
        </section>

        <section className="card">
          <h2>Customer List</h2>
          <div className="customer-list">
            {customers.map((customer) => (
              <button
                key={customer.customer_id}
                className={`customer-item ${
                  selectedCustomerId === customer.customer_id ? "active" : ""
                }`}
                onClick={() => setSelectedCustomerId(customer.customer_id)}
              >
                <strong>{customer.name}</strong>
                <span>{customer.customer_id}</span>
                <span>₹{customer.failed_amount}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="card">
          <h2>Prediction Details</h2>
          {prediction ? (
            <div className="details">
              <p><strong>Customer ID:</strong> {prediction.customer_id}</p>
              <p><strong>Failed Amount:</strong> ₹{prediction.failed_amount}</p>
              <p><strong>Days Since Failure:</strong> {prediction.days_since_failure}</p>
              <p><strong>Failure Reason:</strong> {prediction.failure_reason}</p>
              <p><strong>Prediction:</strong> {prediction.prediction}</p>
              <p><strong>Recovery Score:</strong> {prediction.recovery_score}</p>
              <p><strong>Recommended Action:</strong> {prediction.recommended_action}</p>
              <p><strong>Explanation:</strong> {prediction.explanation}</p>
              <p><strong>Channel:</strong> {prediction.channel}</p>
            </div>
          ) : (
            <p>Loading prediction...</p>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;