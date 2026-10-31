import html
from pathlib import Path

import pandas as pd
import streamlit as st

# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="Blue Economy × Lean Decision Support",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(__file__).with_name("Portal.xlsx")

# Replace these image URLs with your own research/project images if preferred.
IMAGES = {
    "home": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1800&q=85",
    "practice": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1400&q=85",
    "challenge": "https://images.unsplash.com/photo-1516937941344-00b4e0337589?auto=format&fit=crop&w=1400&q=85",
    "lean": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=1400&q=85",
}

# ------------------------------------------------------------
# CUSTOM STYLING
# ------------------------------------------------------------
st.markdown("""
<style>
    .block-container {
        max-width: 1280px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }
    .hero {
        padding: 2rem 2.1rem;
        border-radius: 20px;
        color: white;
        background: linear-gradient(115deg, rgba(5,38,58,.96), rgba(5,110,120,.82));
        margin-bottom: 1.2rem;
    }
    .hero h1 { color: white; font-size: 2.25rem; margin: 0 0 .5rem 0; }
    .hero p { color: #e6f7f7; font-size: 1.02rem; margin: 0; line-height: 1.55; }
    .eyebrow {
        color: #b7eeee; font-size: .76rem; font-weight: 800;
        letter-spacing: .13em; text-transform: uppercase; margin-bottom: .55rem;
    }
    .muted { color: #718096; font-size: .92rem; }
    .step-pill {
        display: inline-block; padding: .32rem .7rem; border-radius: 999px;
        background: rgba(8,145,178,.12); color: #0e7490;
        font-size: .76rem; font-weight: 800; letter-spacing: .04em;
    }
    .info-card {
        border: 1px solid rgba(100,116,139,.28);
        border-radius: 16px; padding: 1rem 1.1rem;
        background: rgba(148,163,184,.055);
        min-height: 120px;
    }
    .info-card h3 { font-size: 1.05rem; margin: .25rem 0 .45rem 0; }
    .info-card p { margin: 0; line-height: 1.45; }
    .challenge-card {
        border-left: 5px solid #e5a33b; border-radius: 12px;
        padding: 1rem 1.1rem; margin: .5rem 0 1rem 0;
        background: rgba(245,158,11,.08);
    }
    .lean-card {
        border-left: 5px solid #8b72c7; border-radius: 12px;
        padding: 1rem 1.1rem; margin: .5rem 0 1rem 0;
        background: rgba(139,114,199,.09);
    }
    div.stButton > button {
        width: 100%; border-radius: 13px; min-height: 3rem;
        white-space: normal; font-weight: 650;
    }
    div.stButton > button[kind="secondary"] {
        border: 1px solid rgba(100,116,139,.35);
    }
    [data-testid="stMetric"] {
        border: 1px solid rgba(100,116,139,.25);
        border-radius: 13px; padding: .8rem 1rem;
        background: rgba(148,163,184,.045);
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------
# LOAD AND NORMALISE EXCEL DATA
# Expected columns: Impact, Practice, Challenge, Lean P.
# ------------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    raw = pd.read_excel(path)
    raw.columns = [str(c).strip() for c in raw.columns]

    # Accept a few common alternative column headings.
    aliases = {
        "Impact": ["Impact", "Impacts", "Impact ID", "Impact Code"],
        "Practice": ["Practice", "Practices", "Blue Economy Practice", "BE Practice"],
        "Challenge": ["Challenge", "Challenges", "Implementation Challenge"],
        "Lean P.": ["Lean P.", "Lean Principle", "Lean Principles", "Lean"],
    }

    rename = {}
    for standard, candidates in aliases.items():
        match = next((c for c in candidates if c in raw.columns), None)
        if match:
            rename[match] = standard
    raw = raw.rename(columns=rename)

    required = ["Impact", "Practice", "Challenge", "Lean P."]
    missing = [c for c in required if c not in raw.columns]
    if missing:
        raise ValueError(
            "The Excel file is missing these required columns: "
            + ", ".join(missing)
            + ". Please use the headings: Impact, Practice, Challenge, Lean P."
        )

    # Optional descriptive columns are retained if present.
    optional_candidates = {
        "Impact Description": ["Impact Description", "Impact Name", "Impact Details"],
        "Practice Description": ["Practice Description", "Practice Name", "Practice Details"],
        "Challenge Description": ["Challenge Description", "Challenge Details"],
        "Lean Description": ["Lean Description", "Lean Principle Description"],
    }
    for standard, candidates in optional_candidates.items():
        match = next((c for c in candidates if c in raw.columns), None)
        if match and match != standard:
            raw = raw.rename(columns={match: standard})

    for col in required + [
        c for c in optional_candidates if c in raw.columns
    ]:
        raw[col] = raw[col].astype("string").str.strip()
        raw[col] = raw[col].replace("", pd.NA)

    return raw.dropna(subset=required).drop_duplicates().reset_index(drop=True)


if not DATA_FILE.exists():
    st.error("I cannot find Portal.xlsx. Please keep Portal.xlsx in the same GitHub repository folder as app.py.")
    st.stop()

try:
    data = load_data(str(DATA_FILE))
except Exception as error:
    st.error(f"Could not read the Excel dataset: {error}")
    st.stop()

if data.empty:
    st.warning("The Excel file does not contain complete impact–practice–challenge–Lean relationships.")
    st.stop()


# ------------------------------------------------------------
# SESSION STATE / NAVIGATION
# ------------------------------------------------------------
for key, default in {
    "page": "impacts",
    "impact": None,
    "practice": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def go_home():
    st.session_state.page = "impacts"
    st.session_state.impact = None
    st.session_state.practice = None


def go_practices(impact):
    st.session_state.impact = impact
    st.session_state.practice = None
    st.session_state.page = "practices"


def go_detail(practice):
    st.session_state.practice = practice
    st.session_state.page = "detail"


def safe(value):
    return html.escape(str(value))


def title_for(value, description_column, frame):
    """Use a descriptive name if an optional description column exists."""
    if description_column in frame.columns:
        values = frame.loc[frame.iloc[:, 0].notna(), description_column].dropna()
        if not values.empty:
            return str(values.iloc[0])
    return str(value)


# ------------------------------------------------------------
# COMMON HEADER / NAVIGATION
# ------------------------------------------------------------
st.markdown("""
<div class="hero">
  <div class="eyebrow">BLUE ECONOMY × LEAN CONSTRUCTION</div>
  <h1>Blue Economy Decision Support</h1>
  <p>Explore the impacts, identify relevant Blue Economy practices, and understand the implementation challenges and Lean principles connected to each practice.</p>
</div>
""", unsafe_allow_html=True)

# Progress indicator
steps = ["1  Impacts", "2  Practices", "3  Challenges & Lean"]
active = {"impacts": 0, "practices": 1, "detail": 2}[st.session_state.page]
progress_cols = st.columns(3)
for i, label in enumerate(steps):
    with progress_cols[i]:
        if i < active:
            st.success("✓ " + label)
        elif i == active:
            st.info("● " + label)
        else:
            st.caption("○ " + label)

st.markdown("")


# ------------------------------------------------------------
# SCREEN 1: SHOW ONLY IMPACTS
# ------------------------------------------------------------
if st.session_state.page == "impacts":
    st.markdown("## What impact do you want to address?")
    st.markdown(
        '<p class="muted">Choose an impact below. The related Blue Economy practices will appear on the next screen.</p>',
        unsafe_allow_html=True,
    )

    # A wide image introduces the subject; no practices/challenges are exposed here.
    st.image(IMAGES["home"], use_container_width=True)
    impacts = sorted(data["Impact"].dropna().unique().tolist())

    # Only impacts are selectable on this first screen.
    cols = st.columns(2)
    for index, impact in enumerate(impacts):
        impact_rows = data[data["Impact"] == impact]
        optional_desc = (
            impact_rows["Impact Description"].dropna().iloc[0]
            if "Impact Description" in impact_rows.columns
            and not impact_rows["Impact Description"].dropna().empty
            else None
        )
        label = str(optional_desc) if optional_desc else str(impact)
        with cols[index % 2]:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown(f'<span class="step-pill">IMPACT {index + 1:02d}</span>', unsafe_allow_html=True)
            st.markdown(f"### 🎯 {safe(label)}")
            if optional_desc and str(optional_desc) != str(impact):
                st.caption(f"Reference: {impact}")
            if st.button("Explore this impact  →", key=f"impact_{index}", type="secondary"):
                go_practices(impact)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")


# ------------------------------------------------------------
# SCREEN 2: PRACTICES FOR SELECTED IMPACT
# ------------------------------------------------------------
elif st.session_state.page == "practices":
    impact = st.session_state.impact
    subset = data[data["Impact"] == impact]

    left, right = st.columns([1, 5])
    with left:
        if st.button("← Back", key="back_to_impacts"):
            go_home()
            st.rerun()

    st.markdown(f"## Selected impact: {safe(impact)}")
    st.image(IMAGES["practice"], use_container_width=True)
    st.markdown("### Related Blue Economy practices")
    st.markdown(
        '<p class="muted">Select a practice to explore the challenges and Lean principles associated with it.</p>',
        unsafe_allow_html=True,
    )

    practices = sorted(subset["Practice"].dropna().unique().tolist())
    cols = st.columns(2)
    for index, practice in enumerate(practices):
        practice_rows = subset[subset["Practice"] == practice]
        challenge_count = practice_rows["Challenge"].nunique()
        lean_count = practice_rows["Lean P."].nunique()

        description = None
        if "Practice Description" in practice_rows.columns:
            vals = practice_rows["Practice Description"].dropna()
            if not vals.empty:
                description = str(vals.iloc[0])

        with cols[index % 2]:
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown('<span class="step-pill">BLUE ECONOMY PRACTICE</span>', unsafe_allow_html=True)
            st.markdown(f"### 🌱 {safe(practice)}")
            if description:
                st.write(description)
            st.caption(f"{challenge_count} challenge(s) · {lean_count} Lean principle(s)")
            if st.button("View challenges & Lean principles  →", key=f"practice_{index}"):
                go_detail(practice)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")


# ------------------------------------------------------------
# SCREEN 3: CHALLENGES AND LEAN PRINCIPLES FOR SELECTED PRACTICE
# ------------------------------------------------------------
elif st.session_state.page == "detail":
    impact = st.session_state.impact
    practice = st.session_state.practice
    subset = data[
        (data["Impact"] == impact) & (data["Practice"] == practice)
    ].copy()

    c1, c2 = st.columns([1, 1])
    with c1:
        if st.button("← Back to practices", key="back_to_practices"):
            st.session_state.page = "practices"
            st.session_state.practice = None
            st.rerun()
    with c2:
        if st.button("⌂ All impacts", key="back_to_home"):
            go_home()
            st.rerun()

    st.markdown(f"## {safe(practice)}")
    st.caption(f"Selected impact: {impact}")
    st.image(IMAGES["challenge"], use_container_width=True)

    st.markdown("### Implementation challenges and associated Lean principles")
    st.markdown(
        '<p class="muted">Each challenge is shown with the Lean principle or principles linked to it in your Excel dataset.</p>',
        unsafe_allow_html=True,
    )

    # Group only exact relationships. No new relationship is inferred.
    grouped = (
        subset.groupby("Challenge", sort=True)["Lean P."]
        .agg(lambda values: sorted(set(str(v) for v in values.dropna())))
        .reset_index()
    )

    for number, row in grouped.iterrows():
        challenge = str(row["Challenge"])
        principles = row["Lean P."]

        st.markdown(f"#### Challenge {number + 1}: {safe(challenge)}")
        col_challenge, col_arrow, col_lean = st.columns([1.05, 0.22, 1.05])

        with col_challenge:
            st.markdown(
                '<div class="challenge-card"><b>⚠️ IMPLEMENTATION CHALLENGE</b><br><br>'
                + safe(challenge) + "</div>",
                unsafe_allow_html=True,
            )
        with col_arrow:
            st.markdown(
                "<div style='text-align:center; padding-top:2.4rem; font-size:1.8rem;'>→</div>",
                unsafe_allow_html=True,
            )
        with col_lean:
            st.markdown('<div class="lean-card"><b>🧭 LEAN PRINCIPLE(S)</b><br><br>'
                        + "<br>".join("• " + safe(p) for p in principles)
                        + "</div>", unsafe_allow_html=True)

    st.image(IMAGES["lean"], caption="Lean thinking: improving value and reducing waste through better processes.", use_container_width=True)

    with st.expander("View the source relationship records from Excel"):
        st.dataframe(
            subset[["Impact", "Practice", "Challenge", "Lean P."]],
            use_container_width=True,
            hide_index=True,
        )


# ------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------
st.markdown("---")
st.caption(
    "Blue Economy × Lean Construction | Research decision-support prototype. "
    "All displayed relationships are taken from Portal.xlsx."
)
