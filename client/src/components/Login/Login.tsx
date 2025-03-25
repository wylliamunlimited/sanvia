import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Login.css"; // Import the CSS file
import { useFirebase } from "../../provider/FirebaseContext";
import { signInWithEmailAndPassword } from "firebase/auth";

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
          
          onLoginSuccess();
          navigate("/");
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
        />
        <div className="password-container">
          <input
            type={showPassword ? "text" : "password"}
            placeholder="Password"
            className="password-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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
