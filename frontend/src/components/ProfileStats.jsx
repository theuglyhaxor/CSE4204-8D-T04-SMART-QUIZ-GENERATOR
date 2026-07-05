import React from "react";
import "./ProfileStats.css";

import {
  FileText,
  HelpCircle,
 Clock3,
  Trophy,
} from "lucide-react";

const ProfileStats = () => {
  return (
    <div className="profile-stats-grid">

      <div className="profile-stat-card">

        <div className="stat-icon purple">
          <FileText size={26} />
        </div>

        <div className="stat-info">
          <h2>148</h2>
          <p>Total Quizzes</p>
        </div>

      </div>

      <div className="profile-stat-card">

        <div className="stat-icon green">
          <HelpCircle size={26} />
        </div>

        <div className="stat-info">
          <h2>3,240</h2>
          <p>Questions Generated</p>
        </div>

      </div>

      <div className="profile-stat-card">

        <div className="stat-icon orange">
          <Clock3 size={26} />
        </div>

        <div className="stat-info">
          <h2>82 hrs</h2>
          <p>Time Saved</p>
        </div>

      </div>

      <div className="profile-stat-card">

        <div className="stat-icon blue">
          <Trophy size={26} />
        </div>

        <div className="stat-info">
          <h2>96%</h2>
          <p>Average Accuracy</p>
        </div>

      </div>

    </div>
  );
};

export default ProfileStats;