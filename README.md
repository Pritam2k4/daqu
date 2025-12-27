# DAQU - Know Your Data

> AI-Powered Data Quality Platform for ML-Ready Datasets

![DAQU](frontend/public/daqu-logo.png)

---

## 🎯 What is DAQU?

DAQU is an enterprise-grade data quality analysis platform that helps you:
- **Analyze** data quality using DAMA & ISO 25024 standards
- **Fix** issues with AI-powered suggestions and one-click fixes
- **Train** ML models with 15+ algorithms
- **Chat** with an AI assistant about your data

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account (free)
- Groq API key (free, optional)

### 1. Clone & Setup Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Create `backend/.env`:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
GROQ_API_KEY=your_groq_api_key
```

Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Setup Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:
```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Run frontend:
```bash
npm run dev
```

### 3. Open the App
Go to **http://localhost:5173**

---

## 📁 Project Structure

```
daqu/
├── backend/                 # FastAPI Python Backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── main.py         # App entry
│   └── requirements.txt
│
├── frontend/               # React + Vite Frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API & Supabase
│   │   └── context/        # React context
│   └── package.json
│
└── README.md
```

---

## ✨ Features

### Data Quality Analysis
- **6 Quality Dimensions**: Completeness, Uniqueness, Validity, Consistency, Accuracy, Timeliness
- **ML Readiness Score**: Class balance, correlation, target leakage detection
- **50+ Quality Metrics** based on industry standards

### AI-Powered Fixes
- Automatic issue detection
- Smart fix recommendations with code snippets
- One-click apply (coming soon)

### Model Studio
- Train 15+ ML models
- Auto hyperparameter tuning
- Feature importance visualization
- Cross-validation scoring

### AI Assistant
- Natural language queries about your data
- Powered by Groq (Llama 3.3 70B)

---

## 🔧 Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Vite, Tailwind CSS |
| Backend | FastAPI, Python 3.11 |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase Auth (Google OAuth) |
| AI | Groq API (Llama 3.3) |
| ML | scikit-learn, pandas, numpy |

---

## 🔐 Environment Variables

### Backend (`backend/.env`)
| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Supabase anon/public key |
| `GROQ_API_KEY` | Groq API key (optional) |

### Frontend (`frontend/.env`)
| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend URL (http://localhost:8000) |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon/public key |

---

## 📝 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/upload/file` | Upload CSV/Excel file |
| GET | `/api/v1/quality/report/{id}` | Get quality report |
| GET | `/api/v1/quality/demo` | Load demo data |
| POST | `/api/v1/models/train` | Train ML model |
| GET | `/api/v1/models/supported` | List available models |
| POST | `/api/v1/assistant/chat` | Chat with AI |

---

## 🎨 Design

- **Theme**: Dark mode with gold/amber accents
- **Font**: Space Grotesk + Orbitron (cyberpunk hero)
- **Style**: 2025 trends - glassmorphism, scroll animations, micro-interactions

---

## 📄 License

MIT License - feel free to use and modify!

---

**Built with ❤️ by Pritam**
