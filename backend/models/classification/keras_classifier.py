# backend/models/classification/keras_classifier.py

import io
import os
from pathlib import Path
from typing import Dict, Any

from PIL import Image
import numpy as np
import importlib.util
import logging

logger = logging.getLogger(__name__)


def _load_classify_model_config() -> Dict[str, Any]:
    """
    Dynamically loads the configuration from classify-model/config.py, 
    allowing model details (like IMAGE_SIZE and CLASS_LABELS) to be defined centrally.
    """
    # Defaults
    defaults = {
        "IMAGE_SIZE": 299,
        "MODEL_PATH": os.path.join("classify-model", "brain_tumor_xception_model.keras"),
        "CLASS_LABELS": ["glioma", "meningioma", "notumor", "pituitary"],
    }

    # Strategy: locate the repo root by walking up from this file's location
    current = Path(__file__).resolve()
    repo_root = current
    for _ in range(6):
        if (repo_root / "README.md").exists() or (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent

    config_path = repo_root / "classify-model" / "config.py"

    if not config_path.exists():
        logger.warning(f"Config file not found. Using defaults: {defaults}")
        return defaults

    try:
        spec = importlib.util.spec_from_file_location("classify_model_config", str(config_path))
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)

        # Load values from config.py module
        IMAGE_SIZE = getattr(module, "IMAGE_SIZE", defaults["IMAGE_SIZE"])
        MODEL_PATH = getattr(module, "MODEL_PATH", defaults["MODEL_PATH"])
        CLASS_LABELS = getattr(module, "CLASS_LABELS", defaults["CLASS_LABELS"])

        # Resolve MODEL_PATH relative to repo root
        if not os.path.isabs(MODEL_PATH):
            # Assumes MODEL_PATH is defined relative to the classify-model directory
            MODEL_PATH = str((repo_root / "classify-model" / MODEL_PATH).resolve())

        return {"IMAGE_SIZE": IMAGE_SIZE, "MODEL_PATH": MODEL_PATH, "CLASS_LABELS": CLASS_LABELS}
    except Exception as e:
        logger.exception("Failed to load classify-model config; falling back to defaults.")
        return defaults


class KerasClassifier:
    def __init__(self, model_path: str = None, image_size: int = None, class_labels=None, device: str = None):
        config = _load_classify_model_config()
        self.model_path = model_path or config["MODEL_PATH"]
        self.image_size = image_size or config["IMAGE_SIZE"]
        self.class_labels = class_labels or config["CLASS_LABELS"]
        self._model = None
        self._loaded = False

    def _load_model(self):
        """Loads the Keras model lazily."""
        if self._loaded:
            return
        try:
            import tensorflow as tf
            from tensorflow.keras.models import load_model

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")

            self._model = load_model(self.model_path, compile=False)
            self._loaded = True
            logger.info("Keras model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load Keras model")
            raise

    def _preprocess(self, pil_image: Image.Image) -> Any:
        """
        Applies the exact preprocessing used in the notebook: resize, convert to 
        array, and rescale pixels to the [0, 1] range.
        """
        try:
            from tensorflow.keras.preprocessing.image import img_to_array
        except Exception as e:
            raise RuntimeError("TensorFlow/Keras is required for preprocessing. Install tensorflow.") from e

        # Ensure RGB
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Resize to 299x299
        pil_image = pil_image.resize((self.image_size, self.image_size))

        # Convert to array (HWC)
        arr = img_to_array(pil_image)

        # CRITICAL FIX: Rescale to [0, 1] (rescale=1./255 from notebook)
        arr = arr / 255.0

        # Add batch dimension (1,H,W,C)
        arr = np.expand_dims(arr, axis=0)

        return arr

    def predict_from_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Accept raw image bytes, run prediction, and return structured results 
        including all class probabilities for front-end analysis.
        """
        # Validate and open image
        try:
            img = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Unable to open image: {e}") from e

        self._load_model()
        x = self._preprocess(img)

        # Predict
        try:
            # verbose=0 matches notebook single-image prediction style
            preds = self._model.predict(x, verbose=0)
        except Exception as e:
            logger.exception("Model prediction failed")
            raise RuntimeError("Model prediction failed") from e

        # Process predictions
        probs = np.squeeze(preds)

        # Apply Softmax if needed (though the model uses 'softmax' activation)
        if probs.ndim > 0 and (probs.min() < 0 or probs.max() > 1):
            e = np.exp(probs - np.max(probs))
            probs = e / e.sum()

        if probs.ndim == 0:
            probs = np.array([probs])

        # Find the top prediction
        top_idx = int(np.argmax(probs))
        top_confidence = float(probs[top_idx])
        top_label = self.class_labels[top_idx] if top_idx < len(self.class_labels) else str(top_idx)

        # Build list of all classes and probabilities
        full_results = []
        for i, label in enumerate(self.class_labels):
            if i < len(probs):
                full_results.append({
                    "label": label,
                    "confidence": float(probs[i]),
                })

        # Return the comprehensive result dictionary
        return {
            "class": top_label,
            "confidence": top_confidence,
            "note": "Prediction successful with notebook-aligned preprocessing.",
            "all_classes": full_results
        }
