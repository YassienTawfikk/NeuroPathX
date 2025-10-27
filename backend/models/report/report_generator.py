import io
import base64
import json
from pathlib import Path
from fpdf import FPDF
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


# --- Configuration Loading ---
def _load_config(filename):
    """Loads a configuration dictionary from the external JSON file."""
    try:
        current_dir = Path(__file__).parent
        json_path = current_dir / filename
        with open(json_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        # Fallback for robustness
        print(f"ERROR: Failed to load configuration file '{filename}': {e}")
        return {}


CLINICAL_DATA = _load_config("clinical_data_config.json")
THEME = _load_config("report_theme.json")


# -----------------------------


def _create_probability_chart(result: dict, predicted_class: str) -> io.BytesIO:
    """Generates a Matplotlib bar chart of class probabilities."""
    labels = [item['label'] for item in result['all_classes']]
    probs = [item['confidence'] for item in result['all_classes']]

    # Define colors, highlighting the predicted class
    colors = [
        CLINICAL_DATA.get(l, {'color': '#AAAAAA'})['color']
        if l == predicted_class else '#DDDDDD'
        for l in labels
    ]

    fig, ax = plt.subplots(figsize=(6, 2.5))
    y_pos = np.arange(len(labels))
    ax.barh(y_pos, probs, color=colors)
    ax.set_yticks(y_pos)
    # Use theme font sizes
    ax.set_yticklabels(labels, fontsize=THEME.get("FONT_BODY_SIZE", 10) * 0.8)
    ax.invert_yaxis()  # Labels read top-to-bottom
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.tick_params(axis='x', labelsize=THEME.get("FONT_BODY_SIZE", 10) * 0.8)

    # Add confidence text next to bars
    for i, prob in enumerate(probs):
        ax.text(prob + 0.01, i, f'{prob * 100:.2f}%', va='center', fontsize=7, color='black' if prob < 0.9 else 'white',
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='none') if prob < 0.9 else None)

    ax.set_title("Model Output Scores", fontsize=THEME.get("FONT_BODY_SIZE", 10))
    plt.tight_layout(pad=0.5)

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=200)
    plt.close(fig)
    chart_buffer.seek(0)
    return chart_buffer


def generate_pdf_report(result: dict) -> bytes:
    """Generates a dynamic, professional clinical PDF report."""

    pdf = FPDF(orientation='P', unit='mm', format=THEME.get("PAPER_SIZE", "A4"))
    MARGIN = THEME.get("MARGIN_MM", 15)

    pdf.set_auto_page_break(auto=True, margin=MARGIN)
    pdf.add_page()

    # --- Data Extraction ---
    predicted_class = result.get('class', 'Unknown')
    confidence = result.get('confidence', 0.0)

    # Retrieve clinical data and safely handle missing keys
    clinical_data = CLINICAL_DATA.get(predicted_class, {
        'title': 'Unknown Result',
        'description_prefix': 'Cannot retrieve clinical details for this prediction.',
        'color': '#AAAAAA',
        'rec_text': 'Further manual analysis required.'
    })

    # --- Header (Professional Look) ---
    HEADER_COLOR = THEME.get("COLOR_HEADER_BG", [32, 150, 243])
    HEADER_HEIGHT = THEME.get("HEADER_HEIGHT_MM", 25)

    pdf.set_fill_color(*HEADER_COLOR)
    pdf.rect(0, 0, 210, HEADER_HEIGHT, 'F')

    pdf.set_font("Arial", "B", THEME.get("FONT_TITLE_SIZE", 18))
    pdf.set_text_color(*THEME.get("COLOR_HEADER_TEXT", [255, 255, 255]))
    pdf.cell(0, 10, "NeuroPathX AI Diagnostic Report", border=0, ln=1, align='C')

    pdf.set_font("Arial", "", THEME.get("FONT_BODY_SIZE", 10))
    pdf.set_text_color(*THEME.get("COLOR_SECONDARY_GRAY", [200, 200, 200]))
    pdf.cell(0, 5, "Powered by Yassien Tawfik's Biomedical AI Pipeline", border=0, ln=1, align='C')
    pdf.ln(10)

    pdf.set_text_color(*THEME.get("COLOR_TEXT_DEFAULT", [0, 0, 0]))
    pdf.set_left_margin(MARGIN)
    pdf.set_right_margin(MARGIN)

    # --- 1. Primary Diagnosis Summary (Section 1) ---
    pdf.set_font("Arial", "B", THEME.get("FONT_SECTION_SIZE", 14))
    pdf.cell(0, 8, f"1. PRIMARY DIAGNOSIS: {clinical_data['title']}", border='B', ln=1, fill=False)

    pdf.set_font("Arial", "", THEME.get("FONT_SUBTITLE_SIZE", 12))
    pdf.ln(2)
    pdf.set_text_color(*THEME.get("COLOR_PRIMARY_BLUE", [32, 150, 243]))
    pdf.cell(50, 6, "CONFIDENCE LEVEL:", border=0)
    pdf.set_text_color(*THEME.get("COLOR_TEXT_DEFAULT", [0, 0, 0]))
    pdf.set_font("Arial", "B", THEME.get("FONT_SECTION_SIZE", 14))
    pdf.cell(0, 6, f"{confidence * 100:.2f}%", ln=1)

    # --- 2. Quantitative Analysis (Section 2) ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", THEME.get("FONT_SECTION_SIZE", 14))
    pdf.cell(0, 8, "2. QUANTITATIVE ANALYSIS", border='B', ln=1)
    pdf.ln(2)

    # Generate and add the Bar Chart
    try:
        chart_buffer = _create_probability_chart(result, predicted_class)
        pdf.image(chart_buffer, x=MARGIN + 5, w=170)
    except Exception as e:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, f"Error generating chart: {e}", ln=1)
        pdf.set_text_color(*THEME.get("COLOR_TEXT_DEFAULT", [0, 0, 0]))

    # --- 3. Visual Evidence (Section 3) ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", THEME.get("FONT_SECTION_SIZE", 14))
    pdf.cell(0, 8, "3. VISUAL EVIDENCE: PREPROCESSED MRI", border='B', ln=1)
    pdf.ln(2)

    # --- Preprocessed Image ---
    if result.get('preprocessed_b64'):
        try:
            IMAGE_WIDTH = THEME.get("IMAGE_WIDTH_MM", 80)
            IMAGE_PADDING = THEME.get("IMAGE_PADDING_MM", 5)
            image_y_start = pdf.get_y()

            pdf.set_font("Arial", "B", THEME.get("FONT_BODY_SIZE", 10))
            pdf.cell(0, 5, "Model Input (Resized & Normalized)", border=0, ln=1)
            pdf.ln(1)

            preprocessed_bytes = base64.b64decode(result['preprocessed_b64'])
            with io.BytesIO(preprocessed_bytes) as buffer:
                pdf.image(buffer, x=MARGIN + 5, w=IMAGE_WIDTH)

            # CRITICAL FIX: Manually advance the Y position past the image's height.
            pdf.set_y(image_y_start + IMAGE_WIDTH + IMAGE_PADDING)

        except Exception as e:
            pdf.cell(0, 5, f"Error rendering preprocessed image: {e}", border=0, ln=1)
            pdf.ln(5)
    else:
        pdf.cell(0, 5, "Preprocessed image data not available.", border=0, ln=1)
        pdf.ln(5)

    # --- 4. Clinical Context & Recommendation (Section 4) ---
    pdf.ln(5)
    pdf.set_font("Arial", "B", THEME.get("FONT_SECTION_SIZE", 14))
    pdf.cell(0, 8, "4. CLINICAL CONTEXT & RECOMMENDATION", border='B', ln=1)
    pdf.ln(2)

    # Detailed Description
    pdf.set_font("Arial", "B", THEME.get("FONT_SUBTITLE_SIZE", 11))
    pdf.cell(0, 7, f"Interpretation ({predicted_class}):", ln=1)
    pdf.set_font("Arial", "", THEME.get("FONT_BODY_SIZE", 10))

    # Placeholder text from shared data
    full_description = clinical_data['description_prefix'] + (
        " This result must be correlated with clinical history and other imaging modalities."
    )
    pdf.multi_cell(0, 5, full_description)

    # Recommendation
    pdf.ln(3)
    pdf.set_font("Arial", "B", THEME.get("FONT_SUBTITLE_SIZE", 11))
    color_hex = clinical_data['color']
    pdf.set_text_color(int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16))
    pdf.cell(0, 7, "Action Recommended:", ln=1)
    pdf.set_text_color(*THEME.get("COLOR_TEXT_DEFAULT", [0, 0, 0]))
    pdf.set_font("Arial", "", THEME.get("FONT_BODY_SIZE", 10))

    # Use the specific recommendation text from the CLINICAL_DATA mapping
    rec_text = clinical_data['rec_text']
    pdf.multi_cell(0, 5, rec_text)

    # --- Footer ---
    pdf.set_y(270)
    pdf.set_font("Arial", "I", THEME.get("FONT_FOOTER_SIZE", 8))
    pdf.cell(0, 5, f"Report Generated by NeuroPathX AI on {result.get('timestamp', 'N/A')}. Case ID: {result.get('session_id', 'N/A')}", border='T', ln=1, align='C')

    return pdf.output(dest='B')
