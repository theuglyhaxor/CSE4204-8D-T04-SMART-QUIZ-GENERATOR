import React, { useState } from "react";
import "./SettingsSystem.css";

import {
  Clock3,
  Target,
  Save,
  Shuffle,
} from "lucide-react";

const SettingsSystem = () => {

  const [quizTime, setQuizTime] = useState(30);
  const [passingMarks, setPassingMarks] = useState(40);
  const [autoSave, setAutoSave] = useState(true);
  const [shuffleQuestions, setShuffleQuestions] = useState(true);

  return (

    <div className="settings-card">

      {/* Header */}

      <div className="card-header">

        <h2>⚙️ System Settings</h2>

        <p>
          Configure default Smart Quiz Generator options.
        </p>

      </div>

      {/* Quiz Time */}

      <div className="system-item">

        <div className="system-info">

          <Clock3 size={20} />

          <div>

            <h4>Default Quiz Time</h4>

            <p>Set the default duration for every quiz.</p>

          </div>

        </div>

        <select
          value={quizTime}
          onChange={(e) => setQuizTime(e.target.value)}
        >

          <option value={15}>15 Minutes</option>
          <option value={30}>30 Minutes</option>
          <option value={45}>45 Minutes</option>
          <option value={60}>60 Minutes</option>

        </select>

      </div>

      {/* Passing Marks */}

      <div className="system-item">

        <div className="system-info">

          <Target size={20} />

          <div>

            <h4>Default Passing Marks</h4>

            <p>Select the minimum passing percentage.</p>

          </div>

        </div>

        <select
          value={passingMarks}
          onChange={(e) => setPassingMarks(e.target.value)}
        >

          <option value={40}>40%</option>
          <option value={50}>50%</option>
          <option value={60}>60%</option>
          <option value={70}>70%</option>

        </select>

      </div>

      {/* Auto Save */}

      <div className="system-item">

        <div className="system-info">

          <Save size={20} />

          <div>

            <h4>Auto Save Quiz</h4>

            <p>Automatically save quizzes while editing.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={autoSave}
            onChange={() => setAutoSave(!autoSave)}
          />

          <span className="slider"></span>

        </label>

      </div>

      {/* Shuffle */}

      <div className="system-item">

        <div className="system-info">

          <Shuffle size={20} />

          <div>

            <h4>Shuffle Questions</h4>

            <p>Randomize question order for every quiz.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={shuffleQuestions}
            onChange={() => setShuffleQuestions(!shuffleQuestions)}
          />

          <span className="slider"></span>

        </label>

      </div>

    </div>

  );

};

export default SettingsSystem;