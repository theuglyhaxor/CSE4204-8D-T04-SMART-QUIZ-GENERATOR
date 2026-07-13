import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { quizzes as quizApi } from "../api/client";
import "./AttemptsModal.css";

const scoreClass = (pct) => (pct >= 80 ? "good" : pct >= 50 ? "ok" : "poor");

export default function AttemptsModal({ quiz, onClose }) {
  const [attempts, setAttempts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;
    quizApi
      .attempts(quiz.id)
      .then((data) => !cancelled && setAttempts(data))
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [quiz.id]);

  // Escape closes the dialog.
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const average = attempts.length
    ? Math.round(attempts.reduce((sum, a) => sum + a.percentage, 0) / attempts.length)
    : 0;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={`Attempts for ${quiz.title}`}
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal__head">
          <div>
            <h2>{quiz.title}</h2>
            <p>
              {attempts.length} attempt{attempts.length === 1 ? "" : "s"}
              {attempts.length > 0 && ` · ${average}% average`}
            </p>
          </div>
          <button type="button" className="modal__close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </header>

        <div className="modal__body">
          {loading && (
            <div className="state-block">
              <div className="spinner" />
            </div>
          )}

          {error && <div className="banner banner--error">{error}</div>}

          {!loading && !error && attempts.length === 0 && (
            <div className="state-block">
              <h3>No attempts yet</h3>
              <p>Results will appear here once students submit this quiz.</p>
            </div>
          )}

          {!loading && attempts.length > 0 && (
            <table className="attempts-table">
              <thead>
                <tr>
                  <th>Student</th>
                  <th>Score</th>
                  <th>Percentage</th>
                  <th>Submitted</th>
                </tr>
              </thead>
              <tbody>
                {attempts.map((attempt) => (
                  <tr key={attempt.id}>
                    <td>{attempt.student_name}</td>
                    <td>
                      {attempt.score} / {attempt.total}
                    </td>
                    <td>
                      <span className={`score score--${scoreClass(attempt.percentage)}`}>
                        {attempt.percentage}%
                      </span>
                    </td>
                    <td>{new Date(attempt.created_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
}
