import json
import streamlit as st

try:
    from classifier import classify_po
except Exception:
    from classfiy import classify_po

try:
    from taxonomy import TAXONOMY
except Exception:
    TAXONOMY = None

st.set_page_config(page_title="PO Category Classifier", layout="wide", initial_sidebar_state="collapsed")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Code+Pro:wght@400;600&display=swap');
:root {
  --bg: #f6f2ea;
  --ink: #1f2937;
  --accent: #0ea5a5;
  --accent2: #f59e0b;
  --card: #ffffff;
  --muted: #6b7280;
  --border: #e5e7eb;
  --shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
}
.stApp {
  background: radial-gradient(1200px 600px at 10% 0%, #fff3dd 0%, var(--bg) 55%, #eef7f6 100%);
  color: var(--ink);
  font-family: 'Space Grotesk', sans-serif;
}
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; letter-spacing: -0.02em; }
.hero {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #ffffff 0%, #fff7e8 40%, #e8fbfb 100%);
  border: 1px solid var(--border);
  border-radius: 22px;
  padding: 1.6rem 1.8rem;
  box-shadow: var(--shadow);
}
.hero h1 { font-size: 2.2rem; margin: 0.2rem 0 0.3rem 0; }
.hero p { color: var(--muted); margin: 0; }
.badge {
  display: inline-block;
  background: #ecfeff;
  color: #0f766e;
  border: 1px solid #99f6e4;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(120px, 1fr));
  gap: 0.75rem;
}
.stat {
  background: #ffffff;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0.8rem;
  text-align: left;
}
.stat .k { font-size: 1.05rem; font-weight: 700; }
.stat .l { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }
textarea, input { border-radius: 14px !important; }
div[data-baseweb="textarea"] textarea {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.98rem;
}
div[data-baseweb="input"] input { font-family: 'Space Grotesk', sans-serif; }
.stButton > button {
  border-radius: 12px;
  padding: 0.55rem 1.1rem;
  font-weight: 600;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0ea5a5, #22c55e);
  border: none;
}
.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.12);
}
.result-box code, pre { font-family: 'Source Code Pro', monospace; }
.small-note { color: var(--muted); font-size: 0.85rem; }
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in { animation: fadeInUp 0.5s ease-out; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero fade-in">
  <div>
    <div class="badge">Procurement Intelligence</div>
    <h1>PO Category Classifier</h1>
    <p>Classify purchase-order descriptions into L1/L2/L3 taxonomy with structured output.</p>
  </div>
  <div class="stat-grid">
    <div class="stat">
      <div class="k">L1 / L2 / L3</div>
      <div class="l">taxonomy depth</div>
    </div>
    <div class="stat">
      <div class="k">JSON Ready</div>
      <div class="l">structured output</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

if "po_description" not in st.session_state:
    st.session_state.po_description = ""
if "supplier" not in st.session_state:
    st.session_state.supplier = ""
if "result_json" not in st.session_state:
    st.session_state.result_json = None
if "result_raw" not in st.session_state:
    st.session_state.result_raw = None
if "last_error" not in st.session_state:
    st.session_state.last_error = None
if "last_input" not in st.session_state:
    st.session_state.last_input = None

examples = [
    "Office janitorial service for HQ - monthly contract",
    "Annual software subscription for project management tool",
    "Employee training workshop on leadership",
    "Airfare for sales trip to Chicago",
    "New laptops and docking stations for engineering team",
]

st.write("")
left_col, right_col = st.columns([1.1, 1])

with left_col:
    st.markdown("### Input")
    st.caption("Provide a concise PO description and optional supplier to get a structured L1/L2/L3 classification.")

    example_choice = st.selectbox("Quick example", ["Select an example"] + examples, index=0)
    load_example = st.button("Load Example")
    if load_example and example_choice != "Select an example":
        st.session_state.po_description = example_choice

    with st.form("classifier_form", clear_on_submit=False):
        st.text_area("PO Description", height=160, key="po_description")
        st.text_input("Supplier (optional)", key="supplier")
        c1, c2, _ = st.columns([1, 1, 2])
        with c1:
            classify_clicked = st.form_submit_button("Classify", type="primary")
        with c2:
            clear_clicked = st.form_submit_button("Clear")

    if clear_clicked:
        st.session_state.po_description = ""
        st.session_state.supplier = ""
        st.session_state.result_json = None
        st.session_state.result_raw = None
        st.session_state.last_error = None
        st.session_state.last_input = None
        st.rerun()

    if classify_clicked:
        if not st.session_state.po_description.strip():
            st.warning("Please enter a PO Description")
        else:
            with st.spinner("Classifying..."):
                raw = classify_po(
                    st.session_state.po_description.strip(),
                    st.session_state.supplier.strip() or "Not provided",
                )
            st.session_state.result_raw = raw
            st.session_state.last_input = {
                "PO Description": st.session_state.po_description.strip(),
                "Supplier": st.session_state.supplier.strip() or "Not provided",
            }
            try:
                st.session_state.result_json = json.loads(raw)
                st.session_state.last_error = None
            except Exception:
                st.session_state.result_json = None
                st.session_state.last_error = "Invalid model response"

    st.write("")
    if TAXONOMY:
        with st.expander("Taxonomy Reference", expanded=False):
            st.code(TAXONOMY.strip(), language="text")

with right_col:
    st.markdown("### Results")
    if st.session_state.last_input:
        st.caption("Last request")
        st.json(st.session_state.last_input)

    if st.session_state.result_json:
        st.success("Parsed JSON ready")
    elif st.session_state.result_raw:
        st.warning("Raw response only (not valid JSON)")
    else:
        st.info("Run a classification to see results.")

    if st.session_state.result_raw:
        tabs = st.tabs(["Parsed JSON", "Raw Response"])
        with tabs[0]:
            if st.session_state.result_json:
                st.json(st.session_state.result_json)
            else:
                st.info("No JSON detected. See raw response.")
        with tabs[1]:
            st.code(st.session_state.result_raw, language="json")

    if st.session_state.last_error:
        st.error(st.session_state.last_error)

st.write("")
st.caption("Tip: Keep descriptions short and specific to get cleaner category mapping.")
