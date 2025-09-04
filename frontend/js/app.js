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
