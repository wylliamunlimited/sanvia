import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./auth.css";
// import { useAuth } from "../../provider/AuthContext";
import { auth } from "../../../api/firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";
import { firestoreApi } from "../../../api/firestoreApi";
import { capitalizeFirstLetter } from "../../../shared/utils/capitalize";

interface SignUpProps {
  onSignUpSuccess: () => void;
}

const SignUp: React.FC<SignUpProps> = ({ onSignUpSuccess }) => {
  const [name, setName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState<boolean>(false);
  const [agreeToTerms, setAgreeToTerms] = useState<boolean>(false);
  const navigate = useNavigate();

  // const { user, loading, logout } = useAuth();

  const handleSignUp = async () => {
    try {
      if (!email || !password || !confirmPassword || !name || !lastName) {
        setError("Please fill out all fields.");
        return;
      }

      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      if (!agreeToTerms) {
        setError("Please agree to the Privacy Policy.");
        return;
      }

      createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          user.getIdToken(true).then((token) => {
            localStorage.setItem("sanvia-refreshToken", token);
            console.log("Token is stored properly.");
          }).then(() => {
            firestoreApi.initializeProfile(name, lastName)
            .then((data) => {
              console.log(`Initialized profile with names, ${data}`);
              setError("");
              onSignUpSuccess();
              navigate("/onboarding");
            })
            .catch((error) => {
              setError(error);
            });
          });
        })
        .catch((error) => {
          console.log("Sign Up Failed.");
          setError(error.message);
        });
    } catch (e) {
      setError(`Error: ${e}`);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Sign Up</h2>
        <p className="welcome-message">Welcome to Sanvia! Sign up to get started.</p>
        <input
          type="name"
          placeholder="First Name"
          className="input"
          value={name}
          onChange={(e) => setName(capitalizeFirstLetter(e.target.value))}
        />
        <input
          type="lastName"
          placeholder="Last Name"
          className="input"
          value={lastName}
          onChange={(e) => setLastName(capitalizeFirstLetter(e.target.value))}
        />
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
        {password && (
          <div className="password-container">
            <input
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirm Password"
              className="password-input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            {confirmPassword && (
              <button
                type="button"
                className="toggle-password"
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              >
                {showConfirmPassword ? "Hide" : "Show"}
              </button>
            )}
          </div>
        )}
        <div className="terms-container">
          <input
            type="checkbox"
            id="terms"
            checked={agreeToTerms}
            onChange={(e) => setAgreeToTerms(e.target.checked)}
            className="terms-checkbox"
          />
          <label htmlFor="terms" className="terms-label">
            I agree to Sanvia's{" "}
            <a 
              href="https://sanvia.app/privacy-policy" 
              target="_blank" 
              className="link"
            >
              Privacy Policy
            </a>.
          </label>
        </div>
        <button className="button" onClick={handleSignUp}>
          Sign Up
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      <p className="toggleText">
        Already have an account?{" "}
        <span className="link" onClick={() => navigate("/onboarding")}>
          Login
        </span>
      </p>
    </div>
  );
};

export default SignUp;
