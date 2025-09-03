from fastapi import FastAPI
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(title="NeuroPathX Backend", version="0.1")


class MRI_Request(BaseModel):
    slice_path: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/mri_prediction")
def mri_prediction(request: MRI_Request):
    return {
        "class": "glioma",
        "confidence": 0.87,
        "note": "This is Dummy Data, model isn't plugget yet",
    }


@app.post("/mri_segmentation")
def mri_segmentation(request: MRI_Request):
    return {
        "mask_url": "https://dummy.com/mask.png",
        "dice_coefficient": 0.87,
        "note": "This is Dummy Data, model isn't plugget yet",
    }
