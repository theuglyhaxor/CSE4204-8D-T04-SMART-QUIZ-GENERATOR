import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { CheckCircle2, Clock, XCircle } from "lucide-react";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import TeamFooter from "../components/TeamFooter";

import { quizzes as quizApi } from "../api/client";
import "./Dashboard.css"; // shared shell layout (.dashboard, .dashboard-body, .dashboard-panel)
import "./TakeQuiz.css";

const LETTERS = ["A", "B", "C", "D"];

const formatTime = (seconds) => {
  const m = String(Math.floor(seconds / 60)).padStart(2, "0");
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
};

/**
 * Student: answer a quiz and submit it.
 *
 * The questions come from /student-questions/, which never includes the correct
 * option — the answers only arrive in the scored response after submitting, so the
 * key is not sitting in the browser waiting to be read out of devtools.
 */
const TakeQuiz = ({ darkMode, setDarkMode }) => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [quiz, setQuiz] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // { [questionId]: "A" }
  const [result, setResult] = useState(null);

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [secondsLeft, setSecondsLeft] = useState(null);

  // Keep the latest answers reachable from the timer without re-arming it each keystroke.
  const answersRef = useRef(answers);
  answersRef.current = answers;
  const submittedRef = useRef(false);

  const submit = useCallback(
    async (auto = false) => {
      if (submittedRef.current) return;

      const payload = Object.entries(answersRef.current).map(([questionId, selected]) => ({
        question: Number(questionId),
        selected_option: selected,
      }));

      if (!payload.length) {
        if (auto) {
          // Time ran out with nothing answered — nothing to score.
          setError("Time is up. You did not answer any questions.");
          return;
        }
        setError("Answer at least one question before submitting.");
        return;
      }

      submittedRef.current = true;
      setSubmitting(true);
      setError("");

      try {
        const scored = await quizApi.submit(id, payload);
        setResult(scored);
        setSecondsLeft(null);
        window.scrollTo({ top: 0, behavior: "smooth" });
      } catch (err) {
        submittedRef.current = false; // let them retry
        setError(err.message);
      } finally {
        setSubmitting(false);
      }
    },
    [id],
  );

  // Load quiz + its answer-free questions.
  useEffect(() => {
    let cancelled = false;
    Promise.all([quizApi.get(id), quizApi.studentQuestions(id)])
      .then(([quizData, questionData]) => {
        if (cancelled) return;
        setQuiz(quizData);
        setQuestions(questionData);
        setSecondsLeft(quizData.duration_minutes * 60);
      })
      .catch((err) => !cancelled && setError(err.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [id]);

  // Countdown. Auto-submits whatever has been answered when it hits zero.
  useEffect(() => {
    if (secondsLeft === null || result) return;

    if (secondsLeft <= 0) {
      submit(true);
      return;
    }

    const timer = setTimeout(() => setSecondsLeft((s) => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [secondsLeft, result, submit]);

  const choose = (questionId, letter) =>
    setAnswers((prev) => ({ ...prev, [questionId]: letter }));

  const answeredCount = Object.keys(answers).length;
  const lowOnTime = secondsLeft !== null && secondsLeft <= 60;

  // --- Result screen ---------------------------------------------------------
  if (result) {
    const passed = result.percentage >= 50;
    const byId = Object.fromEntries(questions.map((q) => [q.id, q]));

    return (
      <div className="dashboard">
        <Sidebar />
        <div className="dashboard-content">
          <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

          <div className="dashboard-body">
            <div className={`result-hero ${passed ? "is-pass" : "is-fail"}`}>
              <div className="result-hero__score">{result.percentage}%</div>
              <h1>{passed ? "Well done!" : "Keep practising"}</h1>
              <p>
                You scored <strong>{result.score}</strong> out of{" "}
                <strong>{result.total}</strong> on “{result.quiz_title}”.
              </p>
              <div className="result-hero__actions">
                <Link to="/attempts" className="btn btn--ghost">
                  My attempts
                </Link>
                <button className="btn btn--primary" onClick={() => navigate("/student")}>
                  Back to quizzes
                </button>
              </div>
            </div>

            <section className="dashboard-panel">
              <div className="panel-head">
                <div>
                  <h2>Review</h2>
                  <p>See which answers were right and why</p>
                </div>
              </div>

              <ol className="review-list">
                {result.responses.map((response, index) => {
                  const question = byId[response.question];
                  return (
                    <li key={response.question} className={response.is_correct ? "ok" : "bad"}>
                      <p className="review-prompt">
                        <span className="review-num">{index + 1}</span>
                        {question?.prompt ?? `Question ${response.question}`}
                        {response.is_correct ? (
                          <CheckCircle2 size={18} className="review-icon ok" />
                        ) : (
                          <XCircle size={18} className="review-icon bad" />
                        )}
                      </p>

                      <div className="review-answers">
                        <span className={response.is_correct ? "chip chip--ok" : "chip chip--bad"}>
                          You chose {response.selected_option}
                          {question && `: ${question[`option_${response.selected_option.toLowerCase()}`]}`}
                        </span>

                        {!response.is_correct && (
                          <span className="chip chip--ok">
                            Correct: {response.correct_option}
                            {question &&
                              `: ${question[`option_${response.correct_option.toLowerCase()}`]}`}
                          </span>
                        )}
                      </div>

                      {response.explanation && (
                        <p className="review-explanation">Why: {response.explanation}</p>
                      )}
                    </li>
                  );
                })}
              </ol>
            </section>

            <TeamFooter />
          </div>
        </div>
      </div>
    );
  }

  // --- Taking the quiz -------------------------------------------------------
  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="dashboard-body">
          {loading ? (
            <div className="state-block">
              <div className="spinner" />
              <p>Loading quiz…</p>
            </div>
          ) : (
            <>
              <div className="take-header">
                <div>
                  <h1>{quiz?.title}</h1>
                  <p>
                    {questions.length} question{questions.length === 1 ? "" : "s"} ·{" "}
                    {quiz?.difficulty} · answered {answeredCount}/{questions.length}
                  </p>
                </div>

                {secondsLeft !== null && (
                  <div className={`take-timer ${lowOnTime ? "is-low" : ""}`}>
                    <Clock size={18} />
                    {formatTime(Math.max(0, secondsLeft))}
                  </div>
                )}
              </div>

              {error && <div className="banner banner--error">{error}</div>}

              {questions.length === 0 ? (
                <div className="state-block">
                  <h3>This quiz has no questions</h3>
                  <p>Ask your teacher to add some.</p>
                </div>
              ) : (
                <>
                  <div className="take-progress">
                    <div
                      className="take-progress__bar"
                      style={{ width: `${(answeredCount / questions.length) * 100}%` }}
                    />
                  </div>

                  <ol className="take-questions">
                    {questions.map((question, index) => (
                      <li key={question.id} className="take-question">
                        <p className="take-prompt">
                          <span className="take-num">{index + 1}</span>
                          {question.prompt}
                        </p>

                        <div className="take-options">
                          {LETTERS.map((letter) => {
                            const selected = answers[question.id] === letter;
                            return (
                              <label
                                key={letter}
                                className={`take-option ${selected ? "is-selected" : ""}`}
                              >
                                <input
                                  type="radio"
                                  name={`q-${question.id}`}
                                  value={letter}
                                  checked={selected}
                                  onChange={() => choose(question.id, letter)}
                                  disabled={submitting}
                                />
                                <span className="take-letter">{letter}</span>
                                <span>{question[`option_${letter.toLowerCase()}`]}</span>
                              </label>
                            );
                          })}
                        </div>
                      </li>
                    ))}
                  </ol>

                  <div className="take-submit">
                    <p>
                      {answeredCount === questions.length
                        ? "All questions answered."
                        : `${questions.length - answeredCount} question(s) still unanswered.`}
                    </p>
                    <button
                      className="btn btn--primary"
                      onClick={() => submit(false)}
                      disabled={submitting}
                    >
                      {submitting ? "Submitting…" : "Submit Quiz"}
                    </button>
                  </div>
                </>
              )}

              <TeamFooter />
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TakeQuiz;
