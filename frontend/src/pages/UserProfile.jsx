import { useEffect, useState } from "react";
import { Mail, Shield, User as UserIcon } from "lucide-react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import TeamFooter from "../components/TeamFooter";

import { useAuth } from "../context/AuthContext";
import { meta } from "../api/client";
import "./Dashboard.css";
import "./UserProfile.css";

const initials = (name = "") =>
  name
    .split(/[\s_.-]+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("") || "?";

/** The signed-in user's own profile, backed by /auth/me/ and /stats/. */
const UserProfile = ({ darkMode, setDarkMode }) => {
  const { user, isTeacher } = useAuth();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    meta
      .stats()
      .then((data) => !cancelled && setStats(data))
      .catch((err) => !cancelled && setError(err.message));
    return () => {
      cancelled = true;
    };
  }, []);

  // Which counters make sense depends on the role.
  const tiles = isTeacher
    ? [
        ["Quizzes created", stats?.total_quizzes],
        ["Questions written", stats?.total_questions],
        ["Attempts received", stats?.total_attempts],
        ["Average score", stats == null ? undefined : `${stats.average_score}%`],
      ]
    : [
        ["Quizzes taken", stats?.quizzes_taken],
        ["Total attempts", stats?.total_attempts],
        ["Average score", stats == null ? undefined : `${stats.average_score}%`],
        ["Best score", stats == null ? undefined : `${stats.best_score}%`],
      ];

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="dashboard-body">
          <div className="dashboard-title">
            <h1>My Profile</h1>
            <p>Your account details and activity</p>
          </div>

          {error && <div className="banner banner--error">{error}</div>}

          <section className="profile-hero">
            <div className="profile-hero__avatar">{initials(user?.username)}</div>

            <div className="profile-hero__info">
              <h2>{user?.username}</h2>

              <ul>
                <li>
                  <Shield size={15} />
                  {isTeacher ? "Teacher" : "Student"}
                </li>
                <li>
                  <UserIcon size={15} />
                  User ID: {user?.id}
                </li>
                <li>
                  <Mail size={15} />
                  {user?.email || "No email on file"}
                </li>
              </ul>
            </div>
          </section>

          <div className="profile-tiles">
            {tiles.map(([label, value]) => (
              <div className="profile-tile" key={label}>
                <h4>{label}</h4>
                <h2>{value ?? "—"}</h2>
              </div>
            ))}
          </div>

          <TeamFooter />
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
