# StepSquad Architecture

## System Architecture

This document provides a detailed view of the StepSquad architecture, focusing on the multi-agent AI system built with Google ADK.

## High-Level Architecture

```mermaid
graph TB
    subgraph "User Layer"
        U[Users]
        D[Garmin/Fitbit Devices]
    end
    
    subgraph "Frontend - Cloud Run"
        WEB[React Web App<br/>www.stepsquad.club<br/>React 18 + TypeScript + Tailwind]
    end
    
    subgraph "Backend Services - Cloud Run"
        API[FastAPI Backend<br/>api.stepsquad.club<br/>Python 3.11 + FastAPI]
        WORKER[Sync Worker Service<br/>Background Processing<br/>Device Sync]
    end
    
    subgraph "AI Agents - Cloud Run"
        AGENTS[AI Agents Service<br/>Google ADK + Gemini 2.5 Flash]
        SYNC[Sync Agent<br/>Missing Data Detection]
        FAIR[Fairness Agent<br/>Anomaly Detection]
        AGENTS --> SYNC
        AGENTS --> FAIR
        SYNC -.->|Communicates| FAIR
    end
    
    subgraph "Data Layer"
        FS[(Firestore<br/>User & Competition Data)]
        BQ[(BigQuery<br/>Analytics & Reporting)]
    end
    
    subgraph "Messaging"
        PUB[Pub/Sub Topic<br/>steps.ingest]
    end
    
    subgraph "AI Services"
        GEMINI[Gemini 2.5 Flash<br/>AI Analysis & Recommendations]
    end
    
    U --> WEB
    D --> API
    WEB -->|HTTPS| API
    API --> FS
    API --> PUB
    PUB --> WORKER
    WORKER --> FS
    WORKER --> BQ
    API --> AGENTS
    AGENTS --> GEMINI
    AGENTS --> FS
    AGENTS --> BQ
    FS --> WEB
    BQ --> AGENTS
    
    style AGENTS fill:#4CAF50,stroke:#2E7D32,color:#fff
    style SYNC fill:#81C784,stroke:#4CAF50,color:#fff
    style FAIR fill:#81C784,stroke:#4CAF50,color:#fff
    style GEMINI fill:#FF9800,stroke:#F57C00,color:#fff
    style WEB fill:#2196F3,stroke:#1976D2,color:#fff
    style API fill:#2196F3,stroke:#1976D2,color:#fff
    style WORKER fill:#2196F3,stroke:#1976D2,color:#fff
```

## AI Agents Architecture

```mermaid
graph LR
    subgraph "AI Agents Service - Cloud Run"
        ADK[Google ADK<br/>Agent Development Kit]
        
        subgraph "Agents"
            SYNC[Sync Agent<br/>Tools: 3]
            FAIR[Fairness Agent<br/>Tools: 3]
        end
        
        subgraph "Orchestration"
            WORKFLOW[Multi-Agent Workflow<br/>Agent Communication]
        end
    end
    
    subgraph "AI Services"
        GEMINI[Gemini 2.5 Flash<br/>AI Analysis]
    end
    
    subgraph "Data Sources"
        FS[(Firestore)]
        BQ[(BigQuery)]
    end
    
    ADK --> SYNC
    ADK --> FAIR
    SYNC --> WORKFLOW
    FAIR --> WORKFLOW
    WORKFLOW --> GEMINI
    SYNC --> FS
    FAIR --> FS
    SYNC --> BQ
    FAIR --> BQ
    GEMINI --> SYNC
    GEMINI --> FAIR
    
    style ADK fill:#4CAF50,stroke:#2E7D32,color:#fff
    style SYNC fill:#81C784,stroke:#4CAF50,color:#fff
    style FAIR fill:#81C784,stroke:#4CAF50,color:#fff
    style WORKFLOW fill:#66BB6A,stroke:#4CAF50,color:#fff
    style GEMINI fill:#FF9800,stroke:#F57C00,color:#fff
```

## Data Flow Architecture

### Step Ingestion Flow

```mermaid
sequenceDiagram
    participant U as User
    participant D as Device
    participant API as API Service
    participant PS as Pub/Sub
    participant W as Worker Service
    participant FS as Firestore
    participant BQ as BigQuery
    
    U->>D: Sync Steps
    D->>API: OAuth Callback
    API->>FS: Store Device Tokens
    API->>PS: Publish Step Event
    PS->>W: Push Message
    W->>FS: Write Daily Steps
    W->>BQ: Insert Analytics
    W->>API: Update Sync Time
```

### AI Agent Analysis Flow

```mermaid
sequenceDiagram
    participant API as API Service
    participant AG as Agents Service
    participant SA as Sync Agent
    participant FA as Fairness Agent
    participant G as Gemini AI
    participant FS as Firestore
    participant BQ as BigQuery
    
    API->>AG: Trigger Analysis
    AG->>SA: Run Sync Agent
    SA->>FS: Check Missing Data
    SA->>BQ: Analyze Patterns
    SA->>G: Get Recommendations
    G-->>SA: AI Insights
    SA->>FA: Notify Findings
    FA->>FS: Check Step Data
    FA->>BQ: Analyze Anomalies
    FA->>G: Get Recommendations
    G-->>FA: AI Insights
    FA->>FS: Flag Unfair Data
    AG->>API: Return Results
```

## Service Communication

```mermaid
graph TB
    subgraph "Cloud Run Services"
        WEB[Web Service<br/>Port 8080]
        API[API Service<br/>Port 8080]
        WORKER[Worker Service<br/>Port 8080]
        AGENTS[Agents Service<br/>Port 8080]
    end
    
    subgraph "Google Cloud Services"
        FS[Firestore]
        BQ[BigQuery]
        PS[Pub/Sub]
        GEMINI[Gemini AI]
    end
    
    WEB -->|HTTPS| API
    API -->|Read/Write| FS
    API -->|Publish| PS
    PS -->|Push| WORKER
    WORKER -->|Write| FS
    WORKER -->|Insert| BQ
    API -->|Trigger| AGENTS
    AGENTS -->|Read| FS
    AGENTS -->|Query| BQ
    AGENTS -->|Analyze| GEMINI
    
    style WEB fill:#2196F3,stroke:#1976D2,color:#fff
    style API fill:#2196F3,stroke:#1976D2,color:#fff
    style WORKER fill:#2196F3,stroke:#1976D2,color:#fff
    style AGENTS fill:#4CAF50,stroke:#2E7D32,color:#fff
    style GEMINI fill:#FF9800,stroke:#F57C00,color:#fff
```

## Technology Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **Authentication**: Firebase Authentication

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11
- **Authentication**: Firebase Admin SDK
- **Database**: Firestore
- **Analytics**: BigQuery

### AI Agents
- **Framework**: Google ADK (Agent Development Kit)
- **AI Model**: Gemini 2.5 Flash
- **Language**: Python 3.11
- **Orchestration**: Multi-agent workflows

### Infrastructure
- **Compute**: Google Cloud Run
- **Database**: Firestore (NoSQL)
- **Analytics**: BigQuery
- **Messaging**: Pub/Sub
- **CI/CD**: GitHub Actions
- **Domains**: Custom domains via Cloud Run

## Deployment Architecture

```mermaid
graph TB
    subgraph "GitHub"
        GH[GitHub Repository]
        ACTIONS[GitHub Actions<br/>CI/CD Pipeline]
    end
    
    subgraph "Google Cloud Build"
        BUILD[Cloud Build<br/>Docker Image Build]
    end
    
    subgraph "Google Cloud Run"
        WEB[Web Service<br/>www.stepsquad.club]
        API[API Service<br/>api.stepsquad.club]
        WORKER[Worker Service]
        AGENTS[Agents Service]
    end
    
    subgraph "Google Cloud Services"
        FS[Firestore]
        BQ[BigQuery]
        PS[Pub/Sub]
    end
    
    GH -->|Push| ACTIONS
    ACTIONS -->|Build| BUILD
    BUILD -->|Deploy| WEB
    BUILD -->|Deploy| API
    BUILD -->|Deploy| WORKER
    BUILD -->|Deploy| AGENTS
    WEB --> FS
    API --> FS
    API --> PS
    WORKER --> FS
    WORKER --> BQ
    AGENTS --> FS
    AGENTS --> BQ
    
    style ACTIONS fill:#9C27B0,stroke:#7B1FA2,color:#fff
    style BUILD fill:#FF9800,stroke:#F57C00,color:#fff
    style WEB fill:#2196F3,stroke:#1976D2,color:#fff
    style API fill:#2196F3,stroke:#1976D2,color:#fff
    style WORKER fill:#2196F3,stroke:#1976D2,color:#fff
    style AGENTS fill:#4CAF50,stroke:#2E7D32,color:#fff
```

## Security Architecture

- **Authentication**: Firebase Authentication (JWT tokens)
- **Authorization**: Role-based access control (ADMIN, MEMBER)
- **API Security**: Firebase Admin SDK token verification
- **Network**: HTTPS only, Cloud Run managed certificates
- **Data**: Firestore security rules, encrypted at rest
- **Secrets**: Environment variables, Google Secret Manager

## Scalability

- **Horizontal Scaling**: Cloud Run auto-scales based on traffic
- **Database**: Firestore scales automatically
- **Messaging**: Pub/Sub handles high throughput
- **Caching**: React Query for frontend caching
- **Load Balancing**: Cloud Run managed load balancing

---

For more details, see:
- [ADK_IMPLEMENTATION.md](./ADK_IMPLEMENTATION.md) - AI Agents implementation details
- [HACKATHON_SUBMISSION.md](./HACKATHON_SUBMISSION.md) - Hackathon submission details

