# backend/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os
import logging

# Import classifier wrapper
from backend.models.classification import KerasClassifier

app = FastAPI(title="NeuroPathX Backend", version="0.1")
logger = logging.getLogger("uvicorn.error")

# Example PDF path (for demonstration/placeholder)
PDF_PATH = "docs/MRI_Report.pdf"

# CORS: allow your static site to call the API in dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev-friendly; tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the classifier once at startup
try:
    classifier = KerasClassifier()
    logger.info("Keras classifier loaded successfully.")
except Exception as e:
    classifier = None
    logger.error(f"Failed to initialize classifier: {e}")


# ------------------------
# PDF Endpoints
# ------------------------
@app.get("/report/preview")
async def preview_report():
    """Serve PDF inline so it opens in <iframe> or browser tab."""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(PDF_PATH, media_type="application/pdf")


@app.get("/report/download")
async def download_report():
    """Serve PDF as a download attachment."""
    if not os.path.exists(PDF_PATH):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(PDF_PATH, media_type="application/pdf", filename="MRI_Report.pdf")


# ------------------------
# Healthcheck
# ------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": classifier is not None}


# ------------------------
# Prediction Endpoint (classification)
# ------------------------
@app.post("/mri_prediction")
async def mri_prediction(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    contents = await file.read()
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        result = classifier.predict_from_bytes(contents)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed")
    # Frontend expects keys: class, confidence, note, all_classes
    return JSONResponse(content=result)


# ------------------------
# Segmentation endpoint (still placeholder)
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
