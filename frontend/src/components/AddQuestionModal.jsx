import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { quizzes as quizApi } from "../api/client";
import "./AddQuestionModal.css";

const LETTERS = ["A", "B", "C", "D"];

/** Create one MCQ against a chosen quiz. */
const AddQuestionModal = ({ quizzes, defaultQuizId, onClose, onCreated }) => {
  const [form, setForm] = useState({
    quiz: defaultQuizId || quizzes[0]?.id || "",
    prompt: "",
    option_a: "",
    option_b: "",
    option_c: "",
    option_d: "",
    correct_option: "A",
    explanation: "",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const update = (field) => (event) =>
    setForm((prev) => ({ ...prev, [field]: event.target.value }));

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");

    if (!form.quiz) return setError("Pick a quiz.");
    if (!form.prompt.trim()) return setError("Enter the question.");

    const missing = LETTERS.filter((l) => !form[`option_${l.toLowerCase()}`].trim());
    if (missing.length) return setError(`Fill in option ${missing.join(", ")}.`);

    setSaving(true);
    try {
      // Posting to the quiz-scoped route lets the server assign the question's order.
      const created = await quizApi.addQuestion(form.quiz, {
        prompt: form.prompt.trim(),
        option_a: form.option_a.trim(),
        option_b: form.option_b.trim(),
        option_c: form.option_c.trim(),
        option_d: form.option_d.trim(),
        correct_option: form.correct_option,
        explanation: form.explanation.trim(),
      });
      onCreated(created);
    } catch (err) {
      setError(err.message);
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label="Add question"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="modal__head">
          <div>
            <h2>Add Question</h2>
            <p>Create a multiple-choice question</p>
          </div>
          <button type="button" className="modal__close" onClick={onClose} aria-label="Close">
            <X size={20} />
          </button>
        </header>

        <form className="modal__body add-question-form" onSubmit={handleSubmit}>
          {error && <div className="banner banner--error">{error}</div>}

          <div className="input-group">
            <label htmlFor="quiz">Quiz</label>
            <select id="quiz" value={form.quiz} onChange={update("quiz")} disabled={saving}>
              {quizzes.map((quiz) => (
                <option key={quiz.id} value={quiz.id}>
                  {quiz.title}
                </option>
              ))}
            </select>
          </div>

          <div className="input-group">
            <label htmlFor="prompt">Question</label>
            <textarea
              id="prompt"
              rows="2"
              placeholder="What do you want to ask?"
              value={form.prompt}
              onChange={update("prompt")}
              disabled={saving}
            />
          </div>

          <div className="options-grid">
            {LETTERS.map((letter) => (
              <div className="input-group" key={letter}>
                <label htmlFor={`option-${letter}`}>Option {letter}</label>
                <input
                  id={`option-${letter}`}
                  type="text"
                  value={form[`option_${letter.toLowerCase()}`]}
                  onChange={update(`option_${letter.toLowerCase()}`)}
                  disabled={saving}
                />
              </div>
            ))}
          </div>

          <div className="input-group">
            <label>Correct Answer</label>
            <div className="correct-toggle">
              {LETTERS.map((letter) => (
                <button
                  key={letter}
                  type="button"
                  className={form.correct_option === letter ? "active" : ""}
                  onClick={() => setForm((p) => ({ ...p, correct_option: letter }))}
                  disabled={saving}
                >
                  {letter}
                </button>
              ))}
            </div>
          </div>

          <div className="input-group">
            <label htmlFor="explanation">Explanation (optional)</label>
            <textarea
              id="explanation"
              rows="2"
              placeholder="Why is that the right answer?"
              value={form.explanation}
              onChange={update("explanation")}
              disabled={saving}
            />
          </div>

          <div className="modal__actions">
            <button type="button" className="btn btn--ghost" onClick={onClose} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="btn btn--primary" disabled={saving}>
              {saving ? "Saving…" : "Add Question"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddQuestionModal;
