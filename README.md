# DataReady AI

AI-powered data preparation platform that transforms messy, unstructured data into clean, AI-training-ready datasets.

## Project Structure

```
dataready-ai/
├── frontend/          # React + Vite
├── backend/           # FastAPI
├── README.md          # This file
└── SUPABASE_SETUP.md  # Database setup guide
```

## Quick Start

### 1. Backend (FastAPI)

```bash
cd backend

# Activate virtual environment
.\venv\Scripts\activate

# Run server
uvicorn app.main:app --reload --port 8000
```

**Backend will run on:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`

### 2. Frontend (React + Vite)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Run dev server
npm run dev
```

**Frontend will run on:** `http://localhost:5173`

---

## Features Implemented

### ✅ Frontend
- Dark theme with purple accents
- Minimal, modern UI
- File upload with drag-and-drop
- Database connection interface
- Real-time API integration
- Loading states and error handling
- Global AI Assistant (accessible from any page)
- ML Model Training Dashboard
- Data Quality Report Viewer

### ✅ Backend - Core Features

#### 1. File Upload & Analysis
- Upload CSV, Excel, JSON files
- Automatic data type detection
- Comprehensive data profiling
- Quality score calculation (DAMA framework)

#### 2. Database Connectivity
- **PostgreSQL** - Full support with table listing, schema analysis
- **MySQL** - Full support for connections and queries
- **MongoDB** - NoSQL document database support
- **SQLite** - Embedded file-based database support
- Test connections, list tables, analyze table data

#### 3. Data Quality Analysis
- Industry-standard metrics (DAMA, ISO 25024)
- Completeness, uniqueness, consistency, validity scores
- Missing data detection and patterns
- Duplicate detection
- Data type validation
- Outlier identification

#### 4. ML Model Training
- **Classification Models:** XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, Logistic Regression, SVM, KNN
- **Regression Models:** XGBoost, LightGBM, CatBoost, Random Forest, Gradient Boosting, Linear Regression, SVR, KNN
- Train single model or compare multiple
- Performance metrics (accuracy, F1, ROC-AUC, RMSE, R²)
- Feature importance visualization
- Training result storage

#### 5. AI-Powered Features
- Model recommendations based on data characteristics
- LLM-powered suggestions (Groq/OpenAI)
- Natural language Q&A about data and models
- AI fix suggestions for data quality issues

#### 6. Global AI Assistant
- Accessible from any page via `/api/v1/assistant/message`
- Platform-aware context (knows about uploads, quality reports, training history)
- Conversational interface with memory
- Integrated with Groq/OpenAI for intelligent responses

#### 7. Export & Processing
- Export quality reports (JSON format)
- Apply data transformations
- Processing history tracking

---

## API Endpoints

### Root Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint - API info |
| GET | `/health` | Health check |

### Upload Endpoints (`/api/v1/upload`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/file` | Upload CSV, Excel, or JSON file |
| POST | `/database` | Database connection endpoint |

### Quality Endpoints (`/api/v1/quality`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/{source_id}` | Analyze data quality |
| GET | `/report/{source_id}` | Get quality report |
| GET | `/templates` | Get ML dataset templates |
| GET | `/demo` | Get demo quality report |

### Processing Endpoints (`/api/v1/processing`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/apply-fixes` | Apply approved data fixes |
| GET | `/history/{source_id}` | Get processing history |
| GET | `/suggestions/{source_id}` | Get AI fix suggestions |
| GET | `/export/{source_id}` | Export quality report |

### Database Endpoints (`/api/v1/database`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/test` | Test database connection |
| POST | `/list-tables` | List all tables in database |
| POST | `/analyze-table` | Analyze specific table |
| POST | `/table-schema` | Get table schema info |
| GET | `/supported-types` | Get supported database types |

### ML Models Endpoints (`/api/v1/models`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/supported` | Get list of supported ML models |
| POST | `/recommend` | Get AI model recommendations |
| POST | `/chat` | Chat about models with LLM |
| POST | `/train` | Train a specific model |
| POST | `/compare` | Train and compare multiple models |
| GET | `/results/{training_id}` | Get training results |
| GET | `/charts/{training_id}/{chart_type}` | Get training visualization chart |
| GET | `/demo-analysis` | Get demo model analysis |

### AI Assistant Endpoints (`/api/v1/assistant`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/message` | Send message to AI assistant |
| GET | `/status` | Get assistant status |
| GET | `/context` | Get current platform context |
| DELETE | `/history/{conversation_id}` | Clear conversation history |

---

## Tech Stack

**Frontend:**
- React 18
- Vite 6
- Tailwind CSS
- Axios
- React Router

**Backend:**
- Python 3.10
- FastAPI
- Uvicorn
- Pandas / NumPy
- Scikit-learn / XGBoost / LightGBM / CatBoost
- Supabase
- Groq / OpenAI (for LLM features)

---

## Environment Variables

Create `.env` files in both directories:

**Frontend `.env`:**
```
VITE_API_URL=http://localhost:8000
```

**Backend `.env`:**
```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
GROQ_API_KEY=your_key
OPENAI_API_KEY=your_key
```

---

## Services Architecture

```
backend/app/services/
├── ai_suggestions.py       # AI-powered fix suggestions
├── data_analyzer.py        # Enterprise-grade data analysis
├── data_export.py          # Export functionality
├── db_connector.py         # Multi-database connector
├── llm_chat.py             # LLM chat service (Groq/OpenAI)
├── ml_templates.py         # ML dataset templates
├── model_recommender.py    # AI model recommendations
├── model_trainer.py        # ML model training
├── platform_context.py     # Global platform context
├── supabase_service.py     # Supabase integration
└── visualization_generator.py  # Chart generation
```

---

## Testing the Integration

1. Open `http://localhost:5173` in your browser
2. Click "Upload File" button to test file upload
3. Click "Connect Database" to test database connection
4. Use the AI Assistant chat to ask questions
5. Navigate to Model Training to train ML models
6. View API logs in the backend terminal
7. Access Swagger docs at `http://localhost:8000/docs`

---

## License

MIT
