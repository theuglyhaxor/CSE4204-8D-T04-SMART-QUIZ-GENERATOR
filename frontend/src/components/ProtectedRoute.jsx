import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

/**
 * Gate a route behind authentication and (optionally) a role.
 *
 *   <ProtectedRoute role="teacher"><CreateQuiz /></ProtectedRoute>
 *
 * While the stored token is being revalidated we render nothing rather than
 * bouncing the user to /login and back — that flicker is what makes a refresh
 * feel like a logout.
 */
export default function ProtectedRoute({ children, role }) {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="route-loading">
        <div className="spinner" />
        <p>Loading…</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // Remember where they were headed so login can send them back.
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (role && user.role !== role) {
    // Logged in, wrong role: send them to their own home rather than a dead end.
    return <Navigate to={user.role === "teacher" ? "/" : "/student"} replace />;
  }

  return children;
}
