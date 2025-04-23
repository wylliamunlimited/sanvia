import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./auth.css";
import { useFirebase } from "../../../context/FirebaseContext";
import { signInWithEmailAndPassword } from "firebase/auth";
import { handleFormNavigation } from "../../../shared/utils/formNavigation";
import securityApi from "../../../api/encryption/security";

interface LoginProps {
  onLoginSuccess: () => void;
}

const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const navigate = useNavigate();

  const { auth } = useFirebase();

  const handleLogin = () => {
    try {
      if (!email || !password) {
        setError("Please enter both email and password.");
        return;
      }

      signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          // Save token to cookie
          const user = userCredential.user;
          user.getIdToken(true).then((token) => {
            localStorage.setItem("sanvia-refreshToken", token);
            console.log("Token is stored properly.");
          });

          securityApi.getEncryptionKey().then((key) => {
            sessionStorage.setItem("AES_KEY", key);
            console.log("AES Encryption Key stored properly.");
          });
          
          onLoginSuccess();
          navigate("/chat");
        })
        .catch((error) => {
          console.log(`Sign In Failed. ${error}`);
          setError(error.message);
          return;
        });
    } catch (e) {
      setError(`Error: ${e}`);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Sign In</h2>
        <p className="welcome-message">Welcome back to Sanvia!</p>
        <input
          type="text"
          placeholder="Email"
          className="input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyDown={(e) => handleFormNavigation(e, 'password')}
        />
        <div className="password-container">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            className="password-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => handleFormNavigation(e, undefined, handleLogin)}
          />
          {password && (
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          )}
        </div>
        <button className="button" onClick={handleLogin}>
          Sign In
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      <p className="toggleText">
        Don't have an account?{" "}
        <span className="link" onClick={() => navigate("/auth/signup")}>
          Sign Up
        </span>
      </p>
    </div>
  );
};

export default Login;
