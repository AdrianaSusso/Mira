# mira.py
import streamlit as st
from datetime import datetime, date
import requests
import json

st.title("🏠 Mira – Tilo Haven Admissions Agent")
st.write("Mira automates the resident intake process for Tilo Haven Senior Living.")

st.header("📋 New Resident Intake Form")
with st.form("intake_form"):
    full_name = st.text_input("Resident Full Name")
    dob = st.date_input("Date of Birth", value=date(1950, 1, 1), min_value=date(1900, 1, 1), max_value=datetime.today().date())
    contact_name = st.text_input("Primary Contact (POA)")
    contact_phone = st.text_input("POA Phone Number")
    contact_email = st.text_input("POA Email")
    insurance_type = st.selectbox("Insurance Type", ["Medicaid", "Medicare", "Private Pay"])
    move_in_date = st.date_input("Preferred Move-in Date")
    needs = st.text_area("Describe any medical or personal care needs")
    hipaa_consent = st.checkbox("I authorize Tilo Haven Senior Living to contact me regarding this intake. My privacy is important and will not be shared.")

    submitted = st.form_submit_button("Submit Intake")

if submitted:
    if not hipaa_consent:
        st.warning("⚠️ Please agree to the HIPAA consent to proceed.")
    else:
        age = (datetime.today().date() - dob).days // 365
        st.success("✅ Mira has received the intake and will process it.")
        st.info(f"Resident Age: {age} years")
        if age < 55:
            st.warning("⚠️ This resident is under the typical senior living threshold (55+). Confirm eligibility.")

        # Prepare data for Zoho CRM
        form_data = {
            "data": [{
                "Resident_Full_Name": full_name,
                "Date_of_Birth": str(dob),
                "POA_Name": contact_name,
                "POA_Email": contact_email,
                "POA_Phone": contact_phone,
                "Insurance_Type": insurance_type,
                "Preferred_Move_in_Date": str(move_in_date),
                "Needs": needs,
                "HIPAA_Consent": hipaa_consent
            }]
        }

        # Load tokens securely (replace with your method if needed)
        access_token = "1000.142399f215d145346f799cb5269bdf24.cc2f02a0c67964a7c979a51c8023acb9"
        api_domain = "https://www.zohoapis.com"

        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json"
        }

        url = f"{api_domain}/crm/v2/Admissions"
        response = requests.post(url, headers=headers, data=json.dumps(form_data))

        if response.status_code == 201:
            st.success("✅ Intake successfully logged to Zoho CRM.")
        else:
            st.error(f"❌ Failed to log intake in Zoho CRM. Status code: {response.status_code}")
            st.error(response.text)

        # Show booking link
        st.markdown("---")
        st.subheader("📞 Book an Admissions Call or Facility Tour")
        st.markdown("[Click here to schedule](https://dmd-tilohaven.zohobookings.com/#/4766432000000048006)")


