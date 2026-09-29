# ContextOS — Enterprise AI Agent & Context Ingestion Platform

ContextOS is an enterprise-grade platform that bridges client data ingestion with autonomous AI agent execution. Built on a headless Flask API Gateway and a Streamlit UI interface, ContextOS enables businesses to securely onboard clients, ingest datasets via zero-trust AWS protocols, manage structured context objects, and execute specialized AI model jobs under strict governance controls.

---

## Key Capabilities

* **Enterprise Client Management**: Onboard business clients, assign industry domains, select service plans, and register 12-digit AWS Account IDs for cross-account STS role assumption.
* **Zero-Trust Data Ingestion**:
  * **Direct Drag & Drop**: Rapid browser file uploads (CSV, JSON, TXT, PDF, XLSX) into the Context Store.
  * **Presigned S3 Upload URLs**: Time-limited S3 upload endpoints requiring no client IAM credentials.
  * **Temporary AWS Credentials**: Transfer datasets using client STS access key, secret key, and session tokens.
  * **Cross-Account IAM Role Assumption**: Zero-credential sharing ingestion assuming client IAM roles via AWS STS `AssumeRole`.
* **Structured Context Store**: Payload registry mapping JSON context objects to client IDs with category tags, ground-truth data schemas, and lifecycle management.
* **Autonomous AI Agent Engine**:
  * **Data Enrichment**: Automated entity resolution, quality scoring, and metadata attribute tagging.
  * **Anomaly Detection**: Outlier detection across transactions, inventory levels, and metric anomalies.
  * **AI Recommendations**: SKU recommendation ranking with predicted revenue lift percentages.
  * **Executive Summaries**: High-level strategic synthesis and key insights generation.
* **Operations Telemetry Dashboard**: Real-time visibility into registered clients, stored context objects, active workloads, and system health metrics.

---

## Architecture & Technology Stack

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
                     |     http://localhost:5001        |
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

* **Frontend UI**: Python Streamlit (`streamlit_app.py`)
* **API Gateway**: Python Flask (`application.py`)
* **Deployment Target**: AWS Elastic Beanstalk (Python 3.11 AL2023 / Gunicorn)

---

## Project Structure

```
context-platform/
├── application.py             # Flask API Gateway Entry Point & WSGI App
├── streamlit_app.py           # Streamlit UI Entry Point & Landing Page
├── Procfile                   # Elastic Beanstalk Process Config
├── requirements.txt           # Python Dependencies
├── .ebextensions/             # AWS Elastic Beanstalk Config Rules
│   └── 01_flask.config
├── .streamlit/                # Streamlit Configuration & Theme
│   └── config.toml
├── api/                       # Flask API Route Modules
│   ├── __init__.py
│   ├── client_routes.py       # Client Registration & Status Routes
│   ├── upload_routes.py       # Data Ingestion & AWS S3 Routes
│   ├── context_routes.py      # Context Store Registry & Payload Routes
│   └── agent_routes.py        # AI Agent Trigger & Telemetry Routes
├── pages/                     # Streamlit Multi-Page Directory
│   ├── 1_Clients.py           # Step 1: Onboarding & Client Roster
│   ├── 2_Data_Upload.py       # Step 2: Data Ingestion Pipeline
│   ├── 3_Context_Store.py     # Step 3: Context Payload Explorer
│   ├── 4_AI_Agents.py         # Step 4: AI Agent Execution Panel
│   └── 5_Dashboard.py         # Operations Telemetry Dashboard
├── utils/                     # Helper Modules
│   ├── __init__.py
│   └── api.py                 # Global CSS & API Request Wrapper
└── assets/                    # Static Assets & Screenshots
```

---

## Quick Start (Local Setup)

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

### 2. Start the Flask API Gateway
In terminal window 1:
```bash
python application.py
```
The Flask API Gateway starts at `http://localhost:5001`.

### 3. Start the Streamlit UI
In terminal window 2:
```bash
streamlit run streamlit_app.py
```
The Streamlit UI opens automatically at `http://localhost:8501`.

---

## API Reference

### Client Management
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/clients/` | List all registered clients |
| `POST` | `/api/v1/clients/register` | Register a new client organization |
| `PATCH` | `/api/v1/clients/<client_id>/status` | Update client account status |

### Data Ingestion
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/uploads/direct` | Direct file upload into Context Store |
| `POST` | `/api/v1/uploads/presigned-url` | Generate S3 presigned upload URL |
| `POST` | `/api/v1/uploads/via-client-keys` | Ingest via client temporary STS keys |
| `POST` | `/api/v1/uploads/assume-role` | Ingest via Cross-Account STS AssumeRole |

### Context Store
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/context/list` | Filter & query stored context payloads |
| `POST` | `/api/v1/context/upload` | Manually inject a JSON context payload |
| `DELETE` | `/api/v1/context/<context_id>` | Remove a context payload entry |

### AI Agents
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/agents/types` | List available AI agent model services |
| `POST` | `/api/v1/agents/trigger` | Queue an AI agent job against a context ID |
| `GET` | `/api/v1/agents/jobs` | Retrieve job list and telemetry |
| `GET` | `/api/v1/agents/status/<job_id>` | Poll job processing status and generated intelligence |

---

## AWS Elastic Beanstalk (EB) Deployment

### 1. Build Deployment Bundle
```bash
zip -r context-platform-deploy.zip . -x ".venv/*" -x ".git/*" -x "__pycache__/*"
```

### 2. Deploy via EB CLI
```bash
eb init -p python-3.11 context-platform --region us-east-1
eb create context-platform-env
eb deploy
```

---

## License
Distributed under the MIT License. See `LICENSE` for more information.
