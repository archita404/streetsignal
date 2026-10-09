import json

import ollama
import streamlit as st

st.set_page_config(
    page_title="StreetSignal",
    page_icon="🌱",
    layout="centered",
)

st.title("🌱 StreetSignal")
st.subheader("Local AI for community issue reporting")

st.write(
    "Upload a photo of a civic issue. Review the AI's observations "
    "and prepare a report. Nothing is automatically submitted."
)

st.info(
    "Your photo is analyzed using your local Ollama model. "
    "AI observations may be inaccurate and should be reviewed."
)

uploaded_file = st.file_uploader(
    "Upload a photo of a civic issue",
    type=["jpg", "jpeg", "png"],
)

location = st.text_input(
    "Approximate location (optional)",
    placeholder="e.g. Near the local bus stop",
)

if uploaded_file is not None:
    st.image(
        uploaded_file,
        caption="Uploaded photo",
        width="stretch",
    )

if st.button("Analyze photo", type="primary"):
    with st.spinner("Analyzing with your local AI model..."):
        try:
            response = ollama.chat(
                model="qwen2.5vl:3b",
                messages=[
                    {
                        "role": "user",
                        "content": (
                            "Analyze this image for a possible civic issue. "
                            "Only report visible evidence. Do not invent "
                            "details, causes, exact locations, or people. "
                            "Return a JSON object with these keys: "
                            "category (string), observations (string), "
                            "severity (Low, Medium, or High), and "
                            "uncertainty (string). Use cautious language "
                            "and explain what cannot be determined from "
                            "the image."
                        ),
                        "images": [uploaded_file.getvalue()],
                    }
                ],
                format="json",
            )

            result = json.loads(response["message"]["content"])

            st.session_state["analysis"] = result
            st.session_state["source_image_name"] = uploaded_file.name

        except json.JSONDecodeError:
            st.error(
                "The AI returned an invalid JSON response. "
                "Please try analyzing the photo again."
            )

        except Exception as error:
            st.error(f"Analysis failed: {error}")
            st.info(
                "Make sure Ollama is running and the model "
                "'qwen2.5vl:3b' is installed."
            )

result = {}
if "analysis" in st.session_state:
    result = st.session_state["analysis"]

st.divider()
st.subheader("Review AI observations")

st.caption(
    "Check every field carefully. You can edit the AI's suggestions "
    "before downloading your report."
)

valid_severities = ["Low", "Medium", "High"]
suggested_severity = result.get("severity", "Medium")

if suggested_severity not in valid_severities:
    suggested_severity = "Medium"

category = st.text_input(
    "Issue category",
    value=str(result.get("category", "Needs review")),
    key="report_category",
)

observations = st.text_area(
    "Visible observations",
    value=str(result.get("observations", "")),
    height=120,
    key="report_observations",
)

severity = st.selectbox(
    "Severity",
    valid_severities,
    index=valid_severities.index(suggested_severity),
    key="report_severity",
)

uncertainty = st.text_area(
    "What is uncertain?",
    value=str(result.get("uncertainty", "")),
    height=80,
    key="report_uncertainty",
)

st.subheader("📋 Report preview")

st.markdown(f"**Category:** {category or 'Not specified'}")
st.markdown(f"**Severity:** {severity}")
st.markdown(f"**Approximate location:** {location or 'Not provided'}")

st.markdown("**Visible observations**")
st.write(observations or "No observations provided.")

st.markdown("**Uncertainty**")
st.write(uncertainty or "No additional uncertainty provided.")

st.warning(
    "This report is AI-assisted and requires human review. "
    "It has not been submitted to any authority."
)

report = {
    "project": "StreetSignal",
    "category": category.strip(),
    "observations": observations.strip(),
    "severity": severity,
    "uncertainty": uncertainty.strip(),
    "approximate_location": location.strip(),
    "source_image": st.session_state.get("source_image_name", ""),
    "requires_human_review": True,
    "submitted_to_authority": False,
}

st.download_button(
    label="Download report as JSON",
    data=json.dumps(report, indent=2, ensure_ascii=False),
    file_name="streetsignal_report.json",
    mime="application/json",
    type="primary",
)

