import React from "react";
import "./QuestionTable.css";

import {
  Pencil,
  Trash2,
} from "lucide-react";

const QuestionTable = () => {

  const questions = [

    {
      id: 1,
      question: "What is React?",
      subject: "Web Development",
      difficulty: "Easy",
      marks: 5,
    },

    {
      id: 2,
      question: "Explain Binary Search Tree.",
      subject: "Data Structure",
      difficulty: "Medium",
      marks: 10,
    },

    {
      id: 3,
      question: "What is Normalization?",
      subject: "Database",
      difficulty: "Hard",
      marks: 15,
    },

    {
      id: 4,
      question: "What is Process Scheduling?",
      subject: "Operating System",
      difficulty: "Medium",
      marks: 10,
    },

    {
      id: 5,
      question: "Difference between Stack and Queue?",
      subject: "Data Structure",
      difficulty: "Easy",
      marks: 5,
    },

  ];

  return (

    <div className="question-table-card">

      <table className="question-table">

        <thead>

          <tr>

            <th>#</th>

            <th>Question</th>

            <th>Subject</th>

            <th>Difficulty</th>

            <th>Marks</th>

            <th>Action</th>

          </tr>

        </thead>

        <tbody>

          {

            questions.map((item) => (

              <tr key={item.id}>

                <td>{item.id}</td>

                <td>{item.question}</td>

                <td>{item.subject}</td>

                <td>

                  <span
                    className={`badge ${item.difficulty.toLowerCase()}`}
                  >

                    {item.difficulty}

                  </span>

                </td>

                <td>{item.marks}</td>

                <td>

                  <div className="action-buttons">

                    <button className="edit-btn">

                      <Pencil size={18} />

                    </button>

                    <button className="delete-btn">

                      <Trash2 size={18} />

                    </button>

                  </div>

                </td>

              </tr>

            ))

          }

        </tbody>

      </table>

    </div>

  );

};

export default QuestionTable;