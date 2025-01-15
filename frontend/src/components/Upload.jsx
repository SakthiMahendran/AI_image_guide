import React, { useState } from "react";

const baseUrl = "http://127.0.0.1:8000/api"; // Backend base URL

const Upload = ({ onSuccess }) => {
  const [file, setFile] = useState(null);
  const [prompt, setPrompt] = useState(""); // State for the user prompt
  const [statusMessage, setStatusMessage] = useState("");
  const [summary, setSummary] = useState(""); // State for storing summary
  const [previewImage, setPreviewImage] = useState(
    "placeholder.jpeg" // Path to your placeholder image
  );
  const [imageUploaded, setImageUploaded] = useState(false); // Tracks if the image is already uploaded
  const [uploadedImageId, setUploadedImageId] = useState(null); // Stores ID of the uploaded image

  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setPreviewImage(URL.createObjectURL(uploadedFile)); // Set uploaded image as preview
      setImageUploaded(false); // Reset the upload status when a new file is selected
    }
  };

  const handleUpload = async () => {
    if (!file && !imageUploaded) {
      alert("Please select an image to upload.");
      return;
    }

    if (!prompt.trim()) {
      alert("Please enter a valid prompt.");
      return;
    }

    const formData = new FormData();

    if (imageUploaded) {
      // Only send the updated prompt for an existing image
      formData.append("image_id", uploadedImageId);
      formData.append("prompt", prompt);
    } else {
      // Send both the image and the prompt for a new upload
      formData.append("image", file);
      formData.append("prompt", prompt);
    }

    try {
      const response = await fetch(`${baseUrl}/upload/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (imageUploaded) {
        setStatusMessage("Prompt updated successfully!");
      } else {
        setStatusMessage("Uploaded successfully!");
        setUploadedImageId(data.image_id); // Store the uploaded image ID for future updates
        setImageUploaded(true); // Mark the image as uploaded
      }
      setSummary(data.summary); // Replace the summary with the updated one
      onSuccess(); // Notify App.jsx to refresh history
    } catch (error) {
      console.error("Error uploading image or updating prompt:", error);
      setStatusMessage("An error occurred while uploading or updating.");
      setSummary(""); // Clear summary on error
    }
  };

  return (
    <div className="main-content">
      <div className="upload-container">
        <div className="upload-preview">
          <img
            src={previewImage}
            alt="Uploaded Preview"
            className="uploaded-image"
          />
        </div>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input"
        />
        <input
          type="text"
          placeholder="Enter your prompt here"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="prompt-input"
        />
        <button className="upload-button" onClick={handleUpload}>
          {imageUploaded ? "Update Prompt" : "Upload"}
        </button>
        {statusMessage && <p className="status-message">{statusMessage}</p>}
        {summary && (
          <div className="summary-container">
            <h4>Summary:</h4>
            <p>{summary}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Upload;
