# Real-Time Explainable Credit Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

**A submission for the CredTech Hackathon, organized by The Programming Club, IITK, and powered by Deep Root Investments.**

---

## 🚀 Live Demo & Walkthrough

* **Live Application URL:** `[(https://real-time-credit-analytics-1.onrender.com)]`
* **Video Walkthrough:** `[(https://youtu.be/fJqxUBaN1kc)]`

---

## 📜 The Problem: The Lagging & Opaque Nature of Credit Ratings

Traditional credit ratings are the bedrock of financial markets, yet they suffer from critical flaws: they are updated infrequently, based on opaque methodologies, and often lag behind significant real-world events. This information gap creates market inefficiencies and mispriced risk. In an era of abundant, high-frequency data, there is a clear opportunity to leverage AI for a more dynamic, transparent, and evidence-backed assessment of creditworthiness.

## 💡 Our Solution: A Transparent, Real-Time Platform

This platform is a real-time, explainable credit intelligence system designed to address these challenges. It ingests multi-source data to generate dynamic credit scores, and crucially, provides clear, feature-level explanations for every score, transforming the "black box" into an interactive and transparent tool for analysts.

---

## ✨ Key Features

### 1. High-Throughput Data Ingestion & Processing
* **Multi-Source Ingestion:** Gathers data from diverse, high-frequency sources including Yahoo Finance (financials), FRED (macroeconomic data), and NewsAPI (unstructured news).
* **Real-Time Processing:** Implements robust pipelines for data cleaning, normalization, and feature engineering (e.g., moving averages, sentiment scores).
* **Scalable & Fault-Tolerant:** The architecture is designed to handle dozens of issuers and is resilient to data source outages.

### 2. Adaptive & Explainable Scoring Engine
* **Custom Scoring:** Assigns a creditworthiness score on a custom 0-100 scale, where higher is better.
* **Interpretable by Design:** Utilizes a **Decision Tree** model, ensuring that every prediction is inherently transparent and can be traced through a series of simple rules.
* **Continuous Improvement:** The system is designed for frequent retraining to adapt to new market conditions.

### 3. Comprehensive Explainability Layer
* **Feature Contribution:** Clearly shows the features that were most influential in determining the score.
* **Event-Driven Reasoning:** Correlates shifts in the score with real-world events identified in unstructured news data.
* **Plain-Language Summaries:** The Decision Tree's logic is presented in a human-readable format, making it accessible to non-technical stakeholders.

### 4. Interactive Analyst Dashboard
* **Modern UI:** A clean, responsive dashboard built with **React, Next.js, and Tailwind CSS**.
* **Insightful Visualizations:** Features interactive charts for score trends and clear tables for feature importance and event logs.
* **The "Why":** The dashboard's primary focus is to answer "Why was this score assigned?" by presenting the model's decision path alongside the data.

---

## 🌐 APIs & Data Sources

This project integrates several external APIs to gather a rich, multi-faceted dataset.

| API / Data Source | Data Provided | Integration Method |
| :--- | :--- | :--- |
| **Yahoo Finance** | Daily stock market data (OHLC, Volume) for listed companies. | `yfinance` Python library |
| **FRED** | Key U.S. macroeconomic indicators (e.g., Treasury rates, CPI). | `fredapi` Python library |
| **NewsAPI** | Real-time news headlines for companies and market events. | Python `requests` library |

---

## 🏗️ System Architecture & Technology Rationale


![System Architecture Diagram](https://github.com/Sanket-1120/real-time-credit-analytics/blob/3b506287320f40af5a1e28c4e699013c3245dbe5/assets/Project_architecture.jpg)

### Data Flow
```
External APIs      [Ingestion Scripts]      [Supabase DB]      [FastAPI Backend]      [React Frontend]
(Yahoo, FRED)──> (Python Schedulers) ──> (Raw/Processed) ──> (Loads Data)  <── (Fetches Score)
      │                                       │                  │ (ML Model)           │
      └───> (NewsAPI) ────> (NLP/Sentiment) ──┘                  └──> (Score + Exp.) ───> (Displays Insight)
```

### Technology Rationale
| Component     | Technology        | Why We Chose It                                                                                               |
| :------------ | :---------------- | :------------------------------------------------------------------------------------------------------------ |
| **Backend** | **FastAPI** | For its high performance, asynchronous support, and automatic API documentation, which accelerates development. |
| **Frontend** | **Next.js (React)** | For its powerful features like server-side rendering and a seamless developer experience for building modern UIs. |
| **Database** | **Supabase (PostgreSQL)** | Provides a generous free tier, a user-friendly interface, and auto-generated APIs, acting as a rapid backend-as-a-service. |
| **ML Model** | **Scikit-learn** | The industry standard for classical ML in Python. Its Decision Tree offers a perfect balance of performance and built-in explainability. |
| **Deployment** | **Docker, Vercel, Render** | **Docker** ensures reproducibility. **Vercel** is optimized for Next.js frontends. **Render** offers a simple, free way to deploy Dockerized backends. |

---

## 🎯 Key Design Tradeoffs
Our most critical strategic decision was the choice of the machine learning model. We considered both a Random Forest and a high-performance LightGBM model.

To make an informed decision, we trained both models on the same historical dataset and evaluated their performance using Mean Squared Error (MSE), where lower is better.

* **Random Forest MSE:** 0.000920
* **LightGBM MSE:** 0.000993

The Random Forest model performed slightly better on our specific dataset. For a hackathon focused on explainability and robustness, a model that is both accurate and reliable is superior. We consciously traded a potential small increase in training speed for better predictive accuracy and native explainability with SHAP, which we believe aligns perfectly with the core spirit of this challenge.

---

## ⚙️ Running the Project Locally

### Prerequisites
* Python 3.11+
* Node.js and npm
* Git
* Docker Desktop

### 1. Setup
```bash
# Clone the repository
git clone [https://github.com/Sanket-1120/real-time-credit-analytics.git](https://github.com/Sanket-1120/real-time-credit-analytics.git)
cd real-time-credit-analytics

# Create a .env file in the root directory and add your secret keys
# (DB credentials, API keys, etc.)
cp .env.example .env
# Now, edit the .env file with your actual keys
```
### 2. Run with Docker (Recommended)
This is the simplest way to run the entire application.
```bash
# Build and start all services
docker-compose up --build
```
The backend will be available at `http://localhost:8000`.

The frontend will be available at `http://localhost:3000`.

### 3. Manual Setup
**Backend (Terminal 1)**
```bash
# Create a Python virtual environment
python -m venv venv
# On Windows use venv\Scripts\activate
source venv/bin/activate 

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.main:app --reload
```
**Frontend (Terminal 2)**
```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies and run
npm install
npm run dev
```
---

## ✨ Future Extensions

* **Automated Retraining Pipeline:** Use GitHub Actions to automatically retrain and deploy the model on a weekly basis.
* **Advanced NLP for Event Detection:** Move beyond sentiment to classify specific events (e.g., M&A, debt restructuring, executive changes).
* **Alternative Datasets:** Integrate satellite imagery or trade flow data to capture non-traditional risk signals.




