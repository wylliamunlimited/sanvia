import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./SignUp.css"; // Import shared styles
import { useAuth } from "../../provider/AuthContext";
import { auth } from "../../api/firebase";
import { createUserWithEmailAndPassword } from "firebase/auth";

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
  const navigate = useNavigate();

  // const { user, loading, logout } = useAuth();

  const handleSignUp = () => {
    try {
      if (!email || !password || !confirmPassword || !name || !lastName) {
        setError("Please fill out all fields.");
        return;
      }

      if (password !== confirmPassword) {
        setError("Passwords do not match.");
        return;
      }

      createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
          const user = userCredential.user;
          user.getIdToken(false).then((token) => {
            localStorage.setItem("sanvia-refreshToken", token);
            console.log("Token is stored properly.");
          });

          onSignUpSuccess();
          navigate("/auth/survey");
        })
        .catch((error) => {
          console.log("Sign Up Failed.");
          setError(error);
        });

      // Update information on firestore

      setError("");
      alert(`Signed up as ${email}`);
    } catch (e) {
      setError(`Error: ${e}`);
    }
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Sign Up</h2>
        {error && <p className="error">{error}</p>}
        <input
          type="name"
          placeholder="Name"
          className="input"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          type="lastName"
          placeholder="Last Name"
          className="input"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
        />
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
        <input
          type="password"
          placeholder="Confirm Password"
          className="input"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />

        <button onClick={handleSignUp} className="button">
          Sign up
        </button>

        <p className="toggleText">
          Already have an account?{" "}
          <span className="link" onClick={() => navigate("/auth/survey")}>
            Login
          </span>
        </p>
      </div>
    </div>
  );
};

export default SignUp;
