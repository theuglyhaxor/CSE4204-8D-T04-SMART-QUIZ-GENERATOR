import React from "react";
import "./QuestionCard.css";

import {
  CheckCircle,
  Edit,
  Trash2,
} from "lucide-react";

const QuestionCard = ({
  number,
  question,
  option1,
  option2,
  option3,
  option4,
  answer,
}) => {
  return (

    <div className="question-card">

      {/* Top */}

      <div className="question-top">

        <div className="question-number">

          {number}

        </div>

        <div className="question-content">

          <h3>{question}</h3>

        </div>

        <div className="question-actions">

          <button className="edit-btn">

            <Edit size={18} />

          </button>

          <button className="delete-btn">

            <Trash2 size={18} />

          </button>

        </div>

      </div>

      {/* Options */}

      <div className="question-options">

        <div
          className={
            answer === option1
              ? "option correct"
              : "option"
          }
        >
          {answer === option1 && (
            <CheckCircle size={18} />
          )}

          <span>{option1}</span>

        </div>

        <div
          className={
            answer === option2
              ? "option correct"
              : "option"
          }
        >
          {answer === option2 && (
            <CheckCircle size={18} />
          )}

          <span>{option2}</span>

        </div>

        <div
          className={
            answer === option3
              ? "option correct"
              : "option"
          }
        >
          {answer === option3 && (
            <CheckCircle size={18} />
          )}

          <span>{option3}</span>

        </div>

        <div
          className={
            answer === option4
              ? "option correct"
              : "option"
          }
        >
          {answer === option4 && (
            <CheckCircle size={18} />
          )}

          <span>{option4}</span>

        </div>

      </div>

    </div>

  );
};

export default QuestionCard;