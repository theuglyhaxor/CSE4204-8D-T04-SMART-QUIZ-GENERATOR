import React, { useState } from "react";
import "./AddQuestionModal.css";

const AddQuestionModal = ({ isOpen, onClose }) => {

  const [formData, setFormData] = useState({

    question: "",

    subject: "Web Development",

    difficulty: "Easy",

    marks: 5,

    optionA: "",

    optionB: "",

    optionC: "",

    optionD: "",

    answer: "A",

  });

  if (!isOpen) return null;

  const handleChange = (e) => {

    setFormData({

      ...formData,

      [e.target.name]: e.target.value,

    });

  };

  const handleSubmit = (e) => {

    e.preventDefault();

    alert("Question Added Successfully!");

    onClose();

  };

  return (

    <div className="modal-overlay">

      <div className="question-modal">

        <div className="modal-header">

          <h2>➕ Add New Question</h2>

          <button
            className="close-btn"
            onClick={onClose}
          >
            ✕
          </button>

        </div>

        <form onSubmit={handleSubmit}>

          <label>Question</label>

          <textarea

            name="question"

            rows="3"

            placeholder="Enter question..."

            value={formData.question}

            onChange={handleChange}

            required

          />

          <div className="two-column">

            <div>

              <label>Subject</label>

              <select

                name="subject"

                value={formData.subject}

                onChange={handleChange}

              >

                <option>Web Development</option>

                <option>Programming</option>

                <option>Database</option>

                <option>Operating System</option>

                <option>Networking</option>

              </select>

            </div>

            <div>

              <label>Difficulty</label>

              <select

                name="difficulty"

                value={formData.difficulty}

                onChange={handleChange}

              >

                <option>Easy</option>

                <option>Medium</option>

                <option>Hard</option>

              </select>

            </div>

          </div>

          <label>Marks</label>

          <input

            type="number"

            name="marks"

            value={formData.marks}

            onChange={handleChange}

          />

          <label>Option A</label>

          <input

            type="text"

            name="optionA"

            value={formData.optionA}

            onChange={handleChange}

          />

          <label>Option B</label>

          <input

            type="text"

            name="optionB"

            value={formData.optionB}

            onChange={handleChange}

          />

          <label>Option C</label>

          <input

            type="text"

            name="optionC"

            value={formData.optionC}

            onChange={handleChange}

          />

          <label>Option D</label>

          <input

            type="text"

            name="optionD"

            value={formData.optionD}

            onChange={handleChange}

          />

          <label>Correct Answer</label>

          <select

            name="answer"

            value={formData.answer}

            onChange={handleChange}

          >

            <option value="A">Option A</option>

            <option value="B">Option B</option>

            <option value="C">Option C</option>

            <option value="D">Option D</option>

          </select>

          <div className="modal-buttons">

            <button
              type="button"
              className="cancel-btn"
              onClick={onClose}
            >

              Cancel

            </button>

            <button
              type="submit"
              className="save-btn"
            >

              Save Question

            </button>

          </div>

        </form>

      </div>

    </div>

  );

};

export default AddQuestionModal;