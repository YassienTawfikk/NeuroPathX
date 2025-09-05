// results.js
diagnoseBtn.addEventListener("click", () => {
    resultsWrapper.style.display = "grid";
    resultsBox.style.display = "flex";
    sessionStorage.setItem("resultsVisible", "true");
});

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