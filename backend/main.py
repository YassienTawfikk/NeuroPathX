from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI(title="NeuroPathX Backend", version="0.1")

# Example PDF path (later this will be dynamically generated)
PDF_PATH = "docs/MRI_Report.pdf"

# CORS: allow your static site (localhost / 63342) to call the API in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-friendly; tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------
# PDF Endpoints
# ------------------------
@app.get("/report/preview")
async def preview_report():
    """Serve PDF inline so it opens in <iframe> or browser tab."""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        PDF_PATH,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=MRI_Report.pdf"},
    )


@app.get("/report/download")
async def download_report():
    """Serve PDF as a download attachment."""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        PDF_PATH,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=MRI_Report.pdf"},
    )


# ------------------------
# Healthcheck
# ------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}


# ------------------------
# Prediction Endpoint
# ------------------------
@app.post("/mri_prediction")
async def mri_prediction(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    _ = await file.read()  # read bytes (not used yet; model comes later)
    return {
        "class": "glioma",
        "confidence": 0.87,
        "note": "Dummy data; model not plugged yet",
    }


# ------------------------
# Segmentation Endpoint
# ------------------------
@app.post("/mri_segmentation")
async def mri_segmentation(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    _ = await file.read()
    return {
        "mask_url": "https://dummy.com/mask.png",
        "dice_coefficient": 0.87,
        "note": "Dummy data; model not plugged yet",
    }
