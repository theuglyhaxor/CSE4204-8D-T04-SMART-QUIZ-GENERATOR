import React from "react";
import "./Activity.css";

const activities = [
  {
    title: "New Quiz Created",
    subtitle: "AI Programming Quiz",
    color: "blue",
  },
  {
    title: "120 New Users",
    subtitle: "Joined Today",
    color: "green",
  },
  {
    title: "Question Bank Updated",
    subtitle: "250 New Questions",
    color: "orange",
  },
  {
    title: "New Category Added",
    subtitle: "Machine Learning",
    color: "purple",
  },
  {
    title: "Quiz Completed",
    subtitle: "Database Management",
    color: "pink",
  },
];

const Activity = () => {
  return (
    <div className="activity-card">

      <div className="activity-header">
        <h2>Recent Activity</h2>
      </div>

      <div className="activity-list">

        {activities.map((item, index) => (

          <div className="activity-item" key={index}>

            <span className={`activity-dot ${item.color}`}></span>

            <div className="activity-info">

              <h4>{item.title}</h4>

              <p>{item.subtitle}</p>

            </div>

          </div>

        ))}

      </div>

    </div>
  );
};

export default Activity;