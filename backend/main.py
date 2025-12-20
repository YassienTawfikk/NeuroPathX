from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import logging
import io
from datetime import datetime
import base64  # <--- CRITICAL FIX: Base64 is required for image encoding

# Import classifier wrapper and new generator
from backend.models.classification import KerasClassifier
from backend.models.report.report_generator import generate_pdf_report

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

# --- Temporary/Shared Cache for Prediction Result ---
# CRITICAL: In a real app, this should be Redis/DB. For this project, a global dict is fine.
LATEST_PREDICTION_CACHE = {}


# ---------------------------------------------------


# ------------------------
# PDF Endpoints (UPDATED TO BE DYNAMIC)
# ------------------------
@app.get("/report/preview")
async def preview_report(session_id: str = "latest"):
    """Generates and serves the dynamic PDF report."""

    # Retrieve the last prediction result from the cache
    cached_result = LATEST_PREDICTION_CACHE.get(session_id)

    if not cached_result:
        raise HTTPException(status_code=404, detail="No recent prediction found for report generation.")

    try:
        pdf_bytes = generate_pdf_report(cached_result)
    except Exception as e:
        logger.exception(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=NeuroPathX_Report_{session_id}.pdf"
        }
    )


@app.get("/report/download")
async def download_report(session_id: str = "latest"):
    """Generates and serves the dynamic PDF report as an attachment."""

    cached_result = LATEST_PREDICTION_CACHE.get(session_id)

    if not cached_result:
        raise HTTPException(status_code=404, detail="No recent prediction found for report generation.")

    try:
        pdf_bytes = generate_pdf_report(cached_result)
    except Exception as e:
        logger.exception(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF report.")

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=NeuroPathX_Report_{session_id}.pdf"
        }
    )


# ------------------------
# Healthcheck
# ------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": classifier is not None}


@app.get("/")
def read_root():
    return {"message": "NeuroPathX Backend is running", "docs": "/docs"}


# ------------------------
# Prediction Endpoint (classification) - FULLY UPDATED FOR REPORT DATA
# ------------------------
@app.post("/mri_prediction")
async def mri_prediction(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    contents = await file.read()
    if classifier is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # 1. Run prediction and generate Grad-CAM
        # (Assumes predict_with_gradcam is now implemented in KerasClassifier)
        result = classifier.predict_with_gradcam(contents)

        # 2. Get the Preprocessed Image for the Report (Requires new KerasClassifier method)
        preprocessed_bytes = classifier.get_preprocessed_image_bytes(contents)
        result["preprocessed_b64"] = base64.b64encode(preprocessed_bytes).decode("utf-8")

        # 3. Add necessary context for the report and cache
        session_id = "latest"  # Hardcoded session ID for simplicity
        result["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result["session_id"] = session_id

        # Store the full result in the cache
        LATEST_PREDICTION_CACHE[session_id] = result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail="Prediction failed")

    # Frontend expects keys: class, confidence, note, all_classes, gradcam_b64, preprocessed_b64
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
