# 🤖 AasthaSathi – Your Trusted AI Companion for Cooperative Banking

![AasthaSathi Banner](http://myaastha.in/wp-content/uploads/2021/06/slider1.jpg)

> **AasthaSathi** is an AI-powered multilingual(English/Bengali/Hindi) assistant developed for **Aastha Co-operative Credit Society**, designed to help employees and agents instantly access scheme information, policy guidelines, and live member account data — all through natural language queries.

AasthaSathi combines **Retrieval-Augmented Generation (RAG)** and **Tools(REST API calls)** to bridge the gap between static documentation and dynamic operational data.  
It represents the next generation of **Agentic AI systems for financial cooperatives**, where trust and intelligence go hand in hand.

---

## 🌟 Key Features

| Feature | Description |
|----------|--------------|
| 🧠 **RAG-Powered Knowledge Retrieval** | Answers queries using data from the Aastha website, policy PDFs, and internal manuals. |
| ⚙️ **Live Data Access via REST API** | Fetches up-to-date account and membership details securely. |
| 🔒 **Role-Based Access Control** | Employees, agents, and administrators receive context-appropriate responses. |
| 🗂️ **Cited & Verified Responses** | Each answer includes the source of truth — page, section, or API endpoint. |
| 🗣️ **Natural Conversational Interface** | Supports question-answer and follow-up conversations. |
| 🧾 **Secure & Auditable** | Logs every API call and retrieved document for transparency. |

---

## 🧭 Project Overview

When an employee asks:

> “What is the withdrawal policy for the Monthly Deposit Scheme of member 2045?”

AasthaSathi:
1. **Retrieves** relevant policy text from its document store using RAG.  
2. **Fetches** the live member’s scheme details from the core banking REST API (via MCP).  
3. **Synthesizes** a combined answer — citing both the policy clause and live data.  
4. **Responds** naturally, in a secure, auditable manner.

---

## 🏗️ System Architecture


---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| **LLM & Framework** | LangChain, LangGraph |
| **Vector Store** | ChromaDB |
| **Embeddings** | OpenAI / Gemini Embeddings |
| **LLM Reasoning** | Gemini Pro / GPT-4 |
| **API Tools** | FastAPI wrapper for REST endpoints |
| **Frontend (Demo)** | Gradio / Streamlit |
| **Auth & Security** | JWT, Role-based Access, HTTPS |
| **Deployment** | Docker, DigitalOcean |

---


## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/arghads9177/AasthaSathi.git
cd AasthaSathi
```

### Create Virtual Environment
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```
### Install Dependencies
```bash
uv add -r requirements.txt
```
### Start the Application
```bash
uvicorn app.backend.main:app --reload
```
---

## 🧩 Example Queries

| Type         | Example                                                                                           |
| ------------ | ------------------------------------------------------------------------------------------------- |
| Policy Query | “What is the early withdrawal rule for the Fixed Deposit Scheme?”                                 |
| Data Query   | “Show account details of member ID 10245.”                                                        |
| Hybrid Query | “What are the eligibility rules for Loan Scheme X, and what is member 101’s current loan status?” |

---

## 💡 Vision

AasthaSathi is designed to **empower cooperative banking employees** with the knowledge and insights they need — instantly, securely, and conversationally.
This project is a step toward **real-world AI integration in FinTech**, bridging human expertise and machine intelligence.

---

## 🧑‍💻 Author

**Argha Dey Sarkar**
Software Engineer | AI Engineer | Generative & Agentic AI Enthusiast
🔗 [LinkedIn](www.linkedin.com/in/argha-deysarkar-data-scientist)
✍️ [Medium](https://medium.com/@email2argha)
💻 [GitHub](https://github.com/arghads9177/)
