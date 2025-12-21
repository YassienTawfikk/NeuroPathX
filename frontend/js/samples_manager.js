import { SAMPLE_DIR } from './samples_manifest.js';

// Global variables from other files that we rely on:
// handleFile (from fileHandler.js)
// inputFile (from events.js/dom.js - we might need to be careful about where this comes from if not global)
// Based on events.js analysis, inputFile seems to be a global ID reference or defined in dom.js. 
// Let's assume standard DOM globals or it's available.

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

            // Assuming inputFile is globally available or we need to look it up
            const inputFile = document.getElementById('file-upload'); 
            if (inputFile) {
                inputFile.files = dataTransfer.files;
                // handleFile is global from fileHandler.js
                if (typeof handleFile === 'function') {
                    handleFile(file);
                } else {
                    console.error("handleFile function not found");
                }
            }
        })
        .catch(error => {
            console.error("❌ Error loading sample file:", error);
            alert("Could not load sample file. Please try another.");
        });
}

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
    // Reset to root on open for clarity
    currentFolder = SAMPLE_DIR;
    pathHistory = [SAMPLE_DIR];
    renderFinder();
    samplesModal.classList.add('show');
}

export function initSampleExplorer() {
    if (openSamplesBtn) {
        openSamplesBtn.addEventListener('click', (e) => {
            e.preventDefault();
            openFinder();
        });
    }

    if (samplesNavBtn) {
        samplesNavBtn.addEventListener('click', openFinder);
    }

    if (closeSamplesBtn) {
        closeSamplesBtn.addEventListener('click', () => {
            samplesModal.classList.remove('show');
        });
    }

    window.addEventListener('click', (e) => {
        if (e.target === samplesModal) {
            samplesModal.classList.remove('show');
        }
    });
    
    // Auto-open logic that was in events.js can be handled here or kept there.
    // events.js had: if (!savedImage) openFinder();
    // We will expose openFinder if needed, or just let events.js handle the initialization logic via this init function.
    // But specific auto-open logic on load typically resides in main init or events.
}

// Export openFinder in case other modules need to trigger it programmatically (like on fresh load)
export { openFinder };
