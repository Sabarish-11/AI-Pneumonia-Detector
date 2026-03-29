import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, useNavigate, Navigate } from "react-router-dom";
import api from "./api";
import Header from "./components/Header.jsx";
import UploadBox from "./components/UploadBox.jsx";
import ResultCard from "./components/ResultCard.jsx";
import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import History from "./components/History.jsx";
import "./styles/App.css";


function Dashboard() {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.get("/history");
        setHistory(response.data);
      } catch (err) {
        console.error(err);
        if (err.response && err.response.status === 401) {
          alert("Session expired. Please login again.");
          localStorage.removeItem("access_token");
          navigate("/login");
        }
      }
    };
    fetchHistory();
  }, [navigate]);

  const handlePredict = async (selectedFile) => {
    if (!selectedFile) {
      setErrorMessage("Please upload a chest X-ray image.");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      setLoading(true);
      setErrorMessage("");
      setResult(null);

      const response = await api.post("/predict", formData);
      setResult(response.data);

      const histRes = await api.get("/history");
      setHistory(histRes.data);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 401) {
        alert("Please login to use the system.");
        navigate("/login");
      } else {
        const detail = err.response?.data?.detail;
        setErrorMessage(detail || "Unable to analyze this file. Please upload a valid chest X-ray image.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (newFile) => {
    setFile(newFile);
    setResult(null);
    setErrorMessage("");

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }

    if (newFile) {
      const url = URL.createObjectURL(newFile);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    navigate("/login");
  };

  return (
    <div className="app">
      <div className="app-inner">
        <div className="top-bar">
          <Header />
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>

        <UploadBox
          setFile={handleFileChange}
          handlePredict={handlePredict}
          loading={loading}
          errorMessage={errorMessage}
        />

        {previewUrl && (
          <div className="preview-box">
            <h3>Image Preview</h3>
            <img src={previewUrl} alt="Preview" />
          </div>
        )}

        <ResultCard result={result} />

        <History items={history} />

        <p className="disclaimer">
          This system is an academic AI screening tool and not a certified medical device.
          Results are probabilistic and must be reviewed by a qualified clinician.
        </p>
      </div>
    </div>
  );
}

function AppRoutes() {
  const navigate = useNavigate();

  const handleLoginSuccess = () => {
    navigate("/app");
  };

  const handleRegisterSuccess = () => {
    navigate("/login");
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/app");
    }
  }, [navigate]);

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />

      <Route
        path="/login"
        element={<Login onLoginSuccess={handleLoginSuccess} />}
      />
      <Route
        path="/register"
        element={<Register onRegisterSuccess={handleRegisterSuccess} />}
      />
      <Route path="/app" element={<Dashboard />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
