import React from "react";
import "./ProfileCard.css";

import {
  Mail,
  Phone,
  MapPin,
  Calendar,
  CheckCircle,
  Crown,
} from "lucide-react";

const ProfileCard = () => {
  return (
    <div className="profile-card">

      {/* Left Side */}

      <div className="profile-left">

        <div className="profile-image">
          AH
        </div>

        <div className="profile-info">

          <div className="name-row">

            <h2>Arif Hossain</h2>

            <span className="premium-badge">
              <Crown size={16} />
              Premium Member
            </span>

          </div>

          <p className="designation">
            Educator & AI Enthusiast
          </p>

          <div className="info-list">

            <div className="info-item">
              <Mail size={18} />
              <span>arif.hossain@example.com</span>
            </div>

            <div className="info-item">
              <Phone size={18} />
              <span>+880 1234-567890</span>
            </div>

            <div className="info-item">
              <MapPin size={18} />
              <span>Dhaka, Bangladesh</span>
            </div>

            <div className="info-item">
              <Calendar size={18} />
              <span>Joined on May 2, 2024</span>
            </div>

          </div>

          <button className="edit-btn">
            Edit Profile
          </button>

        </div>

      </div>

      {/* Right Side */}

      <div className="profile-right">

        <h3>Profile Completion</h3>

        <p>
          Complete your profile to get the best experience.
        </p>

        <div className="progress">

          <div
            className="progress-fill"
            style={{ width: "80%" }}
          ></div>

        </div>

        <div className="progress-value">
          80%
        </div>

        <div className="task-list">

          <div className="task completed">
            <CheckCircle size={18} />
            <span>Personal Information</span>
          </div>

          <div className="task completed">
            <CheckCircle size={18} />
            <span>Change Profile Picture</span>
          </div>

          <div className="task completed">
            <CheckCircle size={18} />
            <span>Add Bio</span>
          </div>

          <div className="task pending">
            <div className="pending-dot"></div>
            <span>Connect Social Accounts</span>
          </div>

        </div>

      </div>

    </div>
  );
};

export default ProfileCard;