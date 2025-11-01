#!/bin/bash
# StepSquad App Health Check Script

echo "🔍 Checking StepSquad Apps..."
echo "================================"

# Check Backend API
echo ""
echo "📦 Backend API (apps/api):"
echo "----------------------------"

cd /Users/bogdan/Development/others/stepsquad/apps/api

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "✓ Python: $PYTHON_VERSION"

# Check if dependencies are installed
if python3 -c "import fastapi, pydantic, uvicorn" 2>/dev/null; then
    echo "✓ Backend dependencies installed"
else
    echo "✗ Backend dependencies NOT installed"
    echo "  Run: cd apps/api && pip install -e ."
fi

# Check if main.py exists and compiles
if [ -f "main.py" ]; then
    if python3 -m py_compile main.py 2>/dev/null; then
        echo "✓ main.py compiles successfully"
    else
        echo "✗ main.py has syntax errors"
    fi
else
    echo "✗ main.py not found"
fi

# Check if storage.py exists
if [ -f "storage.py" ]; then
    echo "✓ storage.py exists"
else
    echo "✗ storage.py not found"
fi

# Check Frontend Web App
echo ""
echo "🌐 Frontend Web App (apps/web):"
echo "----------------------------"

cd /Users/bogdan/Development/others/stepsquad/apps/web

# Check Node.js version
NODE_VERSION=$(node --version 2>&1)
echo "✓ Node.js: $NODE_VERSION"

# Check npm version
NPM_VERSION=$(npm --version 2>&1)
echo "✓ npm: $NPM_VERSION"

# Check if node_modules exists
if [ -d "node_modules" ]; then
    echo "✓ Frontend dependencies installed"
else
    echo "✗ Frontend dependencies NOT installed"
    echo "  Run: cd apps/web && npm install"
fi

# Check if package.json exists
if [ -f "package.json" ]; then
    echo "✓ package.json exists"
else
    echo "✗ package.json not found"
fi

# Check if key files exist
if [ -f "src/App.tsx" ]; then
    echo "✓ src/App.tsx exists"
else
    echo "✗ src/App.tsx not found"
fi

if [ -f "vite.config.ts" ]; then
    echo "✓ vite.config.ts exists"
else
    echo "✗ vite.config.ts not found"
fi

# Summary
echo ""
echo "================================"
echo "📋 Summary:"
echo "================================"

cd /Users/bogdan/Development/others/stepsquad

# Check backend
cd apps/api
if python3 -c "import fastapi" 2>/dev/null && [ -f "main.py" ]; then
    BACKEND_STATUS="✓ Ready"
else
    BACKEND_STATUS="✗ Needs setup"
fi

# Check frontend
cd ../web
if [ -d "node_modules" ] && [ -f "package.json" ] && [ -f "src/App.tsx" ]; then
    FRONTEND_STATUS="✓ Ready"
else
    FRONTEND_STATUS="✗ Needs setup"
fi

echo "Backend API:  $BACKEND_STATUS"
echo "Frontend Web: $FRONTEND_STATUS"

echo ""
echo "🚀 To start the apps:"
if [ "$BACKEND_STATUS" != "✓ Ready" ]; then
    echo "  1. Backend: cd apps/api && pip install -e ."
    echo "  2. Backend: cd apps/api && uvicorn main:app --reload --port 8080"
fi
if [ "$FRONTEND_STATUS" != "✓ Ready" ]; then
    echo "  3. Frontend: cd apps/web && npm install"
fi
echo "  4. Frontend: cd apps/web && npm run dev"
echo ""
echo "   Access at: http://localhost:5173"
