const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("file-upload");

// Highlight on dragover
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
    inputFile.files = e.dataTransfer.files;
    console.log("Dropped files:", inputFile.files);
});

const img = document.getElementById("scanImage");
const resetBtn = document.getElementById("resetBtn");

let scale = 1;
let posX = 0, posY = 0;
let brightness = 1;
let contrast = 1;

let isDragging = false;
let startX, startY;

function updateTransform() {
    img.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
    img.style.filter = `brightness(${brightness}) contrast(${contrast})`;
}

// Zoom (pinch or trackpad pinch, fallback: ctrl + wheel)
img.addEventListener("wheel", e => {
    if (e.ctrlKey) { // trackpad pinch triggers ctrl+wheel on Mac
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(0.5, scale), 5); // clamp
        updateTransform();
    }
});

// Drag to Pan
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

// Trackpad two-finger swipe up/down → brightness
img.addEventListener("wheel", e => {
    if (!e.ctrlKey) { // normal 2-finger scroll
        e.preventDefault();
        if (e.shiftKey) {
            // Hold shift to adjust contrast
            contrast += e.deltaY * -0.005;
            contrast = Math.max(0.2, Math.min(3, contrast));
        } else {
            // Normal scroll → brightness
            brightness += e.deltaY * -0.005;
            brightness = Math.max(0.2, Math.min(3, brightness));
        }
        updateTransform();
    }
});

// Reset Button
resetBtn.addEventListener("click", () => {
    scale = 1;
    posX = 0;
    posY = 0;
    brightness = 1;
    contrast = 1;
    updateTransform();
});

// Initial
updateTransform();