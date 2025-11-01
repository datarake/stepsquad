# StepSquad App Setup & Running Guide

## ✅ Current Status

### Frontend Web App (apps/web)
- ✅ **Dependencies**: Installed (npm install completed)
- ✅ **Files**: All source files exist
- ✅ **Node.js**: v23.6.0 available
- ✅ **Ready to run**: `npm run dev`

### Backend API (apps/api)
- ✅ **Files**: All source files exist and compile
- ⚠️ **Dependencies**: Need to be installed in virtual environment
- ✅ **Python**: 3.13.2 available
- ⚠️ **Ready to run**: After installing dependencies

## 🚀 Quick Start

### 1. Frontend (Ready to run!)

```bash
cd apps/web
npm run dev
```

**Access at**: http://localhost:5173

### 2. Backend (Need to install dependencies)

**Option A: Use Virtual Environment (Recommended)**

```bash
cd apps/api
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows
pip install fastapi "uvicorn[standard]" pydantic python-dateutil
```

**Option B: User Installation**

```bash
cd apps/api
pip3 install --user fastapi "uvicorn[standard]" pydantic python-dateutil
```

**Then run:**
```bash
uvicorn main:app --reload --port 8080
```

**Or if using user install:**
```bash
python3 -m uvicorn main:app --reload --port 8080
```

## 📋 Setup Checklist

- [x] Frontend dependencies installed
- [ ] Backend dependencies installed (in venv or user)
- [ ] Create `.env.local` in `apps/web/` with:
  ```
  VITE_API_BASE_URL=http://localhost:8080
  VITE_USE_DEV_AUTH=true
  VITE_ADMIN_EMAIL=admin@stepsquad.com
  ```
- [ ] Start backend on port 8080
- [ ] Start frontend on port 5173

## 🔍 Verification

Run the health check script:
```bash
./check_apps.sh
```

## 📝 Notes

- **Frontend**: Already set up and ready to run!
- **Backend**: Python environment protection (PEP 668) requires using a virtual environment or `--user` flag
- **GCP Dependencies**: Optional - only needed if `GCP_ENABLED=true`
- **Environment**: Backend runs with `GCP_ENABLED=false` for local dev (uses `X-Dev-User` header)

## 🐛 Troubleshooting

**Backend won't start?**
- Use virtual environment: `python3 -m venv venv && source venv/bin/activate`
- Install dependencies in venv
- Make sure you're using Python 3.11+

**Frontend won't start?**
- Check `node_modules` exists
- Run `npm install` again if needed
- Check port 5173 isn't in use

**Can't connect to API?**
- Make sure backend is running on port 8080
- Check `VITE_API_BASE_URL` in `.env.local`
- Verify backend health: `curl http://localhost:8080/health`
