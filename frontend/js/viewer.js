// viewer.js
function updateTransform() {
    img.style.transform = `translate(${posX}px, ${posY}px) scale(${scale})`;
    img.style.filter = `brightness(${brightness}) contrast(${contrast})`;
}

function resetView() {
    scale = 1;
    posX = 0;
    posY = 0;
    brightness = 1;
    contrast = 1;
    updateTransform();
}