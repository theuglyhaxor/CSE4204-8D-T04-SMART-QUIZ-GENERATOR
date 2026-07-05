import React from "react";
import "./RecentActivity.css";

import {
  CheckCircle,
  FileText,
  Award,
  Clock,
  UserPlus,
} from "lucide-react";

const RecentActivity = () => {
  return (
    <div className="recent-activity">

      <h3>Recent Activity</h3>

      <div className="activity-list">

        <div className="activity-item">

          <div className="activity-icon green">
            <CheckCircle size={18} />
          </div>

          <div className="activity-info">
            <h4>Profile Updated</h4>
            <p>Your profile information has been updated.</p>
            <span>2 hours ago</span>
          </div>

        </div>

        <div className="activity-item">

          <div className="activity-icon blue">
            <FileText size={18} />
          </div>

          <div className="activity-info">
            <h4>Quiz Created</h4>
            <p>Generated "Java Programming Quiz".</p>
            <span>Yesterday</span>
          </div>

        </div>

        <div className="activity-item">

          <div className="activity-icon orange">
            <Award size={18} />
          </div>

          <div className="activity-info">
            <h4>Achievement Unlocked</h4>
            <p>Completed 100 quizzes successfully.</p>
            <span>3 days ago</span>
          </div>

        </div>

        <div className="activity-item">

          <div className="activity-icon purple">
            <Clock size={18} />
          </div>

          <div className="activity-info">
            <h4>Premium Activated</h4>
            <p>Premium membership activated.</p>
            <span>1 week ago</span>
          </div>

        </div>

        <div className="activity-item">

          <div className="activity-icon pink">
            <UserPlus size={18} />
          </div>

          <div className="activity-info">
            <h4>New Team Joined</h4>
            <p>Joined Smart Quiz Generator Team.</p>
            <span>2 weeks ago</span>
          </div>

        </div>

      </div>

    </div>
  );
};

export default RecentActivity;