# Quick Start - Test Firebase Authentication

**Everything is configured!** Follow these steps to test:

---

## 🚀 Quick Test (3 Steps)

### Step 1: Start Backend

```bash
cd apps/api
export GCP_ENABLED=true
export GOOGLE_APPLICATION_CREDENTIALS=/Users/bogdan/.config/stepsquad/firebase-service-account.json
uvicorn main:app --host 0.0.0.0 --port 8080
```

**Expected**: Should see `INFO: Uvicorn running on http://0.0.0.0:8080`

**Test**: Open another terminal and run:
```bash
curl http://localhost:8080/health | python3 -m json.tool
```

Should show `"firebase_initialized": true` ✅

---

### Step 2: Start Frontend

```bash
cd apps/web
pnpm dev
```

**Expected**: Should see `Local: http://localhost:5174/`

**Test**: Open http://localhost:5174 in browser ✅

---

### Step 3: Sign In

1. Click **"Sign in"**
2. Email: `admin@stepsquad.com`
3. Password: (your Firebase password)
4. Click **"Sign in"**

**Expected**: Should redirect to home page with admin access ✅

---

## ✅ Verification

After signing in, you should see:
- ✅ Home page with competitions list
- ✅ "Create Competition" button (admin feature)
- ✅ "Users" menu/link (admin feature)
- ✅ Your email shown in UI
- ✅ "Sign out" button

---

## 🔍 Quick Troubleshooting

**Backend not starting?**
- Check: `export GCP_ENABLED=true`
- Check: `export GOOGLE_APPLICATION_CREDENTIALS=/Users/bogdan/.config/stepsquad/firebase-service-account.json`
- Check: Service account key exists at that path

**Frontend not loading?**
- Check: `.env.local` file exists in `apps/web/`
- Restart: `pnpm dev` (after changing `.env.local`)

**Can't sign in?**
- Check: Email/Password is enabled in Firebase Console
- Check: User exists in Firebase Authentication
- Check: Email/password are correct
- Check: Browser console for errors

**Not getting ADMIN role?**
- User needs to sign out and sign in again (custom claims need fresh token)
- Check: `/me` endpoint returns `role: ADMIN`

---

## 📚 More Details

- [TEST_FIREBASE_AUTH.md](TEST_FIREBASE_AUTH.md) - Detailed testing guide
- [FIREBASE_COMPLETE.md](FIREBASE_COMPLETE.md) - Complete configuration summary
- [SET_CUSTOM_CLAIMS.md](SET_CUSTOM_CLAIMS.md) - Custom claims guide

---

**Ready to test!** 🚀

