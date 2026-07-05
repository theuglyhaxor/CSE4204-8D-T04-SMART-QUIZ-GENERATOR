import React, { useState } from "react";
import "./QuizConfig.css";

import {
  Sparkles,
  Lightbulb,
  Minus,
  Plus,
} from "lucide-react";

const QuizConfig = () => {

  const [difficulty, setDifficulty] = useState("Medium");
  const [questions, setQuestions] = useState(10);

  return (

    <div className="quiz-config">

      {/* Header */}

      <div className="config-title">

        <div className="step-number">
          1
        </div>

        <h2>Quiz Configuration</h2>

      </div>

      {/* Topic */}

      <div className="form-group">

        <label>
          Topic <span>*</span>
        </label>

        <div className="input-icon">

          <input
            type="text"
            defaultValue="Machine Learning"
          />

          <Lightbulb size={18} />

        </div>

      </div>

      {/* Description */}

      <div className="form-group">

        <label>Description (Optional)</label>

        <textarea
          rows="5"
          defaultValue="Basics of machine learning concepts and algorithms."
        />

      </div>

      {/* Difficulty */}

      <div className="form-group">

        <label>Difficulty Level</label>

        <div className="difficulty-buttons">

          <button
            className={difficulty==="Easy" ? "active" : ""}
            onClick={()=>setDifficulty("Easy")}
          >
            Easy
          </button>

          <button
            className={difficulty==="Medium" ? "active" : ""}
            onClick={()=>setDifficulty("Medium")}
          >
            Medium
          </button>

          <button
            className={difficulty==="Hard" ? "active" : ""}
            onClick={()=>setDifficulty("Hard")}
          >
            Hard
          </button>

        </div>

      </div>

      {/* Number of Questions */}

      <div className="form-group">

        <label>Number of Questions</label>

        <div className="counter">

          <button
            onClick={() =>
              setQuestions(Math.max(1, questions - 1))
            }
          >
            <Minus size={16}/>
          </button>

          <span>{questions}</span>

          <button
            onClick={() =>
              setQuestions(questions + 1)
            }
          >
            <Plus size={16}/>
          </button>

        </div>

      </div>

      {/* Question Type */}

      <div className="form-group">

        <label>Question Type</label>

        <select>

          <option>Multiple Choice (MCQ)</option>

          <option>True / False</option>

          <option>Short Answer</option>

        </select>

      </div>

      {/* Instructions */}

      <div className="form-group">

        <label>
          Additional Instructions (Optional)
        </label>

        <textarea
          rows="4"
          placeholder="e.g. Focus on practical applications, include real-world examples..."
        />

      </div>

      {/* Generate Button */}

      <button className="generate-btn">

        <Sparkles size={20}/>

        Generate Quiz

      </button>

      {/* Footer */}

      <div className="config-note">

        AI may generate inaccurate information.
        Please review before use.

      </div>

    </div>

  );

};

export default QuizConfig;