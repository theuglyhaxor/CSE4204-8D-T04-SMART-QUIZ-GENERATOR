import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Award, BarChart3, BookOpen, ClipboardList, Clock, Play } from "lucide-react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import TeamFooter from "../components/TeamFooter";

import { meta, quizzes as quizApi } from "../api/client";
// Dashboard.css owns the shared shell layout (.dashboard, .dashboard-body,
// .stats-grid, .dashboard-panel). Students never render Dashboard, so it has to be
// pulled in here or the page loses its layout in dev.
import "./Dashboard.css";
import "./StudentHome.css";

/** Student landing page: their stats plus every quiz a teacher has published. */
const StudentHome = ({ darkMode, setDarkMode }) => {
  const [stats, setStats] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    Promise.all([meta.stats(), quizApi.list()])
      .then(([statsData, quizData]) => {
        if (cancelled) return;
        setStats(statsData);
        setQuizzes(quizData);
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="dashboard-body">
          <div className="dashboard-title">
            <h1>Available Quizzes</h1>
            <p>Pick a quiz and test what you know</p>
          </div>

          {error && <div className="banner banner--error">{error}</div>}

          {loading ? (
            <div className="state-block">
              <div className="spinner" />
              <p>Loading quizzes…</p>
            </div>
          ) : (
            <>
              <div className="stats-grid">
                <StatCard
                  icon={<BookOpen size={30} />}
                  title="Available"
                  value={stats?.available_quizzes ?? 0}
                  caption="Published quizzes"
                  bgColor="#EEF2FF"
                  iconColor="#4F46E5"
                />
                <StatCard
                  icon={<ClipboardList size={30} />}
                  title="Quizzes Taken"
                  value={stats?.quizzes_taken ?? 0}
                  caption={`${stats?.total_attempts ?? 0} attempts`}
                  bgColor="#ECFDF5"
                  iconColor="#10B981"
                />
                <StatCard
                  icon={<BarChart3 size={30} />}
                  title="Average Score"
                  value={`${stats?.average_score ?? 0}%`}
                  caption="Across your attempts"
                  bgColor="#FEF3C7"
                  iconColor="#F59E0B"
                />
                <StatCard
                  icon={<Award size={30} />}
                  title="Best Score"
                  value={`${stats?.best_score ?? 0}%`}
                  caption="Your personal best"
                  bgColor="#FCE7F3"
                  iconColor="#DB2777"
                />
              </div>

              {quizzes.length === 0 ? (
                <div className="state-block">
                  <h3>No quizzes available yet</h3>
                  <p>Your teacher hasn’t published any quizzes. Check back soon.</p>
                </div>
              ) : (
                <div className="quiz-cards">
                  {quizzes.map((quiz) => (
                    <article className="quiz-card" key={quiz.id}>
                      <div className="quiz-card__top">
                        <span
                          className={`badge-pill badge-pill--${String(
                            quiz.difficulty,
                          ).toLowerCase()}`}
                        >
                          {quiz.difficulty}
                        </span>
                        <span className="quiz-card__time">
                          <Clock size={13} /> {quiz.duration_minutes} min
                        </span>
                      </div>

                      <h3>{quiz.title}</h3>
                      {quiz.description && <p>{quiz.description}</p>}

                      <div className="quiz-card__foot">
                        <span>
                          {quiz.question_count} question{quiz.question_count === 1 ? "" : "s"}
                        </span>

                        {quiz.question_count > 0 ? (
                          <Link to={`/quiz/${quiz.id}`} className="btn btn--primary">
                            <Play size={15} />
                            Start
                          </Link>
                        ) : (
                          <button className="btn btn--ghost" disabled title="No questions yet">
                            Not ready
                          </button>
                        )}
                      </div>
                    </article>
                  ))}
                </div>
              )}

              <TeamFooter />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default StudentHome;
