import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import TeamFooter from "../components/TeamFooter";
import "./Register.css";

const Register = () => {
  const { signUp, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirm: "",
    role: "teacher",
  });
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isAuthenticated) {
    return <Navigate to={user.role === "teacher" ? "/" : "/student"} replace />;
  }

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.username.trim()) return setError("Choose a username.");
    if (form.password !== form.confirm) return setError("The two passwords do not match.");
    if (form.password.length < 8) return setError("Use a password of at least 8 characters.");

    setSubmitting(true);
    try {
      const created = await signUp({
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        role: form.role,
      });
      navigate(created.role === "teacher" ? "/" : "/student", { replace: true });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="register-container">
      {/* Left Side */}
      <div className="left-panel">
        <div className="logo">
          <span className="logo-icon">★</span>
          <h2>SMART QUIZ</h2>
        </div>

        <div className="welcome-content">
          <h1>Get Started</h1>
          <p>
            Create an account to generate AI powered quizzes, manage exams and track your
            progress easily.
          </p>

          <div className="circle circle1" />
          <div className="circle circle2" />
          <div className="circle circle3" />
        </div>
      </div>

      {/* Right Side */}
      <div className="right-panel">
        <div className="form-box">
          <h2>Create Account</h2>
          <p className="subtitle">Please fill the information below.</p>

          <form onSubmit={handleSubmit}>
            {error && (
              <div className="form-error" role="alert">
                {error}
              </div>
            )}

            {/* Role decides which half of the app you land in, so it is asked up front. */}
            <div className="input-group">
              <label>I am a</label>
              <div className="role-toggle">
                <button
                  type="button"
                  className={form.role === "teacher" ? "active" : ""}
                  onClick={() => setForm((p) => ({ ...p, role: "teacher" }))}
                >
                  👩‍🏫 Teacher
                </button>
                <button
                  type="button"
                  className={form.role === "student" ? "active" : ""}
                  onClick={() => setForm((p) => ({ ...p, role: "student" }))}
                >
                  🎓 Student
                </button>
              </div>
            </div>

            <div className="input-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                placeholder="Choose a username"
                value={form.username}
                onChange={update("username")}
                disabled={submitting}
              />
            </div>

            <div className="input-group">
              <label htmlFor="email">Email (optional)</label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="Enter your email"
                value={form.email}
                onChange={update("email")}
                disabled={submitting}
              />
            </div>

            <div className="input-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 8 characters"
                value={form.password}
                onChange={update("password")}
                disabled={submitting}
              />
            </div>

            <div className="input-group">
              <label htmlFor="confirm">Confirm Password</label>
              <input
                id="confirm"
                type="password"
                autoComplete="new-password"
                placeholder="Re-enter your password"
                value={form.confirm}
                onChange={update("confirm")}
                disabled={submitting}
              />
            </div>

            <button className="register-btn" type="submit" disabled={submitting}>
              {submitting ? "Creating account…" : "Create Account"}
            </button>

            <p className="login-text">
              Already have an account? <Link to="/login">Login</Link>
            </p>
          </form>

          <TeamFooter compact />
        </div>
      </div>
    </div>
  );
};

export default Register;
