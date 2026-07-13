import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { BarChart3, FileText, HelpCircle, Users } from "lucide-react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import TeamFooter from "../components/TeamFooter";
import QuizTable from "../components/QuizTable";

import { meta, quizzes as quizApi } from "../api/client";
import "./Dashboard.css";

/** Teacher overview — every number here comes from the API, nothing is hardcoded. */
const Dashboard = ({ darkMode, setDarkMode }) => {
  const [stats, setStats] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [statsData, quizData] = await Promise.all([meta.stats(), quizApi.list()]);
      setStats(statsData);
      setQuizzes(quizData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="dashboard-body">
          <div className="dashboard-title">
            <h1>Overview</h1>
            <p>Monitor your quizzes, questions and student attempts</p>
          </div>

          {error && <div className="banner banner--error">{error}</div>}

          {loading ? (
            <div className="state-block">
              <div className="spinner" />
              <p>Loading your dashboard…</p>
            </div>
          ) : (
            <>
              <div className="stats-grid">
                <StatCard
                  icon={<FileText size={30} />}
                  title="Your Quizzes"
                  value={stats?.total_quizzes ?? 0}
                  caption={`${stats?.active_quizzes ?? 0} active`}
                  bgColor="#EEF2FF"
                  iconColor="#4F46E5"
                />
                <StatCard
                  icon={<HelpCircle size={30} />}
                  title="Questions"
                  value={stats?.total_questions ?? 0}
                  caption="Across all your quizzes"
                  bgColor="#ECFDF5"
                  iconColor="#10B981"
                />
                <StatCard
                  icon={<Users size={30} />}
                  title="Student Attempts"
                  value={stats?.total_attempts ?? 0}
                  caption="Submissions received"
                  bgColor="#FEF3C7"
                  iconColor="#F59E0B"
                />
                <StatCard
                  icon={<BarChart3 size={30} />}
                  title="Average Score"
                  value={`${stats?.average_score ?? 0}%`}
                  caption="Across all attempts"
                  bgColor="#FCE7F3"
                  iconColor="#DB2777"
                />
              </div>

              <section className="dashboard-panel">
                <div className="panel-head">
                  <div>
                    <h2>Your Quizzes</h2>
                    <p>Publish, export or review results</p>
                  </div>
                  <Link to="/create-quiz" className="btn btn--primary">
                    + Create Quiz
                  </Link>
                </div>

                <QuizTable quizzes={quizzes} onChange={load} />
              </section>

              <TeamFooter />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
