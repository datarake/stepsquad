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

// Helper function to extract error code from Firebase error message
function extractErrorCode(error: any): string {
  // Try to get code directly from error object
  if (error?.code) {
    return error.code;
  }
  
  // Try to extract from message string like "Firebase: Error (auth/error-code)."
  const message = error?.message || '';
  const match = message.match(/\(auth\/([^)]+)\)/);
  if (match) {
    return `auth/${match[1]}`;
  }
  
  return '';
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
    
    // Extract error code from error object or message
    const errorCode = extractErrorCode(error);
    
    // Provide user-friendly error messages based on Firebase error codes
    if (errorCode === 'auth/user-not-found') {
      const customError = new Error('No account found with this email address. Please sign up first.');
      (customError as any).code = errorCode;
      throw customError;
    } else if (errorCode === 'auth/wrong-password') {
      throw new Error('Incorrect password. Please try again.');
    } else if (errorCode === 'auth/invalid-credential') {
      // auth/invalid-credential can mean either "user not found" or "wrong password"
      // We'll let the auth.tsx handle this by trying to sign up
      const customError = new Error('No account found with this email address. Please sign up first.');
      (customError as any).code = 'auth/user-not-found';
      throw customError;
    } else if (errorCode === 'auth/invalid-email') {
      throw new Error('Invalid email address. Please check your email and try again.');
    } else if (errorCode === 'auth/user-disabled') {
      throw new Error('This account has been disabled. Please contact support.');
    } else if (errorCode === 'auth/too-many-requests') {
      throw new Error('Too many failed login attempts. Please try again later.');
    } else if (errorCode === 'auth/email-already-in-use') {
      // This shouldn't happen on sign-in, but handle it just in case
      throw new Error('This email is already registered. Please sign in instead.');
    }
    
    // Fallback: provide a generic but user-friendly message
    throw new Error('Sign in failed. Please check your credentials and try again.');
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
    
    // Extract error code from error object or message
    const errorCode = extractErrorCode(error);
    
    // Provide user-friendly error messages
    if (errorCode === 'auth/email-already-in-use') {
      throw new Error('This email is already registered. Please sign in instead.');
    } else if (errorCode === 'auth/weak-password') {
      throw new Error('Password is too weak. Please choose a stronger password (at least 6 characters).');
    } else if (errorCode === 'auth/invalid-email') {
      throw new Error('Invalid email address. Please check your email and try again.');
    }
    
    // Fallback: provide a generic but user-friendly message
    throw new Error('Sign up failed. Please try again.');
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
