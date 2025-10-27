// results.js

import {ClinicalData, DefaultClinicalData} from './clinicalData.js';

// Note: Global variables like resultsBox, resultsWrapper, etc., are accessed directly.

/**
 * Safely converts text with markdown-style bolding (**text**) into HTML strong tags.
 * @param {string} text
 * @returns {string} HTML string
 */
function markdownToHtml(text) {
    // This regular expression now captures text between ** and replaces the entire match
    // with <strong>$1</strong>, correctly rendering the bold text.
    return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

/**
 * Handles the logic for displaying the prediction results with a clinical touch.
 * @param {Object} result - The JSON response from the /mri_prediction endpoint.
 */
export function displayPredictionResults(result) {
    const predictedClass = result.class; // e.g., "Glioma Tumor"
    const clinicalDetails = ClinicalData[predictedClass] || DefaultClinicalData;
    const confidencePercent = (result.confidence * 100).toFixed(2);

    // 1. Update Primary Header/Title
    document.getElementById('clinical-title').innerHTML =
        `<span class="indicator-icon">${clinicalDetails.indicator}</span> ${clinicalDetails.title}`;

    // 2. Update Confidence Badge
    document.getElementById('confidence-badge').textContent = `${confidencePercent}%`;

    // 3. Update Clinical Description
    // We wrap the description's constant title in <strong> and then process the text content.
    document.getElementById('clinical-description').innerHTML =
        `<strong>Classification Overview:</strong> ${markdownToHtml(clinicalDetails.description)}`;

    // 4. Update Clinical Action/Recommendation
    // We wrap the action's constant title in <strong> and then process the text content.
    document.getElementById('clinical-action').innerHTML =
        `<strong>Clinical Recommendation:</strong> ${markdownToHtml(clinicalDetails.action)}`;

    // 5. Update All Class Probabilities List - Enhanced Filtering
    const list = document.getElementById('probability-list');
    list.innerHTML = ''; // Clear previous results

    if (result.all_classes && Array.isArray(result.all_classes)) {
        const MIN_CONFIDENCE_THRESHOLD = 0.001; // 0.1%

        result.all_classes.sort((a, b) => b.confidence - a.confidence); // Sort by confidence

        result.all_classes
            .filter(item => item.confidence > MIN_CONFIDENCE_THRESHOLD)
            .forEach(item => {
                const li = document.createElement('li');
                const itemConfidence = (item.confidence * 100).toFixed(2);
                li.innerHTML = `
                    <span>${item.label}:</span> 
                    <strong>${itemConfidence}%</strong>
                `;
                // Add a visual indicator for the predicted class
                if (item.label === predictedClass) {
                    li.style.fontWeight = 'bold';
                    li.style.color = '#1976d2'; // Highlight predicted class
                }
                list.appendChild(li);
            });
    }

    // Optional: Log the result's 'note' for debugging
    console.log("Model Note:", result.note);
}


// ==============================================================================
// PDF MODAL / Report Logic (Remains unchanged)
// ==============================================================================

// Open results modal with PDF viewer
function openResultsModal(url) {
    resultsIframe.src = url;
    resultsModal.classList.add("show");
}

// Close modal (button or Escape key)
resultsCloseBtn.onclick = () => resultsModal.classList.remove("show");
document.addEventListener("keydown", e => {
    if (e.key === "Escape" && resultsModal.classList.contains("show")) {
        resultsCloseBtn.click();
    }
});

// Preview report in modal
previewBtn.addEventListener("click", () => openResultsModal(REPORT_PREVIEW_URL));

// Download report as PDF
downloadBtn.addEventListener("click", () => {
    const link = document.createElement("a");
    link.href = REPORT_DOWNLOAD_URL;
    link.download = "MRI_Report.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
});