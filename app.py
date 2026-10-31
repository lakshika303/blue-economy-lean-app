import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Blue Economy–Lean Decision Support",
    page_icon="🌊",
    layout="wide",
)

st.title("🌊 Blue Economy–Lean Decision Support")
st.caption("Explore the links between impacts, Blue Economy practices, implementation challenges, and Lean principles.")

DATA_FILE = Path(__file__).with_name("Portal.xlsx")

@st.cache_data
def load_data(file_path):
    data = pd.read_excel(file_path)
    # Normalise column names, including accidental leading/trailing spaces.
    data.columns = [str(c).strip() for c in data.columns]
    required = ["Impact", "Practice", "Challenge", "Lean P."]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(
            "The Excel file is missing these required columns: "
            + ", ".join(missing)
            + ". Required columns are: Impact, Practice, Challenge, Lean P."
        )
    data = data[required].copy()
    for col in required:
        data[col] = data[col].astype("string").str.strip()
        data[col] = data[col].replace("", pd.NA)
    data = data.dropna(subset=required).drop_duplicates().reset_index(drop=True)
    return data

try:
    df = load_data(DATA_FILE)
except Exception as exc:
    st.error(f"Could not load Portal.xlsx: {exc}")
    st.info("Check that Portal.xlsx is in the same GitHub repository as app.py.")
    st.stop()

if df.empty:
    st.warning("No complete relationship records were found in Portal.xlsx.")
    st.stop()

st.sidebar.header("Explore the framework")
st.sidebar.write("Select an impact to see its related practices, challenges, and Lean principles.")

impacts = sorted(df["Impact"].unique().tolist())
selected_impact = st.sidebar.selectbox("1. Select an impact", impacts)

impact_df = df[df["Impact"] == selected_impact].copy()
practices = sorted(impact_df["Practice"].unique().tolist())

selected_practice = st.sidebar.selectbox(
    "2. Filter by practice (optional)",
    ["All practices"] + practices,
)

if selected_practice != "All practices":
    view_df = impact_df[impact_df["Practice"] == selected_practice].copy()
else:
    view_df = impact_df.copy()

st.subheader(f"Selected impact: {selected_impact}")
m1, m2, m3 = st.columns(3)
m1.metric("Practices", view_df["Practice"].nunique())
m2.metric("Challenges", view_df["Challenge"].nunique())
m3.metric("Lean principles", view_df["Lean P."].nunique())

st.divider()
st.subheader("Mitigation pathways")
st.write("Each row shows a relationship recorded in your Excel dataset.")

# Group Lean principles under each impact/practice/challenge combination.
pathways = (
    view_df.groupby(["Impact", "Practice", "Challenge"], dropna=False)["Lean P."]
    .agg(lambda s: ", ".join(sorted(set(s.astype(str)))))
    .reset_index()
    .rename(columns={"Lean P.": "Associated Lean principles"})
)
st.dataframe(pathways, use_container_width=True, hide_index=True)

st.subheader("Explore a challenge")
challenge_options = sorted(view_df["Challenge"].unique().tolist())
selected_challenge = st.selectbox("3. Select a challenge", challenge_options)
challenge_df = view_df[view_df["Challenge"] == selected_challenge]

principles = sorted(challenge_df["Lean P."].unique().tolist())
related_practices = sorted(challenge_df["Practice"].unique().tolist())

left, right = st.columns(2)
with left:
    st.markdown("**Related practice(s)**")
    for item in related_practices:
        st.write(f"• {item}")
with right:
    st.markdown("**Associated Lean principle(s)**")
    for item in principles:
        st.write(f"• {item}")

with st.expander("View all records for this impact"):
    st.dataframe(impact_df, use_container_width=True, hide_index=True)

st.caption(
    "This application displays relationships contained in Portal.xlsx. "
    "It does not infer or validate new relationships."
)
