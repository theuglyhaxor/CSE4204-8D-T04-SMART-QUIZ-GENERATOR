import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import TeamFooter from "../components/TeamFooter";

import { attempts as attemptsApi } from "../api/client";
import "./Dashboard.css"; // shared shell layout (.dashboard, .dashboard-body, .dashboard-panel)
import "./MyAttempts.css";

const scoreClass = (pct) => (pct >= 80 ? "good" : pct >= 50 ? "ok" : "poor");

/** Student: their own attempt history. The API only ever returns their own rows. */
const MyAttempts = ({ darkMode, setDarkMode }) => {
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    attemptsApi
      .mine()
      .then((data) => !cancelled && setAttempts(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  const best = attempts.length ? Math.max(...attempts.map((a) => a.percentage)) : 0;

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="dashboard-body">
          <div className="dashboard-title">
            <h1>My Attempts</h1>
            <p>Every quiz you have submitted</p>
          </div>

          {error && <div className="banner banner--error">{error}</div>}

          {loading ? (
            <div className="state-block">
              <div className="spinner" />
              <p>Loading your history…</p>
            </div>
          ) : attempts.length === 0 ? (
            <div className="state-block">
              <h3>No attempts yet</h3>
              <p>Take a quiz and your results will show up here.</p>
              <Link to="/student" className="btn btn--primary">
                Browse quizzes
              </Link>
            </div>
          ) : (
            <section className="dashboard-panel">
              <div className="panel-head">
                <div>
                  <h2>{attempts.length} attempt{attempts.length === 1 ? "" : "s"}</h2>
                  <p>Personal best: {best}%</p>
                </div>
                <Link to="/student" className="btn btn--ghost">
                  Take another quiz
                </Link>
              </div>

              <div className="attempts-list">
                {attempts.map((attempt) => (
                  <article className="attempt-row" key={attempt.id}>
                    <div className="attempt-row__main">
                      <h3>{attempt.quiz_title}</h3>
                      <p>{new Date(attempt.created_at).toLocaleString()}</p>
                    </div>

                    <div className="attempt-row__score">
                      <span className={`score score--${scoreClass(attempt.percentage)}`}>
                        {attempt.percentage}%
                      </span>
                      <small>
                        {attempt.score} / {attempt.total} correct
                      </small>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          <TeamFooter />
        </div>
      </div>
    </div>
  );
};

export default MyAttempts;
