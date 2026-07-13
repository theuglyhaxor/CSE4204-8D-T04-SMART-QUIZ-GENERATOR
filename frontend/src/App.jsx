import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { useEffect, useState } from "react";

import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

// Public
import Login from "./pages/Login";
import Register from "./pages/Register";

// Teacher
import Dashboard from "./pages/Dashboard";
import CreateQuiz from "./pages/CreateQuiz";
import QuestionBank from "./pages/QuestionBank";

// Student
import StudentHome from "./pages/StudentHome";
import TakeQuiz from "./pages/TakeQuiz";
import MyAttempts from "./pages/MyAttempts";

// Shared
import UserProfile from "./pages/UserProfile";
import Settings from "./pages/Settings";

/** Sends "/" to the right home for whoever is signed in. */
function RoleHome({ theme }) {
  const { isTeacher } = useAuth();
  return isTeacher ? <Dashboard {...theme} /> : <Navigate to="/student" replace />;
}

function AppRoutes({ theme }) {
  return (
    <Routes>
      {/* Public */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Teacher home ("/" resolves by role) */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <RoleHome theme={theme} />
          </ProtectedRoute>
        }
      />

      {/* Teacher only */}
      <Route
        path="/create-quiz"
        element={
          <ProtectedRoute role="teacher">
            <CreateQuiz {...theme} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/question-bank"
        element={
          <ProtectedRoute role="teacher">
            <QuestionBank {...theme} />
          </ProtectedRoute>
        }
      />

      {/* Student only */}
      <Route
        path="/student"
        element={
          <ProtectedRoute role="student">
            <StudentHome {...theme} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/quiz/:id"
        element={
          <ProtectedRoute role="student">
            <TakeQuiz {...theme} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/attempts"
        element={
          <ProtectedRoute role="student">
            <MyAttempts {...theme} />
          </ProtectedRoute>
        }
      />

      {/* Any signed-in user */}
      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <UserProfile {...theme} />
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <Settings {...theme} />
          </ProtectedRoute>
        }
      />

      {/* Unknown URL → home, which redirects by role. */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    document.body.classList.toggle("dark", darkMode);
    localStorage.setItem("theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes theme={{ darkMode, setDarkMode }} />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
