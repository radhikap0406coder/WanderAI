# 🌐 WanderAI — Frontend Client

This folder contains the consumer-facing frontend for **WanderAI**, built with modern **HTML5**, **CSS3**, and **Vanilla JavaScript (ES6+)**.

## Architecture & Technology
- **Pure Web Standards**: Zero runtime frontend framework dependencies (No React, Vue, Angular, or TypeScript required).
- **FastAPI Integration**: Communicates directly with the FastAPI backend over REST (`/api/plan-trip`, `/api/trips`, `/api/auth`, `/api/chat`) and Server-Sent Events (SSE) streaming (`/api/plan-trip/stream`).
- **Icons**: Lucide Icons loaded via CDN.
- **Typography**: Google Fonts (*Plus Jakarta Sans* and *JetBrains Mono*).

## Key Files
- `index.html`: Main application markup containing navigation, trip parameter form, travel dossier, and auth modals.
- `style.css`: Responsive glassmorphism layout, color tokens, and animation styling.
- `app.js`: Application logic handling user interactions, API requests, dynamic dossier rendering, budget balance charts, and chat assistant.

## How to Run

### Option 1: Served by FastAPI (Default)
When the FastAPI backend is running (`uvicorn app.main:app`), the built static assets in `dist/` are automatically mounted and served at:
**http://127.0.0.1:8000**

### Option 2: Standalone Static Server
To run the frontend in a separate terminal:
```bash
python -m http.server 3000
```
Open **http://localhost:3000** in your browser. The client automatically connects to the backend at `http://127.0.0.1:8000`.
