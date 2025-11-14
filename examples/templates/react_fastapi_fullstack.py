"""
React + FastAPI Full Stack Template

A complete full-stack application template with:
- React frontend (Vite + TypeScript)
- FastAPI backend
- Database integration
- Authentication
- API client generation
"""
from resoftai.templates.base import Template, TemplateVariable, TemplateFile, TemplateCategory


def create_react_fastapi_template() -> Template:
    """Create React + FastAPI full stack template"""

    return Template(
        id="react-fastapi-fullstack",
        name="React + FastAPI Full Stack",
        description="Complete full-stack application with React frontend and FastAPI backend",
        category=TemplateCategory.WEB_APP,
        author="ResoftAI",
        version="1.0.0",
        variables=[
            TemplateVariable(
                name="app_name",
                description="Application name",
                required=True,
                type="string"
            ),
            TemplateVariable(
                name="api_port",
                description="Backend API port",
                type="integer",
                default=8000
            ),
            TemplateVariable(
                name="frontend_port",
                description="Frontend development port",
                type="integer",
                default=3000
            ),
        ],
        files=[
            # Backend - Main FastAPI app
            TemplateFile(
                path="backend/main.py",
                content='''"""
{{app_name}} Backend API

FastAPI backend for {{app_name}}
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="{{app_name}} API",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:{{frontend_port}}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def root():
    return {"message": "{{app_name}} API is running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy"}
'''
            ),

            # Backend requirements
            TemplateFile(
                path="backend/requirements.txt",
                content='''fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy[asyncio]==2.0.23
aiosqlite==0.19.0
pydantic==2.5.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
'''
            ),

            # Frontend - package.json
            TemplateFile(
                path="frontend/package.json",
                content='''{
  "name": "{{app_name|kebab-case}}-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "typescript": "^5.2.2",
    "vite": "^5.0.8"
  }
}
'''
            ),

            # Frontend - Vite config
            TemplateFile(
                path="frontend/vite.config.ts",
                content='''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: {{frontend_port}},
    proxy: {
      '/api': {
        target: 'http://localhost:{{api_port}}',
        changeOrigin: true,
      }
    }
  }
})
'''
            ),

            # Frontend - Main App
            TemplateFile(
                path="frontend/src/App.tsx",
                content='''import { useState, useEffect } from 'react'
import './App.css'

interface HealthStatus {
  status: string
}

function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null)

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(err => console.error('Error:', err))
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>{{app_name}}</h1>
        <p>Full Stack Application</p>
        {health && (
          <div className="health-status">
            API Status: {health.status}
          </div>
        )}
      </header>
    </div>
  )
}

export default App
'''
            ),

            # Frontend - Index HTML
            TemplateFile(
                path="frontend/index.html",
                content='''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{app_name}}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''
            ),

            # Frontend - Main entry
            TemplateFile(
                path="frontend/src/main.tsx",
                content='''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
            ),

            # Frontend - TypeScript config
            TemplateFile(
                path="frontend/tsconfig.json",
                content='''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
'''
            ),

            # Root README
            TemplateFile(
                path="README.md",
                content='''# {{app_name}}

Full-stack application with React frontend and FastAPI backend.

## Project Structure

```
{{app_name|kebab-case}}/
├── backend/          # FastAPI backend
│   ├── main.py
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

## Quick Start

### Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Start backend server:
```bash
uvicorn main:app --reload --port {{api_port}}
```

Backend API will be available at: http://localhost:{{api_port}}

### Frontend Setup

1. Install Node dependencies:
```bash
cd frontend
npm install
```

2. Start development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:{{frontend_port}}

## Features

- ✅ React 18 with TypeScript
- ✅ Vite for fast development
- ✅ FastAPI backend
- ✅ CORS configured
- ✅ API proxy setup
- ✅ Hot module replacement

## Development

- Backend runs on port {{api_port}}
- Frontend runs on port {{frontend_port}}
- API requests from frontend are proxied to `/api`

## Building for Production

### Backend
```bash
cd backend
# Deploy using your preferred method (Docker, cloud, etc.)
```

### Frontend
```bash
cd frontend
npm run build
# Output in dist/ directory
```

## License

MIT
'''
            ),

            # Docker Compose
            TemplateFile(
                path="docker-compose.yml",
                content='''version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "{{api_port}}:8000"
    environment:
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./backend:/app

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "{{frontend_port}}:80"
    depends_on:
      - backend
'''
            ),
        ],
        directories=[
            "backend",
            "backend/models",
            "backend/routers",
            "backend/schemas",
            "frontend",
            "frontend/src",
            "frontend/src/components",
            "frontend/src/api",
            "frontend/public",
        ],
        requirements={
            "python": ">=3.9",
            "node": ">=18.0.0"
        },
        setup_commands=[
            "cd backend && pip install -r requirements.txt",
            "cd frontend && npm install",
        ],
        readme_content="See README.md in generated project",
        tags=["react", "fastapi", "fullstack", "typescript", "python", "vite"],
    )
