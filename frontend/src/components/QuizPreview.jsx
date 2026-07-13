import { CheckCircle2, Download, Rocket, Sparkles, Trash2 } from "lucide-react";
import "./QuizPreview.css";

const LETTERS = ["a", "b", "c", "d"];

/** Right-hand pane of Create Quiz: empty state → generating → generated questions. */
const QuizPreview = ({ quiz, questions, generating, busy, onPublish, onDiscard, onExport }) => {
  if (generating) {
    return (
      <div className="quiz-preview">
        <div className="preview-head">
          <div className="step-number">2</div>
          <h2>Generating…</h2>
        </div>
        <div className="state-block">
          <div className="spinner" />
          <p>
            The AI is writing your questions.
            <br />
            This usually takes a few seconds.
          </p>
        </div>
      </div>
    );
  }

  if (!quiz) {
    return (
      <div className="quiz-preview">
        <div className="preview-head">
          <div className="step-number">2</div>
          <h2>Preview</h2>
        </div>
        <div className="state-block">
          <Sparkles size={32} color="#c7d2fe" />
          <h3>Nothing generated yet</h3>
          <p>
            Fill in the configuration and hit “Generate Quiz”. Your questions will appear
            here for review.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="quiz-preview">
      <div className="preview-head">
        <div className="step-number">2</div>
        <h2>Review &amp; Publish</h2>
      </div>

      <div className="banner banner--success">
        Generated {questions.length} question{questions.length === 1 ? "" : "s"} and saved as a
        draft. Publish it to make it visible to students.
      </div>

      <div className="preview-meta">
        <h3>{quiz.title}</h3>
        <div className="preview-meta__chips">
          <span className={`badge-pill badge-pill--${String(quiz.difficulty).toLowerCase()}`}>
            {quiz.difficulty}
          </span>
          <span className="badge-pill badge-pill--draft">{quiz.duration_minutes} min</span>
          <span className="badge-pill badge-pill--draft">{questions.length} questions</span>
        </div>
      </div>

      <ol className="preview-questions">
        {questions.map((question, index) => (
          <li key={question.id}>
            <p className="preview-prompt">
              <span className="preview-num">{index + 1}</span>
              {question.prompt}
            </p>

            <ul className="preview-options">
              {LETTERS.map((letter) => {
                const isCorrect = String(question.correct_option).toLowerCase() === letter;
                return (
                  <li key={letter} className={isCorrect ? "is-correct" : ""}>
                    <span className="preview-letter">{letter.toUpperCase()}</span>
                    <span>{question[`option_${letter}`]}</span>
                    {isCorrect && <CheckCircle2 size={14} className="preview-tick" />}
                  </li>
                );
              })}
            </ul>

            {question.explanation && (
              <p className="preview-explanation">Why: {question.explanation}</p>
            )}
          </li>
        ))}
      </ol>

      <div className="preview-actions">
        <button type="button" className="btn btn--primary" onClick={onPublish} disabled={busy}>
          <Rocket size={16} />
          Publish to students
        </button>

        <button
          type="button"
          className="btn btn--ghost"
          onClick={() => onExport(true)}
          disabled={busy}
        >
          <Download size={16} />
          PDF (answer key)
        </button>

        <button
          type="button"
          className="btn btn--ghost"
          onClick={() => onExport(false)}
          disabled={busy}
        >
          <Download size={16} />
          PDF (handout)
        </button>

        <button type="button" className="btn btn--danger" onClick={onDiscard} disabled={busy}>
          <Trash2 size={16} />
          Discard
        </button>
      </div>
    </div>
  );
};

export default QuizPreview;
