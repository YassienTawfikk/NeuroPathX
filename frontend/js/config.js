// config.js

// API_BASE_URL: The base URL for the backend API.
// Default for local development: "http://127.0.0.1:8000"
// For production, change this to your deployed backend URL (e.g., https://your-space-name.hf.space)

const API_BASE_URL = "http://127.0.0.1:7860"; 
// Note: Docker container exposes 7860 by default for HF Spaces compatibility.
// If running locally with uvicorn directly outside docker, you might need 8000.
// But we'll default to 7860 here to align with the Docker setup recommendations.

window.NEUROPATHX_CONFIG = {
    API_BASE_URL: API_BASE_URL
};
