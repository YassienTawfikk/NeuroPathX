// events.js

// CRITICAL FIX: Import the display function from results.js
import { displayPredictionResults } from './results.js';
import { SAMPLE_DIR } from './samples_manifest.js';

function loadSampleFile(url) {
    fetch(url)
        .then(response => {
            if (!response.ok) throw new Error(`Failed to fetch sample: ${response.statusText}`);
            return response.blob();
        })
        .then(blob => {
            const fileName = url.substring(url.lastIndexOf('/') + 1);
            const file = new File([blob], fileName, { type: blob.type });

            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);

            inputFile.files = dataTransfer.files;
            handleFile(file);
        })
        .catch(error => {
            console.error("❌ Error loading sample file:", error);
            // inputFile.click(); // Don't open file picker on error, just log it.
            alert("Could not load sample file. Please try another.");
        });
}

// =========================================================================
// Finder-Style Explorer Logic
// =========================================================================
const samplesModal = document.getElementById('samples-modal');
const openSamplesBtn = document.getElementById('openSamplesBtn');
const samplesNavBtn = document.getElementById('samplesNavBtn');
const closeSamplesBtn = document.getElementById('closeSamplesBtn');
const finderContent = document.getElementById('finderContent');
const finderBreadcrumbs = document.getElementById('finderBreadcrumbs');

// State
let currentFolder = SAMPLE_DIR; // Start at root
let pathHistory = [SAMPLE_DIR]; // Breadcrumb stack

function renderFinder() {
    finderContent.innerHTML = '';

    // Safety check
    if (!currentFolder || !currentFolder.children) return;

    currentFolder.children.forEach(item => {
        const el = document.createElement('div');
        el.className = item.type === 'folder' ? 'finder-item folder-item' : 'finder-item file-item';

        // Icon / Thumbnail
        if (item.type === 'folder') {
            el.innerHTML = `
                <i class="fa-solid fa-folder finder-icon"></i>
                <div class="finder-label">${item.name}</div>
            `;
            el.onclick = () => navigateToFolder(item);
        } else {
            // It's a file
            el.innerHTML = `
                <img src="${item.path}" class="finder-thumb" loading="lazy">
                <div class="finder-label">${item.name}</div>
            `;
            el.onclick = () => selectSample(item.path);
        }
        finderContent.appendChild(el);
    });

    renderBreadcrumbs();
}

function renderBreadcrumbs() {
    finderBreadcrumbs.innerHTML = '';

    pathHistory.forEach((folder, index) => {
        // Add Button
        const btn = document.createElement('button');
        btn.className = 'crumb-btn';
        if (index === pathHistory.length - 1) btn.classList.add('active');

        // Root gets a home icon
        if (index === 0) {
            btn.innerHTML = '<i class="fa-solid fa-house"></i> Home';
        } else {
            btn.textContent = folder.name;
        }

        btn.onclick = () => navigateToBreadcrumb(index);
        finderBreadcrumbs.appendChild(btn);

        // Add Separator (unless last item)
        if (index < pathHistory.length - 1) {
            const sep = document.createElement('span');
            sep.className = 'crumb-separator';
            sep.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
            finderBreadcrumbs.appendChild(sep);
        }
    });
}

function navigateToFolder(folderNode) {
    pathHistory.push(folderNode);
    currentFolder = folderNode;
    renderFinder();
}

function navigateToBreadcrumb(index) {
    // Slice history to jump back
    pathHistory = pathHistory.slice(0, index + 1);
    currentFolder = pathHistory[pathHistory.length - 1];
    renderFinder();
}

function selectSample(path) {
    loadSampleFile(path);
    samplesModal.classList.remove('show');
}

// Modal Controls
function openFinder() {
    // Reset to root on open? Or keep state? Let's reset to root for clarity.
    currentFolder = SAMPLE_DIR;
    pathHistory = [SAMPLE_DIR];
    renderFinder();
    samplesModal.classList.add('show');
}

openSamplesBtn.addEventListener('click', (e) => {
    e.preventDefault();
    openFinder();
});

samplesNavBtn.addEventListener('click', openFinder);

closeSamplesBtn.addEventListener('click', () => {
    samplesModal.classList.remove('show');
});

window.addEventListener('click', (e) => {
    if (e.target === samplesModal) {
        samplesModal.classList.remove('show');
    }
});


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
    // Reset Finder
    currentFolder = SAMPLE_DIR;

    document.body.classList.remove("uploaded");
    sessionStorage.clear();
});

// --- Restore state on reload ---
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

        const resultsVisible = sessionStorage.getItem("resultsVisible");
        resultsBox.style.display = resultsVisible === "true" ? "flex" : "none";
        resultsWrapper.style.display = resultsVisible === "true" ? "grid" : "block";

        resetView();
    }
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
    if (!inputFile.files.length) {
        // Use a custom message box instead of alert()
        console.error("Please upload an MRI image first.");
        return;
    }

    // 1. Show Loader and Disable Button
    globalLoader.classList.add("show");
    diagnoseBtn.disabled = true;
    diagnoseBtn.classList.add("disabled");

    const file = inputFile.files[0];
    const formData = new FormData();
    formData.append("file", file);

    try {
        const baseUrl = window.NEUROPATHX_CONFIG ? window.NEUROPATHX_CONFIG.API_BASE_URL : "http://127.0.0.1:8000";
        const response = await fetch(`${baseUrl}/mri_prediction`, {
            method: "POST",
            body: formData,
        });

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
        alert(`Error: ${err.message}. Check console for details.`);
    } finally {
        // 2. Hide Loader and Enable Button
        globalLoader.classList.remove("show");
        diagnoseBtn.disabled = false;
        diagnoseBtn.classList.remove("disabled");
    }
});