---
title: NeuroPathX Backend
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# NeuroPathX

![App Design Overview](https://github.com/user-attachments/assets/d55cddc4-67d7-4443-9b0a-83968fdc7baa)

---

## 🌐 Live Demo

> <a href="https://neuropathx.vercel.app" target="_blank" rel="noopener noreferrer">NeuroPathX</a>

---

## Model Overview

* **Architecture:** Xception
* **Classes:** Glioma, Meningioma, Pituitary, No Tumor
* **Accuracy:** 92%

| Class      | Precision | Recall | F1-Score |
| ---------- | --------- | ------ | -------- |
| Glioma     | 0.93      | 0.91   | 0.92     |
| Meningioma | 0.86      | 0.79   | 0.83     |
| No Tumor   | 0.94      | 0.97   | 0.95     |
| Pituitary  | 0.92      | 0.99   | 0.95     |

---

## Visual Insights

The following visuals illustrate how NeuroPathX processes and interprets MRI brain scans:

1. **Model Architecture Overview**

   <img height="800" alt="model_architecture" src="https://github.com/user-attachments/assets/bee7786d-2bd9-48af-8649-46bfef6c0831"/>

   A visual breakdown of the Xception network used for tumor classification.

2. **Confusion Matrix**

   <img width="800" height="600" alt="confusion_matrix" src="https://github.com/user-attachments/assets/2f263e94-8a03-4d2d-92e8-bad291b8663d" />

   Depicts the prediction performance across all tumor classes, highlighting classification accuracy and error distribution.

3. **Automated Clinical Report Template**

   NeuroPathX automatically generates structured diagnostic PDFs summarizing each scan analysis. Example output:

   <img width="681" height="923" alt="Screenshot 2025-10-27 at 7 40 11 PM" src="https://github.com/user-attachments/assets/fd112888-f9d6-4ad3-833d-c04f37085f55" />

---

## Run the Project

**Frontend:**

```
cd frontend
python -m http.server 3000 &
open http://localhost:3000
```

**Backend:**

```
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Dependencies

```
pip install -r requirements.txt
```

Main libraries: TensorFlow, FastAPI, NumPy, scikit-learn, Pillow

---

## Structure

```
/
├── backend/
│   └── main.py
├── frontend/
│   └── index.html
├── notebooks/
│   └── xception-for-brain-mri-tumor-classification.ipynb
├── reports/
│   └── training_metrics_plot.png
├── test/
│   └── classification_samples/
│       ├── giloma_tumor/
│       ├── healthy_control/
│       ├── meningioma_tumor/
│       └── pituitary_tumor/
└── requirements.txt
```

> The test/ directory includes sample brain MRI images for validating the model’s predictions and testing the inference pipeline end-to-end.

---

### Author

<div>
  <table align="center">
    <tr>
      <td align="center">
        <a href="https://github.com/YassienTawfikk" target="_blank">
          <img src="https://avatars.githubusercontent.com/u/126521373?v=4" width="120px;" alt="Yassien Tawfik"/><br/>
          <sub><b>Yassien Tawfik</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>
