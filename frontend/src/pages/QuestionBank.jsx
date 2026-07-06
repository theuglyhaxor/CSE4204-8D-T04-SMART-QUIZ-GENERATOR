 import React, { useState } from "react";
import "./QuestionBank.css";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

import QuestionStats from "../components/QuestionStats";
import QuestionFilter from "../components/QuestionFilter";
import QuestionTable from "../components/QuestionTable";
import AddQuestionModal from "../components/AddQuestionModal";

const QuestionBank = ({ darkMode, setDarkMode }) => {

  const [showModal, setShowModal] = useState(false);

  return (

    <div className="dashboard">

      {/* Sidebar */}

      <Sidebar />

      {/* Main */}

      <div className="dashboard-content">

        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />

        <div className="question-bank">

          {/* Title */}

          <div className="page-title">

            <h1>📚 Question Bank</h1>

            <p>

              Manage all quiz questions from one place.

            </p>

          </div>

          {/* Statistics */}

          <QuestionStats />

          {/* Filter */}

          <QuestionFilter
            onAddQuestion={() => setShowModal(true)}
          />

          {/* Table */}

          <QuestionTable />

          {/* Modal */}

          <AddQuestionModal
            isOpen={showModal}
            onClose={() => setShowModal(false)}
          />

        </div>

      </div>

    </div>

  );

};

export default QuestionBank;