import React from "react";
import "./SettingsAppearance.css";

import {
  Moon,
  Palette,
  Type,
} from "lucide-react";

const SettingsAppearance = ({ darkMode, setDarkMode }) => {
  return (
    <div className="settings-card">

      {/* Header */}

      <div className="card-header">

        <h2>🎨 Appearance Settings</h2>

        <p>
          Customize the appearance of your dashboard.
        </p>

      </div>

      {/* Dark Mode */}

      <div className="appearance-item">

        <div className="appearance-info">

          <Moon size={20} />

          <div>

            <h4>Dark Mode</h4>

            <p>Enable or disable dark mode.</p>

          </div>

        </div>

        <label className="switch">

          <input
            type="checkbox"
            checked={darkMode}
            onChange={() => setDarkMode(!darkMode)}
          />

          <span className="slider"></span>

        </label>

      </div>

      {/* Theme Color */}

      <div className="appearance-item">

        <div className="appearance-info">

          <Palette size={20} />

          <div>

            <h4>Theme Color</h4>

            <p>Select your preferred dashboard color.</p>

          </div>

        </div>

        <select>

          <option>Blue</option>
          <option>Green</option>
          <option>Purple</option>
          <option>Orange</option>
          <option>Red</option>

        </select>

      </div>

      {/* Font Size */}

      <div className="appearance-item">

        <div className="appearance-info">

          <Type size={20} />

          <div>

            <h4>Font Size</h4>

            <p>Choose your preferred text size.</p>

          </div>

        </div>

        <select defaultValue="Medium">

          <option>Small</option>
          <option>Medium</option>
          <option>Large</option>

        </select>

      </div>

    </div>
  );
};

export default SettingsAppearance;