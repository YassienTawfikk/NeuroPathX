// fileHandler.js
function handleFile(file) {
    if (!ALLOWED.includes(file.type)) {
        alert("Only JPG and PNG are supported.");
        return;
    }
    if (file.size > MAX_BYTES) {
        alert(`File exceeds ${MAX_MB} MB limit.`);
        return;
    }
    if (objectURL) URL.revokeObjectURL(objectURL);

    objectURL = URL.createObjectURL(file);
    img.src = objectURL;
    img.alt = file.name;

    resetView();

    // Update UI
    document.body.classList.add("uploaded");
    document.querySelector(".upload-box").style.display = "none";
    document.querySelector(".scan-box").style.display = "grid";
    resultsWrapper.style.display = "block";
    resultsBox.style.display = "none";
    document.querySelector(".start-header .title-autograph").style.transform =
        "translateX(calc(-50vw + 150px))";

    // Persist
    sessionStorage.setItem("uploadedImage", objectURL);
    sessionStorage.setItem("uploadedName", file.name);
    sessionStorage.setItem("resultsVisible", "false");

    // Re-enable diagnose button on new upload
    diagnoseBtn.disabled = false;
    diagnoseBtn.classList.remove("disabled");
}