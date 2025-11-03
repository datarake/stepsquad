# StepSquad

A fitness competition platform that brings teams together to compete in step challenges. Built for the Google Cloud Run Hackathon with ADK (Agent Development Kit).

## 🎯 Overview

StepSquad enables users to:
- Create and participate in fitness competitions
- Join teams and compete together
- Track daily step counts
- View real-time leaderboards
- Integrate with Garmin and Fitbit devices
- Get AI-powered insights and fairness checks

## 🏗️ Architecture

### Frontend (`apps/web`)
- **Tech Stack**: React 18, Vite, TypeScript, Tailwind CSS
- **Authentication**: Firebase Authentication
- **State Management**: React Query
- **Testing**: Vitest, React Testing Library, Playwright
- **Deployment**: Cloud Run (custom domain: `https://www.stepsquad.club`)

### Backend (`apps/api`)
- **Tech Stack**: FastAPI, Python 3.11
- **Database**: Firestore
- **Authentication**: Firebase Admin SDK
- **Testing**: Pytest
- **Deployment**: Cloud Run (custom domain: `https://api.stepsquad.club`)

### AI Agents (`apps/agents`)
- **Tech Stack**: Google ADK (Agent Development Kit), Gemini AI
- **Agents**:
  - **Sync Agent**: Automatically syncs step data from linked devices
  - **Fairness Agent**: Detects and flags suspicious step data patterns
- **Workflow**: Multi-agent orchestration for automated step ingestion and validation
- **Deployment**: Cloud Run

## 🚀 Features

### Core Features
- ✅ **User Management**: Role-based access control (ADMIN, MEMBER)
- ✅ **Competition Management**: Create, view, update competitions with status workflow
- ✅ **Team Management**: Create teams, join/leave teams
- ✅ **Step Ingestion**: Manual and automatic step entry
- ✅ **Leaderboards**: Individual and team leaderboards
- ✅ **Device Integration**: OAuth integration with Garmin and Fitbit

### AI-Powered Features
- ✅ **Automated Sync**: AI agent automatically syncs steps from linked devices
- ✅ **Fairness Checks**: AI agent detects suspicious patterns in step data
- ✅ **Multi-Agent Workflow**: Orchestrated agents for step validation

### Infrastructure
- ✅ **Custom Domains**: `www.stepsquad.club` and `api.stepsquad.club`
- ✅ **CI/CD**: Automated deployment via GitHub Actions
- ✅ **Firebase Authentication**: Production-ready authentication
- ✅ **Firestore Database**: Scalable NoSQL database

## 📁 Project Structure

```
stepsquad/
├── apps/
│   ├── api/              # FastAPI backend
│   ├── web/              # React frontend
│   └── agents/           # Google ADK AI agents
├── .github/
│   └── workflows/        # CI/CD pipelines
└── README.md             # This file
```

## 🔧 Development

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+ and uv
- Google Cloud SDK (gcloud)
- Firebase project setup

### Local Development

#### Backend
```bash
cd apps/api
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Configure `.env.local`:
```bash
GCP_ENABLED=true
ALLOW_DEV_AUTH_LOCAL=true
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
GOOGLE_CLOUD_PROJECT=stepsquad-46d14
```

#### Frontend
```bash
cd apps/web
pnpm install
pnpm dev
```

Configure `.env.local`:
```bash
VITE_API_BASE_URL=http://localhost:8080
VITE_USE_DEV_AUTH=false
VITE_FIREBASE_API_KEY=...
# ... other Firebase config
```

### Environment Setup

The project supports both development and production modes:

- **Development Mode**: Uses Firestore with optional dev auth bypass
- **Production Mode**: Uses Firestore with Firebase authentication

See `apps/api/env.local.example` for configuration options.

## 🧪 Testing

### Frontend
```bash
cd apps/web
pnpm test              # Unit tests
pnpm test:e2e          # E2E tests
pnpm test:coverage     # Coverage report
```

### Backend
```bash
cd apps/api
uv run pytest          # Run all tests
uv run pytest -v       # Verbose output
```

## 🚀 Deployment

### CI/CD
Deployments are automated via GitHub Actions:
- Push to `main` triggers deployment
- Backend deployed to Cloud Run
- Frontend deployed to Cloud Run
- Custom domains configured automatically

### Manual Deployment

#### Backend
```bash
cd apps/api
gcloud run deploy stepsquad-api \
  --source . \
  --region us-central1 \
  --project stepsquad-46d14
```

#### Frontend
```bash
cd apps/web
gcloud run deploy stepsquad-web \
  --source . \
  --region us-central1 \
  --project stepsquad-46d14
```

## 🌐 Production URLs

- **Frontend**: https://www.stepsquad.club
- **Backend API**: https://api.stepsquad.club

## 📚 Documentation

- **API Documentation**: Available at `/docs` endpoint (Swagger UI)
- **Code Documentation**: Inline comments and docstrings

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## 📝 License

[Add your license here]

## 🏆 Hackathon Submission

Built for: [Google Cloud Run Hackathon](https://run.devpost.com/)

**Key Highlights**:
- Uses Google ADK (Agent Development Kit) for AI-powered features
- Multi-agent workflow for automated step ingestion
- Fairness detection using AI
- Production-ready with custom domains
- Full CI/CD pipeline
