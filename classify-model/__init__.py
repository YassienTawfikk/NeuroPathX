# classify-model/__init__.py

from .predictor import BrainTumorPredictor

# Optional: Define what is available when someone uses 'from classify_model import *'
__all__ = [
    "BrainTumorPredictor"
]
