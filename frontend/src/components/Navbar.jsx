 import React from "react";
import "./Navbar.css";
import { useNavigate, useLocation } from "react-router-dom";

import {
  Search,
  Bell,
  Moon,
  Sun,
  ChevronDown,
} from "lucide-react";

const Navbar = ({ darkMode, setDarkMode }) => {

  const navigate = useNavigate();
  const location = useLocation();

  const handleProfileClick = () => {
    if (location.pathname === "/profile") {
      navigate("/");
    } else {
      navigate("/profile");
    }
  };

  return (
    <div className="navbar">

      {/* Search */}

      <div className="navbar-left">

        <div className="search-box">

          <Search size={18} />

          <input
            type="text"
            placeholder="Search quizzes, users..."
          />

        </div>

      </div>

      {/* Right */}

      <div className="navbar-right">

        {/* Notification */}

        <div className="nav-icon">

          <Bell size={20} />

          <span className="badge">3</span>

        </div>

        {/* Dark Mode */}

        <div
          className="nav-icon"
          onClick={() => setDarkMode(!darkMode)}
          title={darkMode ? "Light Mode" : "Dark Mode"}
        >
          {darkMode ? (
            <Sun size={20} />
          ) : (
            <Moon size={20} />
          )}
        </div>

        {/* Profile */}

        <div
          className="profile-box"
          onClick={handleProfileClick}
          style={{ cursor: "pointer" }}
        >

          <div className="profile-avatar">
            A
          </div>

          <div>

            <h4>Admin User</h4>

            <p>Administrator</p>

          </div>

          <ChevronDown size={18} />

        </div>

      </div>

    </div>
  );
};

export default Navbar;