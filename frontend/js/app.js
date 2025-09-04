const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("file-upload");
const img = document.getElementById("scanImage");
const resetBtn = document.getElementById("resetBtn");

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
    // Validate type
    if (!ALLOWED.includes(file.type)) {
        alert("Only JPG and PNG are supported.");
        return;
    }

    // Validate size
    if (file.size > MAX_BYTES) {
        alert(`File exceeds ${MAX_MB} MB limit.`);
        return;
    }

    // Clean up old URL if exists
    if (objectURL) URL.revokeObjectURL(objectURL);

    // Create a new preview URL
    objectURL = URL.createObjectURL(file);
    img.src = objectURL;
    img.alt = file.name;

    resetView();

    // Mark UI as "uploaded"
    document.body.classList.add("uploaded");
}

// --- Drag & Drop ---
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.classList.add("dragover");
});

dropArea.addEventListener("dragleave", () => {
    dropArea.classList.remove("dragover");
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
        handleFile(e.dataTransfer.files[0]);
    }
});

// --- File Input ---
inputFile.addEventListener("change", (e) => {
    if (e.target.files.length) {
        handleFile(e.target.files[0]);
    }
});

// --- Reset Button ---
resetBtn.addEventListener("click", resetView);

// --- Zoom (trackpad pinch = ctrl+wheel) ---
img.addEventListener("wheel", e => {
    if (e.ctrlKey) {
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(0.5, scale), 5);
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

// --- Brightness & Contrast (2-finger scroll, Shift for contrast) ---
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

// --- Init ---
updateTransform();