import React from "react";
import "./BottomActions.css";

import {
  Save,
  Eye,
  Sparkles,
} from "lucide-react";

const BottomActions = () => {
  return (

    <div className="bottom-actions">

      <button className="draft-btn">

        <Save size={18} />

        Save Draft

      </button>

      <button className="preview-btn">

        <Eye size={18} />

        Preview

      </button>

      <button className="generate-final-btn">

        <Sparkles size={18} />

        Generate Quiz

      </button>

    </div>

  );
};

export default BottomActions;