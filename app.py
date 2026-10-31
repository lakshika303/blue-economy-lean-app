import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Blue Economy × Lean | Decision Support",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path(__file__).with_name("Portal.xlsx")

st.markdown("""
<style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px;}
    .hero {
        padding: 1.5rem 1.7rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #0b3954 0%, #087e8b 62%, #38a3a5 100%);
        color: white;
        margin-bottom: 1.25rem;
    }
    .hero h1 {color: white; font-size: 2.05rem; margin: 0 0 .45rem 0;}
    .hero p {color: #e9fbff; font-size: 1rem; margin: 0; line-height: 1.5;}
    .section-label {
        font-size: .78rem; font-weight: 700; letter-spacing: .08em;
        text-transform: uppercase; color: #64748b; margin-bottom: .35rem;
    }
    .result-card {
        border: 1px solid rgba(128, 145, 164, .30);
        border-radius: 14px; padding: 1rem 1.05rem;
        min-height: 125px; background: rgba(128, 145, 164, .045);
    }
    .result-card h3 {font-size: 1rem; margin: .3rem 0 .55rem 0;}
    .result-card p {margin: 0; font-size: .96rem; line-height: 1.45;}
    .path-step {
        border-radius: 12px; padding: .85rem 1rem; margin-bottom: .4rem;
        border: 1px solid rgba(128,145,164,.25);
    }
    .small-muted {font-size: .84rem; opacity: .75;}
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,145,164,.25);
        padding: .8rem 1rem; border-radius: 12px;
        background: rgba(128,145,164,.04);
    }
    [data-testid="stSidebar"] {border-right: 1px solid rgba(128,145,164,.2);}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data(file_path):
    data = pd.read_excel(file_path)
    data.columns = [str(c).strip() for c in data.columns]
    required = ["Impact", "Practice", "Challenge", "Lean P."]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(
            "Missing required Excel columns: " + ", ".join(missing)
            + ". Expected columns: Impact, Practice, Challenge, Lean P."
        )
    data = data[required].copy()
    for col in required:
        data[col] = data[col].astype("string").str.strip()
        data[col] = data[col].replace("", pd.NA)
    return data.dropna(subset=required).drop_duplicates().reset_index(drop=True)


try:
    df = load_data(DATA_FILE)
except Exception as exc:
    st.error(f"Unable to load Portal.xlsx: {exc}")
    st.info("Make sure Portal.xlsx is in the same repository folder as app.py.")
    st.stop()

if df.empty:
    st.warning("No complete relationship records were found in Portal.xlsx.")
    st.stop()

# Header
st.markdown("""
<div class="hero">
  <div style="font-size:.8rem; font-weight:700; letter-spacing:.12em; margin-bottom:.55rem;">
    BLUE ECONOMY &nbsp;×&nbsp; LEAN CONSTRUCTION
  </div>
  <h1>Decision Support Platform</h1>
  <p>Explore how impacts connect to mitigation practices, implementation challenges, and relevant Lean principles.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## Explore the framework")
    st.caption("Start with an impact. The options below will update to show only related findings.")
    impact_options = sorted(df["Impact"].unique().tolist())
    selected_impact = st.selectbox("1 · Select an impact", impact_options)
    impact_df = df[df["Impact"] == selected_impact].copy()
    practice_options = sorted(impact_df["Practice"].unique().tolist())
    selected_practice = st.selectbox(
        "2 · Select a practice",
        ["All related practices"] + practice_options,
    )
    if selected_practice != "All related practices":
        filtered_df = impact_df[impact_df["Practice"] == selected_practice].copy()
    else:
        filtered_df = impact_df.copy()

    st.divider()
    st.markdown("**About this tool**")
    st.caption("This application presents relationships recorded in the research dataset. It does not generate or validate new relationships.")

# Summary metrics
st.markdown(f"### Selected impact: `{selected_impact}`")
m1, m2, m3 = st.columns(3)
m1.metric("Related practices", filtered_df["Practice"].nunique())
m2.metric("Implementation challenges", filtered_df["Challenge"].nunique())
m3.metric("Lean principles", filtered_df["Lean P."].nunique())

st.markdown("---")
st.markdown("### Explore the mitigation pathway")
st.caption("Choose a challenge to see its linked practice or practices and associated Lean principle(s).")

challenge_options = sorted(filtered_df["Challenge"].unique().tolist())
if not challenge_options:
    st.info("No linked challenges are available for this selection.")
    st.stop()

selected_challenge = st.selectbox("3 · Select an implementation challenge", challenge_options)
challenge_df = filtered_df[filtered_df["Challenge"] == selected_challenge].copy()
linked_practices = sorted(challenge_df["Practice"].unique().tolist())
linked_principles = sorted(challenge_df["Lean P."].unique().tolist())

# Four connected visual cards
c1, c2, c3, c4 = st.columns([1, .22, 1, 1.15])
with c1:
    st.markdown('<div class="result-card" style="border-top:4px solid #1783a5;">'
                '<div class="section-label">01 · Impact</div>'
                f'<h3>{selected_impact}</h3>'
                '<p class="small-muted">Selected issue to mitigate</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown("<div style='text-align:center; padding-top:3.1rem; font-size:1.4rem;'>→</div>", unsafe_allow_html=True)
with c3:
    practice_text = "<br>".join("• " + str(x) for x in linked_practices)
    st.markdown('<div class="result-card" style="border-top:4px solid #299764;">'
                '<div class="section-label">02 · Practice</div>'
                f'<p>{practice_text}</p></div>', unsafe_allow_html=True)
with c4:
    challenge_text = str(selected_challenge)
    st.markdown('<div class="result-card" style="border-top:4px solid #d9912b;">'
                '<div class="section-label">03 · Challenge</div>'
                f'<h3>{challenge_text}</h3></div>', unsafe_allow_html=True)

st.markdown("")
st.markdown("#### 04 · Associated Lean principles")
principle_cols = st.columns(min(3, max(1, len(linked_principles))))
for i, principle in enumerate(linked_principles):
    with principle_cols[i % len(principle_cols)]:
        st.markdown(
            '<div class="result-card" style="border-top:4px solid #8064b5; min-height:90px;">'
            f'<div class="section-label">Lean principle</div><h3>{principle}</h3></div>',
            unsafe_allow_html=True
        )

st.markdown("---")
with st.expander("View the underlying relationship records"):
    st.caption("These rows are taken directly from your Excel dataset.")
    st.dataframe(
        filtered_df.rename(columns={
            "Impact": "Impact code",
            "Practice": "Blue Economy practice",
            "Challenge": "Implementation challenge",
            "Lean P.": "Lean principle",
        }),
        use_container_width=True,
        hide_index=True,
    )

st.markdown(
    '<p class="small-muted" style="text-align:center; padding-top:1rem;">'
    'Blue Economy × Lean Construction · Research decision-support prototype</p>',
    unsafe_allow_html=True
)
