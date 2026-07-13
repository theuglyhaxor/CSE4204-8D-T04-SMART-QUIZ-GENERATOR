import { useNavigate } from "react-router-dom";
import { Moon, Sun } from "lucide-react";

import { useAuth } from "../context/AuthContext";
import "./Navbar.css";

const Navbar = ({ darkMode, setDarkMode }) => {
  const navigate = useNavigate();
  const { user, isTeacher } = useAuth();

  return (
    <div className="navbar">
      <div className="navbar-left" />

      <div className="navbar-right">
        <div
          className="nav-icon"
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? "Switch to light mode" : "Switch to dark mode"}
          role="button"
          tabIndex={0}
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </div>

        <div
          className="profile-box"
          onClick={() => navigate("/profile")}
          style={{ cursor: "pointer" }}
        >
          <div className="profile-avatar">
            {user?.username?.[0]?.toUpperCase() ?? "?"}
          </div>

          <div>
            <h4>{user?.username}</h4>
            <p>{isTeacher ? "Teacher" : "Student"}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
