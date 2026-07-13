import { useState } from "react";
import { Download, Eye, Trash2 } from "lucide-react";
import { downloadQuizPdf, quizzes as quizApi } from "../api/client";
import AttemptsModal from "./AttemptsModal";
import "./QuizTable.css";

const difficultyClass = (difficulty) =>
  `badge-pill badge-pill--${String(difficulty || "medium").toLowerCase()}`;

export default function QuizTable({ quizzes, onChange }) {
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState("");
  const [viewing, setViewing] = useState(null);

  const run = async (id, action) => {
    setBusyId(id);
    setError("");
    try {
      await action();
      onChange?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const togglePublish = (quiz) =>
    run(quiz.id, () => quizApi.update(quiz.id, { is_active: !quiz.is_active }));

  const remove = (quiz) => {
    if (!window.confirm(`Delete "${quiz.title}" and all of its questions and attempts?`)) return;
    run(quiz.id, () => quizApi.remove(quiz.id));
  };

  const exportPdf = (quiz, answers) =>
    run(quiz.id, () =>
      downloadQuizPdf(quiz.id, {
        answers,
        filename: `${quiz.title.replace(/[^\w]+/g, "_")}_${answers ? "answer_key" : "handout"}.pdf`,
      }),
    );

  if (!quizzes.length) {
    return (
      <div className="state-block">
        <h3>No quizzes yet</h3>
        <p>Create your first quiz — you can generate the questions with AI.</p>
      </div>
    );
  }

  return (
    <>
      {error && <div className="banner banner--error">{error}</div>}

      <div className="quiz-table-wrap">
        <table className="quiz-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Difficulty</th>
              <th>Questions</th>
              <th>Duration</th>
              <th>Status</th>
              <th className="quiz-table__actions-head">Actions</th>
            </tr>
          </thead>
          <tbody>
            {quizzes.map((quiz) => (
              <tr key={quiz.id} className={busyId === quiz.id ? "is-busy" : ""}>
                <td>
                  <span className="quiz-table__title">{quiz.title}</span>
                </td>
                <td>
                  <span className={difficultyClass(quiz.difficulty)}>{quiz.difficulty}</span>
                </td>
                <td>{quiz.question_count}</td>
                <td>{quiz.duration_minutes} min</td>
                <td>
                  <button
                    type="button"
                    className={`badge-pill ${
                      quiz.is_active ? "badge-pill--active" : "badge-pill--draft"
                    } quiz-table__toggle`}
                    onClick={() => togglePublish(quiz)}
                    disabled={busyId === quiz.id}
                    title={quiz.is_active ? "Unpublish (hide from students)" : "Publish to students"}
                  >
                    {quiz.is_active ? "Published" : "Draft"}
                  </button>
                </td>
                <td>
                  <div className="quiz-table__actions">
                    <button
                      type="button"
                      className="icon-btn"
                      title="Download PDF with answer key"
                      onClick={() => exportPdf(quiz, true)}
                      disabled={busyId === quiz.id}
                    >
                      <Download size={16} />
                      <span>Answer key</span>
                    </button>
                    <button
                      type="button"
                      className="icon-btn"
                      title="Download student handout (no answers)"
                      onClick={() => exportPdf(quiz, false)}
                      disabled={busyId === quiz.id}
                    >
                      <Download size={16} />
                      <span>Handout</span>
                    </button>
                    <button
                      type="button"
                      className="icon-btn"
                      title="View student attempts"
                      onClick={() => setViewing(quiz)}
                    >
                      <Eye size={16} />
                      <span>Results</span>
                    </button>
                    <button
                      type="button"
                      className="icon-btn icon-btn--danger"
                      title="Delete quiz"
                      onClick={() => remove(quiz)}
                      disabled={busyId === quiz.id}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {viewing && <AttemptsModal quiz={viewing} onClose={() => setViewing(null)} />}
    </>
  );
}
