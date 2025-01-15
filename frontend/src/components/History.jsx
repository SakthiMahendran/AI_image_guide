import React, { useState, useEffect } from "react";

const baseUrl = "http://127.0.0.1:8000"; // Django backend

const History = ({ refreshTrigger }) => {
  const [history, setHistory] = useState([]);

  const fetchHistory = async () => {
    try {
      const response = await fetch(`${baseUrl}/api/history/`);
      const data = await response.json();

      if (response.ok) {
        setHistory(data);
      } else {
        console.error("Failed to fetch history:", data.error);
      }
    } catch (error) {
      console.error("Error fetching history:", error);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [refreshTrigger]); // Fetch history when refreshTrigger changes

  return (
    <div className="history-content">
      <h3>Your History</h3>
      <div className="history-list">
        {history.map((item) => (
          <div key={item.image_id} className="history-item">
            <img
              src={`http://127.0.0.1:8000${item.image}`} // Display the image
              alt={`Image ID: ${item.image_id}`}
              className="history-image"
            />
            <p>
              <strong>ID:</strong> {item.image_id}
            </p>
            <p>
              <strong>Summary:</strong> {item.summary || "No summary available"}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default History;
