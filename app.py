# Streamlit App: Mira – Admissions & Intake Agent
import streamlit as st
from datetime import datetime, date
import requests
from email.message import EmailMessage
import msal
import os

# Title & Intro
st.title("🏠 Mira – Tilo Haven Admissions Agent")
st.write("Mira helps automate the resident intake process for Tilo Haven Senior Living.")

# Intake Form
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
    authorize = st.checkbox("I authorize Tilo Haven Senior Living to contact me. My privacy is respected and information will not be shared.")
    submitted = st.form_submit_button("Submit Intake")

# After Submission
if submitted:
    if not authorize:
        st.warning("⚠️ You must authorize contact to proceed.")
    else:
        age = (datetime.today().date() - dob).days // 365
        st.success("✅ Mira has received the resident information and will process the intake.")
        st.info("An email has been sent to the admissions team with next steps. Schedule your admissions call below.")

        # Generate message
        intake_body = (
            f"New Resident Intake Received:\n\n"
            f"Resident Name: {full_name}\n"
            f"Date of Birth: {dob} (Age: {age})\n"
            f"Primary Contact (POA): {contact_name}\n"
            f"POA Phone: {contact_phone}\n"
            f"POA Email: {contact_email}\n"
            f"Insurance Type: {insurance_type}\n"
            f"Preferred Move-In Date: {move_in_date}\n"
            f"Needs: {needs}"
        )

        # -------------------
        # Send Email via Microsoft Graph
        # -------------------
        TENANT_ID = st.secrets["TENANT_ID"]
        CLIENT_ID = st.secrets["CLIENT_ID"]
        CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
        AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
        SCOPE = ["https://graph.microsoft.com/.default"]

        app = msal.ConfidentialClientApplication(
            CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET
        )
        result = app.acquire_token_for_client(scopes=SCOPE)

        if "access_token" in result:
            access_token = result["access_token"]
            email_payload = {
                "message": {
                    "subject": "New Resident Intake Submission",
                    "body": {
                        "contentType": "Text",
                        "content": intake_body,
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": "dmd@tilohaven.com"}},
                    ],
                    "ccRecipients": [
                        {"emailAddress": {"address": "staff@tilohaven.com"}},
                        {"emailAddress": {"address": "admin@tilohaven.com"}}
                    ]
                },
                "saveToSentItems": "true"
            }

            response = requests.post(
                "https://graph.microsoft.com/v1.0/users/adriana@azauricommunications.net/sendMail",
                headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
                json=email_payload,
            )

            if response.status_code == 202:
                st.success("✉️ Intake email sent successfully.")
            else:
                st.error(f"❌ Failed to send email. Status: {response.status_code}\n{response.text}")
        else:
            st.error("🔒 Failed to authenticate with Microsoft Graph.")

        # -------------------
        # Schedule Booking Link
        # -------------------
        st.markdown(
            """
            📅 [Click here to schedule your admissions call](https://dmd-tilohaven.zohobookings.com/#/4766432000000048006)
            """
        )

        # -------------------
        # Push to Zoho CRM
        # -------------------
        ZOHO_TOKEN = st.secrets["ZOHO_ACCESS_TOKEN"]
        ZOHO_API_DOMAIN = "https://www.zohoapis.com"
        zoho_headers = {
            "Authorization": f"Zoho-oauthtoken {ZOHO_TOKEN}",
            "Content-Type": "application/json"
        }

        crm_payload = {
            "data": [{
                "Full_Name": full_name,
                "Date_of_Birth": str(dob),
                "POA_Name": contact_name,
                "POA_Phone": contact_phone,
                "POA_Email": contact_email,
                "Insurance_Type": insurance_type,
                "Preferred_Move_In": str(move_in_date),
                "Needs": needs,
                "Authorized_Contact": True
            }]
        }

        crm_response = requests.post(
            f"{ZOHO_API_DOMAIN}/crm/v2/Admissions",
            headers=zoho_headers,
            json=crm_payload
        )

        if crm_response.status_code == 201:
            st.success("✅ Intake logged in Zoho CRM.")
        else:
            st.error(f"❌ Failed to log intake in Zoho CRM. Status code: {crm_response.status_code}\n\n{crm_response.text}")


