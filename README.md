# 🌍 WanderAI — AI-Powered Multi-Agent Trip Planner

An intelligent travel planning platform powered by **FastAPI**, **LangGraph**, **Google Gemini**, **SQLite**, and modern **Vanilla JavaScript (HTML5/CSS3)**. 

WanderAI automatically generates realistic, day-by-day travel itineraries with verified landmarks, intercity transit routing, detailed group budget estimation, and seasonal packing checklists.

---

## 🏗️ Architecture & Multi-Agent Workflow

WanderAI coordinates travel planning using a 7-agent hierarchical pipeline orchestrated with **LangGraph**:

```
                       USER TRIP INPUT
                              ↓
                FastAPI Backend (/api/plan-trip)
                              ↓
                   LangGraph StateGraph
                              ↓
         ┌────────────────────┼────────────────────┐
         ↓                    ↓                    ↓
  Destination Agent      Budget Agent       Preferences Agent
(Viability & Circuits) (Financial Strategy) (Pacing & Style)
         ↓                    ↓                    ↓
         └────────────────────┼────────────────────┘
                              ↓
                    Research / Search Agent
                (Verified Sights & Curated POIs)
                              ↓
                     Itinerary Generator
            (Day-by-Day Schedule & Travel Legs)
                              ↓
                     Budget Calculator
          (Itemized Expenses & Shortfall Analysis)
                              ↓
                       Final Planner
          (Dossier Assembly & Packing Checklist)
                              ↓
           SQLite Database (`backend/data/trips.db`)
                              ↓
              Frontend Dossier & UI Display
```

### Agent Roles & Responsibilities

| Agent | Responsibility |
| :--- | :--- |
| **Destination Agent** | Classifies destination type (Single City, State/Region, Multi-City), determines geographic viability, and selects logical circuit hubs. |
| **Budget Agent** | Formulates financial strategy based on target budget, traveler party size, duration, and currency exchange rates. |
| **Preferences Agent** | Tailors the itinerary style according to traveler profile (Solo, Couple, Family with Kids, Friends), preferred pace, and interests. |
| **Research Agent** | Curates verified, real-world attractions, cultural landmarks, and dining hotspots for each destination hub. |
| **Itinerary Generator** | Builds an optimized day-by-day schedule with morning, afternoon, and evening activities, intercity travel legs, transit guidelines, and overnight stays. Powered by Google Gemini with fallback to a built-in heuristic routing engine. |
| **Budget Calculator** | Computes itemized expenses (intercity transport, lodging, meals, transit, activities, contingency), enforces strict mathematical consistency, compares against total group budget, and suggests actionable savings tips. |
| **Final Planner** | Packages the complete travel dossier: structured itinerary, packing checklist, cultural customs, and local emergency contacts. |

---

## ✨ Key Features

- **Multi-Destination & State-Level Routing**:
  - **Single City**: Anchors all days strictly in the requested city (e.g. *Jaipur*, *Dehradun*, *Paris*, *Tokyo*).
  - **State / Large Region**: Automatically selects a duration-scaled circuit of logical hubs (e.g. entering *Uttarakhand* for 10 days visits *Haridwar* $\rightarrow$ *Rishikesh* $\rightarrow$ *Dehradun* $\rightarrow$ *Mussoorie* with intercity travel legs; for 3 days selects *Haridwar* $\rightarrow$ *Rishikesh*).
  - **Explicit Multi-City**: Preserves user-specified multi-city routes (e.g. *"Dehradun, Mussoorie, and Rishikesh"*).
- **Realistic Group Budget Engine**:
  - The entered budget is treated as the **total group budget** for all travelers combined.
  - Computes room-night counts based on party composition (e.g., 4 friends require 2 hotel rooms for $N-1$ nights).
  - Calculates intercity transportation (train/bus/flight estimates based on distance) and regional transit between circuit hubs.
  - Enforces strict mathematical consistency:
    $$\text{Cost Per Person} = \frac{\text{Estimated Total Cost}}{\text{Travelers Count}}$$
    $$\text{Daily Spend Per Person} = \frac{\text{Cost Per Person}}{\text{Duration Days}}$$
  - Identifies and clearly highlights **Budget Shortfall** with actionable trade-off advice when estimated costs exceed the group budget.
- **User Authentication & Saved Trips**:
  - Secure registration and login using **bcrypt** password hashing and **JWT** session tokens.
  - HTTP-only cookie support (`wanderai_token`) and Bearer token authentication.
  - Complete trip dossiers are saved to **SQLite** (`backend/data/trips.db`) with user ownership.
- **AI Conversational Assistant**:
  - Slide-out travel assistant chat powered by Google Gemini with destination-context awareness.
- **Markdown Export**:
  - Download complete itineraries in GitHub-flavored Markdown (`POST /api/export/markdown` and client-side generator).
- **Real-Time Streaming**:
  - Server-Sent Events (SSE) streaming (`POST /api/plan-trip/stream`) displaying live progress messages as each agent executes.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pydantic v2
- **AI & Orchestration**: LangGraph, LangChain, Google Gemini API (`gemini-2.5-flash`), `google-genai`
- **Database**: SQLite 3 (`backend/data/trips.db`)
- **Authentication**: `bcrypt` (password hashing), `PyJWT` (JSON Web Tokens)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+) — *No heavy frontend framework required*
- **Icons & Styling**: Lucide Icons (CDN), Plus Jakarta Sans font, custom responsive glassmorphism CSS

---

## 📁 Project Directory Structure

```
AI trip planner/
├── .env.example                       # Root environment configuration template
├── .gitignore                         # Git exclusion rules (secrets, db, venv, caches)
├── README.md                          # Project documentation
├── backend/
│   ├── .env.example                   # Backend environment configuration template
│   ├── requirements.txt               # Python package dependencies
│   ├── data/
│   │   ├── .gitkeep                   # Preserves data directory in git
│   │   └── trips.db                   # SQLite database (auto-generated, git-ignored)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app, API routes, SSE stream & static mount
│   │   ├── config.py                  # Settings, CORS, and JWT configurations
│   │   ├── models/
│   │   │   ├── request.py             # Pydantic request models
│   │   │   ├── response.py            # Pydantic response models
│   │   │   ├── user.py                # User authentication schemas
│   │   │   └── trip_plan.py           # Trip plan data structures
│   │   ├── db/
│   │   │   └── database.py            # SQLite connection, migrations, and CRUD
│   │   ├── services/
│   │   │   ├── auth_service.py        # Password hashing & JWT token issuance
│   │   │   └── chat_service.py        # Conversational AI assistant
│   │   ├── agents/
│   │   │   ├── state.py               # LangGraph TripPlannerState
│   │   │   ├── llm_factory.py         # Google Gemini initialization & fallback handler
│   │   │   ├── destination_agent.py   # Destination classifier & circuit hub selector
│   │   │   ├── budget_agent.py        # Financial strategist & currency tiers
│   │   │   ├── preferences_agent.py   # Traveler style & pacing curator
│   │   │   ├── research_agent.py      # Verified sights & dining research
│   │   │   ├── itinerary_agent.py     # Day-by-day routing & schedule builder
│   │   │   ├── calculator_agent.py    # Itemized expenses & shortfall calculator
│   │   │   └── final_planner_agent.py # Dossier compiler & packing checklist
│   │   ├── graph/
│   │   │   └── trip_graph.py          # Compiled LangGraph StateGraph pipeline
│   │   └── data/
│   │       └── destination_knowledge.py # Curated destinations, state circuits & landmarks
│   └── tests/
│       ├── test_wanderai.py           # Core agent, budget & currency unit tests
│       ├── test_multi_destination.py  # Single-city, state-level & multi-city routing tests
│       ├── test_auth_and_persistence.py # Auth, JWT & SQLite trip persistence tests
│       └── test_cleanup_verification.py # Endpoint & UI regression tests
└── frontend/
    ├── index.html                     # Consumer-facing application UI
    ├── style.css                      # Modern responsive styling
    ├── app.js                         # Application controller & API integration (Vanilla JS)
    └── dist/                          # Static distribution assets served by FastAPI
        ├── index.html
        ├── style.css
        └── app.js
```

---

## ⚙️ Installation & Setup

### Prerequisites
- **Python**: Version 3.10, 3.11, 3.12, or 3.13 installed
- **Git**: Installed for version control
- **Google Gemini API Key** *(Optional but recommended)*: Get a free key at [Google AI Studio](https://aistudio.google.com/)

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/wanderai.git
cd wanderai
```

---

### Step 2: Set Up Python Virtual Environment
On **Windows (Command Prompt / PowerShell)**:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

On **macOS / Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Step 3: Install Dependencies
```bash
pip install -r backend/requirements.txt
```

---

### Step 4: Configure Environment Variables
Copy the template file to create your local `.env`:

On **Windows**:
```powershell
copy .env.example backend\.env
```

On **macOS / Linux**:
```bash
cp .env.example backend/.env
```

Open `backend/.env` in any text editor and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
HOST=127.0.0.1
PORT=8000
JWT_SECRET_KEY=wanderai-super-secret-jwt-key-2026-production-grade-at-least-32-bytes
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=10080
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500,http://localhost:8000,http://127.0.0.1:8000
```

> **Note:** If `GEMINI_API_KEY` is omitted, WanderAI automatically operates in **Intelligent Offline Fallback Mode** using its built-in curated destination database without crashing.

---

## 🚀 Running the Application

You can run WanderAI using either of the following approaches:

### Method A: Single Command (Unified Full-Stack)
FastAPI automatically serves the frontend at the root URL:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your web browser.

---

### Method B: Separate Terminals (Independent Development)

**Terminal 1 — Backend API Server:**
```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --app-dir backend
```

**Terminal 2 — Frontend Static Server:**
```powershell
python -m http.server 3000 --directory frontend
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser. The frontend automatically routes API requests to `http://127.0.0.1:8000`.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status and active AI provider check |
| `POST` | `/api/auth/register` | Register a new user account with hashed password |
| `POST` | `/api/auth/login` | Authenticate credentials and receive JWT cookie/token |
| `POST` | `/api/auth/logout` | Clear user session cookie |
| `GET` | `/api/auth/me` | Fetch authenticated user profile |
| `GET` | `/api/auth/my-trips` | Fetch trips owned by the authenticated user |
| `GET` | `/api/destinations/featured` | Retrieve featured destination quick-pick cards |
| `GET` | `/api/trips` | Retrieve list of all saved itineraries |
| `GET` | `/api/trips/{trip_id}` | Retrieve complete travel dossier for a specific trip |
| `DELETE` | `/api/trips/{trip_id}` | Delete a saved trip from SQLite |
| `POST` | `/api/plan-trip` | Synchronous end-to-end trip generation |
| `POST` | `/api/plan-trip/stream` | Server-Sent Events (SSE) live multi-agent streaming |
| `POST` | `/api/chat` | Context-aware AI travel assistant chat reply |
| `POST` | `/api/export/markdown` | Export itinerary dossier to formatted Markdown |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## 🧪 Running Automated Tests

WanderAI includes automated unit and integration tests covering multi-destination routing, group budget calculations, user authentication, and API endpoints:

```bash
# Run all tests
python -m unittest discover -s backend/tests -p "test_*.py"

# Run specific test suites
python -m unittest backend/tests/test_multi_destination.py
python -m unittest backend/tests/test_auth_and_persistence.py
python -m unittest backend/tests/test_wanderai.py
python -m unittest backend/tests/test_cleanup_verification.py
```

---

## 🔍 Troubleshooting

- **Gemini API Error / Quota Exhaustion**:
  - WanderAI catches Gemini network or quota exceptions and automatically activates its built-in **Smart Fallback Engine**. The UI will display a `⚡ Offline Engine (Fallback)` badge.
  - Verify that your API key is correctly entered in `backend/.env` without leading or trailing quotes.
- **Port 8000 Already in Use**:
  - If port 8000 is occupied, run on another port:
    ```bash
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload --app-dir backend
    ```
- **Database Lock or Permission Error**:
  - The SQLite database file is located at `backend/data/trips.db`. Ensure the application has write permissions to the `backend/data` folder.

---

## 📋 Security & GitHub Readiness

- `.env` files containing credentials are excluded via `.gitignore`.
- SQLite database files (`*.db`) are excluded to avoid committing user records or local databases.
- Passwords are securely hashed using `bcrypt`.
- No sensitive API keys are printed in server logs or committed to version control.

Open **[http://localhost:3000](http://localhost:3000)** in your browser. The frontend automatically routes API requests to `http://127.0.0.1:8000`.

---

## 📡 API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health status and active AI provider check |
| `POST` | `/api/auth/register` | Register a new user account with hashed password |
| `POST` | `/api/auth/login` | Authenticate credentials and receive JWT cookie/token |
| `POST` | `/api/auth/logout` | Clear user session cookie |
| `GET` | `/api/auth/me` | Fetch authenticated user profile |
| `GET` | `/api/auth/my-trips` | Fetch trips owned by the authenticated user |
| `GET` | `/api/destinations/featured` | Retrieve featured destination quick-pick cards |
| `GET` | `/api/trips` | Retrieve list of all saved itineraries |
| `GET` | `/api/trips/{trip_id}` | Retrieve complete travel dossier for a specific trip |
| `DELETE` | `/api/trips/{trip_id}` | Delete a saved trip from SQLite |
| `POST` | `/api/plan-trip` | Synchronous end-to-end trip generation |
| `POST` | `/api/plan-trip/stream` | Server-Sent Events (SSE) live multi-agent streaming |
| `POST` | `/api/chat` | Context-aware AI travel assistant chat reply |
| `POST` | `/api/export/markdown` | Export itinerary dossier to formatted Markdown |
| `GET` | `/docs` | Interactive Swagger API documentation |

---

## 🧪 Running Automated Tests

WanderAI includes automated unit and integration tests covering multi-destination routing, group budget calculations, user authentication, and API endpoints:

```bash
# Run all tests
python -m unittest discover -s backend/tests -p "test_*.py"

# Run specific test suites
python -m unittest backend/tests/test_multi_destination.py
python -m unittest backend/tests/test_auth_and_persistence.py
python -m unittest backend/tests/test_wanderai.py
python -m unittest backend/tests/test_cleanup_verification.py
```

---

## 🔍 Troubleshooting

- **Gemini API Error / Quota Exhaustion**:
  - WanderAI catches Gemini network or quota exceptions and automatically activates its built-in **Smart Fallback Engine**. The UI will display a `⚡ Offline Engine (Fallback)` badge.
  - Verify that your API key is correctly entered in `backend/.env` without leading or trailing quotes.
- **Port 8000 Already in Use**:
  - If port 8000 is occupied, run on another port:
    ```bash
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload --app-dir backend
    ```
- **Database Lock or Permission Error**:
  - The SQLite database file is located at `backend/data/trips.db`. Ensure the application has write permissions to the `backend/data` folder.

---

## 📋 Security & GitHub Readiness

- `.env` files containing credentials are excluded via `.gitignore`.
- SQLite database files (`*.db`) are excluded to avoid committing user records or local databases.
- Passwords are securely hashed using `bcrypt`.
- No sensitive API keys are printed in server logs or committed to version control.

