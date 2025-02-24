import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Auth.css"; // Import shared styles

interface RegisterProps {
  onRegisterSuccess: () => void;
}

const Register: React.FC<RegisterProps> = ({ onRegisterSuccess }) => {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  const handleRegister = () => {
    if (!username || !password || !confirmPassword) {
      setError("Please fill out all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setError("");
    alert(`Registered as ${username}`);
    onRegisterSuccess();
    navigate("/login");
  };

  return (
    <div className="container">
      <div className="card">
        <h2 className="title">Register</h2>
        {error && <p className="error">{error}</p>}
        
        <input
          type="text"
          placeholder="Username"
          className="input"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
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

        <button onClick={handleRegister} className="button">
          Register
        </button>

        <p className="toggleText">
          Already have an account?{" "}
          <span className="link" onClick={() => navigate("/login")}>
            Login
          </span>
        </p>
      </div>
    </div>
  );
};

export default Register;
