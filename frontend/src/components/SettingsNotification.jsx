import React, { useState } from "react";
import "./SettingsNotification.css";

import {
  Mail,
  Bell,
  FileText,
  CalendarDays,
} from "lucide-react";

const SettingsNotification = () => {

  const [emailNotification, setEmailNotification] = useState(true);
  const [quizNotification, setQuizNotification] = useState(true);
  const [systemNotification, setSystemNotification] = useState(false);
  const [weeklyReport, setWeeklyReport] = useState(true);

  return (

    <div className="settings-card">

      {/* Header */}

      <div className="card-header">

        <h2>🔔 Notification Settings</h2>

        <p>
          Choose which notifications you would like to receive.
        </p>

      </div>

      {/* Email */}

      <div className="notification-item">

        <div className="notification-info">

          <Mail size={20} />

          <div>

            <h4>Email Notifications</h4>

            <p>Receive important updates via email.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={emailNotification}
            onChange={() =>
              setEmailNotification(!emailNotification)
            }
          />

          <span className="slider"></span>

        </label>

      </div>

      {/* Quiz */}

      <div className="notification-item">

        <div className="notification-info">

          <FileText size={20} />

          <div>

            <h4>Quiz Notifications</h4>

            <p>Receive alerts when quizzes are created or updated.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={quizNotification}
            onChange={() =>
              setQuizNotification(!quizNotification)
            }
          />

          <span className="slider"></span>

        </label>

      </div>

      {/* System */}

      <div className="notification-item">

        <div className="notification-info">

          <Bell size={20} />

          <div>

            <h4>System Notifications</h4>

            <p>Receive maintenance and system update alerts.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={systemNotification}
            onChange={() =>
              setSystemNotification(!systemNotification)
            }
          />

          <span className="slider"></span>

        </label>

      </div>

      {/* Weekly Report */}

      <div className="notification-item">

        <div className="notification-info">

          <CalendarDays size={20} />

          <div>

            <h4>Weekly Reports</h4>

            <p>Receive weekly performance summaries.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={weeklyReport}
            onChange={() =>
              setWeeklyReport(!weeklyReport)
            }
          />

          <span className="slider"></span>

        </label>

      </div>

    </div>

  );

};

export default SettingsNotification;