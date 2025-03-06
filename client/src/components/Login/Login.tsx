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
          user.getIdToken(false).then((token) => {
            localStorage.setItem("sanvia-refreshToken", token);
            console.log("Token is stored properly.");
          });

          onLoginSuccess();
          navigate("/");
        })
        .catch((error) => {
          console.log("Sign In Failed.");
          setError(error);
        });
    } catch (e) {
      setError(`Error: ${e}`);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Login</h2>
        {error && <p className="error">{error}</p>}
        <input
          type="text"
          placeholder="Email"
          className="input"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="input"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button onClick={handleLogin} className="button">
          Login
        </button>

        <p className="toggleText">
          Don't have an account?{" "}
          <span className="link" onClick={() => navigate("/auth/signup")}>
            Sign Up here
          </span>
        </p>
      </div>
    </div>
  );
};

export default Login;
