// events.js

import { displayPredictionResults } from './results.js';
import { initSampleExplorer, openFinder } from './samples_manager.js';

// Initialize the Sample Explorer Listeners
initSampleExplorer();

// Sample Explorer Logic has been moved to samples_manager.js


// --- File upload (Original Browse Button) ---
uploadBtn.addEventListener("click", () => {
    inputFile.click();
});
inputFile.addEventListener("change", (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

// --- Home reset ---
homeBtn.addEventListener("click", () => {
    document.querySelector(".upload-box").style.display = "grid";
    document.querySelector(".scan-box").style.display = "none";
    resultsWrapper.style.display = "none";
    resultsBox.style.display = "none";
    document.querySelector(".start-header .title-autograph").style.transform = "translateX(0)";
    img.src = "";

    if (objectURL) {
        URL.revokeObjectURL(objectURL);
        objectURL = null;
    }
    resetView();
    resetView();
    // Reset Finder handled by openFinder() in samples_manager.js when needed

    document.body.classList.remove("uploaded");
    sessionStorage.clear();
});

// --- Restore state on reload ---
// --- Restore state on reload ---
window.addEventListener("DOMContentLoaded", () => {
    // We do NOT restore the image from sessionStorage because Blob URLs are revoked on reload.
    // Instead, we just open the Finder/Sample explorer if starting fresh.
    openFinder();
});

// --- Drag & drop upload ---
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

// --- Viewer controls ---
resetBtn.addEventListener("click", resetView);

// Zoom with Ctrl + wheel
img.addEventListener("wheel", (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(0.8, scale), 5);
        updateTransform();
    }
});
// Pan with mouse drag
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

// Brightness/contrast with wheel
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

// --- Diagnose button → API call with Loader Integration ---
diagnoseBtn.addEventListener("click", async () => {
    if (!currentFile) {
        // Use a custom message box instead of alert()
        console.error("Please upload an MRI image first.");
        showErrorModal("Please upload an MRI image first.");
        return;
    }

    // 1. Show Loader and Disable Button
    const loaderText = globalLoader.querySelector(".loader-text");
    const loaderSubtext = globalLoader.querySelector(".loader-subtext");

    loaderText.innerText = "Analyzing MRI Scan...";
    loaderSubtext.innerText = "";

    globalLoader.classList.add("show");
    diagnoseBtn.disabled = true;
    diagnoseBtn.classList.add("disabled");

    // Timeout to show "Server Waking Up" message if it takes too long
    const wakeupTimeout = setTimeout(() => {
        loaderText.innerText = "Server is waking up...";
        loaderSubtext.innerText = "This may take a minute for the cold start. Subsequent predictions will be fast!";
    }, 3000); // 3 seconds

    const formData = new FormData();
    formData.append("file", currentFile);

    try {
        const baseUrl = window.NEUROPATHX_CONFIG ? window.NEUROPATHX_CONFIG.API_BASE_URL : "http://127.0.0.1:8000";
        const response = await fetch(`${baseUrl}/mri_prediction`, {
            method: "POST",
            body: formData,
        });

        clearTimeout(wakeupTimeout); // Clear timeout on response

        if (!response.ok) {
            let errorMessage = `Server error: ${response.status}`;
            try {
                const errorData = await response.json();
                if (errorData.detail) errorMessage = errorData.detail;
            } catch (e) {
                // Could not parse JSON, stick to generic error
            }
            throw new Error(errorMessage);
        }
        const result = await response.json();

        // Call the imported function to display the rich results
        displayPredictionResults(result);
        // Note: The visibility is handled by this function

        resultsBox.style.display = "flex";
        resultsWrapper.style.display = "grid";

        sessionStorage.setItem("resultsVisible", "true");
    } catch (err) {
        console.error("❌ API error:", err);
        showErrorModal(err.message);
    } finally {
        clearTimeout(wakeupTimeout); // Ensure timeout is cleared on error too
        // 2. Hide Loader and Enable Button
        globalLoader.classList.remove("show");
        diagnoseBtn.disabled = false;
        diagnoseBtn.classList.remove("disabled");
    }
});

// --- Error Modal Logic ---
const errorModal = document.getElementById("error-modal");
const errorMessageEl = document.getElementById("error-message");
const closeErrorBtn = document.getElementById("closeErrorBtn");

function showErrorModal(message) {
    if (errorMessageEl) errorMessageEl.innerText = message;
    if (errorModal) errorModal.classList.add("show");
}

if (closeErrorBtn) {
    closeErrorBtn.addEventListener("click", () => {
        if (errorModal) errorModal.classList.remove("show");
    });
}

if (errorModal) {
    window.addEventListener("click", (e) => {
        if (e.target === errorModal) {
            errorModal.classList.remove("show");
        }
    });
}