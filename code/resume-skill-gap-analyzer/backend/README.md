# Resume Skill Gap Analyzer - Backend Setup

## Setup Commands (Windows)

### 1. Create virtual environment
```powershell
cd backend
python -m venv venv
```

### 2. Activate virtual environment
```powershell
.\venv\Scripts\Activate
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Copy environment file
```powershell
copy .env.example .env
```

### 5. Run the server
```powershell
python -m app.main
```

### Or use Uvicorn
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Base
- `GET /` - Welcome message
- `GET /health` - Health check

### Authentication
- `POST /api/v1/auth/register` - Register user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/logout` - Logout user
- `GET /api/v1/auth/me` - Current user

### Resume
- `POST /api/v1/resume/upload` - Upload resume
- `GET /api/v1/resume/{id}` - Get resume
- `DELETE /api/v1/resume/{id}` - Delete resume

### Analysis
- `POST /api/v1/analysis/analyze` - Analyze resume
- `GET /api/v1/analysis/categories` - Get categories
- `GET /api/v1/analysis/history` - Get history

## Testing the API

### Using Swagger UI
Open: http://localhost:8000/docs

### Using PowerShell
```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/health"

# Register user
$body = @{
    name = "John Doe"
    email = "john@example.com"
    password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method Post -Body $body -ContentType "application/json"

# Analyze resume
$body = @{
    resume_text = "Java Python JavaScript developer"
    category = "software"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/analysis/analyze" -Method Post -Body $body -ContentType "application/json"
```

## Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── config.py       # Settings
│   └── routes/
│       ├── __init__.py
│       ├── auth.py     # Authentication
│       ├── resume.py  # Resume upload
│       └── analysis.py # Analysis
├── uploads/           # Uploaded files
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md         # This file
```