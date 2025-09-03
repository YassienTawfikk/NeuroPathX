import streamlit as st
import requests

st.title("NeuroPathX")

uploaded_file = st.file_uploader("Upload MRI slice", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    if st.button("Classify Tumor"):
        # Send dummy request to backend
        response = requests.post(
            "http://127.0.0.1:8000/mri_prediction",
            json={"slice_path": "dummy_path"}
        )
        st.json(response.json())
