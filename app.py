import streamlit as st
import pandas as pd
from pathlib import Path
import html

st.set_page_config(
    page_title="Blue Economy × Lean Decision Support",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_FILE = Path(__file__).with_name("Portal.xlsx")

st.markdown("""
<style>
.block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {
    background: linear-gradient(120deg, #0b3954 0%, #087e8b 65%, #38a3a5 100%);
    border-radius: 18px; padding: 1.7rem 1.8rem; color: white; margin-bottom: 1.5rem;
}
.hero h1 {color: white; margin: 0 0 .45rem 0; font-size: 2.1rem;}
.hero p {color: #e9fbff; margin: 0; font-size: 1rem; line-height: 1.55;}
.eyebrow {font-size: .76rem; font-weight: 750; letter-spacing: .13em; margin-bottom: .6rem;}
.impact-note {color: #64748b; font-size: .95rem; margin-bottom: 1.2rem;}
div.stButton > button {
    width: 100%; min-height: 94px; white-space: normal; text-align: left;
    border-radius: 14px; border: 1px solid rgba(100,116,139,.35);
    padding: 1rem 1.1rem; font-size: 1.05rem; font-weight: 650;
}
div.stButton > button:hover {border-color: #159a9c; color: #159a9c;}
.practice-card {
    border: 1px solid rgba(100,116,139,.30); border-radius: 14px;
    padding: 1rem 1.1rem; margin-bottom: .5rem;
    background: rgba(128,145,164,.045);
}
.tag {font-size: .75rem; font-weight: 750; letter-spacing: .07em; text-transform: uppercase; color: #64748b;}
.challenge {
    border-left: 4px solid #d9912b; border-radius: 8px;
    padding: .8rem 1rem; margin: .5rem 0;
    background: rgba(217,145,43,.08);
}
.lean {
    border-left: 4px solid #8064b5; border-radius: 8px;
    padding: .8rem 1rem; margin: .5rem 0;
    background: rgba(128,100,181,.08);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(path):
    data = pd.read_excel(path)
    data.columns = [str(c).strip() for c in data.columns]
    required = ["Impact", "Practice", "Challenge", "Lean P."]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Portal.xlsx must contain columns: Impact, Practice, Challenge, Lean P.")
    data = data[required].copy()
    for col in required:
        data[col] = data[col].astype("string").str.strip().replace("", pd.NA)
    return data.dropna(subset=required).drop_duplicates().reset_index(drop=True)

try:
    df = load_data(DATA_FILE)
except Exception as exc:
    st.error(f"Could not load Portal.xlsx: {exc}")
    st.stop()

if df.empty:
    st.warning("No complete relationships were found in Portal.xlsx.")
    st.stop()

# Navigation state: landing -> selected impact -> selected practice detail
if "selected_impact" not in st.session_state:
    st.session_state.selected_impact = None
if "selected_practice" not in st.session_state:
    st.session_state.selected_practice = None

def reset_home():
    st.session_state.selected_impact = None
    st.session_state.selected_practice = None

def show_impacts():
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">BLUE ECONOMY × LEAN CONSTRUCTION</div>
      <h1>Decision Support Platform</h1>
      <p>Select an impact to explore the Blue Economy practices that may mitigate it, the challenges linked to those practices, and the associated Lean principles.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## Select an impact")
    st.markdown('<div class="impact-note">Choose one of the impacts below to view its related practices.</div>', unsafe_allow_html=True)
    impacts = sorted(df["Impact"].unique().tolist())
    # Show only impacts on the landing page.
    cols = st.columns(2)
    for i, impact in enumerate(impacts):
        with cols[i % 2]:
            n_practices = df.loc[df["Impact"] == impact, "Practice"].nunique()
            if st.button(f"🎯  {impact}\n\nExplore {n_practices} related practice(s)  →", key=f"impact_{impact}"):
                st.session_state.selected_impact = impact
                st.session_state.selected_practice = None
                st.rerun()

def show_practices(impact):
    top_left, top_right = st.columns([1, 5])
    with top_left:
        if st.button("← All impacts", key="back_impacts"):
            reset_home()
            st.rerun()
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">SELECTED IMPACT</div>
      <h1>{html.escape(str(impact))}</h1>
      <p>Explore the practices associated with this impact. Select a practice to see its challenges and linked Lean principles.</p>
    </div>
    """, unsafe_allow_html=True)
    subset = df[df["Impact"] == impact]
    practices = sorted(subset["Practice"].unique().tolist())
    st.markdown("## Related Blue Economy practices")
    cols = st.columns(2)
    for i, practice in enumerate(practices):
        p_df = subset[subset["Practice"] == practice]
        n_challenges = p_df["Challenge"].nunique()
        n_lean = p_df["Lean P."].nunique()
        with cols[i % 2]:
            st.markdown('<div class="practice-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="tag">BLUE ECONOMY PRACTICE</div><h3>{html.escape(str(practice))}</h3><p>{n_challenges} linked challenge(s) · {n_lean} Lean principle(s)</p>', unsafe_allow_html=True)
            if st.button(f"Explore {practice}  →", key=f"practice_{impact}_{practice}"):
                st.session_state.selected_practice = practice
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def show_practice_detail(impact, practice):
    a, b = st.columns([1, 1])
    with a:
        if st.button("← Back to practices", key="back_practices"):
            st.session_state.selected_practice = None
            st.rerun()
    with b:
        if st.button("⌂ All impacts", key="back_home_detail"):
            reset_home()
            st.rerun()

    subset = df[(df["Impact"] == impact) & (df["Practice"] == practice)]
    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">IMPACT: {html.escape(str(impact))}</div>
      <h1>{html.escape(str(practice))}</h1>
      <p>Review the implementation challenges associated with this practice and the Lean principles linked to each challenge in the research dataset.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Implementation challenges and Lean principles")
    # Preserve the exact row-level relationships; group principles for repeated challenge entries.
    grouped = subset.groupby("Challenge", sort=True)["Lean P."].agg(
        lambda values: sorted(set(str(v) for v in values))
    ).reset_index()

    for _, row in grouped.iterrows():
        challenge = str(row["Challenge"])
        principles = row["Lean P."]
        left, right = st.columns([1.15, 1])
        with left:
            st.markdown('<div class="challenge"><div class="tag">IMPLEMENTATION CHALLENGE</div>'
                        f'<h4>{html.escape(challenge)}</h4></div>', unsafe_allow_html=True)
        with right:
            st.markdown('<div class="lean"><div class="tag">ASSOCIATED LEAN PRINCIPLES</div>'
                        + "".join(f"<p>• {html.escape(p)}</p>" for p in principles)
                        + "</div>", unsafe_allow_html=True)

    with st.expander("View the underlying research records"):
        st.dataframe(
            subset.rename(columns={
                "Impact": "Impact",
                "Practice": "Blue Economy practice",
                "Challenge": "Implementation challenge",
                "Lean P.": "Lean principle",
            }),
            use_container_width=True,
            hide_index=True,
        )

if st.session_state.selected_impact is None:
    show_impacts()
elif st.session_state.selected_practice is None:
    show_practices(st.session_state.selected_impact)
else:
    show_practice_detail(st.session_state.selected_impact, st.session_state.selected_practice)

st.markdown("---")
st.caption("Research decision-support prototype · Displays relationships recorded in Portal.xlsx; it does not invent new relationships.")
