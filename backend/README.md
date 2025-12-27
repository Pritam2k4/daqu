# DataReady AI Backend

FastAPI backend for the DataReady AI platform - an AI-powered data preparation solution.

## Setup

1. Create virtual environment (Python 3.10):
```bash
py -3.10 -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy environment variables:
```bash
copy .env.example .env
```

5. Run development server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`  
API docs at `http://localhost:8000/docs`

---

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Supabase** - Database and authentication
- **Pandas / NumPy** - Data manipulation
- **Scikit-learn** - ML algorithms
- **XGBoost, LightGBM, CatBoost** - Gradient boosting frameworks
- **Groq / OpenAI** - LLM integration for AI features

---

## Project Structure

```
backend/
├── app/
│   ├── api/v1/              # API endpoints
│   │   ├── __init__.py
│   │   ├── router.py        # Main API router
│   │   ├── upload.py        # File upload endpoints
│   │   ├── quality.py       # Data quality endpoints
│   │   ├── processing.py    # Data processing endpoints
│   │   ├── database.py      # Database connection endpoints
│   │   ├── models.py        # ML model training endpoints
│   │   └── assistant.py     # AI assistant endpoints
│   ├── models/              # Database models (Pydantic)
│   ├── schemas/             # Request/Response schemas
│   ├── services/            # Business logic
│   │   ├── ai_suggestions.py
│   │   ├── data_analyzer.py
│   │   ├── data_export.py
│   │   ├── db_connector.py
│   │   ├── llm_chat.py
│   │   ├── ml_templates.py
│   │   ├── model_recommender.py
│   │   ├── model_trainer.py
│   │   ├── platform_context.py
│   │   ├── supabase_service.py
│   │   └── visualization_generator.py
│   ├── utils/               # Utility functions
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI application
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## API Endpoints

### Root
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |

---

### Upload (`/api/v1/upload`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/file` | Upload CSV/Excel/JSON file for analysis |
| POST | `/database` | Database connection placeholder |

**File Upload Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/upload/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@data.csv"
```

---

### Quality (`/api/v1/quality`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze/{source_id}` | Analyze data quality |
| GET | `/report/{source_id}` | Get quality report |
| GET | `/templates` | Get ML dataset templates |
| GET | `/demo` | Get demo quality report (DAMA framework) |

**Quality Report includes:**
- Completeness score
- Uniqueness score
- Consistency score
- Validity score
- Overall quality score with grade (A-F)
- Column-level statistics
- Issue identification

---

### Processing (`/api/v1/processing`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/apply-fixes` | Apply data transformations |
| GET | `/history/{source_id}` | Get processing history |
| GET | `/suggestions/{source_id}` | Get AI-generated fix suggestions |
| GET | `/export/{source_id}` | Export quality report (JSON) |

---

### Database (`/api/v1/database`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/test` | Test database connection |
| POST | `/list-tables` | List all tables in database |
| POST | `/analyze-table` | Analyze specific table |
| POST | `/table-schema` | Get table schema |
| GET | `/supported-types` | Get supported database types |

**Supported Databases:**
- PostgreSQL (port 5432)
- MySQL (port 3306)
- MongoDB (port 27017)
- SQLite (file-based)

**Connection Example:**
```json
{
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "mydb",
  "username": "user",
  "password": "pass"
}
```

---

### ML Models (`/api/v1/models`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/supported` | List all supported ML models |
| POST | `/recommend` | Get AI model recommendations |
| POST | `/chat` | Chat about models with LLM |
| POST | `/train` | Train a specific model |
| POST | `/compare` | Train and compare multiple models |
| GET | `/results/{training_id}` | Get training results |
| GET | `/charts/{training_id}/{chart_type}` | Get visualization chart |
| GET | `/demo-analysis` | Demo model analysis |

**Supported Models:**

*Classification:*
- XGBoost, LightGBM, CatBoost
- Random Forest, Gradient Boosting
- Logistic Regression, SVM, KNN

*Regression:*
- XGBoost, LightGBM, CatBoost
- Random Forest, Gradient Boosting
- Linear Regression, SVR, KNN

**Training Request Example:**
```json
{
  "source_id": "abc-123",
  "model_name": "xgboost",
  "target_column": "price",
  "test_size": 0.2
}
```

---

### AI Assistant (`/api/v1/assistant`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/message` | Send message to AI assistant |
| GET | `/status` | Get assistant status and capabilities |
| GET | `/context` | Get current platform context |
| DELETE | `/history/{conversation_id}` | Clear conversation history |

**Chat Example:**
```json
{
  "message": "What models would you recommend for my data?",
  "conversation_id": "default"
}
```

**The AI Assistant can:**
- Answer questions about your data
- Recommend ML models
- Explain quality scores
- Guide model training
- Track uploads and history

---

## Services

### `data_analyzer.py`
Enterprise-grade data analysis with:
- Basic statistics (rows, columns, memory usage)
- Column type detection (numeric, categorical, datetime, text)
- Missing data analysis with patterns
- Duplicate detection
- Statistical summaries
- Outlier detection using IQR/Z-score

### `model_trainer.py`
Unified ML model trainer:
- Automatic task type detection (classification/regression)
- Data preprocessing (encoding, imputation)
- Cross-validation support
- Comprehensive metrics calculation
- Feature importance extraction

### `model_recommender.py`
AI-powered recommendations:
- Data profiling and characteristic analysis
- Model scoring based on data properties
- Natural language explanations
- Chatbot-style responses

### `llm_chat.py`
LLM integration service:
- Groq and OpenAI support
- Automatic fallback between providers
- Platform context injection
- Conversation management

### `db_connector.py`
Multi-database connector:
- PostgreSQL, MySQL, MongoDB, SQLite
- Connection testing
- Table listing and schema extraction
- Data fetching with limits

---

## Environment Variables

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# LLM Providers (at least one required for AI features)
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## Development

**Run with auto-reload:**
```bash
uvicorn app.main:app --reload --port 8000
```

**View API documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## License

MIT
