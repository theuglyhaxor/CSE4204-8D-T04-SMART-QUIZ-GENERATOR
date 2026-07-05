 import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect, useState } from "react";

// Pages
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import UserProfile from "./pages/UserProfile";
import CreateQuiz from "./pages/CreateQuiz";

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("theme") === "dark";
  });

  useEffect(() => {
    if (darkMode) {
      document.body.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.body.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  return (
    <BrowserRouter>
      <Routes>

        {/* Dashboard */}
        <Route
          path="/"
          element={
            <Dashboard
              darkMode={darkMode}
              setDarkMode={setDarkMode}
            />
          }
        />

        {/* Login */}
        <Route
          path="/login"
          element={<Login />}
        />

        {/* Register */}
        <Route
          path="/register"
          element={<Register />}
        />

        {/* User Profile */}
        <Route
          path="/profile"
          element={
            <UserProfile
              darkMode={darkMode}
              setDarkMode={setDarkMode}
            />
          }
        />

        {/* Create Quiz */}
        <Route
          path="/create-quiz"
          element={
            <CreateQuiz
              darkMode={darkMode}
              setDarkMode={setDarkMode}
            />
          }
        />

      </Routes>
    </BrowserRouter>
  );
}

export default App;