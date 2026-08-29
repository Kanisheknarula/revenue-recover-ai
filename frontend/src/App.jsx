import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function getRiskTone(prediction) {
  if (prediction === "recovery likely") return "good";
  if (prediction === "recovery possible") return "medium";
  return "bad";
}

const initialForm = {
  customer_id: "cust_custom_001",
  failed_amount: 750,
  days_since_failure: 3,
  failure_reason: "insufficient_funds",
};

function App() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [selectedCustomerId, setSelectedCustomerId] = useState("cust_001");
  const [prediction, setPrediction] = useState(null);
  const [actionData, setActionData] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [customForm, setCustomForm] = useState(initialForm);
  const [customPrediction, setCustomPrediction] = useState(null);
  const [customLoading, setCustomLoading] = useState(false);

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

    setActionMessage("");

    fetch(`${API_BASE_URL}/predict/${selectedCustomerId}`)
      .then((response) => response.json())
      .then((data) => setPrediction(data))
      .catch((error) => console.error("Prediction fetch error:", error));

    fetch(`${API_BASE_URL}/actions/${selectedCustomerId}`)
      .then((response) => response.json())
      .then((data) => setActionData(data))
      .catch((error) => console.error("Action fetch error:", error));
  }, [selectedCustomerId]);

  const filteredCustomers = useMemo(() => {
    const term = searchTerm.toLowerCase().trim();

    if (!term) return customers;

    return customers.filter((customer) => {
      return (
        customer.name.toLowerCase().includes(term) ||
        customer.customer_id.toLowerCase().includes(term) ||
        String(customer.failed_amount).includes(term)
      );
    });
  }, [customers, searchTerm]);

  function handleSimulateAction() {
    if (!actionData) return;

    setActionMessage(
      `Success: ${actionData.recommended_action} triggered for ${actionData.customer_id} via ${actionData.channel}.`
    );
  }

  function handleFormChange(event) {
    const { name, value } = event.target;

    setCustomForm((prev) => ({
      ...prev,
      [name]:
        name === "failed_amount" || name === "days_since_failure"
          ? Number(value)
          : value,
    }));
  }

  function handleCustomPrediction(event) {
    event.preventDefault();
    setCustomLoading(true);

    fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(customForm),
    })
      .then((response) => response.json())
      .then((data) => setCustomPrediction(data))
      .catch((error) => console.error("Custom prediction error:", error))
      .finally(() => setCustomLoading(false));
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">RevenueRecover AI</p>
          <h1>Failed Payment Recovery Dashboard</h1>
          <p className="subtitle">
            Monitor failed payments, view recovery predictions, and decide the next
            action from one place.
          </p>
        </div>

        {prediction && (
          <div className="hero-badge">
            <span>Current Recommendation</span>
            <strong>{prediction.recommended_action}</strong>
            <small>{prediction.channel}</small>
          </div>
        )}
      </header>

      <main className="dashboard">
        <section className="card">
          <div className="section-head">
            <h2>Recovery Summary</h2>
            <span className="section-tag">Live Overview</span>
          </div>

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
              <div className="stat-box success">
                <span>Likely Recoveries</span>
                <strong>{summary.likely_recoveries}</strong>
              </div>
              <div className="stat-box warning">
                <span>Possible Recoveries</span>
                <strong>{summary.possible_recoveries}</strong>
              </div>
              <div className="stat-box danger">
                <span>Unlikely Recoveries</span>
                <strong>{summary.unlikely_recoveries}</strong>
              </div>
            </div>
          ) : (
            <p>Loading summary...</p>
          )}
        </section>

        <section className="card">
          <div className="section-head">
            <h2>Customer List</h2>
            <span className="section-tag">Choose Customer</span>
          </div>

          <input
            className="search-box"
            type="text"
            placeholder="Search by name, id, or amount"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
          />

          <div className="customer-list">
            {filteredCustomers.length > 0 ? (
              filteredCustomers.map((customer) => (
                <button
                  key={customer.customer_id}
                  className={`customer-item ${
                    selectedCustomerId === customer.customer_id ? "active" : ""
                  }`}
                  onClick={() => setSelectedCustomerId(customer.customer_id)}
                >
                  <div className="customer-top">
                    <strong>{customer.name}</strong>
                    <span className="status-pill">Failed</span>
                  </div>
                  <span>{customer.customer_id}</span>
                  <span>₹{customer.failed_amount}</span>
                </button>
              ))
            ) : (
              <div className="empty-state">
                No customers matched your search.
              </div>
            )}
          </div>
        </section>

        <section className="card">
          <div className="section-head">
            <h2>Prediction Details</h2>
            <span className="section-tag">Selected Case</span>
          </div>

          {prediction ? (
            <div className="details">
              <div className={`highlight-box risk-${getRiskTone(prediction.prediction)}`}>
                <span>Prediction</span>
                <strong>{prediction.prediction}</strong>
              </div>

              <div className="highlight-box">
                <span>Recovery Score</span>
                <strong>{prediction.recovery_score}</strong>
              </div>

              <p><strong>Customer ID:</strong> {prediction.customer_id}</p>
              <p><strong>Failed Amount:</strong> ₹{prediction.failed_amount}</p>
              <p><strong>Days Since Failure:</strong> {prediction.days_since_failure}</p>
              <p><strong>Failure Reason:</strong> {prediction.failure_reason}</p>
              <p><strong>Recommended Action:</strong> {prediction.recommended_action}</p>
              <p><strong>Explanation:</strong> {prediction.explanation}</p>
              <p><strong>Channel:</strong> {prediction.channel}</p>
            </div>
          ) : (
            <p>Loading prediction...</p>
          )}
        </section>

        <section className="card action-card">
          <div className="section-head">
            <h2>Next Action</h2>
            <span className="section-tag">Execution View</span>
          </div>

          {actionData ? (
            <div className="details">
              <div className="highlight-box action-box">
                <span>Recommended Action</span>
                <strong>{actionData.recommended_action}</strong>
              </div>

              <p><strong>Prediction:</strong> {actionData.prediction}</p>
              <p><strong>Channel:</strong> {actionData.channel}</p>
              <p><strong>Next Step:</strong> {actionData.next_step}</p>

              <button className="simulate-button" type="button" onClick={handleSimulateAction}>
                Simulate Recovery Action
              </button>

              {actionMessage && <div className="success-banner">{actionMessage}</div>}
            </div>
          ) : (
            <p>Loading action...</p>
          )}
        </section>

        <section className="card action-card">
          <div className="section-head">
            <h2>Custom Prediction Lab</h2>
            <span className="section-tag">Manual Test</span>
          </div>

          <form className="custom-form" onSubmit={handleCustomPrediction}>
            <div className="form-grid">
              <label>
                Customer ID
                <input
                  name="customer_id"
                  value={customForm.customer_id}
                  onChange={handleFormChange}
                />
              </label>

              <label>
                Failed Amount
                <input
                  name="failed_amount"
                  type="number"
                  value={customForm.failed_amount}
                  onChange={handleFormChange}
                />
              </label>

              <label>
                Days Since Failure
                <input
                  name="days_since_failure"
                  type="number"
                  value={customForm.days_since_failure}
                  onChange={handleFormChange}
                />
              </label>

              <label>
                Failure Reason
                <select
                  name="failure_reason"
                  value={customForm.failure_reason}
                  onChange={handleFormChange}
                >
                  <option value="insufficient_funds">insufficient_funds</option>
                  <option value="card_expired">card_expired</option>
                  <option value="bank_declined">bank_declined</option>
                  <option value="upi_failed">upi_failed</option>
                </select>
              </label>
            </div>

            <button className="simulate-button" type="submit">
              {customLoading ? "Running Prediction..." : "Run Custom Prediction"}
            </button>
          </form>

          {customPrediction ? (
            <div className="custom-result">
              <div className={`highlight-box risk-${getRiskTone(customPrediction.prediction)}`}>
                <span>Custom Prediction</span>
                <strong>{customPrediction.prediction}</strong>
              </div>
              <p><strong>Recovery Score:</strong> {customPrediction.recovery_score}</p>
              <p><strong>Recommended Action:</strong> {customPrediction.recommended_action}</p>
              <p><strong>Explanation:</strong> {customPrediction.explanation}</p>
              <p><strong>Channel:</strong> {customPrediction.channel}</p>
            </div>
          ) : (
            <div className="empty-state">
              Run a manual prediction to test a new recovery scenario.
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;