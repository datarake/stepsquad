# StepSquad API

A FastAPI-based backend for managing fitness competitions with role-based access control.

## Features

- **Authentication**: Firebase ID token (production) or Dev bypass via `X-Dev-User` header (local)
- **Role-based Access**: ADMIN and MEMBER roles with different permissions
- **Competition Management**: Full CRUD operations for admins, read-only for members
- **Data Validation**: Comprehensive validation for dates, limits, and business rules
- **Soft Delete**: Competitions are archived rather than permanently deleted
- **Audit Logging**: Admin actions are logged for observability

## Tech Stack

- **FastAPI** (Python 3.11)
- **Firestore** for data storage
- **Firebase Authentication** (production)
- **Pydantic** for data validation
- **Uvicorn** for ASGI server

## Environment Variables

### Required
- `GCP_ENABLED`: `"true"` for production (Firebase auth), `"false"` for local dev
- `COMP_TZ`: Default timezone (default: `"Europe/Bucharest"`)

### Optional
- `FIREBASE_WEB_CLIENT_ID`: Required for Firebase token verification in production
- `BQ_DATASET`: BigQuery dataset for analytics (default: `"stepsquad"`)
- `PUBSUB_TOPIC_INGEST`: Pub/Sub topic for step ingestion
- `PUBSUB_SUB_INGEST`: Pub/Sub subscription for step ingestion
- `GRACE_DAYS`: Grace period for step submissions (default: `2`)

## Authentication

### Development Mode (`GCP_ENABLED=false`)
- Use `X-Dev-User: <email>` header
- Email `admin@stepsquad.club` gets ADMIN role
- All other emails get MEMBER role
- Users are created automatically on first access

### Production Mode (`GCP_ENABLED=true`)
- Use `Authorization: Bearer <Firebase ID token>` header
- Firebase token verification (implementation pending)
- User roles determined by Firebase custom claims or email

## API Endpoints

### Health
- `GET /health` → `{ ok: true, time, tz }`

### Authentication & Profile
- `GET /me` → `{ uid, email, role }` (creates user if missing)

### Competitions
- `GET /competitions` → `{ rows: Competition[] }` (ordered by created_at desc)
- `GET /competitions/{comp_id}` → `Competition` or `404`
- `POST /competitions` → `{ ok: true, comp_id }` (ADMIN only)
- `PATCH /competitions/{comp_id}` → `{ ok: true }` (ADMIN only)
- `DELETE /competitions/{comp_id}` → `{ ok: true }` (ADMIN only, soft delete)

### Legacy Endpoints (unchanged)
- `POST /ingest/steps` → queues/write steps
- `GET /leaderboard/individual` → `{ rows }`
- `GET /leaderboard/team` → `{ rows }`
- `POST /teams` → create team
- `POST /teams/join` → join team

## Data Models

### User Document
```json
{
  "uid": "string",
  "email": "string (lowercase)",
  "role": "ADMIN" | "MEMBER",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

### Competition Document
```json
{
  "comp_id": "string (unique)",
  "name": "string",
  "status": "DRAFT" | "REGISTRATION" | "ACTIVE" | "ENDED" | "ARCHIVED",
  "tz": "string (IANA timezone)",
  "registration_open_date": "YYYY-MM-DD",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "max_teams": "number (1-500)",
  "max_members_per_team": "number (1-200)",
  "created_by": "string (user uid)",
  "created_at": "ISO timestamp",
  "updated_at": "ISO timestamp"
}
```

## Validation Rules

### Competition Creation/Update
- **Date Ordering**: `registration_open_date <= start_date <= end_date`
- **Date Format**: All dates must be in `YYYY-MM-DD` format
- **Max Teams**: 1-500
- **Max Members per Team**: 1-200
- **Comp ID**: Must be unique, 3-20 characters
- **Name**: 3-80 characters

### Status Transitions
- All statuses can be set to any other status except `ARCHIVED`
- `ARCHIVED` status is only set via `DELETE` endpoint (soft delete)

## Error Responses

- `401` - Missing/invalid authentication
- `403` - Role forbidden (non-admin trying admin operations)
- `404` - Resource not found
- `409` - Conflict (duplicate `comp_id`)
- `422` - Validation error (invalid dates, ranges, etc.)
- `501` - Firebase authentication not implemented (when using Bearer token)

All errors return JSON: `{ "detail": "human readable message" }`

## Getting Started

### Local Development

1. Install dependencies:
```bash
pip install fastapi uvicorn python-multipart
```

2. Set environment variables:
```bash
export GCP_ENABLED=false
export COMP_TZ=Europe/Bucharest
```

3. Run the server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

4. Test the API:
```bash
python test_api.py
```

### Production Deployment

1. Set environment variables:
```bash
export GCP_ENABLED=true
export FIREBASE_WEB_CLIENT_ID=your-firebase-client-id
export COMP_TZ=Europe/Bucharest
```

2. Deploy to Cloud Run:
```bash
gcloud run deploy stepsquad-api --source . --port 8080
```

## Testing

The included `test_api.py` script tests all major functionality:

- Health check
- Authentication (admin and member)
- Competition CRUD operations
- Validation rules
- Access control
- Soft delete

Run tests:
```bash
python test_api.py
```

## Security Considerations

- **Dev Mode**: Only honor `X-Dev-User` when `GCP_ENABLED=false`
- **Production**: Require valid Firebase tokens
- **Role-based Access**: Enforce ADMIN-only operations server-side
- **Input Validation**: Validate all inputs with Pydantic models
- **Audit Logging**: Log all admin actions with user email and action details

## Firestore Indexing

For optimal performance, create these composite indexes:

- `{ status: asc, created_at: desc }` - for filtering competitions by status
- `{ created_at: desc }` - for listing competitions (single field sort usually fine)

## Monitoring & Observability

- All admin actions are logged with:
  - Admin email
  - Action type (create/update/archive)
  - Competition ID and name
  - Timestamp

- Health endpoint provides basic service status
- Error responses include detailed error messages
- All timestamps are in ISO format UTC

## Future Enhancements

- [ ] Implement Firebase token verification
- [ ] Add pagination to competitions list
- [ ] Add filtering by status/timezone
- [ ] Add user management endpoints
- [ ] Add competition analytics
- [ ] Add rate limiting
- [ ] Add request/response logging middleware
