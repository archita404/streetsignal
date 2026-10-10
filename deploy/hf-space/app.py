import json
import os

import ollama
import streamlit as st

MODEL_NAME = "qwen2.5vl:3b"
VALID_SEVERITIES = ["Low", "Medium", "High"]

# Where analysis runs: on the user's machine ("local") or inside this app's
# own Docker container when deployed, e.g. to a Hugging Face Space ("space"),
# or a temporary cloud demo session such as Colab ("cloud").
HOST_MODE = os.environ.get("STREET_SIGNAL_HOST_MODE", "local")
if HOST_MODE == "space":
    LOCAL_BADGE = "No third-party AI APIs"
    LOCAL_NOTE = (
        "Photos are analyzed by a locally-run Ollama model inside this app's "
        "own container — never sent to any third-party AI API."
    )
elif HOST_MODE == "cloud":
    LOCAL_BADGE = "No third-party AI APIs"
    LOCAL_NOTE = (
        "Photos are analyzed by a locally-run Ollama model inside this "
        "demo session's own server — never sent to any third-party AI API."
    )
else:
    LOCAL_BADGE = "Runs 100% on your machine"
    LOCAL_NOTE = (
        "Photos are analyzed on this machine only, by your local Ollama "
        "model — never uploaded anywhere."
    )

# Status colors from a validated accessible palette. A color never carries
# meaning alone: each is paired with a dot and a text label.
SEVERITY_STATUS = {
    "Low": "#0ca30c",  # good
    "Medium": "#fab219",  # warning
    "High": "#d03b3b",  # critical
}

REPORT_KEYS = (
    "report_category",
    "report_observations",
    "report_severity",
    "report_uncertainty",
)

st.set_page_config(
    page_title="StreetSignal",
    page_icon="🌱",
    layout="centered",
)

# Cosmetic only: rounded photo previews.
st.markdown(
    """<style>
      [data-testid="stImage"] img {border-radius: 12px;}
    </style>""",
    unsafe_allow_html=True,
)


def severity_pill(severity):
    """An inline colored dot + label, so severity never rests on color alone."""
    color = SEVERITY_STATUS.get(severity, "#898781")
    return (
        f'<span style="display:inline-flex;align-items:center;gap:0.45rem;'
        f'padding:0.15rem 0.7rem;border-radius:999px;background:{color}1f;'
        f'border:1px solid {color}55;font-weight:600;font-size:0.85rem;">'
        f'<span style="width:8px;height:8px;border-radius:50%;'
        f'background:{color};"></span>{severity}</span>'
    )


def on_report_download():
    st.toast(
        "Report saved to your downloads. It has not been sent to anyone.",
        icon="📄",
    )


st.title("🌱 StreetSignal")
st.caption("Local AI for community issue reporting")

badge_col_1, badge_col_2 = st.columns(2, gap="small")
with badge_col_1:
    st.badge(LOCAL_BADGE, icon=":material/shield:", color="green")
with badge_col_2:
    st.badge("Human review required", icon=":material/visibility:", color="blue")

st.write(
    "Upload a photo of a civic issue — a pothole, garbage, a broken streetlight, "
    "waterlogging — and a locally-run AI drafts an editable report. Nothing is "
    "submitted anywhere without your review."
)

st.subheader("Step 1 · Capture the issue")

with st.container(border=True):
    uploaded_file = st.file_uploader(
        "Photo of the civic issue",
        type=["jpg", "jpeg", "png"],
        help=LOCAL_NOTE + " JPG or PNG.",
    )

    preview_col, controls_col = st.columns([1.1, 1], vertical_alignment="top")

    with preview_col:
        if uploaded_file is not None:
            st.image(
                uploaded_file,
                width="stretch",
                caption="Analyzed locally — never uploaded.",
                alt="Uploaded photo of a possible civic issue",
            )
        else:
            st.markdown(
                '<div style="border:1.5px dashed rgba(11,11,11,0.16);'
                "border-radius:12px;padding:2.2rem 1rem;text-align:center;"
                'color:#898781;font-size:0.9rem;">'
                "Your photo preview will appear here</div>",
                unsafe_allow_html=True,
            )

    with controls_col:
        location = st.text_input(
            "Approximate location (optional)",
            placeholder="e.g. Near the local bus stop",
            help="A landmark in words is enough — no exact coordinates needed.",
        )
        if HOST_MODE in ("space", "cloud"):
            st.caption(
                "Running on this demo's own CPU — analysis can take a "
                "minute or two."
            )
        analyze_clicked = st.button(
            "Analyze photo",
            type="primary",
            width="stretch",
            disabled=uploaded_file is None,
            help=(
                "Upload a photo to enable analysis"
                if uploaded_file is None
                else "Ask the locally-run AI model for a draft report"
            ),
        )

    if analyze_clicked:
        with st.status(
            "Analyzing with your local AI model…", expanded=True
        ) as status:
            try:
                response = ollama.chat(
                    model=MODEL_NAME,
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
                # Fresh widgets for the new draft, so a re-analysis replaces
                # the previous AI values instead of keeping stale text.
                for key in REPORT_KEYS:
                    st.session_state.pop(key, None)

                status.update(
                    label="Draft ready — review it in Step 2",
                    state="complete",
                    expanded=False,
                )
                st.toast("Analysis complete", icon="✅")

            except json.JSONDecodeError:
                status.update(
                    label="The AI returned an invalid response", state="error"
                )
                st.error(
                    "The AI returned an invalid JSON response. "
                    "Please try analyzing the photo again."
                )

            except Exception as error:
                status.update(label="Analysis failed", state="error")
                st.error(f"Analysis failed: {error}")
                st.info(
                    f"Make sure Ollama is running and the model "
                    f"'{MODEL_NAME}' is installed."
                )

has_analysis = "analysis" in st.session_state

st.subheader("Step 2 · Review the AI's draft")

if not has_analysis:
    with st.container(border=True):
        st.caption(
            "Analyze a photo in Step 1 and the AI's editable draft will appear "
            "here. Nothing is final until you download the report."
        )
else:
    with st.container(border=True):
        result = st.session_state["analysis"]

        st.caption(
            "AI observations may be inaccurate — check every field and edit freely."
        )

        suggested_severity = result.get("severity", "Medium")
        if suggested_severity not in VALID_SEVERITIES:
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
            VALID_SEVERITIES,
            index=VALID_SEVERITIES.index(suggested_severity),
            key="report_severity",
            help="The AI's suggestion is preselected — correct it if needed.",
        )

        uncertainty = st.text_area(
            "What is uncertain?",
            value=str(result.get("uncertainty", "")),
            height=80,
            key="report_uncertainty",
        )

st.subheader("Step 3 · Export your report")

if not has_analysis:
    with st.container(border=True):
        st.caption(
            "Your final, human-reviewed report will appear here once a photo "
            "has been analyzed."
        )
else:
    with st.container(border=True):
        category_col, severity_col, location_col = st.columns(3)

        category_col.markdown("**Category**")
        category_col.write(category or "Not specified")
        severity_col.markdown("**Severity**")
        severity_col.markdown(severity_pill(severity), unsafe_allow_html=True)
        location_col.markdown("**Approximate location**")
        location_col.write(location or "Not provided")

        st.markdown("**Visible observations**")
        st.write(observations.strip() or "No observations provided.")

        st.markdown("**Uncertainty**")
        st.write(uncertainty.strip() or "No additional uncertainty provided.")

        st.info(
            "This report is AI-assisted and has not been submitted to any "
            "authority. You choose what happens to it."
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
            width="stretch",
            on_click=on_report_download,
        )

st.divider()
st.caption(
    "StreetSignal · Reports leave this app only when you download them."
)
