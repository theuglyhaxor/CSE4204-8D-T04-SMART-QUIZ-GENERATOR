import React from "react";
import "./AIIntegrationCard.css";

import {
  Bot,
  Cpu,
  Activity,
  Sparkles,
  Settings,
  PlayCircle,
} from "lucide-react";

const AIIntegrationCard = () => {

  return (

    <div className="ai-card">

      {/* Header */}

      <div className="ai-header">

        <div className="ai-title">

          <Bot size={30} />

          <div>

            <h2>AI Integration</h2>

            <p>Manage your Smart Quiz AI system</p>

          </div>

        </div>

        <span className="status connected">

          ● Connected

        </span>

      </div>

      {/* Cards */}

      <div className="ai-info-grid">

        <div className="info-box">

          <Cpu size={22} />

          <h4>AI Model</h4>

          <span>GPT-4</span>

        </div>

        <div className="info-box">

          <Activity size={22} />

          <h4>Today's Requests</h4>

          <span>1,245</span>

        </div>

        <div className="info-box">

          <Sparkles size={22} />

          <h4>Remaining</h4>

          <span>8,755</span>

        </div>

      </div>

      {/* Progress */}

      <div className="usage">

        <div className="usage-top">

          <span>API Usage</span>

          <span>65%</span>

        </div>

        <div className="progress-bar">

          <div
            className="progress-fill"
            style={{ width: "65%" }}
          ></div>

        </div>

      </div>

      {/* Buttons */}

      <div className="ai-buttons">

        <button className="generate-btn">

          <Sparkles size={18} />

          Generate Quiz

        </button>

        <button className="setting-btn">

          <Settings size={18} />

          API Settings

        </button>

        <button className="test-btn">

          <PlayCircle size={18} />

          Test AI

        </button>

      </div>

    </div>

  );

};

export default AIIntegrationCard;