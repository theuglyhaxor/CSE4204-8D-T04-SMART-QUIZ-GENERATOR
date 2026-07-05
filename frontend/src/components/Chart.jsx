import React from "react";
import "./Chart.css";

const Chart = () => {
  const bars = [65, 40, 90, 55, 100, 75, 85];

  return (
    <div className="chart-card">

      <div className="chart-header">
        <div>
          <h2>User Growth</h2>
          <p>Last 7 Days</p>
        </div>

        <button>View Report</button>
      </div>

      <div className="chart-bars">

        {bars.map((item, index) => (
          <div className="bar-wrapper" key={index}>

            <div
              className="bar"
              style={{ height: `${item}%` }}
            ></div>

            <span>
              {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"][index]}
            </span>

          </div>
        ))}

      </div>

    </div>
  );
};

export default Chart;