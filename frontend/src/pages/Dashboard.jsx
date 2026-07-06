 import React from "react";
import "./Dashboard.css";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import StatCard from "../components/StatCard";
import Chart from "../components/Chart";
import Activity from "../components/Activity";
import CategoryCard from "../components/CategoryCard";
import UserTable from "../components/UserTable";
import AIIntegrationCard from "../components/AIIntegrationCard";

import {
  Users,
  FileText,
  HelpCircle,
  DollarSign,
} from "lucide-react";

const Dashboard = ({ darkMode, setDarkMode }) => {

  return (

    <div className="dashboard">

      {/* Sidebar */}

      <Sidebar />

      {/* Main Content */}

      <div className="dashboard-content">

        {/* Navbar */}

        <Navbar
          darkMode={darkMode}
          setDarkMode={setDarkMode}
        />

        {/* Dashboard Body */}

        <div className="dashboard-body">

          {/* Page Title */}

          <div className="dashboard-title">

            <h1>Overview</h1>

            <p>
              Monitor your Smart Quiz Generator performance
            </p>

          </div>

          {/* Statistics */}

          <div className="stats-grid">

            <StatCard
              icon={<Users size={30} />}
              title="Total Users"
              value="12,845"
              growth="+12%"
              bgColor="#EEF2FF"
              iconColor="#4F46E5"
            />

            <StatCard
              icon={<FileText size={30} />}
              title="Total Quizzes"
              value="2,540"
              growth="+18%"
              bgColor="#ECFDF5"
              iconColor="#10B981"
            />

            <StatCard
              icon={<HelpCircle size={30} />}
              title="Questions"
              value="18,230"
              growth="+8%"
              bgColor="#FEF3C7"
              iconColor="#F59E0B"
            />

            <StatCard
              icon={<DollarSign size={30} />}
              title="Revenue"
              value="$24,500"
              growth="+21%"
              bgColor="#FCE7F3"
              iconColor="#DB2777"
            />

          </div>

          {/* Chart + Activity */}

          <div className="dashboard-row">

            <section className="chart-section">

              <Chart />

            </section>

            <section className="activity-section">

              <Activity />

            </section>

          </div>

          {/* Bottom Section */}

          <div className="bottom-grid">

            <CategoryCard />

            <UserTable />

          </div>

          {/* AI Integration */}

          <AIIntegrationCard />

        </div>

      </div>

    </div>

  );

};

export default Dashboard;