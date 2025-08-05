import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

# Free text search
search_name = st.text_input("Search for HCP (Doctor) Name")
filtered = recommendations[recommendations['Account'].str.contains(search_name, case=False)] if search_name else recommendations

if not filtered.empty:
    hcp_name = st.selectbox("Select HCP from results", sorted(filtered['Account'].unique()))
    hcp_data = filtered[filtered['Account'] == hcp_name].iloc[0]

    st.subheader("HCP Profile & Recommendations")
    st.markdown(f"**Segment (RACE):** {hcp_data['RACE']}")
    st.markdown(f"**Description:** {hcp_data['Description']}")
    st.markdown(f"**Main Barrier:** {hcp_data['Limitation / Barriers to expand']}")
    st.markdown(f"**Recommended Action:** {hcp_data['Proposed Action']}")

    # Notes input
    notes = st.text_area("Add your notes for this HCP")

    # PDF generation
    def generate_pdf(hcp_data, notes):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()
        story = []

        story.append(Paragraph("HCP Sales Call Recommendation", styles['Title']))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"HCP Name: {hcp_data['Account']}", styles['Normal']))
        story.append(Paragraph(f"Segment (RACE): {hcp_data['RACE']}", styles['Normal']))
        story.append(Paragraph(f"Description: {hcp_data['Description']}", styles['Normal']))
        story.append(Paragraph(f"Main Barrier: {hcp_data['Limitation / Barriers to expand']}", styles['Normal']))
        story.append(Paragraph(f"Recommended Action: {hcp_data['Proposed Action']}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Rep Notes:", styles['Heading3']))
        story.append(Paragraph(notes if notes else "No notes provided.", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer

    if st.button("Download as PDF"):
        pdf_buffer = generate_pdf(hcp_data, notes)
        st.download_button(label="Download PDF", data=pdf_buffer, file_name=f"{hcp_data['Account']}_recommendation.pdf", mime="application/pdf")
else:
    st.warning("No matching HCPs found.")
