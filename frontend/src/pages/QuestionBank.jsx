import { useCallback, useEffect, useMemo, useState } from "react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import QuestionStats from "../components/QuestionStats";
import QuestionFilter from "../components/QuestionFilter";
import QuestionTable from "../components/QuestionTable";
import AddQuestionModal from "../components/AddQuestionModal";
import TeamFooter from "../components/TeamFooter";

import { questions as questionApi, quizzes as quizApi } from "../api/client";
import "./Dashboard.css";
import "./QuestionBank.css";

/** Teacher: every question across their quizzes, filterable, with add/delete. */
const QuestionBank = ({ darkMode, setDarkMode }) => {
  const [quizzes, setQuizzes] = useState([]);
  const [questions, setQuestions] = useState([]);
  const [quizFilter, setQuizFilter] = useState("");   // quiz id, "" = all
  const [search, setSearch] = useState("");
  const [showModal, setShowModal] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [quizData, questionData] = await Promise.all([
        quizApi.list(),
        questionApi.list(),
      ]);
      setQuizzes(quizData);
      setQuestions(questionData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const quizTitles = useMemo(
    () => Object.fromEntries(quizzes.map((quiz) => [quiz.id, quiz.title])),
    [quizzes],
  );

  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase();
    return questions.filter((question) => {
      if (quizFilter && String(question.quiz) !== String(quizFilter)) return false;
      if (needle && !question.prompt.toLowerCase().includes(needle)) return false;
      return true;
    });
  }, [questions, quizFilter, search]);

  const remove = async (question) => {
    if (!window.confirm("Delete this question?")) return;
    try {
      await questionApi.remove(question.id);
      setQuestions((prev) => prev.filter((q) => q.id !== question.id));
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="question-bank">
          <div className="page-title">
            <h1>📚 Question Bank</h1>
            <p>Manage all quiz questions from one place.</p>
          </div>

          {error && <div className="banner banner--error">{error}</div>}

          {loading ? (
            <div className="state-block">
              <div className="spinner" />
              <p>Loading questions…</p>
            </div>
          ) : (
            <>
              <QuestionStats questions={questions} quizCount={quizzes.length} />

              <QuestionFilter
                quizzes={quizzes}
                quizFilter={quizFilter}
                onQuizFilter={setQuizFilter}
                search={search}
                onSearch={setSearch}
                onAddQuestion={() => setShowModal(true)}
                canAdd={quizzes.length > 0}
              />

              <QuestionTable
                questions={visible}
                quizTitles={quizTitles}
                onDelete={remove}
                totalCount={questions.length}
              />

              {showModal && (
                <AddQuestionModal
                  quizzes={quizzes}
                  defaultQuizId={quizFilter}
                  onClose={() => setShowModal(false)}
                  onCreated={(created) => {
                    setQuestions((prev) => [...prev, created]);
                    setShowModal(false);
                  }}
                />
              )}

              <TeamFooter />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuestionBank;
