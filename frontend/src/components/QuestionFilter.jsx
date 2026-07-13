import { Plus, Search } from "lucide-react";
import "./QuestionFilter.css";

/** Filters the question bank by quiz and free-text. Both are controlled by the page. */
const QuestionFilter = ({
  quizzes,
  quizFilter,
  onQuizFilter,
  search,
  onSearch,
  onAddQuestion,
  canAdd,
}) => {
  return (
    <div className="question-filter">
      <div className="search-box">
        <Search size={18} />
        <input
          type="text"
          placeholder="Search question…"
          value={search}
          onChange={(e) => onSearch(e.target.value)}
        />
      </div>

      {/* Filter by quiz — the model has no "subject" field, quizzes are the grouping. */}
      <select value={quizFilter} onChange={(e) => onQuizFilter(e.target.value)}>
        <option value="">All quizzes</option>
        {quizzes.map((quiz) => (
          <option key={quiz.id} value={quiz.id}>
            {quiz.title}
          </option>
        ))}
      </select>

      <button
        onClick={onAddQuestion}
        disabled={!canAdd}
        title={canAdd ? "Add a question" : "Create a quiz first"}
      >
        <Plus size={18} />
        Add Question
      </button>
    </div>
  );
};

export default QuestionFilter;
