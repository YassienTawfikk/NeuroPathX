// config.js

// API_BASE_URL: The base URL for the backend API.
// Default for local development: "http://127.0.0.1:8000"
// For production, change this to your deployed backend URL (e.g., https://your-space-name.hf.space)

// Determines if we are running locally or in production (Vercel)
const isLocalhost = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1";

// PROD: The Hugging Face Spaces Backend URL
const PROD_API_URL = "https://yassientawfikk-neuropathx-backend.hf.space";

// LOCAL: Local python backend
const LOCAL_API_URL = "http://127.0.0.1:8000";

const API_BASE_URL = isLocalhost ? LOCAL_API_URL : PROD_API_URL;

console.log(`[Config] Running on ${window.location.hostname}. using API: ${API_BASE_URL}`);

window.NEUROPATHX_CONFIG = {
    API_BASE_URL: API_BASE_URL
};
