import { Trash2 } from "lucide-react";
import "./QuestionTable.css";

const LETTERS = ["a", "b", "c", "d"];

/** The real question list: prompt, its quiz, the four options and the correct one. */
const QuestionTable = ({ questions, quizTitles, onDelete, totalCount }) => {
  if (!totalCount) {
    return (
      <div className="state-block">
        <h3>No questions yet</h3>
        <p>Generate a quiz with AI, or add a question manually.</p>
      </div>
    );
  }

  if (!questions.length) {
    return (
      <div className="state-block">
        <h3>No matches</h3>
        <p>No question matches your current filter.</p>
      </div>
    );
  }

  return (
    <div className="question-table-card">
      <table className="question-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Question</th>
            <th>Quiz</th>
            <th>Options</th>
            <th>Answer</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody>
          {questions.map((question) => (
            <tr key={question.id}>
              <td>{question.order}</td>

              <td>
                <span className="question-prompt">{question.prompt}</span>
                {question.explanation && (
                  <span className="question-explanation">{question.explanation}</span>
                )}
              </td>

              <td>{quizTitles[question.quiz] ?? `Quiz #${question.quiz}`}</td>

              <td>
                <ul className="question-options">
                  {LETTERS.map((letter) => (
                    <li
                      key={letter}
                      className={
                        String(question.correct_option).toLowerCase() === letter
                          ? "is-correct"
                          : ""
                      }
                    >
                      <b>{letter.toUpperCase()}</b> {question[`option_${letter}`]}
                    </li>
                  ))}
                </ul>
              </td>

              <td>
                <span className="badge correct">{question.correct_option}</span>
              </td>

              <td>
                <div className="action-buttons">
                  <button
                    className="delete-btn"
                    onClick={() => onDelete(question)}
                    title="Delete question"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default QuestionTable;
