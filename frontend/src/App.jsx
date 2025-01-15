import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from "react-router-dom";
import Upload from "./components/Upload";
import History from "./components/History";
import DeleteHistory from "./components/DeleteHistory";
import OceanAnimation from "./components/OceanAnimation";
import LoginPage from "./components/LoginPage";
import SignupPage from "./components/SignupPage";
import "./App.css";

const App = () => {
  const [showHistory, setShowHistory] = useState(false);
  const [showDelete, setShowDelete] = useState(false);
  const [historyTrigger, setHistoryTrigger] = useState(0); // Trigger for refreshing history

  const handleUploadSuccess = () => {
    setHistoryTrigger((prev) => prev + 1); // Increment trigger to refresh history
  };

  return (
    <Router>
      <DynamicBackground>
        <div className="app">
          {/* Ocean Animation */}
          <OceanAnimation />

          {/* Routes */}
          <Routes>
            {/* Base URL redirects to login */}
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route
              path="/app"
              element={
                <AppContent
                  showHistory={showHistory}
                  setShowHistory={setShowHistory}
                  showDelete={showDelete}
                  setShowDelete={setShowDelete}
                  historyTrigger={historyTrigger}
                  handleUploadSuccess={handleUploadSuccess}
                />
              }
            />
          </Routes>
        </div>
      </DynamicBackground>
    </Router>
  );
};

const AppContent = ({
  showHistory,
  setShowHistory,
  showDelete,
  setShowDelete,
  historyTrigger,
  handleUploadSuccess,
}) => {
  return (
    <>
      {/* Top Buttons */}
      <div className="top-buttons">
        <button
          className="view-history-button"
          onClick={() => setShowHistory(true)}
        >
          View History
        </button>
        <button
          className="delete-history-button"
          onClick={() => setShowDelete(!showDelete)}
        >
          {showDelete ? "Close Delete" : "Delete History"}
        </button>
      </div>

      {/* Sliding Sidebar */}
      <div className={`history-sidebar ${showHistory ? "open" : ""}`}>
        <button
          className="close-sidebar-button"
          onClick={() => setShowHistory(false)}
        >
          &times;
        </button>
        <History refreshTrigger={historyTrigger} />
      </div>

      {/* Main Content */}
      <div className="main-content">
        <Upload onSuccess={handleUploadSuccess} />
        {showDelete && <DeleteHistory />}
      </div>
    </>
  );
};

/**
 * DynamicBackground component
 * Dynamically sets a background image based on the route
 */
const DynamicBackground = ({ children }) => {
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === "/app") {
      // Set a background for the main app
      document.body.style.background = 'url("mainbg.jpeg") no-repeat center center fixed';
      document.body.style.backgroundSize = "cover";
    } else {
      // Clear background for other routes (like login/signup)
      document.body.style.background = "none";
    }

    // Cleanup background when unmounting or switching routes
    return () => {
      document.body.style.background = "none";
    };
  }, [location.pathname]);

  return <>{children}</>;
};

export default App;
