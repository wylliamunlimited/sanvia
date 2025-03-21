
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { onAuthStateChanged, signOut, User } from "firebase/auth";
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
        }
        
        setUser(currentUser);
        setLoading(false);
    });

    return () => unsubscribe(); // Cleanup listener on unmount
  }, [auth]);

  const logout = async () => {
    try {
      await signOut(auth);
      setUser(null); // 🔹 Update state after logout
      localStorage.removeItem("sanvia-refreshToken");
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