// state.js
let scale = 1, posX = 0, posY = 0;
let brightness = 1, contrast = 1;
let isDragging = false, startX, startY;
let objectURL = null;

const MAX_MB = 200;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/jpg"];
const REPORT_URL = "assets/report-sample.pdf";