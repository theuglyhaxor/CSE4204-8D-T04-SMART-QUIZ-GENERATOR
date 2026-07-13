import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import TeamFooter from "../components/TeamFooter";
import "./Login.css";

const Login = () => {
  const { signIn, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  // Already signed in? Don't show the login form again.
  if (isAuthenticated) {
    return <Navigate to={user.role === "teacher" ? "/" : "/student"} replace />;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!username.trim() || !password) {
      setError("Enter both your username and password.");
      return;
    }

    setSubmitting(true);
    try {
      const signedIn = await signIn(username.trim(), password);
      // Send them where they were originally headed, else to their role's home.
      const target =
        location.state?.from?.pathname ??
        (signedIn.role === "teacher" ? "/" : "/student");
      navigate(target, { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="login-page">
      {/* Left Section */}
      <div className="left-side">
        <div className="logo">
          <div className="logo-icon">🧠</div>
          <div>
            <h2>Smart Quiz</h2>
            <span>Generator</span>
          </div>
        </div>

        <div className="badge">✨ AI-Powered Learning</div>

        <h1>Welcome Back!</h1>

        <p>Log in to your account and continue your learning journey with AI.</p>

        <div className="illustration">
          <div className="card">
            <div className="card-top" />
            <div className="card-body">
              <div className="avatar" />
              <div className="lines">
                <div />
                <div />
                <div />
              </div>
            </div>
          </div>
          <div className="lock">🔒</div>
        </div>

        <div className="features">
          <div className="feature">
            <div className="icon">✨</div>
            <h4>AI-Powered</h4>
            <p>Smart quiz generation</p>
          </div>
          <div className="feature">
            <div className="icon">📊</div>
            <h4>Track Progress</h4>
            <p>Monitor and improve</p>
          </div>
          <div className="feature">
            <div className="icon">🎯</div>
            <h4>Achieve Goals</h4>
            <p>Learn, practice and excel</p>
          </div>
        </div>
      </div>

      {/* Right Section */}
      <div className="right-side">
        <div className="login-box">
          <h2>Login to Your Account</h2>
          <p>Enter your credentials to access your account</p>

          <form onSubmit={handleSubmit}>
            {error && (
              <div className="form-error" role="alert">
                {error}
              </div>
            )}

            {/* The backend authenticates on username, not email. */}
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              placeholder="Enter your username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={submitting}
            />

            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={submitting}
            />

            <button type="submit" disabled={submitting}>
              {submitting ? "Logging in…" : "Login"}
            </button>
          </form>

          <div className="signup">
            Don&apos;t have an account? <Link to="/register">Sign up</Link>
          </div>

          <TeamFooter compact />
        </div>
      </div>
    </div>
  );
};

export default Login;
