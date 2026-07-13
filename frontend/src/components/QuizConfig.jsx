import { useRef, useState } from "react";
import { FileUp, Lightbulb, Minus, Plus, Sparkles, X } from "lucide-react";
import "./QuizConfig.css";

const DIFFICULTIES = ["Easy", "Medium", "Hard"];

/**
 * The quiz generation form. Fully controlled; hands a config object up to
 * CreateQuiz, which does the API work.
 */
const QuizConfig = ({ onGenerate, generating }) => {
  const fileInput = useRef(null);

  const [topic, setTopic] = useState("");
  const [title, setTitle] = useState("");
  const [syllabus, setSyllabus] = useState("");
  const [instruction, setInstruction] = useState("");
  const [difficulty, setDifficulty] = useState("Medium");
  const [questionCount, setQuestionCount] = useState(5);
  const [durationMinutes, setDurationMinutes] = useState(10);
  const [provider, setProvider] = useState("");
  const [file, setFile] = useState(null);
  const [touched, setTouched] = useState(false);

  // The model needs something to work from: either a topic or a source document.
  const canGenerate = Boolean(topic.trim() || file) && !generating;

  const handleSubmit = (event) => {
    event.preventDefault();
    setTouched(true);
    if (!canGenerate) return;

    onGenerate({
      topic: topic.trim(),
      title: title.trim(),
      syllabus: syllabus.trim(),
      instruction: instruction.trim(),
      difficulty,
      questionCount,
      durationMinutes,
      provider,
      file,
    });
  };

  const pickFile = (event) => {
    const chosen = event.target.files?.[0];
    if (chosen) setFile(chosen);
  };

  const clearFile = () => {
    setFile(null);
    if (fileInput.current) fileInput.current.value = "";
  };

  return (
    <form className="quiz-config" onSubmit={handleSubmit}>
      <div className="config-title">
        <div className="step-number">1</div>
        <h2>Quiz Configuration</h2>
      </div>

      {/* Topic */}
      <div className="form-group">
        <label htmlFor="topic">
          Topic <span>*</span>
        </label>
        <div className="input-icon">
          <input
            id="topic"
            type="text"
            placeholder="e.g. Machine Learning basics"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={generating}
          />
          <Lightbulb size={18} />
        </div>
        {touched && !topic.trim() && !file && (
          <small className="field-error">Enter a topic, or upload a source document.</small>
        )}
      </div>

      {/* Source document */}
      <div className="form-group">
        <label>Source Document (Optional)</label>
        <p className="field-hint">
          Upload a PDF, TXT, MD, CSV or JSON file and the questions will be generated from
          its contents.
        </p>

        {file ? (
          <div className="file-chip">
            <FileUp size={16} />
            <span className="file-chip__name">{file.name}</span>
            <button type="button" onClick={clearFile} disabled={generating} aria-label="Remove file">
              <X size={14} />
            </button>
          </div>
        ) : (
          <label className="file-drop">
            <FileUp size={18} />
            <span>Choose a file</span>
            <input
              ref={fileInput}
              type="file"
              accept=".pdf,.txt,.md,.csv,.json"
              onChange={pickFile}
              disabled={generating}
              hidden
            />
          </label>
        )}
      </div>

      {/* Title */}
      <div className="form-group">
        <label htmlFor="title">Quiz Title (Optional)</label>
        <input
          id="title"
          type="text"
          placeholder="Leave blank to let the AI name it"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={generating}
        />
      </div>

      {/* Syllabus */}
      <div className="form-group">
        <label htmlFor="syllabus">Syllabus / Context (Optional)</label>
        <textarea
          id="syllabus"
          rows="4"
          placeholder="Paste the material the questions should be drawn from."
          value={syllabus}
          onChange={(e) => setSyllabus(e.target.value)}
          disabled={generating}
        />
      </div>

      {/* Difficulty */}
      <div className="form-group">
        <label>Difficulty Level</label>
        <div className="difficulty-buttons">
          {DIFFICULTIES.map((level) => (
            <button
              key={level}
              type="button"
              className={difficulty === level ? "active" : ""}
              onClick={() => setDifficulty(level)}
              disabled={generating}
            >
              {level}
            </button>
          ))}
        </div>
      </div>

      {/* Counts */}
      <div className="form-row">
        <div className="form-group">
          <label>Number of Questions</label>
          <div className="counter">
            <button
              type="button"
              onClick={() => setQuestionCount((n) => Math.max(1, n - 1))}
              disabled={generating}
            >
              <Minus size={16} />
            </button>
            <span>{questionCount}</span>
            <button
              type="button"
              onClick={() => setQuestionCount((n) => Math.min(50, n + 1))}
              disabled={generating}
            >
              <Plus size={16} />
            </button>
          </div>
        </div>

        <div className="form-group">
          <label>Duration (minutes)</label>
          <div className="counter">
            <button
              type="button"
              onClick={() => setDurationMinutes((n) => Math.max(1, n - 5))}
              disabled={generating}
            >
              <Minus size={16} />
            </button>
            <span>{durationMinutes}</span>
            <button
              type="button"
              onClick={() => setDurationMinutes((n) => n + 5)}
              disabled={generating}
            >
              <Plus size={16} />
            </button>
          </div>
        </div>
      </div>

      {/* Provider */}
      <div className="form-group">
        <label htmlFor="provider">AI Provider</label>
        <select
          id="provider"
          value={provider}
          onChange={(e) => setProvider(e.target.value)}
          disabled={generating}
        >
          <option value="">Server default</option>
          <option value="gemini">Google Gemini</option>
          <option value="claude">Anthropic Claude</option>
        </select>
      </div>

      {/* Instructions */}
      <div className="form-group">
        <label htmlFor="instruction">Additional Instructions (Optional)</label>
        <textarea
          id="instruction"
          rows="3"
          placeholder="e.g. Focus on practical applications, include real-world examples…"
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          disabled={generating}
        />
      </div>

      <button className="generate-btn" type="submit" disabled={!canGenerate}>
        {generating ? (
          <>
            <span className="spinner spinner--sm" />
            Generating…
          </>
        ) : (
          <>
            <Sparkles size={20} />
            Generate Quiz
          </>
        )}
      </button>

      <div className="config-note">
        AI may generate inaccurate information. Please review before use.
      </div>
    </form>
  );
};

export default QuizConfig;
