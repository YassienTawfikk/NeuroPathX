// ======================================================
// DOM ELEMENTS
// ======================================================
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


// ======================================================
// STATE
// ======================================================
let scale = 1, posX = 0, posY = 0;
let brightness = 1, contrast = 1;
let isDragging = false, startX, startY;
let objectURL = null;

const MAX_MB = 200;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/jpg"];
const REPORT_URL = "assets/MRI_Report.pdf";


// ======================================================
// IMAGE VIEWER FUNCTIONS (transform, reset, drag, zoom)
// ======================================================
function updateTransform() {
    img.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
    img.style.filter = `brightness(${brightness}) contrast(${contrast})`;
}

function resetView() {
    scale = 1;
    posX = 0;
    posY = 0;
    brightness = 1;
    contrast = 1;
    updateTransform();
}


// ======================================================
// FILE HANDLING
// ======================================================
function handleFile(file) {
    if (!ALLOWED.includes(file.type)) {
        alert("Only JPG and PNG are supported.");
        return;
    }
    if (file.size > MAX_BYTES) {
        alert(`File exceeds ${MAX_MB} MB limit.`);
        return;
    }
    if (objectURL) URL.revokeObjectURL(objectURL);

    objectURL = URL.createObjectURL(file);
    img.src = objectURL;
    img.alt = file.name;

    resetView();

    // Update UI
    document.body.classList.add("uploaded");
    document.querySelector(".upload-box").style.display = "none";
    document.querySelector(".scan-box").style.display = "grid";
    resultsWrapper.style.display = "block";
    resultsBox.style.display = "none";
    document.querySelector(".start-header .title-autograph").style.transform =
        "translateX(calc(-50vw + 150px))";

    // Persist
    sessionStorage.setItem("uploadedImage", objectURL);
    sessionStorage.setItem("uploadedName", file.name);
    sessionStorage.setItem("resultsVisible", "false");
}


// ======================================================
// EVENT HANDLERS: UPLOAD / HOME / RESTORE
// ======================================================
uploadBtn.addEventListener("click", () => inputFile.click());

inputFile.addEventListener("change", (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

homeBtn.addEventListener("click", () => {
    // Reset UI
    document.querySelector(".upload-box").style.display = "grid";
    document.querySelector(".scan-box").style.display = "none";
    resultsWrapper.style.display = "none";
    resultsBox.style.display = "none";
    document.querySelector(".start-header .title-autograph").style.transform = "translateX(0)";
    img.src = "";

    // Cleanup
    if (objectURL) {
        URL.revokeObjectURL(objectURL);
        objectURL = null;
    }
    resetView();
    document.body.classList.remove("uploaded");
    sessionStorage.clear();
});

window.addEventListener("DOMContentLoaded", () => {
    const savedImage = sessionStorage.getItem("uploadedImage");
    const savedName = sessionStorage.getItem("uploadedName");

    if (savedImage) {
        objectURL = savedImage;
        img.src = savedImage;
        img.alt = savedName || "Uploaded Image";

        document.body.classList.add("uploaded");
        document.querySelector(".upload-box").style.display = "none";
        document.querySelector(".scan-box").style.display = "grid";
        document.querySelector(".start-header .title-autograph").style.transform =
            "translateX(calc(-50vw + 150px))";

        // Restore results state
        const resultsVisible = sessionStorage.getItem("resultsVisible");
        resultsBox.style.display = resultsVisible === "true" ? "flex" : "none";
        resultsWrapper.style.display = resultsVisible === "true" ? "grid" : "block";

        resetView();
    }
});


// ======================================================
// DRAG & DROP
// ======================================================
document.addEventListener("dragover", (e) => {
    e.preventDefault();
    document.body.classList.add("dragover");
});
document.addEventListener("dragleave", (e) => {
    e.preventDefault();
    document.body.classList.remove("dragover");
});
document.addEventListener("drop", (e) => {
    e.preventDefault();
    document.body.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});


// ======================================================
// VIEWER CONTROLS (zoom, pan, brightness, contrast)
// ======================================================
resetBtn.addEventListener("click", resetView);

// Zoom with Ctrl + wheel
img.addEventListener("wheel", (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(1, scale), 5);
        updateTransform();
    }
});

// Pan
img.addEventListener("mousedown", (e) => {
    isDragging = true;
    startX = e.clientX - posX;
    startY = e.clientY - posY;
});
window.addEventListener("mouseup", () => isDragging = false);
window.addEventListener("mousemove", (e) => {
    if (isDragging) {
        posX = e.clientX - startX;
        posY = e.clientY - startY;
        updateTransform();
    }
});

// Brightness & Contrast (wheel without ctrl)
img.addEventListener("wheel", (e) => {
    if (!e.ctrlKey) {
        e.preventDefault();
        if (e.shiftKey) {
            contrast -= e.deltaY * -0.005;
            contrast = Math.max(0.2, Math.min(3, contrast));
        } else {
            brightness -= e.deltaY * -0.005;
            brightness = Math.max(0.2, Math.min(3, brightness));
        }
        updateTransform();
    }
});

// Prevent unwanted interactions
img.addEventListener("dragstart", (e) => e.preventDefault());
img.addEventListener("mousedown", (e) => {
    if (e.detail > 1) e.preventDefault();
});
img.addEventListener("contextmenu", (e) => e.preventDefault());


// ======================================================
// DIAGNOSE BUTTON
// ======================================================
diagnoseBtn.addEventListener("click", () => {
    resultsWrapper.style.display = "grid";
    resultsBox.style.display = "flex";
    sessionStorage.setItem("resultsVisible", "true");
});


// ======================================================
// RESULTS MODAL (Preview + Download)
// ======================================================
function openResultsModal(url) {
    resultsIframe.src = url;
    resultsModal.classList.add("show");
}

resultsCloseBtn.onclick = () => resultsModal.classList.remove("show");
document.addEventListener("keydown", e => {
    if (e.key === "Escape" && resultsModal.classList.contains("show")) {
        resultsCloseBtn.click();
    }
});

previewBtn.addEventListener("click", () => openResultsModal(REPORT_URL));

downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = REPORT_URL;
    link.download = "MRI_Report.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});


// ======================================================
// INIT
// ======================================================
updateTransform();