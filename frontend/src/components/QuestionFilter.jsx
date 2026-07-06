 import React from "react";
import "./QuestionFilter.css";

import {
  Search,
  Plus,
} from "lucide-react";

const QuestionFilter = ({ onAddQuestion }) => {

  return (

    <div className="question-filter">

      {/* Search Box */}

      <div className="search-box">

        <Search size={18} />

        <input
          type="text"
          placeholder="Search question..."
        />

      </div>

      {/* Subject Filter */}

      <select>

        <option>All Subjects</option>

        <option>Web Development</option>

        <option>Programming</option>

        <option>Database</option>

        <option>Operating System</option>

        <option>Networking</option>

        <option>Data Structure</option>

      </select>

      {/* Difficulty Filter */}

      <select>

        <option>All Difficulty</option>

        <option>Easy</option>

        <option>Medium</option>

        <option>Hard</option>

      </select>

      {/* Add Question Button */}

      <button onClick={onAddQuestion}>

        <Plus size={18} />

        Add Question

      </button>

    </div>

  );

};

export default QuestionFilter;