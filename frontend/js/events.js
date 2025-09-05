// events.js
uploadBtn.addEventListener("click", () => inputFile.click());
inputFile.addEventListener("change", (e) => {
    if (e.target.files.length) handleFile(e.target.files[0]);
});

// Home reset
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
    document.body.classList.remove("uploaded");
    sessionStorage.clear();
});

// Restore on load
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

// Drag & Drop
document.addEventListener("dragover", (e) => { e.preventDefault(); document.body.classList.add("dragover"); });
document.addEventListener("dragleave", (e) => { e.preventDefault(); document.body.classList.remove("dragover"); });
document.addEventListener("drop", (e) => {
    e.preventDefault();
    document.body.classList.remove("dragover");
    if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
});

// Viewer controls
resetBtn.addEventListener("click", resetView);

// Zoom + Pan + Brightness/Contrast...
resetBtn.addEventListener("click", resetView);

// Zoom with Ctrl + wheel
img.addEventListener("wheel", (e) => {
    if (e.ctrlKey) {
        e.preventDefault();
        scale += e.deltaY * -0.01;
        scale = Math.min(Math.max(1, scale), 5);
        updateTransform();
    }
});

// Pan
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

// Brightness & Contrast (wheel without ctrl)
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
