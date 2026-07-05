import React from "react";
import "./CreateQuiz.css";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

import QuizConfig from "../components/QuizConfig";
import QuizPreview from "../components/QuizPreview";
import BottomActions from "../components/BottomActions";

const CreateQuiz = ({ darkMode, setDarkMode }) => {
  return (
    <div className="dashboard">

      {/* Sidebar */}

      <Sidebar />

      {/* Main Content */}

      <div className="dashboard-content">

        {/* Navbar */}

        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />

        {/* Body */}

        <div className="createquiz-body">

          {/* Page Title */}

          <div className="createquiz-header">

            <div>

              <h1>
                Create New Quiz
                <span className="sparkle"> ✨</span>
              </h1>

              <p>
                Generate engaging quizzes in seconds with AI
              </p>

            </div>

          </div>

          {/* Main Grid */}

          <div className="createquiz-grid">

            {/* Left Panel */}

            <div className="left-panel">

              <QuizConfig />

            </div>

            {/* Right Panel */}

            <div className="right-panel">

              <QuizPreview />

            </div>

          </div>

          {/* Bottom Buttons */}

          <BottomActions />

        </div>

      </div>

    </div>
  );
};

export default CreateQuiz;