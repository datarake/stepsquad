# StepSquad Frontend

A React-based web application for managing fitness competitions with role-based access control.

## Features

- **Authentication**: Firebase Authentication with dev mode support
- **Role-based Access**: ADMIN and MEMBER roles with different permissions
- **Competition Management**: Full CRUD operations for admins, read-only for members
- **Modern UI**: Built with React 18, TypeScript, Tailwind CSS, and Lucide icons
- **State Management**: React Query for efficient API state management

## Tech Stack

- React 18 + Vite
- TypeScript
- React Router for navigation
- Firebase Authentication
- Tailwind CSS for styling
- Lucide React for icons
- React Query for data fetching
- React Hot Toast for notifications

## Getting Started

### Prerequisites

- Node.js 18+ 
- pnpm (recommended) or npm

### Installation

1. Install dependencies:
```bash
pnpm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
```

Edit `.env.local` with your configuration:
```env
VITE_API_BASE_URL=http://localhost:8080
VITE_USE_DEV_AUTH=true
VITE_ADMIN_EMAIL=admin@stepsquad.com
```

3. Start the development server:
```bash
pnpm dev
```

The app will be available at `http://localhost:5173`

## Environment Variables

- `VITE_API_BASE_URL`: API base URL (default: `http://localhost:8080`)
- `VITE_USE_DEV_AUTH`: Enable dev mode authentication (`true`/`false`)
- `VITE_ADMIN_EMAIL`: Default admin email for dev mode
- `VITE_FIREBASE_*`: Firebase configuration (when dev mode is disabled)

## Development Mode

When `VITE_USE_DEV_AUTH=true`, the app uses a simplified authentication flow:
- Enter any email to "login"
- The email is stored in localStorage
- Admin role is assigned if email matches `VITE_ADMIN_EMAIL`
- All other emails get MEMBER role

## Project Structure

```
src/
├── types.ts              # TypeScript type definitions
├── api.ts                # API client with authentication
├── auth.tsx              # Authentication context and hooks
├── App.tsx               # Main app component with routing
├── main.tsx              # App entry point
├── AppShell.tsx          # Layout component with navigation
├── LoginForm.tsx         # Authentication form
├── ProtectedRoute.tsx    # Route guards
├── HomePage.tsx          # Competitions list page
├── CompetitionList.tsx   # Competitions list component
├── CompetitionForm.tsx   # Create/edit competition form
├── CompetitionDetail.tsx # Competition detail view
├── CompetitionDetailPage.tsx
├── CompetitionCreatePage.tsx
└── CompetitionEditPage.tsx
```

## API Integration

The frontend integrates with the StepSquad API:

- `GET /health` - Health check
- `GET /me` - Get current user info
- `GET /competitions` - List competitions
- `GET /competitions/:id` - Get competition details
- `POST /competitions` - Create competition (ADMIN only)
- `PATCH /competitions/:id` - Update competition (ADMIN only)
- `DELETE /competitions/:id` - Delete competition (ADMIN only)

## Building for Production

```bash
pnpm build
```

The built files will be in the `dist/` directory, ready for deployment to any static hosting service.

## Testing

```bash
# Type checking
pnpm type-check

# Run tests (when implemented)
pnpm test
```
