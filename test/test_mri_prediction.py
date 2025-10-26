import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data

@pytest.mark.skipif(not os.path.exists("classify-model/brain_tumor_xception_model.keras"), reason="Model artifact not present")
def test_predict_with_sample_image():
    # Add a small sample image at tests/fixtures/sample.jpg to run this test
    with open("tests/fixtures/sample.jpg", "rb") as f:
        r = client.post("/mri_prediction", files={"file": ("sample.jpg", f, "image/jpeg")})
    assert r.status_code == 200
    data = r.json()
    assert "class" in data and "confidence" in data
    assert isinstance(data["confidence"], float)