import { useNavigate, useLocation } from "react-router-dom";
import {
  BookOpen,
  ClipboardList,
  FileText,
  LayoutDashboard,
  LogOut,
  Settings,
  User,
} from "lucide-react";

import { useAuth } from "../context/AuthContext";
import "./Sidebar.css";

// The menu is derived from the signed-in user's role — a student must not be shown
// teacher-only destinations they would just be bounced away from.
const TEACHER_MENU = [
  { title: "Dashboard", icon: <LayoutDashboard size={20} />, path: "/" },
  { title: "Create Quiz", icon: <FileText size={20} />, path: "/create-quiz" },
  { title: "Question Bank", icon: <BookOpen size={20} />, path: "/question-bank" },
  { title: "Profile", icon: <User size={20} />, path: "/profile" },
  { title: "Settings", icon: <Settings size={20} />, path: "/settings" },
];

const STUDENT_MENU = [
  { title: "Quizzes", icon: <LayoutDashboard size={20} />, path: "/student" },
  { title: "My Attempts", icon: <ClipboardList size={20} />, path: "/attempts" },
  { title: "Profile", icon: <User size={20} />, path: "/profile" },
  { title: "Settings", icon: <Settings size={20} />, path: "/settings" },
];

const initials = (name = "") =>
  name
    .split(/[\s_.-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "?";

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, isTeacher, signOut } = useAuth();

  const menuItems = isTeacher ? TEACHER_MENU : STUDENT_MENU;
  const home = isTeacher ? "/" : "/student";

  const handleLogout = async () => {
    await signOut();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="sidebar">
      <div className="logo" onClick={() => navigate(home)} style={{ cursor: "pointer" }}>
        <div className="logo-icon">🧠</div>
        <div>
          <h2>Smart Quiz</h2>
          <span>Generator</span>
        </div>
      </div>

      <div className="admin-badge">{isTeacher ? "Teacher Panel" : "Student Portal"}</div>

      <ul className="menu">
        {menuItems.map((item) => (
          <li
            key={item.path}
            className={location.pathname === item.path ? "active" : ""}
            onClick={() => navigate(item.path)}
          >
            {item.icon}
            <span>{item.title}</span>
          </li>
        ))}
      </ul>

      <div className="sidebar-bottom">
        <div
          className="profile"
          onClick={() => navigate("/profile")}
          style={{ cursor: "pointer" }}
        >
          <div className="avatar">{initials(user?.username)}</div>
          <div>
            <h4>{user?.username}</h4>
            <p>{isTeacher ? "Teacher" : "Student"}</p>
          </div>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
