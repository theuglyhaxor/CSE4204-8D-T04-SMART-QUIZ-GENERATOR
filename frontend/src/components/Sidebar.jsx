 import React from "react";
import "./Sidebar.css";

import { useNavigate, useLocation } from "react-router-dom";

import {
  LayoutDashboard,
  FileText,
  BookOpen,
  User,
  Settings,
  LogOut,
} from "lucide-react";

const Sidebar = () => {

  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [

    {
      title: "Dashboard",
      icon: <LayoutDashboard size={20} />,
      path: "/",
    },

    {
      title: "Create Quiz",
      icon: <FileText size={20} />,
      path: "/create-quiz",
    },

    {
      title: "Question Bank",
      icon: <BookOpen size={20} />,
      path: "/question-bank",
    },

    {
      title: "Profile",
      icon: <User size={20} />,
      path: "/profile",
    },

    {
      title: "Settings",
      icon: <Settings size={20} />,
      path: "/settings",
    },

  ];

  return (

    <aside className="sidebar">

      {/* Logo */}

      <div
        className="logo"
        onClick={() => navigate("/")}
        style={{ cursor: "pointer" }}
      >

        <div className="logo-icon">
          🧠
        </div>

        <div>

          <h2>Smart Quiz</h2>

          <span>Generator</span>

        </div>

      </div>

      {/* Admin Badge */}

      <div className="admin-badge">

        Admin Panel

      </div>

      {/* Menu */}

      <ul className="menu">

        {

          menuItems.map((item) => (

            <li
              key={item.title}
              className={
                location.pathname === item.path
                  ? "active"
                  : ""
              }
              onClick={() => navigate(item.path)}
            >

              {item.icon}

              <span>{item.title}</span>

            </li>

          ))

        }

      </ul>

      {/* Bottom */}

      <div className="sidebar-bottom">

        <div
          className="profile"
          onClick={() => navigate("/profile")}
          style={{ cursor: "pointer" }}
        >

          <div className="avatar">

            PT

          </div>

          <div>

            <h4>Pial Tarofder</h4>

            <p>Administrator</p>

          </div>

        </div>

        <button
          className="logout-btn"
          onClick={() => navigate("/login")}
        >

          <LogOut size={18} />

          Logout

        </button>

      </div>

    </aside>

  );

};

export default Sidebar;