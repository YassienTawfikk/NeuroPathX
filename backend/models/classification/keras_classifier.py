import io
import os
import sys
from pathlib import Path
from typing import Dict, Any

from PIL import Image
import numpy as np
import importlib.util
import logging

logger = logging.getLogger(__name__)


def _load_classify_model_config() -> Dict[str, Any]:
    """
    Try several strategies to load the config from the repo's classify-model/config.py
    Returns a dict with keys: IMAGE_SIZE, MODEL_PATH, CLASS_LABELS
    """
    # Defaults
    defaults = {
        "IMAGE_SIZE": 299,
        "MODEL_PATH": os.path.join("classify-model", "brain_tumor_xception_model.keras"),
        "CLASS_LABELS": ["glioma", "meningioma", "notumor", "pituitary"],
    }

    # Strategy: locate the repo root (assume this file is at backend/models/classification/)
    current = Path(__file__).resolve()
    repo_root = current
    for _ in range(6):
        if (repo_root / "README.md").exists() or (repo_root / ".git").exists():
            break
        repo_root = repo_root.parent

    config_path = repo_root / "classify-model" / "config.py"
    if not config_path.exists():
        # Try alternative: repo_root/classify_model/config.py
        alt = repo_root / "classify_model" / "config.py"
        if alt.exists():
            config_path = alt

    if not config_path.exists():
        logger.warning(f"Config file not found at expected locations. Using defaults: {defaults}")
        return defaults

    try:
        spec = importlib.util.spec_from_file_location("classify_model_config", str(config_path))
        module = importlib.util.module_from_spec(spec)
        loader = spec.loader
        assert loader is not None
        loader.exec_module(module)
        IMAGE_SIZE = getattr(module, "IMAGE_SIZE", defaults["IMAGE_SIZE"])
        MODEL_PATH = getattr(module, "MODEL_PATH", defaults["MODEL_PATH"])
        CLASS_LABELS = getattr(module, "CLASS_LABELS", defaults["CLASS_LABELS"])
        # If MODEL_PATH is relative, make it repo-root relative
        MODEL_PATH = str((repo_root / MODEL_PATH).resolve()) if not os.path.isabs(MODEL_PATH) else MODEL_PATH
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
        self.device = device or os.environ.get("MODEL_DEVICE", None)
        self._model = None
        # Defer heavy imports / load until needed
        self._loaded = False

    def _load_model(self):
        """Load the Keras model. Import TensorFlow lazily to avoid heavy import at module load time."""
        if self._loaded:
            return
        try:
            import tensorflow as tf  # local import
            from tensorflow.keras.models import load_model
            # Allow both single-file .keras/.h5 or SavedModel dir
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")
            # load_model may raise useful errors if model is incompatible
            self._model = load_model(self.model_path, compile=False)
            self._loaded = True
            logger.info("Keras model loaded from %s", self.model_path)
        except Exception as e:
            logger.exception("Failed to load Keras model")
            raise

    def _preprocess(self, pil_image: Image.Image) -> Any:
        # Lazily import Keras preprocessing
        try:
            from tensorflow.keras.preprocessing.image import img_to_array
            # NOTE: We DO NOT import Xception's preprocess_input.
            # We must use simple rescaling (0-1) as seen in the training notebook.
        except Exception as e:
            raise RuntimeError("TensorFlow/Keras is required for image preprocessing. Install tensorflow.") from e

        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Resize the image
        pil_image = pil_image.resize((self.image_size, self.image_size))

        # Convert to array (HWC)
        arr = img_to_array(pil_image)

        # Normalize/Rescale to [0, 1] (as per the training notebook: img_input / 255.0)
        arr = arr / 255.0

        # Expand dimensions (1,H,W,C)
        arr = np.expand_dims(arr, axis=0)

        return arr

    def predict_from_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Accept raw image bytes and return the top prediction and all class probabilities.
        """
        # Validate and open image
        try:
            img = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            raise ValueError(f"Unable to open image: {e}") from e

        # Ensure model is loaded (this will raise with a clear message if TF/model missing)
        self._load_model()

        x = self._preprocess(img)

        # Predict
        try:
            # Setting verbose=0 to match the notebook's prediction style
            preds = self._model.predict(x, verbose=0)
        except Exception as e:
            logger.exception("Model prediction failed")
            raise RuntimeError("Model prediction failed") from e

        # Normalize and process predictions
        probs = np.squeeze(preds)

        # If the model didn't use softmax in the final layer, apply it here
        if probs.ndim > 0 and (probs.min() < 0 or probs.max() > 1):
            e = np.exp(probs - np.max(probs))
            probs = e / e.sum()

        # Handle single class case (rare for this model)
        if probs.ndim == 0:
            probs = np.array([probs])

        # Get the top prediction
        top_idx = int(np.argmax(probs))
        top_confidence = float(probs[top_idx])
        top_label = self.class_labels[top_idx] if top_idx < len(self.class_labels) else str(top_idx)

        # Build the list of all class results for the frontend
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
            "note": "Predicted by Xception classifier",
            "all_classes": full_results
        }
