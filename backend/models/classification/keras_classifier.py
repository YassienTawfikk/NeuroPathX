import io
import os
from pathlib import Path
from typing import Dict, Any, Tuple
import base64  # <-- NEW IMPORT for Grad-CAM
import cv2  # <-- NEW IMPORT for Grad-CAM image processing
from matplotlib import cm  # <-- NEW IMPORT for Grad-CAM color map

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
            import keras
            from keras.models import load_model
            from keras.layers import Flatten

            # --- MONKEY PATCH: Fix for Keras 3 "Flatten received list" error ---
            # The saved model seems to pass a list [tensor] to Flatten, which Keras 3 rejects.
            # We patch compute_output_spec to unwrap the list if encountered.
            if not hasattr(Flatten, "_original_compute_output_spec"):
                Flatten._original_compute_output_spec = Flatten.compute_output_spec

                def _patched_compute_output_spec(self, inputs, **kwargs):
                    # Unwrap list if it contains a single tensor
                    if isinstance(inputs, list) and len(inputs) == 1:
                        inputs = inputs[0]
                    return self._original_compute_output_spec(inputs, **kwargs)

                Flatten.compute_output_spec = _patched_compute_output_spec

                # AND patch the 'call' method itself (runtime execution)
                if not hasattr(Flatten, "_original_call"):
                    Flatten._original_call = Flatten.call
                    
                    def _patched_call(self, inputs, *args, **kwargs):
                        if isinstance(inputs, list) and len(inputs) == 1:
                            inputs = inputs[0]
                        return self._original_call(inputs, *args, **kwargs)
                    
                    Flatten.call = _patched_call

                logger.info("Monkey-patched keras.layers.Flatten (output_spec & call) to handle list inputs.")
            # -------------------------------------------------------------------

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at: {self.model_path}")

            # Ensure Keras/TF knows where to load the model
            self._model = load_model(self.model_path, compile=False)
            self._loaded = True
            logger.info("Keras model loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load Keras model")
            raise

    # <--- NEW GRAD-CAM METHOD START --->
    def _get_gradcam_heatmap(self, preprocessed_input, last_conv_layer_name, pred_index=None) -> np.ndarray:
        """Generates the Grad-CAM heatmap."""
        import tensorflow as tf

        # 1. Create a model that maps the input image to the activations of the last
        #    convolutional layer and the final prediction output.
        grad_model = tf.keras.models.Model(
            self._model.inputs,
            [self._model.get_layer(last_conv_layer_name).output, self._model.output]
        )

        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(preprocessed_input)

            # If no specific index is passed (e.g., to explain the predicted class)
            if pred_index is None:
                pred_index = tf.argmax(preds[0])

            # 2. Get the score of the predicted class
            class_channel = preds[:, pred_index]

        # 3. Compute the gradient of the predicted class score with respect to
        #    the output feature map of the last convolutional layer.
        grads = tape.gradient(class_channel, last_conv_layer_output)

        # 4. Compute the 'Global Average Pooling' (or Mean) of the gradients
        #    over the spatial dimensions (H, W) to get the 'weights'
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

        # Ensure outputs are NumPy arrays
        last_conv_layer_output = last_conv_layer_output[0].numpy()
        pooled_grads = pooled_grads.numpy()

        # 5. Multiply each channel in the feature map array by the importance
        #    weight (the average gradient) for that channel.
        for i in range(pooled_grads.shape[-1]):
            last_conv_layer_output[:, :, i] *= pooled_grads[i]

        # 6. Average the weighted feature map across all channels and normalize.
        heatmap = np.mean(last_conv_layer_output, axis=-1)
        # Apply ReLU to get only positive influence (Max is used for normalization)
        heatmap = np.maximum(heatmap, 0) / np.max(heatmap)

        return heatmap

    def predict_with_gradcam(self, file_bytes: bytes) -> Dict[str, Any]:
        """
        Runs prediction and generates the Grad-CAM heatmap, returning results
        and the heatmap as a Base64-encoded JPEG image string.
        """
        # 1. Prediction and Preprocessing
        self._load_model()

        # We need the original image for the overlay later
        img_original = Image.open(io.BytesIO(file_bytes)).convert("RGB")

        # Get preprocessed array (1, H, W, C)
        x = self._preprocess(img_original)

        # Predict to get the class index
        preds = self._model.predict(x, verbose=0)
        top_idx = int(np.argmax(np.squeeze(preds)))

        # Get standard prediction results using the existing method (or copy logic)
        results = self.predict_from_bytes(file_bytes)

        try:
            # 2. Grad-CAM Generation
            # --- IMPORTANT: Find the name of your last Conv layer! ---
            # A common name for Xception is 'block14_sepconv2_act'. Check your model summary!
            LAST_CONV_LAYER_NAME = "xception" # This might be the name of the nested functional model if wrapping

            # Try to handle potential nested model naming issues or find the real last layer
            # For now, we attempt with the provided name, but catch errors safely.
            heatmap = self._get_gradcam_heatmap(x, LAST_CONV_LAYER_NAME, pred_index=top_idx)
            
            # 3. Overlay and Encoding
            # Resize heatmap to match original image size for overlay
            heatmap_resized = cv2.resize(heatmap, (img_original.width, img_original.height))
    
            # Convert heatmap array to a colored image (using jet colormap)
            cmap = cm.get_cmap("jet")
            # Get RGB channels and convert to 0-255 range
            heatmap_colored = cmap(heatmap_resized)[:, :, :3]
            heatmap_colored = (heatmap_colored * 255).astype(np.uint8)
    
            # Convert PIL image to OpenCV BGR format (needed for weighted overlay)
            img_cv2 = cv2.cvtColor(np.array(img_original), cv2.COLOR_RGB2BGR)
    
            # Create a weighted overlay (0.6 for MRI image, 0.4 for heatmap)
            overlay = cv2.addWeighted(img_cv2, 0.6, heatmap_colored, 0.4, 0)
    
            # 4. Encode the result (original + overlay) to Base64 JPEG
            # Encode as JPEG bytes
            _, buffer = cv2.imencode('.jpeg', overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            # Convert bytes to Base64 string for JSON transport
            gradcam_b64 = base64.b64encode(buffer).decode("utf-8")
    
            results["gradcam_b64"] = gradcam_b64
            results["note"] += " | Grad-CAM heatmap included."
            
        except Exception as e:
            logger.error(f"Grad-CAM generation failed: {e}")
            results["gradcam_b64"] = ""
            results["note"] += " | Grad-CAM skipped due to error."
            # We purposely do NOT raise here, so the user at least gets the text prediction.

        return results

        # 3. Overlay and Encoding
        # Resize heatmap to match original image size for overlay
        heatmap_resized = cv2.resize(heatmap, (img_original.width, img_original.height))

        # Convert heatmap array to a colored image (using jet colormap)
        cmap = cm.get_cmap("jet")
        # Get RGB channels and convert to 0-255 range
        heatmap_colored = cmap(heatmap_resized)[:, :, :3]
        heatmap_colored = (heatmap_colored * 255).astype(np.uint8)

        # Convert PIL image to OpenCV BGR format (needed for weighted overlay)
        img_cv2 = cv2.cvtColor(np.array(img_original), cv2.COLOR_RGB2BGR)

        # Create a weighted overlay (0.6 for MRI image, 0.4 for heatmap)
        overlay = cv2.addWeighted(img_cv2, 0.6, heatmap_colored, 0.4, 0)

        # 4. Encode the result (original + overlay) to Base64 JPEG
        # Encode as JPEG bytes
        _, buffer = cv2.imencode('.jpeg', overlay, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        # Convert bytes to Base64 string for JSON transport
        gradcam_b64 = base64.b64encode(buffer).decode("utf-8")

        results["gradcam_b64"] = gradcam_b64
        results["note"] += " | Grad-CAM heatmap included."
        return results

    # <--- NEW GRAD-CAM METHOD END --->

    def _preprocess(self, pil_image: Image.Image) -> Any:
        # ... existing _preprocess method (keep as is) ...
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
        # ... existing predict_from_bytes method (keep as is) ...
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

    def get_preprocessed_image_bytes(self, file_bytes: bytes) -> bytes:
        """
        Loads the image from bytes, preprocesses it (resize/convert to RGB),
        and returns the resulting PIL image as JPEG bytes for display in the report.
        """
        # Validate and open image
        try:
            # Note: We convert to RGB immediately, which is crucial for consistency.
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        except Exception as e:
            # Raise a specific ValueError if the image cannot be opened
            raise ValueError(f"Unable to open or process image for visualization: {e}") from e

        # 1. Apply the preprocessing steps (resize/convert)
        # We only need the PIL image output, resized to the model's required dimensions.
        pil_image = img.resize((self.image_size, self.image_size)).convert("RGB")

        # 2. Save the PIL image to a buffer as JPEG
        output_buffer = io.BytesIO()
        # Save as JPEG with high quality to minimize visual artifacts in the PDF
        pil_image.save(output_buffer, format="JPEG", quality=95)
        output_buffer.seek(0)

        # 3. Return the raw bytes
        return output_buffer.read()
