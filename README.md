# ContextOS — Enterprise AI Agent & Context Ingestion Platform

ContextOS is a secure, end-to-end platform designed to bridge enterprise client data with autonomous AI agents. Built with a **Flask API Gateway** and a **Streamlit UI**, ContextOS allows businesses to onboard clients, securely ingest data via zero-trust AWS protocols, manage structured context objects, and execute specialized AI model workloads.

---

## 🔄 End-to-End Workflow Flowchart

```mermaid
flowchart LR
    A[Step 1: Client Onboarding] -->|Register Client & AWS IAM Role| B[Step 2: Data Upload]
    B -->|Direct Upload / Presigned URL / STS / AssumeRole| C[Step 3: Context Store]
    C -->|Select Context Payload & Trigger Agent| D[Step 4: AI Agent Jobs]
    D -->|Generated Insights & Raw Telemetry| E[Step 5: Operations Dashboard]

    style A fill:#3b82f6,color:#fff,stroke-width:2px
    style B fill:#6366f1,color:#fff,stroke-width:2px
    style C fill:#8b5cf6,color:#fff,stroke-width:2px
    style D fill:#ec4899,color:#fff,stroke-width:2px
    style E fill:#10b981,color:#fff,stroke-width:2px
```

---

## 🎯 What Each Tab Does & How to Proceed

### 🏢 **Tab 1: Clients (`1_Clients.py`) — Client Onboarding**
* **What it does:** Register enterprise client profiles, set up company metadata, assign service tiers, and configure 12-digit AWS Account IDs for cross-account IAM role assumption.
* **How to proceed:** 
  1. Go to **Clients** tab.
  2. Fill out the **Client Onboarding Form** (Company Name, AWS Account ID, Region, Tier).
  3. Click **Register Client**. You can view all registered clients in the roster tab.

---

### 📤 **Tab 2: Data Upload (`2_Data_Upload.py`) — Zero-Trust Ingestion**
* **What it does:** Ingest enterprise datasets into the platform using 4 flexible ingestion methods depending on client security needs.
* **Ingestion Methods:**
  * **Direct Drag & Drop:** Upload CSV, JSON, TXT, PDF, or XLSX files directly.
  * **Presigned S3 URLs:** Generate temporary time-limited S3 URLs for zero-credential browser uploads.
  * **Temporary AWS STS Keys:** Transfer files using client-provided STS access key, secret key, and session tokens.
  * **Cross-Account AWS AssumeRole:** Zero-trust ingestion by assuming client IAM roles via AWS STS `AssumeRole`.
* **How to proceed:**
  1. Select a registered Client from the dropdown.
  2. Pick an ingestion method (e.g., *Direct Drag & Drop*).
  3. Upload your dataset — it automatically converts into a structured Context Payload in the Context Store.

---

### 🗄️ **Tab 3: Context Store (`3_Context_Store.py`) — Data Payload Explorer**
* **What it does:** View, filter, query, and manage all ingested client context objects.
* **How to proceed:**
  1. Filter context payloads by Client ID or Category.
  2. Click on any context item to inspect its JSON schema, payload size, creation timestamp, and raw payload data.
  3. Easily copy a `Context ID` to use when launching AI Agent jobs.

---

### 🤖 **Tab 4: AI Agents (`4_AI_Agents.py`) — Autonomous AI Workloads**
* **What it does:** Execute specialized AI agent models against stored context payloads and view real-time telemetry and generated intelligence.
* **Available AI Agents:**
  * 🪄 **Data Enrichment:** Automated entity resolution, quality scoring (`98.4%`), and metadata tagging.
  * ⚠️ **Anomaly Detection:** Outlier detection across transactions, inventory levels, and metric anomalies.
  * 🛍️ **Recommendation Engine:** SKU recommendation ranking with predicted revenue lift percentages.
  * 📊 **Executive Summaries:** High-level strategic synthesis and key insights generation.
* **How to proceed:**
  1. Pick a Client ID and Context ID.
  2. Select an AI Agent type (e.g., *Data Enrichment* or *Anomaly Detection*).
  3. Click **Trigger AI Agent Job**.
  4. Switch to the **Job Monitor & Telemetry** tab to inspect generated insights and raw JSON responses.

---

### 📊 **Tab 5: Dashboard (`5_Dashboard.py`) — Operations Telemetry**
* **What it does:** Provides a high-level operational command center showing live platform metrics, active client statistics, total context storage usage, and active AI agent jobs.
* **How to proceed:**
  * Check overall system health, total registered clients, stored context payloads, and executed agent workloads at a glance.

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
* Python 3.10 or higher
* `pip` and `virtualenv`

### 1. Clone & Set Up Environment
```bash
git clone https://github.com/shivanshinigam/context-platform.git
cd context-platform

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Services

You can run both Flask backend and Streamlit frontend using the unified startup script:
```bash
./start_services.sh
```

Or run them individually:
* **Flask API Gateway (Port 8000):** `python application.py`
* **Streamlit UI (Port 8501):** `streamlit run streamlit_app.py`

---

## 🏗️ Architecture & Technology Stack

```
                  +----------------------------------+
                  |       Streamlit Frontend         |
                  |     http://localhost:8501        |
                  +-----------------+----------------+
                                    |
                                    | HTTP REST API
                                    v
                  +-----------------+----------------+
                  |        Flask API Gateway         |
                  |     http://localhost:8000        |
                  +-----------------+----------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+----------------------+   +----------------------+   +----------------------+
|  Client Directory    |   |    Context Store     |   |   AI Agent Engine    |
|  AWS STS Management  |   | Zero-Trust Ingest    |   | Workload Processor   |
+----------------------+   +----------------------+   +----------------------+
```

* **Frontend UI:** Streamlit (`streamlit_app.py`)
* **API Gateway:** Flask (`application.py`)
* **Deployment Target:** AWS Elastic Beanstalk (Python 3.11 AL2023 / Nginx Reverse Proxy / Gunicorn)

---

## 📄 License
Distributed under the MIT License.
