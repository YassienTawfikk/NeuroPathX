import io
import os
from pathlib import Path
from typing import Dict, Any

from PIL import Image
import numpy as np
import logging

# --- CRITICAL CHANGE: Direct Import of Local Config ---
# We now import configuration variables directly from the new config.py in the same package
try:
    from .config import IMAGE_SIZE, MODEL_PATH, CLASS_LABELS
except ImportError:
    # Define fallback defaults if config is missing (for robust startup)
    IMAGE_SIZE = 299
    MODEL_PATH = "artifacts/classification/brain_tumor_xception_model.keras"  # Assume new location
    CLASS_LABELS = ["glioma", "meningioma", "notumor", "pituitary"]
    logging.warning("Failed to import config.py. Using hardcoded defaults.")
# ------------------------------------------------------

logger = logging.getLogger(__name__)


def _resolve_model_path(relative_path: str) -> str:
    """
    Resolves the model path relative to the project root.
    It walks up from the current file until it finds the project root marker (e.g., README.md).
    """
    # Strategy: locate the repo root by walking up from this file's location
    current = Path(__file__).resolve()
    repo_root = current
    # Search up to 6 levels for the project root (NeuroPathX/)
    for _ in range(6):
        if (repo_root / "README.md").exists() or (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent

    # Resolve the path relative to the found repo root
    absolute_path = (repo_root / relative_path).resolve()

    return str(absolute_path)


class KerasClassifier:
    def __init__(self, model_path: str = None, image_size: int = None, class_labels=None, device: str = None):
        # Use imported constants as defaults
        self.image_size = image_size or IMAGE_SIZE
        self.class_labels = class_labels or CLASS_LABELS

        # Resolve path: use the user-provided path or the path from config.py
        effective_model_path = model_path or MODEL_PATH
        self.model_path = _resolve_model_path(effective_model_path)

        self._model = None
        self._loaded = False
        logger.info(f"KerasClassifier initialized. Will load model from: {self.model_path}")

    def _load_model(self):
        """Loads the Keras model lazily."""
        if self._loaded:
            return
        try:
            # We delay the TF import to allow the class to be instantiated without TF being installed
            import tensorflow as tf
            from tensorflow.keras.models import load_model

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")

            # Ensure Keras/TF knows where to load the model
            self._model = load_model(self.model_path, compile=False)
            self._loaded = True
            logger.info("Keras model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load Keras model")
            raise

    def _preprocess(self, pil_image: Image.Image) -> Any:
        """
        Applies the exact preprocessing used in the notebook: resize, convert to
        array, cast to float32, and rescale pixels to the [0, 1] range.
        """
        try:
            from tensorflow.keras.preprocessing.image import img_to_array
        except Exception as e:
            raise RuntimeError("TensorFlow/Keras is required for preprocessing. Install tensorflow.") from e

        # Ensure RGB
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Resize to target size
        pil_image = pil_image.resize((self.image_size, self.image_size))

        # Convert to array (HWC)
        arr = img_to_array(pil_image)

        # ***CRITICAL FIX: Explicitly cast to float32 to match Keras generator output***
        arr = arr.astype(np.float32)

        # Rescale to [0, 1] (rescale=1./255 from notebook)
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

        # Apply Softmax if needed (this should ideally be handled by the model's output)
        if probs.ndim > 0 and (probs.min() < 0 or probs.max() > 1):
            e = np.exp(probs - np.max(probs))
            probs = e / e.sum()

        # Handle single class case (if model had only one output)
        if probs.ndim == 0:
            probs = np.array([probs])

        # Get the top prediction
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
            "note": "Prediction successful with fixed preprocessing. Ensure model file is correct.",
            "all_classes": full_results
        }
