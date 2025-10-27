import os
import pytest
from pathlib import Path  # Recommended for robust path handling
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

# Define project-relative paths based on the new structure
MODEL_PATH = Path("artifacts/classification/brain_tumor_xception_model.keras")
# Using the new standardized demo sample image
SAMPLE_IMAGE_PATH = Path("data/demo_samples/classification/glioma/NPX-001.jpg")


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data


@pytest.mark.skipif(
    not MODEL_PATH.exists(),
    reason=f"Model artifact not present at {MODEL_PATH.as_posix()}"
)
def test_predict_with_sample_image():
    # Check if the demo sample exists before running the test
    if not SAMPLE_IMAGE_PATH.exists():
        pytest.skip(f"Demo image not found at {SAMPLE_IMAGE_PATH.as_posix()}.")

    # Use the demo sample path for the test
    with open(SAMPLE_IMAGE_PATH, "rb") as f:
        # Pass the file object with its clean, new name
        r = client.post("/mri_prediction", files={"file": ("NPX-001.jpg", f, "image/jpeg")})

    assert r.status_code == 200
    data = r.json()
    assert "class" in data and "confidence" in data
    assert isinstance(data["confidence"], float)
