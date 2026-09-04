import { useEffect, useMemo, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";
const initialForm = { customer_id: "cust_custom_001", failed_amount: 750, days_since_failure: 3, failure_reason: "insufficient_funds" };

function tone(prediction) {
  if (prediction === "recovery likely") return "good";
  if (prediction === "recovery possible") return "medium";
  return "bad";
}

function money(value) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);
}

function App() {
  const [view, setView] = useState("overview");
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [model, setModel] = useState(null);
  const [selectedId, setSelectedId] = useState("cust_001");
  const [prediction, setPrediction] = useState(null);
  const [action, setAction] = useState(null);
  const [playbook, setPlaybook] = useState(null);
  const [search, setSearch] = useState("");
  const [form, setForm] = useState(initialForm);
  const [customResult, setCustomResult] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        const responses = await Promise.all([
          fetch(`${API}/recoveries/summary`), fetch(`${API}/customers`),
          fetch(`${API}/analytics/portfolio`), fetch(`${API}/model/insights`),
        ]);
        if (responses.some((response) => !response.ok)) throw new Error("Could not load the recovery workspace.");
        const [summaryData, customersData, analyticsData, modelData] = await Promise.all(responses.map((response) => response.json()));
        setSummary(summaryData); setCustomers(customersData.customers || []); setAnalytics(analyticsData); setModel(modelData);
      } catch (loadError) { setError(loadError.message); }
    }
    load();
  }, []);

  useEffect(() => {
    async function loadCase() {
      try {
        const responses = await Promise.all([fetch(`${API}/predict/${selectedId}`), fetch(`${API}/actions/${selectedId}`), fetch(`${API}/playbooks/${selectedId}`)]);
        if (responses.some((response) => !response.ok)) throw new Error("Could not load this customer case.");
        const [predictionData, actionData, playbookData] = await Promise.all(responses.map((response) => response.json()));
        setPrediction(predictionData); setAction(actionData); setPlaybook(playbookData); setMessage("");
      } catch (loadError) { setError(loadError.message); }
    }
    loadCase();
  }, [selectedId]);

  const filteredCustomers = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return customers;
    return customers.filter((customer) => customer.name.toLowerCase().includes(query) || customer.customer_id.toLowerCase().includes(query) || String(customer.failed_amount).includes(query));
  }, [customers, search]);

  const maximumReasonAmount = Math.max(...(analytics?.reason_breakdown.map((item) => item.amount) || [1]));

  function chooseCustomer(customerId, nextView = "overview") { setSelectedId(customerId); setView(nextView); }
  function simulateAction() { if (action) setMessage(`Action queued: ${action.recommended_action} via ${action.channel.replace("_", " ")}. This is a safe product simulation.`); }
  function updateForm(event) { const { name, value } = event.target; setForm((current) => ({ ...current, [name]: ["failed_amount", "days_since_failure"].includes(name) ? Number(value) : value })); }

  async function runCustomPrediction(event) {
    event.preventDefault(); setIsRunning(true); setError("");
    try {
      const response = await fetch(`${API}/predict`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(form) });
      if (!response.ok) throw new Error("Custom prediction could not be completed.");
      setCustomResult(await response.json());
    } catch (predictionError) { setError(predictionError.message); } finally { setIsRunning(false); }
  }

  return <div className="app-shell">
    <header className="topbar">
      <button className="brand" type="button" onClick={() => setView("overview")}><span className="brand-mark">R</span><span><strong>RevenueRecover</strong><small>AI recovery operations</small></span></button>
      <nav className="nav-tabs">
        <button className={view === "overview" ? "active" : ""} type="button" onClick={() => setView("overview")}>Overview</button>
        <button className={view === "intelligence" ? "active" : ""} type="button" onClick={() => setView("intelligence")}>Recovery Intelligence</button>
        <button className={view === "model" ? "active" : ""} type="button" onClick={() => setView("model")}>Model Center</button>
      </nav>
      <div className="live-status"><i />System online</div>
    </header>
    {error && <div className="error-banner">{error} Make sure the FastAPI backend is running on port 8000.</div>}

    {view === "overview" && <main className="workspace">
      <section className="hero"><div><p className="eyebrow">AI Recovery Workspace</p><h1>Turn failed payments into recoverable revenue.</h1><p>Prioritize the right customers, understand recovery probability, and coordinate the next best action in one operational view.</p></div>{prediction && <div className="hero-callout"><span>Next best action</span><strong>{prediction.recommended_action}</strong><small>{prediction.channel.replace("_", " ")} · {prediction.confidence} confidence</small></div>}</section>
      <section className="metric-grid">
        <Metric label="Failed customers" value={summary?.total_failed_customers} note="Active recovery cases" />
        <Metric label="Failed payment value" value={summary ? money(summary.total_failed_amount) : "-"} note="Current portfolio exposure" />
        <Metric special label="Estimated recoverable" value={analytics ? money(analytics.estimated_recoverable_amount) : "-"} note="ML probability weighted" />
        <Metric success label="Likely recoveries" value={summary?.likely_recoveries} note="Prioritize these today" />
      </section>
      <section className="overview-grid">
        <article className="panel"><Heading kicker="Recovery queue" title="Customer cases" side={`${filteredCustomers.length} cases`} /><input className="search" placeholder="Search name, ID, or amount" value={search} onChange={(event) => setSearch(event.target.value)} />
          <div className="customer-list">{filteredCustomers.map((customer) => <button className={`customer ${selectedId === customer.customer_id ? "selected" : ""}`} type="button" key={customer.customer_id} onClick={() => chooseCustomer(customer.customer_id)}><b>{customer.name[0]}</b><span><strong>{customer.name}</strong><small>{customer.customer_id} · {customer.failure_reason.replaceAll("_", " ")}</small></span><em>{money(customer.failed_amount)}</em></button>)}{!filteredCustomers.length && <Empty>Nothing matches this search.</Empty>}</div>
        </article>
        <article className="panel"><Heading kicker="Selected case" title="AI decision brief" side={prediction && <span className={`chip ${tone(prediction.prediction)}`}>{prediction.confidence} confidence</span>} />{prediction ? <Decision prediction={prediction} /> : <Empty>Loading selected case...</Empty>}</article>
      </section>
    </main>}

    {view === "intelligence" && <main className="workspace">
      <section className="page-title"><p className="eyebrow">Recovery Intelligence</p><h1>Focus work on the value most likely to return.</h1><p>Portfolio analytics, a priority work queue, and safe action simulation.</p></section>
      <section className="intelligence-grid">
        <article className="panel"><Heading kicker="Failure analysis" title="Value by failure reason" /> <div className="bar-chart">{analytics?.reason_breakdown.map((item) => <div className="bar-row" key={item.reason}><span>{item.reason.replaceAll("_", " ")}<small>{item.cases} case{item.cases === 1 ? "" : "s"}</small></span><div><i style={{ width: `${(item.amount / maximumReasonAmount) * 100}%` }} /></div><strong>{money(item.amount)}</strong></div>)}</div></article>
        <article className="panel"><Heading kicker="Portfolio health" title="Predicted outcomes" /> <div className="outcomes">{analytics?.outcome_breakdown.map((item) => <div className={`outcome ${tone(item.label)}`} key={item.label}><span>{item.label}</span><strong>{item.cases}</strong></div>)}</div><p className="note">All portfolio outcomes use the same ML decision service as the customer-level prediction view.</p></article>
      </section>
      <section className="panel priority"><Heading kicker="Recommended work order" title="Priority recovery queue" side="Sorted by expected recovery" /><div className="table"><div className="table-head"><span>Customer</span><span>Payment value</span><span>Recovery probability</span><span>Expected recovery</span><span /></div>{analytics?.priority_cases.map((item, index) => <button className="table-row" type="button" key={item.customer_id} onClick={() => chooseCustomer(item.customer_id)}><span><b>0{index + 1}</b><strong>{item.name}</strong><small>{item.recommended_action}</small></span><span>{money(item.failed_amount)}</span><span className="probability"><i style={{ width: `${item.recovery_score * 100}%` }} />{Math.round(item.recovery_score * 100)}%</span><strong>{money(item.expected_recovery)}</strong><em>View</em></button>)}</div></section>
      <section className="intelligence-grid">
        <article className="panel"><Heading kicker="Execution simulation" title="Next recovery action" />{action ? <><div className="action-callout"><span>Recommended for this case</span><strong>{action.recommended_action}</strong><small>{action.channel.replace("_", " ")} · {action.confidence} confidence</small></div><p className="action-text">{action.next_step}</p><button className="primary" type="button" onClick={simulateAction}>Simulate recovery action</button>{message && <div className="success-banner">{message}</div>}{playbook && <div className="playbook"><span className="panel-kicker">AI-guided recovery playbook</span>{playbook.steps.map((step) => <div className="playbook-step" key={step.timing}><b>{step.timing}</b><span><strong>{step.title}</strong><small>{step.detail}</small></span></div>)}</div>}</> : <Empty>Select a customer case first.</Empty>}</article>
        <article className="panel"><Heading kicker="Scenario simulator" title="Custom prediction lab" /><form onSubmit={runCustomPrediction}><div className="form-grid"><label>Customer ID<input name="customer_id" value={form.customer_id} onChange={updateForm} /></label><label>Failed amount<input name="failed_amount" type="number" min="1" value={form.failed_amount} onChange={updateForm} /></label><label>Days since failure<input name="days_since_failure" type="number" min="0" value={form.days_since_failure} onChange={updateForm} /></label><label>Failure reason<select name="failure_reason" value={form.failure_reason} onChange={updateForm}><option value="insufficient_funds">Insufficient funds</option><option value="card_expired">Card expired</option><option value="bank_declined">Bank declined</option><option value="upi_failed">UPI failed</option></select></label></div><button className="primary" disabled={isRunning}>{isRunning ? "Running model..." : "Run custom prediction"}</button></form>{customResult && <div className={`custom-result ${tone(customResult.prediction)}`}><strong>{customResult.prediction}</strong><span>{Math.round(customResult.recovery_score * 100)}% probability · {customResult.recommended_action}</span></div>}</article>
      </section>
    </main>}

    {view === "model" && <main className="workspace"><section className="page-title"><p className="eyebrow">Model Center</p><h1>Transparent ML decisions, built for responsible recovery.</h1><p>Explore the signals behind this trained recovery probability classifier.</p></section><section className="metric-grid"><Metric special label="Model" value={model?.model_type || "Loading"} note="Classification decision engine" /><Metric label="Training scenarios" value={model?.training_rows || "-"} note="Synthetic labeled recovery records" /><Metric success label="Test accuracy" value={model?.evaluation?.accuracy ? `${Math.round(model.evaluation.accuracy * 100)}%` : "Train model"} note="Held-out synthetic test split" /><Metric label="F1 score" value={model?.evaluation?.f1_score ? `${Math.round(model.evaluation.f1_score * 100)}%` : "Train model"} note="Precision and recall balance" /></section><section className="model-grid"><article className="panel"><Heading kicker="Explainability" title="Feature importance" /><p className="note">Higher bars mean the feature had more influence during training for this demo model.</p><div className="importance">{model?.feature_importance.map((item) => <div key={item.feature}><span>{item.feature}</span><i><b style={{ width: `${item.importance * 100}%` }} /></i><strong>{Math.round(item.importance * 100)}%</strong></div>)}</div></article><article className="panel responsible"><p className="panel-kicker">Responsible prototype</p><h2>What this AI does and does not do</h2><div><strong>It does</strong><p>Prioritize demo payment-failure cases, estimate recovery probability, and recommend an action.</p></div><div><strong>It does not</strong><p>Use live Razorpay data, contact customers, make financial decisions, or guarantee recovery outcomes.</p></div><aside>{model?.disclaimer}</aside></article></section></main>}
  </div>;
}

function Metric({ label, value = "-", note, special, success }) { return <article className={`metric ${special ? "special" : ""} ${success ? "success" : ""}`}><span>{label}</span><strong>{value}</strong><small>{note}</small></article>; }
function Heading({ kicker, title, side }) { return <div className="heading"><div><p className="panel-kicker">{kicker}</p><h2>{title}</h2></div>{side && <span>{side}</span>}</div>; }
function Empty({ children }) { return <div className="empty">{children}</div>; }
function Decision({ prediction }) { return <div className="decision"><div className={`decision-status ${tone(prediction.prediction)}`}><span>Recovery outlook</span><strong>{prediction.prediction}</strong><b>{Math.round(prediction.recovery_score * 100)}%</b></div><div className="facts"><span><small>Failed amount</small><strong>{money(prediction.failed_amount)}</strong></span><span><small>Days unresolved</small><strong>{prediction.days_since_failure}</strong></span><span><small>Failure reason</small><strong>{prediction.failure_reason.replaceAll("_", " ")}</strong></span></div><div className="explanation"><strong>Why the model recommends this</strong><p>{prediction.explanation}</p><ul>{prediction.key_factors.map((factor) => <li key={factor}>{factor}</li>)}</ul><small>{prediction.model_type} · {prediction.data_source}</small></div></div>; }

export default App;
