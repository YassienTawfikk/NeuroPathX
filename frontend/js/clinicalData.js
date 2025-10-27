// frontend/js/clinicalData.js

/**
 * Maps model class labels to rich, clinical-friendly data for display.
 */
const ClinicalData = {
    // NOTE: These keys MUST match the CLASS_LABELS in backend/models/classification/config.py
    "Glioma Tumor": {
        title: "Suspected High-Grade Glioma",
        description: "The model indicates a high probability of a **Glioma**, a primary brain neoplasm arising from glial cells. Gliomas typically present with **irregular, enhancing borders** and surrounding vasogenic edema.",
        action: "Immediate neuro-oncology consult and consideration for surgical biopsy and definitive grading (e.g., GBM).",
        indicator: "★"
    },
    "Meningioma Tumor": {
        title: "Presumed Benign Meningioma",
        description: "High confidence in a **Meningioma**, a generally slow-growing tumor originating from the meninges. Key radiological features often include the characteristic **dural tail sign** and a broad base against the dura mater.",
        action: "Follow-up MRI surveillance is often recommended. Surgical planning based on tumor size and neurological impact.",
        indicator: "✓"
    },
    "Pituitary Tumor": {
        title: "Pituitary Adenoma / Sellar Mass",
        description: "The classification points to a **Pituitary Adenoma**, a mass in the sella turcica. Evaluation is critical for **optic chiasm compression** and hormonal activity (e.g., prolactin, ACTH).",
        action: "Endocrinology and neurosurgery consultations required for hormonal analysis and management (pharmacological or surgical).",
        indicator: "⧈"
    },
    "No Tumor": {
        title: "Non-Pathological Scan Result",
        description: "No definitive primary brain tumor evidence was detected by the model. The scan is **radiologically unremarkable** for the targeted tumor types. Result does not exclude other pathologies or metastatic disease.",
        action: "Continue routine patient care. Repeat imaging as clinically indicated or if symptoms progress.",
        indicator: "●"
    }
};

// Fallback for unexpected or missing labels
const DefaultClinicalData = {
    title: "Analysis Complete",
    description: "Prediction received but clinical details are missing for this class. Please consult the model documentation.",
    action: "Data validation error.",
    indicator: "!"
};

export {ClinicalData, DefaultClinicalData};