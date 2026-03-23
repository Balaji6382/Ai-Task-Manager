# 🧠 AI Task Manager Agent Version 1

> **An enterprise-grade, multi-agent AI system** that transforms unstructured natural language into structured, prioritized, and searchable tasks — powered entirely by **local LLMs, LangGraph orchestration, and FAISS vector search**.

---

## 🚀 Why This Project?

Traditional task managers are **manual, rigid, and inefficient**.

This system introduces an **AI-first workflow**:

> Just describe your task — the system handles everything else.

```text
"Fix the memory leak before production deployment tomorrow"
```

### ✅ Automatically Extracted:

* 📂 Category → Development
* ⚡ Priority → Critical
* 🧾 Summary → Fix memory leak
* 🏷 Tags → ["bug", "performance"]
* ⏱ Estimated Duration → AI-generated

---

## ✨ Core Features

### 🧠 Intelligent Task Understanding

* Accepts **free-form natural language**
* Converts into **clean, structured JSON (Pydantic enforced)**

---

### ⚙️ Multi-Agent Pipeline (LangGraph)

A **modular AI workflow**, not a single LLM call:

| Stage | Agent            | Responsibility             |
| ----- | ---------------- | -------------------------- |
| 1     | Input Validator  | Ensures valid input        |
| 2     | Categorizer      | Assigns category, priority |
| 3     | Quality Reviewer | Verifies correctness       |
| 4     | Storage Layer    | Saves to vector DB         |

---

### 🔍 Semantic Task Search (FAISS)

* Meaning-based retrieval (not keyword matching)
* Enables intelligent queries like:

  ```
  FIND backend performance issues
  ```

---

### 🔒 Fully Local AI System

* Powered by **Ollama**
* No external APIs
* Zero cost + full privacy

---

### 📊 Interactive Dashboard (Streamlit)

* Task creation UI
* Search interface
* Task management (update/delete)
* Real-time analytics dashboard

---

## 🧱 System Architecture

```
User Input
   ↓
LangGraph Workflow (task_manager_graph.py)
   ├── Input Validation
   ├── Categorization (LLM)
   ├── Quality Check (LLM)
   ↓
Structured Task (Pydantic Model)
   ↓
Embedding Generation (Ollama)
   ↓
FAISS Vector Store
   ↓
Streamlit UI / CLI Interface
```

---

## 🛠 Tech Stack

| Layer            | Technology         | Purpose                    |
| ---------------- | ------------------ | -------------------------- |
| 🧠 LLM           | Ollama (llama3:8b) | Task understanding         |
| 🔢 Embeddings    | nomic-embed-text   | Semantic vectors           |
| 🔄 Orchestration | LangGraph          | Multi-agent pipeline       |
| 📦 Validation    | Pydantic           | Reliable structured output |
| 🗄 Storage       | FAISS              | Vector database            |
| 🎨 Frontend      | Streamlit          | UI dashboard               |

---

## 📂 Project Structure

```
AI_Task_Manager_Agent-main/
│
├── agents/                     # AI logic (core intelligence)
│   ├── task_categorizer.py     # LLM categorization agent
│   ├── task_manager_graph.py   # LangGraph workflow
│
├── core/                       # Core system modules
│   ├── config.py               # Configuration
│   ├── models.py               # Pydantic schemas
│   ├── vector_store.py         # FAISS operations
│
├── data/                       # Stored vector index
│
├── app.py                      # Streamlit frontend
├── main.py                     # CLI interface
├── pipeline.py                 # Pipeline runner
│
├── requirements.txt
└── README.md
```

---

## ⚡ Installation & Setup

### 1️⃣ Prerequisites

* Python **3.10+**
* Ollama running locally:

```
http://127.0.0.1:11434
```

---

### 2️⃣ Setup Environment

```bash
git clone https://github.com/Balaji6382/Ai-Task-Manager.git
cd AI_Task_Manager_Agent-main

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

---

### 3️⃣ Install Models

```bash
ollama pull llama3:8b
ollama pull nomic-embed-text
```

---

### 4️⃣ Run Application

#### ▶ CLI Mode

```bash
python main.py
```

#### ▶ Web UI

```bash
streamlit run app.py
```

---

## 💻 Usage

### ➕ Add Task

```text
ADD Review API performance before release
```

---

### 🔍 Search Tasks

```text
FIND database optimization
```

---

## 📊 Dashboard Capabilities

* 📈 Total tasks overview
* ✅ Completion rate
* ⚡ Priority distribution
* 📂 Category breakdown
* 🔄 Status tracking

---

## 🔄 Pipeline Design (Key Strength)

```
Input → Validate → Categorize → Review → Store → Retrieve
```

### 🎯 Why This Matters

* Prevents LLM hallucinations
* Ensures structured outputs
* Adds reliability layer
* Mimics real-world AI systems

---

## 🧪 Example Output

```json
{
  "task_id": "a1b2c3",
  "summary": "Optimize database queries",
  "category": "Development",
  "priority": "High",
  "status": "Pending"
}
```

---

## 🌟 Highlights (Resume / Interview Ready 🚀)

* Multi-agent AI architecture (LangGraph)
* Fully local LLM system (Ollama)
* Semantic search using FAISS
* Modular & scalable design
* CLI + Web UI integration
* Production-style pipeline engineering

---

## 🔮 Future Enhancements

* FastAPI backend (production APIs)
* JWT-based authentication
* Multi-user support
* Task deadlines & reminders
* Docker & Kubernetes deployment
* Real-time notifications

---

## 📺 Demo

🎥 

---
## 💡 Final Note

This project is more than a task manager —
it’s a **complete AI system design showcasing**:

* LLM orchestration
* Structured AI outputs
* Semantic retrieval
* Scalable architecture

---


