# RevenueRecover AI

RevenueRecover AI is a full-stack failed-payment recovery dashboard. It analyzes failed payment cases, estimates the likelihood of recovery with a machine-learning model, and recommends the next action and communication channel.

> Demo note: this project uses synthetic customer and recovery data. It is a working prototype designed for future integration with real payment events and recovery workflows.

## What it does

- Shows a portfolio view of failed-payment cases and recovery opportunity.
- Generates ML-backed recovery probabilities for existing and custom cases.
- Recommends a recovery action, including reminder, discount offer, or support escalation.
- Selects a suggested outreach channel: email, WhatsApp, or support call.
- Explains the main signals behind each recommendation.
- Provides a polished React dashboard for reviewing cases and simulating action execution.
- Ranks a recovery queue by expected recovered value, not just payment size.
- Includes a three-step AI-guided recovery playbook for each selected case.
- Shows model feature importance and evaluation metrics in a transparent Model Center.

## Architecture

```text
React + Vite dashboard
        |
        | HTTP API
        v
FastAPI backend
        |
        +-- Customer demo data
        +-- Random Forest recovery model
        +-- Recommendation and explanation service
```

## Run locally

### 1. Install Python dependencies

```powershell
pip install -r requirements.txt
```

### 2. Train or refresh the demo ML model

```powershell
python ml/train_model.py
```

### 3. Start the API

```powershell
uvicorn backend.app:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

### 4. Start the dashboard in a second terminal

```powershell
cd frontend
npm install
npm run dev
```

Dashboard: `http://localhost:5173`

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/customers` | Lists failed-payment cases |
| GET | `/predict/{customer_id}` | Returns an explainable ML prediction for a customer |
| POST | `/predict` | Runs a prediction for manually entered data |
| GET | `/recoveries/summary` | Returns portfolio-level recovery counts |
| GET | `/actions/{customer_id}` | Returns a recommended action and channel |

## ML approach

The model is a `RandomForestClassifier` trained on synthetic labeled recovery scenarios. It uses failed amount, days since failure, and failure reason as input features. Predictions include a probability, an action recommendation, confidence band, and human-readable contributing factors.

The training workflow uses a deterministic synthetic dataset and keeps a held-out test split. The latest demo model reports its accuracy, precision, recall, and F1 score in `ml/model_metadata.json`, which is displayed in the dashboard. These metrics evaluate synthetic data only and should not be interpreted as real-world collection performance.

This is a prototype ML workflow. Real-world deployment would use consented historical payment and recovery outcomes, bias checks, monitoring, encrypted storage, and controlled campaign integrations.

## Product views

- **Overview**: customer recovery queue, exposure metrics, and an explainable AI decision brief.
- **Recovery Intelligence**: failure-reason analysis, predicted outcome distribution, expected-recovery priority queue, scenario simulator, and action playbooks.
- **Model Center**: ML feature importance, synthetic test metrics, and responsible-AI boundaries.

## Demo data and safety

The repository includes 12 fictional customer cases. No real customer data, payment credentials, API secrets, or personal financial data are used. The recovery-action button and outreach playbook are simulations; the prototype does not send any messages or make payment changes.

## Future scope

- Razorpay/payment-webhook integration
- Secure database and authentication
- Real email, WhatsApp, and support workflow integrations
- Model monitoring and retraining on validated production data
- Recovery campaign analytics and audit logs
