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
