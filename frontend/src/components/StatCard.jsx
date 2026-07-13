import React from "react";
import "./StatCard.css";

const StatCard = ({
  icon,
  title,
  value,
  caption,
  bgColor,
  iconColor,
}) => {
  return (
    <div className="stat-card">

      <div
        className="stat-icon"
        style={{
          background: bgColor,
          color: iconColor,
        }}
      >
        {icon}
      </div>

      <div className="stat-content">

        <h4>{title}</h4>

        <h2>{value}</h2>

        {/* Only render a caption when there is something true to say — the old
            hardcoded "↑ x% from last month" was not backed by any data. */}
        {caption && <p>{caption}</p>}

      </div>

    </div>
  );
};

export default StatCard;