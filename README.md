# 🧠 IntelliBrowse – AI Web Navigator Agent

> “Search smarter, browse faster, and learn seamlessly — powered by local AI.”

---

## 🧩 a) Problem Statement Reference

### 🧠 Problem Statement Chosen  
**Web Navigator AI Agent** – Build an AI agent that can take natural language instructions and autonomously drive the web on a local computer.

### 💡 Reason to Choose the Problem Statement  
We selected this challenge because it merges our core expertise in **AI, browser automation, and full-stack development**. It demonstrates how locally running LLMs can interpret human instructions, automate browser actions, and extract structured insights — all **without cloud dependency**, ensuring privacy and offline usability.

---

## 🚀 b) Solution Overview

### 🧭 Proposed Approach (2–3 lines)  
IntelliBrowse uses a **local LLM (Ollama + Mistral)** to convert natural-language commands into executable plans, which are carried out by a **Playwright-based browser controller**. Results are parsed, stored, and returned to a **React frontend** for visualization and download.

### ⚙️ Key Features / Modules  
- **LLM Planner:** Converts user instructions into structured JSON plans.  
- **Browser Controller:** Uses Playwright to automate real web interactions.  
- **Extractors:** Domain-specific scrapers for Amazon, Flipkart, and Web.  
- **Search Dock UI:** Modern, animated interface for query input and results.  
- **Dual Modes:**  
  - *Product Mode* → Amazon/Flipkart grid view  
  - *Research Mode* → Web article list view  
- **Download Center:** Export results as `.csv` or `.json` files from database.  
- **Offline Execution:** Entire system runs locally (no external API calls).  

---

## 🏗️ c) System Architecture

### 🧩 Architecture Diagram / Workflow
```

User Query
│
▼
React + Tailwind Frontend ──► FastAPI Backend ──► LLM Planner (Ollama + Mistral)
│
▼
Playwright Browser
│
▼
Data Extraction Layer
│
▼
SQLite Database (navigator.db)
│
▼
Structured Results → JSON/CSV → Download UI

````

### 🔁 Data Flow Explanation  
1. **Input:** User submits a query in plain English.  
2. **Planning:** FastAPI invokes the LLM planner to infer intent (`shop`, `learn`, `explore`, `news`).  
3. **Execution:** Browser Controller (Playwright) navigates and extracts relevant information.  
4. **Storage:** Parsed results are saved to `data/navigator.db`.  
5. **Frontend Rendering:** React components render grid or list view.  
6. **Download:** User can download results in CSV or JSON format via `/download/...` endpoints.

---

## 🧰 d) Technology Stack

| Layer | Tools / Frameworks |
|-------|--------------------|
| **Backend** | Python 3 · FastAPI · Playwright · Pydantic · SQLite |
| **Frontend** | React + TypeScript · Vite · Tailwind CSS v4 · Framer Motion |
| **Database** | SQLite (`navigator.db`) |
| **ML / AI Frameworks** | Ollama · Mistral LLM |
| **APIs / Libraries** | Axios · Sonner (Toast UI) · Lucide Icons · AsyncIO · CSV / JSON exporters |

---

## 🧮 e) Algorithms & Models

| Component | Description |
|------------|-------------|
| **Algorithm(s) Chosen** | LLM-based semantic planner generating normalized JSON schema |
| **Reason for Choice** | Provides flexible understanding of user queries while remaining locally executable |
| **Model Training & Testing Approach** | Utilizes pretrained Mistral model via Ollama; evaluated on multiple test prompts (“laptops under 50 k”, “AI in healthcare”) to verify correct intent & structured plan generation |

---

## 📊 f) Data Handling

| Stage | Details |
|--------|----------|
| **Data Sources Used** | Amazon · Flipkart · Web (DuckDuckGo / real pages) |
| **Preprocessing Methods** | HTML parsing, price normalization, duplicate removal, text cleaning |
| **Storage / Pipeline Setup** | Results inserted into `navigator.db` → retrieved for download or display; exports saved to `data/` folder (`.csv`, `.json`) |

---

## 🧱 g) Implementation Plan

### 🪜 Initial Setup & Environment  
- Create virtual environment and install dependencies (`FastAPI`, `Playwright`, `Ollama`).  
- Configure Tailwind v4 + Vite for React frontend.  
- Initialize SQLite DB (`navigator.db`).

### ⚙️ Core Module Development  
- Implement `plan_from_instruction()` → LLM planner.  
- Develop `BrowserController` → page automation handler.  
- Build extractors: `amazon.py`, `flipkart.py`, `web.py`.  

### 🔗 Integration & Testing  
- Connect frontend search box (`SearchDock`) with FastAPI `/orchestrate` endpoint.  
- Validate JSON/CSV exports.  
- Add Sonner toasts for network errors or success.

### 🚀 Final Deployment-ready Build  
- Dockerfile for combined backend + frontend build.  
- Local run:  
  ```bash
  ollama run mistral &
  uvicorn app.main:app --reload
  npm run dev

## 🧪 h) Performance & Validation

| Metric                 | Strategy                                                                                                     |
| ---------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Evaluation Metrics** | Response latency < 5 s per query; 95 % parsing accuracy on product pages                                     |
| **Testing Strategy**   | Unit testing of extractor functions; end-to-end runs via sample commands; visual validation through frontend |

---

## ☁️ i) Deployment & Scalability

### 🧩 Deployment Plan

* **Local Mode:** Runs fully offline with Ollama + Playwright.
* **Dockerized Mode:** Combined container for backend + frontend.
* **Optional Cloud Mode:** Can be hosted with headless browser instances (e.g., Render / Railway / AWS EC2).

### 📈 Scalability Considerations

* Modular extractors for adding new websites easily.
* Task queue (Celery + Redis) for parallel searches.
* Persistent caching of search results for faster re-queries.

## 📁 Folder Structure

```
AI-Web-Navigator/
│
├── server/
│   ├── app/
│   │   ├── main.py
│   │   ├── browser/
│   │   │   └── controller.py
│   │   ├── skills/
│   │   │   ├── extractors/
│   │   │   │   ├── amazon.py
│   │   │   │   ├── flipkart.py
│   │   │   │   └── web.py
│   │   ├── llm/
│   │   │   ├── planner.py
│   │   │   └── prompts.py
│   │   └── services/
│   │       └── aggregator.py
│   ├── data/
│   │   └── navigator.db
│   ├── runs/
│   └── .venv/
│
└── client/
    ├── index.html
    ├── package.json
    ├── tailwind.config.ts
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── index.css
        ├── lib/
        │   └── api.ts
        ├── components/
        │   ├── SearchDock.tsx
        │   ├── ProductCard.tsx
        │   ├── ResultsGrid.tsx
        │   ├── ResultsList.tsx
        │   ├── ThemeToggle.tsx
        │   └── LoadingDots.tsx
        └── types/
            ├── product.ts
            ├── research.ts
            └── api.ts
```

### 🌟 *“IntelliBrowse — Where AI meets effortless exploration.”*

**Developed by Team CIVICAURA | SKCET | HackXlerate 2025**

