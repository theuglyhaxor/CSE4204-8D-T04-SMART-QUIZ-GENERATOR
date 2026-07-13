import { BookOpen, CheckCircle, FolderOpen, ListChecks } from "lucide-react";
import "./QuestionStats.css";

/** Counters derived from the real question list — nothing here is hardcoded. */
const QuestionStats = ({ questions, quizCount }) => {
  const withExplanation = questions.filter((q) => q.explanation?.trim()).length;
  const averagePerQuiz = quizCount ? Math.round((questions.length / quizCount) * 10) / 10 : 0;

  const stats = [
    {
      title: "Total Questions",
      value: questions.length,
      icon: <BookOpen size={28} />,
      color: "#2563eb",
      bg: "#DBEAFE",
    },
    {
      title: "Quizzes",
      value: quizCount,
      icon: <FolderOpen size={28} />,
      color: "#10B981",
      bg: "#D1FAE5",
    },
    {
      title: "With Explanation",
      value: withExplanation,
      icon: <CheckCircle size={28} />,
      color: "#059669",
      bg: "#DCFCE7",
    },
    {
      title: "Avg / Quiz",
      value: averagePerQuiz,
      icon: <ListChecks size={28} />,
      color: "#D97706",
      bg: "#FEF3C7",
    },
  ];

  return (
    <div className="question-stats">
      {stats.map((item) => (
        <div className="question-stat-card" key={item.title}>
          <div
            className="question-stat-icon"
            style={{ background: item.bg, color: item.color }}
          >
            {item.icon}
          </div>

          <div>
            <h4>{item.title}</h4>
            <h2>{item.value}</h2>
          </div>
        </div>
      ))}
    </div>
  );
};

export default QuestionStats;
