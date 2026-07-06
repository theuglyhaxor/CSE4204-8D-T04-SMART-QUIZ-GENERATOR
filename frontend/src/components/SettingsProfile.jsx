import React from "react";
import "./SettingsProfile.css";

import {
  User,
  Mail,
  Phone,
  GraduationCap,
} from "lucide-react";

const SettingsProfile = () => {
  return (
    <div className="settings-card">

      <div className="card-header">

        <h2>👤 Profile Settings</h2>

        <p>Update your personal information.</p>

      </div>

      <div className="settings-form">

        {/* Name */}

        <div className="input-group">

          <label>Full Name</label>

          <div className="input-box">

            <User size={18} />

            <input
              type="text"
              defaultValue="Pial Tarofder"
            />

          </div>

        </div>

        {/* Email */}

        <div className="input-group">

          <label>Email Address</label>

          <div className="input-box">

            <Mail size={18} />

            <input
              type="email"
              defaultValue="pialtarofder00@gmail.com"
            />

          </div>

        </div>

        {/* Phone */}

        <div className="input-group">

          <label>Phone Number</label>

          <div className="input-box">

            <Phone size={18} />

            <input
              type="text"
              defaultValue="+880 1234-567890"
            />

          </div>

        </div>

        {/* Department */}

        <div className="input-group">

          <label>Department</label>

          <div className="input-box">

            <GraduationCap size={18} />

            <input
              type="text"
              defaultValue="Computer Science & Engineering"
            />

          </div>

        </div>

      </div>

      <div className="profile-btn">

        <button>

          Update Profile

        </button>

      </div>

    </div>
  );
};

export default SettingsProfile;