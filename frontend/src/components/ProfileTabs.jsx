import React from "react";
import "./ProfileTabs.css";

import {
  User,
  GraduationCap,
  Briefcase,
  Award,
  Globe,
} from "lucide-react";

const ProfileTabs = () => {
  return (
    <div className="profile-tabs">

      {/* About */}

      <div className="tab-card">

        <div className="tab-title">
          <User size={20} />
          <h3>About Me</h3>
        </div>

        <p>
          Passionate software developer and educator with experience in
          Artificial Intelligence, Web Development and Smart Learning
          Systems. Loves building modern applications with React,
          Node.js and Machine Learning.
        </p>

      </div>

      {/* Education */}

      <div className="tab-card">

        <div className="tab-title">
          <GraduationCap size={20} />
          <h3>Education</h3>
        </div>

        <div className="timeline">

          <div className="timeline-item">
            <h4>BSc in Computer Science</h4>
            <span>2021 - Present</span>
            <p>National University, Bangladesh</p>
          </div>

          <div className="timeline-item">
            <h4>Higher Secondary Certificate</h4>
            <span>2018 - 2020</span>
            <p>Science Group</p>
          </div>

        </div>

      </div>

      {/* Experience */}

      <div className="tab-card">

        <div className="tab-title">
          <Briefcase size={20} />
          <h3>Experience</h3>
        </div>

        <div className="timeline">

          <div className="timeline-item">
            <h4>Frontend Developer</h4>
            <span>2024 - Present</span>
            <p>React • Vite • Node.js</p>
          </div>

          <div className="timeline-item">
            <h4>AI Quiz System Project</h4>
            <span>2025</span>
            <p>Smart Quiz Generator</p>
          </div>

        </div>

      </div>

      {/* Skills */}

      <div className="tab-card">

        <div className="tab-title">
          <Award size={20} />
          <h3>Skills</h3>
        </div>

        <div className="skills">

          <span>React</span>
          <span>JavaScript</span>
          <span>Node.js</span>
          <span>Express</span>
          <span>MongoDB</span>
          <span>Python</span>
          <span>Machine Learning</span>
          <span>UI/UX</span>

        </div>

      </div>

      {/* Social */}

      <div className="tab-card">

        <div className="tab-title">
          <Globe size={20} />
          <h3>Social Links</h3>
        </div>

        <div className="social-links">

          <a href="#">🌐 Website</a>

          <a href="#">💼 LinkedIn</a>

          <a href="#">🐙 GitHub</a>

          <a href="#">📘 Facebook</a>

        </div>

      </div>

    </div>
  );
};

export default ProfileTabs;