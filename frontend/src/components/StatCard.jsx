import React from "react";
import "./StatCard.css";

const StatCard = ({
  icon,
  title,
  value,
  growth,
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

        <p>
          <span>↑ {growth}</span> from last month
        </p>

      </div>

    </div>
  );
};

export default StatCard;