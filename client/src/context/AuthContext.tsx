import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { onAuthStateChanged, signOut, User, onIdTokenChanged } from "firebase/auth";
import { auth } from "../api/firebase";

const AuthContext = createContext<{ user: User | null; loading: boolean, logout: () => void }>({
  user: null,
  loading: true,
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Firebase will detect token & restore session automatically
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
        if (currentUser) {
            console.log("User detected. Sign in automatically happens.");
            console.log("User:", currentUser.email);
        }
        
        setUser(currentUser);
        setLoading(false);
    });

    return () => unsubscribe(); // Cleanup listener on unmount
  }, []);

  // Add token refresh listener
  useEffect(() => {
    const tokenRefreshUnsubscribe = onIdTokenChanged(auth, async (currentUser) => {
      if (currentUser) {
        // Get fresh token when ID token changes
        try {
          const token = await currentUser.getIdToken();
          localStorage.setItem("sanvia-refreshToken", token);
          console.log("Token refreshed and stored");
        } catch (error) {
          console.error("Error refreshing token:", error);
        }
      } else {
        // Clear token when user not available
        localStorage.removeItem("sanvia-refreshToken");
      }
    });

    // Force token refresh every 55 minutes (before 60-minute expiration)
    const tokenRefreshInterval = setInterval(async () => {
      const currentUser = auth.currentUser;
      if (currentUser) {
        try {
          // Force refresh token
          const token = await currentUser.getIdToken(true);
          localStorage.setItem("sanvia-refreshToken", token);
          console.log("Token refreshed proactively");
        } catch (error) {
          console.error("Error during scheduled token refresh:", error);
        }
      }
    }, 55 * 60 * 1000);

    return () => {
      tokenRefreshUnsubscribe();
      clearInterval(tokenRefreshInterval);
    };
  }, []);

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null); // 🔹 Update state after logout
      localStorage.removeItem("sanvia-refreshToken");
      sessionStorage.removeItem("AES_KEY")
    } catch (error) {
      console.error("Logout Error:", error);
    }
    console.log("Logout successful.");
  };

  return (
    <AuthContext.Provider value={{ user, loading, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom Hook for easy access
export const useAuth = () => useContext(AuthContext);