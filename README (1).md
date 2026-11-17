# 🛒 Shopit AI -- E-commerce Analytics Assistant

Shopit AI is an AI-powered e-commerce analytics assistant that helps
users explore sales, customers, products, orders, and company policies
using natural-language questions.

Instead of writing SQL queries or manually searching policy documents,
users can ask questions in a chat interface and receive answers,
business insights, and visualizations.

> **Project status:** Portfolio project. Update this README as features
> and deployment configuration evolve.

## ✨ Key Features

-   Natural-language analytics for e-commerce data.
-   AI-assisted SQL workflow for database questions.
-   Retrieval-Augmented Generation (RAG) for Shopit policy questions.
-   Business insights based on query results.
-   Bar, line, scatter, and pie chart support where configured.
-   Streamlit conversational interface with chat history.
-   Monitoring dashboard for request counts, success/failure counts,
    response time, and request categories, when configured.

## 🏗️ Architecture

``` text
                    USER
                     |
                     v
             STREAMLIT FRONTEND
                     |
                     v
                FASTAPI API
                     |
                     v
              LANGGRAPH WORKFLOW
                     |
              QUERY CLASSIFIER
                     |
          +----------+-----------+
          |                      |
          v                      v
    DATABASE ROUTE           POLICY / RAG ROUTE
          |                      |
          v                      v
     SQL WORKFLOW          DOCUMENT RETRIEVAL
          |                      |
          v                      v
     QUERY RESULTS          FAISS VECTOR STORE
          |                      |
          v                      v
     DATA ANALYSIS             GEMINI LLM
          |                      |
          +----------+-----------+
                     |
                     v
              FINAL RESPONSE
                     |
          +----------+-----------+
          |                      |
          v                      v
       INSIGHTS              VISUALIZATION
          |                      |
          +----------+-----------+
                     |
                     v
               STREAMLIT UI
```

The exact graph nodes and routing depend on the implementation in
`graph.py` and the agent modules.

## 🧰 Technology Stack

  Area                  Technology
  --------------------- -------------------
  Language              Python
  Frontend              Streamlit
  Backend API           FastAPI
  API server            Uvicorn
  Agent orchestration   LangGraph
  LLM                   Google Gemini API
  LLM framework         LangChain
  Database              SQLite
  Data processing       Pandas
  Visualization         Matplotlib
  Vector store          FAISS
  Document processing   PyPDF
  HTTP requests         Requests
  Logging               Python logging

## 📁 Project Structure

This is a representative structure. Keep the actual filenames and
folders in your repository; some modules may have different names.

``` text
AI ANALYTICS PROJECT/
│
├── streamlit_app.py       # Streamlit user interface
├── api.py                 # FastAPI application
├── api_client.py          # Frontend-to-backend communication
├── graph.py               # LangGraph workflow
├── monitoring.py          # Request logging and metrics
│
├── router.py              # Query routing
├── sql_agent.py            # SQL workflow
├── query_executor.py      # SQL execution
├── database_agent.py      # Database question handling
├── response_agent.py      # Analysis and response generation
├── rag.py                 # Policy retrieval and answering
├── INGEST.PY              # Ingestion script, if present
│
├── DATA/                  # CSV datasets and policy PDFs
├── vectorstore/           # Saved FAISS index
├── logs/                  # Application logs and metrics
├── shopit.db              # SQLite database
│
├── requirements.txt       # Python dependencies
├── .env                   # Local secrets (never commit)
├── .gitignore             # Git exclusions
└── README.md              # Project documentation
```

## ⚙️ Prerequisites

-   Python 3.10 or a compatible version for your dependencies.
-   Git.
-   VS Code (recommended).
-   A Google Gemini API key.
-   Internet access for model/API requests.

## 🚀 Installation and Setup

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR_USERNAME/shopit-ai-analytics.git
cd shopit-ai-analytics
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows PowerShell:**

``` powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

``` cmd
venv\Scripts\activate.bat
```

### 3. Install dependencies

``` bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

``` env
GOOGLE_API_KEY=your_gemini_api_key
```

Add any other environment variables required by your implementation.

**Never upload `.env` or API keys to GitHub.**

### 5. Check required data files

Make sure the files required by your implementation are present:

-   SQLite database, if the application uses a prebuilt database.
-   CSV datasets and policy PDFs in the expected data folder.
-   FAISS index files, if `rag.py` loads an existing vector store.

If the project requires an ingestion step to create the database or
vector store, run the appropriate ingestion script. Avoid rebuilding the
vector store unnecessarily on every application startup.

## ▶️ Running the Application Locally

The project uses two services: FastAPI for the backend and Streamlit for
the frontend.

### 1. Start FastAPI

Open the first terminal:

``` powershell
python -m uvicorn api:app --reload
```

The backend should be available at:

``` text
http://127.0.0.1:8000
```

API documentation:

``` text
http://127.0.0.1:8000/docs
```

### 2. Start Streamlit

Open a second terminal, activate the same virtual environment, and run:

``` powershell
streamlit run streamlit_app.py
```

Streamlit normally opens at:

``` text
http://localhost:8501
```

Keep both services running while using the application.

## 💬 Example Questions

### Database and sales analytics

-   Which products generated the highest revenue?
-   Show the top 5 customers by total spending.
-   Which products have the highest sales?
-   Analyze the sales performance of our products.

### Policy and document questions

-   What is Shopit's shipping policy?
-   What is the return and refund policy?
-   Can a customer cancel an order?
-   What is the seller policy?

Answer availability depends on the data and policy documents included in
the project.

## 📊 Monitoring

The monitoring module records operational information about requests.
Depending on the implementation, this can include:

-   Request completion and failure.
-   Request category.
-   Request duration.
-   Whether an answer was generated.

The Streamlit Monitoring Dashboard reads aggregated metrics from the
backend monitoring endpoint. It may display total requests, successful
and failed requests, success rate, average response time, and request
category distribution.

The exact metrics depend on the monitoring API and the data it stores.

## 🔐 Environment Variables and Security

  Variable           Purpose
  ------------------ -------------------------------------------------
  `GOOGLE_API_KEY`   Authenticates requests to Google Gemini
  `API_BASE_URL`     Backend URL used by the frontend, if configured

Use `.env` for local development. For cloud deployment, configure
secrets through the hosting provider.

Do not commit API keys, passwords, private customer information, or
sensitive production data.

## ☁️ Deployment

A possible portfolio deployment arrangement is:

  Component            Hosting option
  -------------------- ---------------------------
  Source code          GitHub
  Streamlit frontend   Streamlit Community Cloud
  FastAPI backend      Render
  LLM services         Google Gemini API

General deployment steps:

1.  Push the project to GitHub.
2.  Deploy FastAPI as a web service.
3.  Configure required backend environment variables.
4.  Configure the frontend API client to use the public backend URL
    instead of `127.0.0.1`.
5.  Deploy `streamlit_app.py` using Streamlit Community Cloud.
6.  Add the backend URL and any frontend-required secrets to Streamlit
    secrets.
7.  Test database queries, policy retrieval, charts, and monitoring.

**Free-tier limitations:** Hosting providers may sleep inactive
services, impose resource limits, or use temporary storage. SQLite data
changes, FAISS files, and logs need an appropriate persistence strategy
for production. Check current provider terms before deploying.

## 🧪 Troubleshooting

  -----------------------------------------------------------------------
  Problem                             What to check
  ----------------------------------- -----------------------------------
  Streamlit cannot connect to FastAPI Confirm FastAPI is running and
                                      check the configured API URL

  FastAPI returns HTTP 500            Inspect the FastAPI terminal or
                                      hosting logs for the traceback

  Gemini quota error                  Check API quota and model
                                      availability

  Policy questions return no useful   Verify policy PDFs, FAISS files,
  answer                              and retrieval configuration

  Database query fails                Check database path, table names,
                                      and SQL execution logs

  Charts do not appear                Check visualization metadata and
                                      returned data columns

  Monitoring dashboard is empty       Check the monitoring endpoint and
                                      whether requests have been recorded
  -----------------------------------------------------------------------

## 🛣️ Possible Future Improvements

-   Persistent cloud database instead of local SQLite.
-   Persistent storage for monitoring metrics.
-   API authentication and request rate limiting.
-   Automated tests for SQL generation and query routing.
-   Evaluation of RAG retrieval quality and answer correctness.
-   Better observability and error tracking.
-   Docker-based deployment.
-   CI/CD using GitHub Actions.
-   User authentication and multi-user chat history.

## 👨‍💻 Author

**Krishna Kartik Mishra**

AI / ML Engineering and Data Analytics Projects

GitHub: `https://github.com/YOUR_USERNAME`

LinkedIn: `https://www.linkedin.com/in/YOUR_PROFILE/`

## 📄 License

Choose and add a license before allowing others to reuse or distribute
this project. For example, you can use the MIT License by adding a
`LICENSE` file.

------------------------------------------------------------------------

**If you find this project useful, consider giving the repository a star
⭐**
