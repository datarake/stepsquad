// Firebase configuration and initialization
import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import { 
  getAuth, 
  Auth, 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  User as FirebaseUser
} from 'firebase/auth';

interface FirebaseConfig {
  apiKey: string;
  authDomain: string;
  projectId: string;
  storageBucket: string;
  messagingSenderId: string;
  appId: string;
}

let firebaseApp: FirebaseApp | null = null;
let firebaseAuth: Auth | null = null;

export function initFirebase(): { app: FirebaseApp; auth: Auth } | null {
  // Return null if Firebase is not configured
  const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
  if (!apiKey) {
    console.warn('Firebase not configured - missing VITE_FIREBASE_API_KEY');
    return null;
  }

  // Initialize only once
  if (firebaseApp && firebaseAuth) {
    return { app: firebaseApp, auth: firebaseAuth };
  }

  const config: FirebaseConfig = {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: import.meta.env.VITE_FIREBASE_APP_ID,
  };

  try {
    // Initialize Firebase only if not already initialized
    const apps = getApps();
    if (apps.length === 0) {
      firebaseApp = initializeApp(config);
    } else {
      firebaseApp = apps[0];
    }

    firebaseAuth = getAuth(firebaseApp);
    return { app: firebaseApp, auth: firebaseAuth };
  } catch (error) {
    console.error('Firebase initialization error:', error);
    return null;
  }
}

export async function firebaseSignIn(email: string, password: string): Promise<string> {
  const firebase = initFirebase();
  if (!firebase) {
    throw new Error('Firebase not configured');
  }

  try {
    const userCredential = await signInWithEmailAndPassword(firebase.auth, email, password);
    const token = await userCredential.user.getIdToken();
    return token;
  } catch (error: any) {
    console.error('Firebase sign in error:', error);
    throw new Error(error.message || 'Sign in failed');
  }
}

export async function firebaseSignUp(email: string, password: string): Promise<string> {
  const firebase = initFirebase();
  if (!firebase) {
    throw new Error('Firebase not configured');
  }

  try {
    const userCredential = await createUserWithEmailAndPassword(firebase.auth, email, password);
    const token = await userCredential.user.getIdToken();
    return token;
  } catch (error: any) {
    console.error('Firebase sign up error:', error);
    throw new Error(error.message || 'Sign up failed');
  }
}

export async function firebaseSignOut(): Promise<void> {
  const firebase = initFirebase();
  if (!firebase) {
    return;
  }

  try {
    await signOut(firebase.auth);
  } catch (error) {
    console.error('Firebase sign out error:', error);
  }
}

export function firebaseGetCurrentUser(): Promise<FirebaseUser | null> {
  return new Promise((resolve) => {
    const firebase = initFirebase();
    if (!firebase) {
      resolve(null);
      return;
    }

    const unsubscribe = onAuthStateChanged(firebase.auth, (user) => {
      unsubscribe();
      resolve(user);
    });
  });
}

export async function firebaseGetIdToken(): Promise<string | null> {
  const firebase = initFirebase();
  if (!firebase) {
    return null;
  }

  try {
    const user = firebase.auth.currentUser;
    if (user) {
      return await user.getIdToken();
    }
    return null;
  } catch (error) {
    console.error('Error getting Firebase ID token:', error);
    return null;
  }
}
