const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("file-upload");
const img = document.getElementById("scanImage");
const resetBtn = document.getElementById("resetBtn");
const uploadBtn = document.getElementById("uploadBtn");
const homeBtn = document.querySelector(".go-to-options .options-btn:nth-child(3)");

let scale = 1;
let posX = 0, posY = 0;
let brightness = 1;
let contrast = 1;

let isDragging = false;
let startX, startY;
let objectURL = null;

const MAX_MB = 200;
const MAX_BYTES = MAX_MB * 1024 * 1024;
const ALLOWED = ["image/jpeg", "image/png", "image/jpg"];

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

    // Mark UI as "uploaded"
    document.body.classList.add("uploaded");
    document.querySelector(".upload-box").style.display = "none";
    document.querySelector(".scan-box").style.display = "grid";
    document.querySelector(".start-header .title-autograph").style.transform = "translateX(calc(-50vw + 150px))";

    // Save to localStorage (persist state)
    localStorage.setItem("uploadedImage", objectURL);
    localStorage.setItem("uploadedName", file.name);
}

// --- Upload Button ---
uploadBtn.addEventListener("click", () => {
    inputFile.click();
});

// --- File Input ---
inputFile.addEventListener("change", (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

// --- Home Button ---
homeBtn.addEventListener("click", () => {
    document.querySelector(".upload-box").style.display = "grid";
    document.querySelector(".scan-box").style.display = "none";
    document.querySelector(".start-header .title-autograph").style.transform = "translateX(0)";
    img.src = "";

    if (objectURL) {
        URL.revokeObjectURL(objectURL);
        objectURL = null;
    }
    resetView();

    document.body.classList.remove("uploaded");

    // Clear persistence
    localStorage.removeItem("uploadedImage");
    localStorage.removeItem("uploadedName");
});

// --- Restore on Page Load ---
window.addEventListener("DOMContentLoaded", () => {
    const savedImage = localStorage.getItem("uploadedImage");
    const savedName = localStorage.getItem("uploadedName");

    if (savedImage) {
        objectURL = savedImage;
        img.src = savedImage;
        img.alt = savedName || "Uploaded Image";

        document.body.classList.add("uploaded");
        document.querySelector(".upload-box").style.display = "none";
        document.querySelector(".scan-box").style.display = "grid";
        document.querySelector(".start-header .title-autograph").style.transform = "translateX(calc(-50vw + 150px))";

        resetView();
    }
});

// --- Drag & Drop Anywhere ---
document.addEventListener("dragover", (e) => {
    e.preventDefault();
    document.body.classList.add("dragover"); // optional styling
});

document.addEventListener("dragleave", (e) => {
    e.preventDefault();
    document.body.classList.remove("dragover");
});

document.addEventListener("drop", (e) => {
    e.preventDefault();
    document.body.classList.remove("dragover");

    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});
// --- Reset Button ---
resetBtn.addEventListener("click", resetView);

// --- Zoom ---
img.addEventListener("wheel", e => {
    if (e.ctrlKey) {
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(1, scale), 5);
        updateTransform();
    }
});

// --- Drag to Pan ---
img.addEventListener("mousedown", e => {
    isDragging = true;
    startX = e.clientX - posX;
    startY = e.clientY - posY;
});
window.addEventListener("mouseup", () => isDragging = false);
window.addEventListener("mousemove", e => {
    if (isDragging) {
        posX = e.clientX - startX;
        posY = e.clientY - startY;
        updateTransform();
    }
});

// --- Brightness & Contrast ---
img.addEventListener("wheel", e => {
    if (!e.ctrlKey) {
        e.preventDefault();
        if (e.shiftKey) {
            contrast += e.deltaY * -0.005;
            contrast = Math.max(0.2, Math.min(3, contrast));
        } else {
            brightness += e.deltaY * -0.005;
            brightness = Math.max(0.2, Math.min(3, brightness));
        }
        updateTransform();
    }
});

// Prevent dragging the image into a new tab
img.addEventListener("dragstart", (e) => e.preventDefault());

// Prevent double-click opening image in new tab / selecting it
img.addEventListener("mousedown", (e) => {
    if (e.detail > 1) e.preventDefault(); // disable double click default
});

// --- Disable right-click on the image ---
img.addEventListener("contextmenu", e => {
    e.preventDefault();
    return false;
});
// --- Init ---
updateTransform();