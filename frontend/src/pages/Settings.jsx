import React from "react";
import "./Settings.css";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

import SettingsProfile from "../components/SettingsProfile";
import SettingsAppearance from "../components/SettingsAppearance";
import SettingsNotification from "../components/SettingsNotification";
import SettingsSystem from "../components/SettingsSystem";

const Settings = ({ darkMode, setDarkMode }) => {
  return (
    <div className="settings-page">

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="settings-content">

        {/* Navbar */}
        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />

        {/* Body */}
        <div className="settings-body">

          {/* Title */}
          <div className="settings-title">

            <h1>⚙️ Settings</h1>

            <p>
              Manage your Smart Quiz Generator preferences and system settings.
            </p>

          </div>

          {/* Profile */}
          <SettingsProfile />

          {/* Appearance */}
          <SettingsAppearance
            darkMode={darkMode}
            setDarkMode={setDarkMode}
          />

          {/* Notification */}
          <SettingsNotification />

          {/* System */}
          <SettingsSystem />

          {/* Save Button */}

          <div className="settings-save">

            <button className="save-btn">
              Save Changes
            </button>

          </div>

        </div>

      </div>

    </div>
  );
};

export default Settings;