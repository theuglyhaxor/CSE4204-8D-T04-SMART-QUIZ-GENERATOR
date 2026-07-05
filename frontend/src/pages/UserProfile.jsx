import React from "react";
import "./UserProfile.css";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

import ProfileCard from "../components/ProfileCard";
import ProfileStats from "../components/ProfileStats";
import ProfileTabs from "../components/ProfileTabs";
import RecentActivity from "../components/RecentActivity";

const UserProfile = ({ darkMode, setDarkMode }) => {
  return (
    <div className="profile-page">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="profile-content">

        {/* Navbar */}
        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />

        {/* Body */}
        <div className="profile-body">

          {/* Page Title */}
          <div className="profile-title">
            <h1>User Profile</h1>

            <p>
              Dashboard &gt; Profile
            </p>
          </div>

          {/* Top Profile Section */}
          <div className="profile-top">

            <ProfileCard />

          </div>

          {/* Statistics */}
          <div className="profile-stats">

            <ProfileStats />

          </div>

          {/* Bottom Section */}

          <div className="profile-bottom">

            <div className="left-panel">
              <ProfileTabs />
            </div>

            <div className="right-panel">
              <RecentActivity />
            </div>

          </div>

        </div>

      </div>

    </div>
  );
};

export default UserProfile;