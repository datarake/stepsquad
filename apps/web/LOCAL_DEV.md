# StepSquad Frontend - Local Development Guide

## Quick Start

1. **Navigate to the web directory:**
```bash
cd apps/web
```

2. **Install dependencies** (if not already installed):
```bash
npm install
# or if you prefer pnpm:
pnpm install
```

3. **Create environment file** (if it doesn't exist):
```bash
# Create .env.local file
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8080
VITE_USE_DEV_AUTH=true
VITE_ADMIN_EMAIL=admin@stepsquad.com
EOF
```

4. **Start the development server:**
```bash
npm run dev
# or:
pnpm dev
```

5. **Access the app:**
   - Open your browser and go to: **http://localhost:5173**
   - The app will automatically reload when you make changes

## Prerequisites

- **Node.js** (v18 or higher)
- **npm** or **pnpm** package manager
- **Backend API** running on `http://localhost:8080` (optional, but needed for full functionality)

## Environment Variables

Create a `.env.local` file in `apps/web/` with:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8080

# Authentication Configuration
VITE_USE_DEV_AUTH=true
VITE_ADMIN_EMAIL=admin@stepsquad.com

# Firebase Configuration (when VITE_USE_DEV_AUTH=false)
# VITE_FIREBASE_API_KEY=your-api-key
# VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
# VITE_FIREBASE_PROJECT_ID=your-project-id
# VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
# VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
# VITE_FIREBASE_APP_ID=1:123456789:web:abcdef
```

## First Time Setup

1. Install dependencies:
```bash
cd apps/web
npm install
```

2. Start the dev server:
```bash
npm run dev
```

3. Open http://localhost:5173 in your browser

4. Login with:
   - Email: `admin@stepsquad.com` (gets ADMIN role)
   - Any other email (gets MEMBER role)

## Troubleshooting

**Port 5173 already in use?**
- Vite will automatically use the next available port
- Check the terminal output for the actual port number

**Can't connect to API?**
- Make sure the backend is running on `http://localhost:8080`
- Check `VITE_API_BASE_URL` in `.env.local`

**Module not found errors?**
- Run `npm install` again
- Delete `node_modules` and `package-lock.json`, then run `npm install`

**TypeScript errors?**
- Run `npm run type-check` to see detailed errors
- Make sure all dependencies are installed

## Available Scripts

- `npm run dev` - Start development server (port 5173)
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Check TypeScript types

## Development Tips

- The app uses hot module replacement (HMR) - changes appear instantly
- Check browser console for errors
- Use React DevTools for debugging
- API errors are shown as toast notifications
