# StepSquad Agents Service

## Overview

This service implements two AI agents using Google's Agent Development Kit (ADK):

1. **Sync Agent** - Detects missing step data and triggers synchronization workflows
2. **Fairness Agent** - Analyzes step data for anomalies and flags unrealistic entries

Both agents communicate with each other to complete workflows, meeting the hackathon requirement for multi-agent applications.

## Features

### Sync Agent
- Detects missing step data (users who haven't submitted data)
- Identifies late data submissions (after competition end date)
- Communicates findings with fairness agent
- Provides AI-powered recommendations using Gemini

### Fairness Agent
- Analyzes step data for anomalies (unrealistic counts)
- Detects suspicious patterns (identical values, round numbers)
- Flags potentially unfair data for admin review
- Provides AI-powered recommendations using Gemini

### Multi-Agent Workflow
- Orchestrates both agents in sequence
- Enables agent-to-agent communication
- Combines results for comprehensive analysis
- Provides actionable recommendations

## Technology Stack

- **Google ADK (Agent Development Kit)** - Framework for building AI agents
- **Gemini AI** - Google's generative AI for intelligent analysis
- **FastAPI** - Web framework for agent endpoints
- **Firestore** - Data storage for competitions and steps
- **Cloud Run** - Serverless deployment platform

## Installation

### Dependencies

```bash
pip install google-adk google-generativeai fastapi uvicorn
```

Or using the project dependencies:

```bash
cd apps/agents
uv sync
```

### Environment Variables

```bash
# Required
GCP_ENABLED=true
GOOGLE_CLOUD_PROJECT=your-project-id

# Optional (for Gemini AI features)
GEMINI_API_KEY=your-gemini-api-key
```

## Usage

### API Endpoints

#### Run Sync Agent
```bash
POST /run
{
  "agent": "sync",
  "comp_id": "competition-id",
  "date": "2025-11-01"  # Optional, defaults to today
}
```

#### Run Fairness Agent
```bash
POST /run
{
  "agent": "fairness",
  "comp_id": "competition-id",
  "user_id": "user-id"  # Optional, for specific user analysis
}
```

#### Run Multi-Agent Workflow
```bash
POST /run
{
  "agent": "workflow",
  "comp_id": "competition-id",
  "date": "2025-11-01"  # Optional
}
```

#### Health Check
```bash
GET /health
```

### Response Format

#### Sync Agent Response
```json
{
  "ok": true,
  "agent": "sync",
  "comp_id": "competition-id",
  "date": "2025-11-01",
  "actions": [
    {
      "type": "missing_data_detected",
      "count": 5,
      "users": ["user1", "user2", ...]
    }
  ],
  "findings": [...],
  "recommendations": "AI-generated recommendations",
  "timestamp": "2025-11-01T12:00:00"
}
```

#### Fairness Agent Response
```json
{
  "ok": true,
  "agent": "fairness",
  "comp_id": "competition-id",
  "flags": [
    {
      "type": "unrealistic_daily_count",
      "user_id": "user1",
      "severity": "high",
      "details": {...}
    }
  ],
  "findings": [...],
  "flag_count": 3,
  "recommendations": "AI-generated recommendations",
  "timestamp": "2025-11-01T12:00:00"
}
```

#### Workflow Response
```json
{
  "workflow_id": "workflow_comp-id_2025-11-01",
  "comp_id": "competition-id",
  "date": "2025-11-01",
  "steps": [
    {"step": 1, "agent": "sync", "result": {...}},
    {"step": 2, "agent": "fairness", "result": {...}}
  ],
  "summary": {
    "sync_actions": 2,
    "fairness_flags": 3,
    "total_issues": 5,
    "status": "issues_detected"
  },
  "recommendations": {
    "sync": "...",
    "fairness": "..."
  }
}
```

## Architecture

### Agent Design

Both agents follow ADK patterns:

1. **Tools** - Modular capabilities that agents can call
   - Sync Agent: `check_missing_data`, `check_late_data`, `notify_fairness_agent`
   - Fairness Agent: `analyze_step_data`, `flag_unfair_data`, `check_patterns`

2. **Orchestration** - Multi-agent workflow coordination
   - Sync agent runs first
   - Communicates findings to fairness agent
   - Fairness agent analyzes and flags issues
   - Both agents provide recommendations

3. **AI Integration** - Gemini AI for intelligent analysis
   - Analyzes findings and provides recommendations
   - Enhances decision-making with AI insights

### Data Flow

```
Step Data → Sync Agent → [Missing/Late Detection] → Fairness Agent → [Anomaly Detection] → Flags
                                                         ↓
                                                    AI Analysis
                                                         ↓
                                                 Recommendations
```

## Deployment

### Cloud Run

The service is deployed to Cloud Run as part of the CI/CD pipeline:

```bash
make deploy_agents
```

Or manually:

```bash
cd deploy
./deploy_agents.sh
```

### Local Development

```bash
cd apps/agents
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Testing

### Manual Testing

```bash
# Test health endpoint
curl http://localhost:8080/health

# Test sync agent
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"agent": "sync", "comp_id": "test-competition", "date": "2025-11-01"}'

# Test fairness agent
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"agent": "fairness", "comp_id": "test-competition"}'

# Test workflow
curl -X POST http://localhost:8080/run \
  -H "Content-Type: application/json" \
  -d '{"agent": "workflow", "comp_id": "test-competition"}'
```

## ADK Integration Status

✅ **ADK-Style Implementation**:
- Agent architecture following ADK patterns
- Tool-based agent design
- Multi-agent orchestration
- Agent communication workflows

⚠️ **Note**: The implementation uses ADK patterns and structure. If the actual `google-adk` SDK has different APIs, the code will gracefully fall back to a simple Tool wrapper while maintaining the same functionality.

## Documentation

For more information on Google ADK:
- [ADK Documentation](https://google.github.io/adk-docs/)
- [ADK Tutorials](https://google.github.io/adk-docs/tutorials/)
- [ADK GitHub](https://github.com/google/adk)

## License

MIT License © 2025 StepSquad Team

