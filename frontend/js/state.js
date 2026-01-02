let scale = 1, posX = 0, posY = 0;
let brightness = 1, contrast = 1;
let isDragging = false, startX, startY;
let objectURL = null;
let currentFile = null;

const MAX_MB = 200;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/jpg"];
const SESSION_ID = "latest";
const baseUrl = window.NEUROPATHX_CONFIG ? window.NEUROPATHX_CONFIG.API_BASE_URL : "http://127.0.0.1:8000";
const REPORT_PREVIEW_URL = `${baseUrl}/report/preview?session_id=${SESSION_ID}`;
const REPORT_DOWNLOAD_URL = `${baseUrl}/report/download?session_id=${SESSION_ID}`;