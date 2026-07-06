import React from "react";
import "./QuestionStats.css";

import {
  BookOpen,
  FolderOpen,
  CheckCircle,
  AlertTriangle,
} from "lucide-react";

const QuestionStats = () => {

  const stats = [

    {
      title: "Total Questions",
      value: "150",
      icon: <BookOpen size={28} />,
      color: "#2563eb",
      bg: "#DBEAFE",
    },

    {
      title: "Subjects",
      value: "8",
      icon: <FolderOpen size={28} />,
      color: "#10B981",
      bg: "#D1FAE5",
    },

    {
      title: "Easy",
      value: "60",
      icon: <CheckCircle size={28} />,
      color: "#059669",
      bg: "#DCFCE7",
    },

    {
      title: "Hard",
      value: "35",
      icon: <AlertTriangle size={28} />,
      color: "#DC2626",
      bg: "#FEE2E2",
    },

  ];

  return (

    <div className="question-stats">

      {

        stats.map((item, index) => (

          <div
            className="question-stat-card"
            key={index}
          >

            <div
              className="question-stat-icon"
              style={{
                background: item.bg,
                color: item.color,
              }}
            >

              {item.icon}

            </div>

            <div>

              <h4>{item.title}</h4>

              <h2>{item.value}</h2>

            </div>

          </div>

        ))

      }

    </div>

  );

};

export default QuestionStats;