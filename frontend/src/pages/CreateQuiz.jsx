import { useState } from "react";
import { useNavigate } from "react-router-dom";

import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import QuizConfig from "../components/QuizConfig";
import QuizPreview from "../components/QuizPreview";
import TeamFooter from "../components/TeamFooter";

import { documents, downloadQuizPdf, quizzes as quizApi } from "../api/client";
import "./CreateQuiz.css";

/**
 * Teacher: configure a quiz, generate its questions with AI, review them, then
 * publish or export. The AI call persists the quiz server-side and returns it,
 * so "generated" already means "saved as a draft".
 */
const CreateQuiz = ({ darkMode, setDarkMode }) => {
  const navigate = useNavigate();

  const [result, setResult] = useState(null); // { quiz, questions }
  const [generating, setGenerating] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const handleGenerate = async (config) => {
    setGenerating(true);
    setError("");
    setNotice("");
    setResult(null);

    try {
      let syllabus = config.syllabus;

      // If a source document was attached, parse it server-side first and feed the
      // extracted text to the model as the syllabus.
      if (config.file) {
        setNotice(`Reading ${config.file.name}…`);
        const parsed = await documents.parse(config.file);
        syllabus = parsed.text;
        setNotice(`Read ${parsed.word_count} words from ${config.file.name}. Generating…`);
      }

      const generated = await quizApi.generate({
        title: config.title || undefined,
        topic: config.topic,
        difficulty: config.difficulty,
        question_count: config.questionCount,
        duration_minutes: config.durationMinutes,
        instruction: config.instruction,
        syllabus,
        provider: config.provider || undefined,
      });

      setResult(generated);
      setNotice("");
    } catch (err) {
      setError(err.message);
      setNotice("");
    } finally {
      setGenerating(false);
    }
  };

  const publish = async () => {
    setBusy(true);
    setError("");
    try {
      await quizApi.update(result.quiz.id, { is_active: true });
      navigate("/", { replace: true });
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  };

  const discard = async () => {
    if (!window.confirm("Discard this generated quiz? It will be deleted.")) return;
    setBusy(true);
    setError("");
    try {
      await quizApi.remove(result.quiz.id);
      setResult(null);
      setNotice("Draft discarded.");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const exportPdf = async (answers) => {
    setBusy(true);
    setError("");
    try {
      await downloadQuizPdf(result.quiz.id, { answers });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="dashboard">
      <Sidebar />

      <div className="dashboard-content">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

        <div className="createquiz-body">
          <div className="createquiz-header">
            <div>
              <h1>
                Create New Quiz
                <span className="sparkle"> ✨</span>
              </h1>
              <p>Generate engaging quizzes in seconds with AI</p>
            </div>
          </div>

          {error && <div className="banner banner--error">{error}</div>}
          {notice && <div className="banner banner--info">{notice}</div>}

          <div className="createquiz-grid">
            <div className="left-panel">
              <QuizConfig onGenerate={handleGenerate} generating={generating} />
            </div>

            <div className="right-panel">
              <QuizPreview
                quiz={result?.quiz}
                questions={result?.questions}
                generating={generating}
                busy={busy}
                onPublish={publish}
                onDiscard={discard}
                onExport={exportPdf}
              />
            </div>
          </div>

          <TeamFooter />
        </div>
      </div>
    </div>
  );
};

export default CreateQuiz;
