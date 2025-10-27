# Image size used during training (299x299 for Xception)
IMAGE_SIZE = 299

# This assumes the model file is moved to the artifacts/classification folder.
MODEL_PATH = "artifacts/classification/brain_tumor_xception_model.keras"

# Class labels in the order determined by the Keras generator during training.
CLASS_LABELS = ["glioma", "meningioma", "notumor", "pituitary"]
