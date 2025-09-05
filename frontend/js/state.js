// state.js
let scale = 1, posX = 0, posY = 0;
let brightness = 1, contrast = 1;
let isDragging = false, startX, startY;
let objectURL = null;

const MAX_MB = 200;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/jpg"];
const REPORT_PREVIEW_URL = "http://127.0.0.1:8000/report/preview";
const REPORT_DOWNLOAD_URL = "http://127.0.0.1:8000/report/download";