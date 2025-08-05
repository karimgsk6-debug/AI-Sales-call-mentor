
import streamlit as st
import pandas as pd

# Load the data files
@st.cache_data
def load_data():
    survey_df = pd.read_excel("segmentation survey.xlsx")
    actions_df = pd.read_excel("Shingrix RACE segmentation actions.xlsx")

    # Clean and merge data
    actions_cleaned = actions_df[['RACE', 'Description', 'Limitation / Barriers to expand', 'Proposed Action']].dropna(subset=['RACE'])
    actions_cleaned = actions_cleaned.drop_duplicates(subset=['RACE'])

    hcp_race = survey_df[['Account', 'RACE']].drop_duplicates()
    recommendations = pd.merge(hcp_race, actions_cleaned, on='RACE', how='left')
    return recommendations

recommendations = load_data()

# UI
st.title("AI Sales Call Assistant for Pharma Reps")
st.write("Helps reps prepare for HCPs based on segmentation and barriers")

hcp_name = st.selectbox("Select HCP (Doctor) Name", sorted(recommendations['Account'].unique()))

hcp_data = recommendations[recommendations['Account'] == hcp_name].iloc[0]

st.subheader("HCP Profile & Recommendations")
st.markdown(f"**Segment (RACE):** {hcp_data['RACE']}")
st.markdown(f"**Description:** {hcp_data['Description']}")
st.markdown(f"**Main Barrier:** {hcp_data['Limitation / Barriers to expand']}")
st.markdown(f"**Recommended Action:** {hcp_data['Proposed Action']}")
