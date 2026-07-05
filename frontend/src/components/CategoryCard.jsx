import React from "react";
import "./CategoryCard.css";

const categories = [
  {
    name: "Programming",
    quizzes: 540,
    width: "90%",
    color: "purple",
  },
  {
    name: "Mathematics",
    quizzes: 430,
    width: "75%",
    color: "blue",
  },
  {
    name: "Science",
    quizzes: 390,
    width: "65%",
    color: "green",
  },
  {
    name: "Database",
    quizzes: 320,
    width: "55%",
    color: "orange",
  },
];

const CategoryCard = () => {
  return (
    <div className="category-card">

      <div className="category-header">
        <h2>Top Categories</h2>
        <span>View All</span>
      </div>

      <div className="category-list">

        {categories.map((item, index) => (
          <div className="category-item" key={index}>

            <div className="category-info">

              <div>
                <h4>{item.name}</h4>
                <p>{item.quizzes} Quizzes</p>
              </div>

            </div>

            <div className="progress">

              <div
                className={`progress-fill ${item.color}`}
                style={{ width: item.width }}
              ></div>

            </div>

          </div>
        ))}

      </div>

    </div>
  );
};

export default CategoryCard;