import React from "react";
import "./QuizPreview.css";

import {
  Sparkles,
  Clock,
 CheckCircle,
} from "lucide-react";

import QuestionCard from "./QuestionCard";

const QuizPreview = () => {
  return (

    <div className="quiz-preview">

      {/* Header */}

      <div className="preview-header">

        <div>

          <h2>

            <Sparkles size={22} />

            AI Generated Quiz

          </h2>

          <p>
            Preview generated questions before publishing
          </p>

        </div>

        <span className="status">
          Ready
        </span>

      </div>

      {/* Quiz Info */}

      <div className="preview-info">

        <div className="info-card">

          <Clock size={18} />

          <div>

            <h4>Estimated Time</h4>

            <p>15 Minutes</p>

          </div>

        </div>

        <div className="info-card">

          <CheckCircle size={18} />

          <div>

            <h4>Total Questions</h4>

            <p>10 Questions</p>

          </div>

        </div>

      </div>

      {/* Questions */}

      <div className="question-list">

        <QuestionCard
          number="01"
          question="What is Machine Learning?"
          option1="A subset of Artificial Intelligence"
          option2="A programming language"
          option3="A database software"
          option4="A networking protocol"
          answer="A subset of Artificial Intelligence"
        />

        <QuestionCard
          number="02"
          question="Which algorithm is used for classification?"
          option1="Linear Regression"
          option2="Decision Tree"
          option3="K-Means"
          option4="Apriori"
          answer="Decision Tree"
        />

        <QuestionCard
          number="03"
          question="Which library is commonly used for Machine Learning in Python?"
          option1="NumPy"
          option2="TensorFlow"
          option3="Pandas"
          option4="Bootstrap"
          answer="TensorFlow"
        />

      </div>

    </div>

  );
};

export default QuizPreview;