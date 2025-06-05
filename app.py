# Streamlit App: Clara – Admissions & Intake Agent
import streamlit as st
from datetime import datetime

st.title("🏠 Clara – Tilo Haven Admissions Agent")
st.write("Clara helps automate the resident intake process for Tilo Haven Senior Living.")

st.header("📋 New Resident Intake Form")
with st.form("intake_form"):
    full_name = st.text_input("Resident Full Name")
    dob = st.date_input("Date of Birth")
    contact_name = st.text_input("Primary Contact (POA)")
    contact_phone = st.text_input("POA Phone Number")
    contact_email = st.text_input("POA Email")
    insurance_type = st.selectbox("Insurance Type", ["Medicaid", "Medicare", "Private Pay"])
    move_in_date = st.date_input("Preferred Move-in Date")
    needs = st.text_area("Describe any medical or personal care needs")
    submitted = st.form_submit_button("Submit Intake")

if submitted:
    st.success("✅ Clara has received the resident information and will process the intake.")
    st.info("An email has been sent to the admissions team and POA with the next steps.")
