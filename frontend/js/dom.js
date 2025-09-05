// dom.js
const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("file-upload");
const img = document.getElementById("scanImage");
const resetBtn = document.getElementById("resetBtn");
const uploadBtn = document.getElementById("uploadBtn");
const homeBtn = document.querySelector(".go-to-options .options-btn:nth-child(3)");
const diagnoseBtn = document.querySelector(".diagnose-btn");

const resultsWrapper = document.querySelector(".scan-results-wrapper");
const resultsBox = document.querySelector(".results-box");

// Modal
const resultsModal = document.getElementById("results-modal");
const resultsIframe = resultsModal.querySelector("iframe");
const resultsCloseBtn = resultsModal.querySelector(".close-btn");
const previewBtn = document.querySelector(".preview-btn");
const downloadBtn = document.getElementById("downloadReport");