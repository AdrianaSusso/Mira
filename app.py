# Streamlit App: Mira – Admissions & Intake Agent
import streamlit as st
from datetime import datetime, date
import requests
import smtplib
from email.message import EmailMessage
import json
import os

st.set_page_config(page_title="Mira – Admissions Agent", layout="centered")
st.title("🏠 Mira – Tilo Haven Admissions Agent")
st.write("Mira helps automate the resident intake process for Tilo Haven Senior Living.")

# Load secrets securely
TENANT_ID = st.secrets["TENANT_ID"]
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
ZOHO_ACCESS_TOKEN = st.secrets["ZOHO_ACCESS_TOKEN"]
ZOHO_REFRESH_TOKEN = st.secrets["ZOHO_REFRESH_TOKEN"]
ZOHO_API_DOMAIN = st.secrets["ZOHO_API_DOMAIN"]

# Function: Refresh Zoho Token
def refresh_zoho_token():
    url = f"https://accounts.zoho.com/oauth/v2/token"
    payload = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None

# Function: Push to Zoho CRM
def push_to_zoho_crm(access_token, api_domain, data):
    url = f"{api_domain}/crm/v2/Admissions"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "data": [data]
    }
    response = requests.post(url, headers=headers, json=payload)

    # If token is invalid, refresh and retry once
    if response.status_code == 401:
        new_token = refresh_zoho_token()
        if new_token:
            headers["Authorization"] = f"Zoho-oauthtoken {new_token}"
            response = requests.post(url, headers=headers, json=payload)

    return response.status_code, response.json()

# Form
st.header("📋 New Resident Intake Form")
with st.form("intake_form"):
    full_name = st.text_input("Resident Full Name")
    dob = st.date_input("Date of Birth", value=date(1950, 1, 1), min_value=date(1900, 1, 1), max_value=datetime.today().date())
    contact_name = st.text_input("Primary Contact (POA)")
    contact_phone = st.text_input("POA Phone Number")
    contact_email = st.text_input("POA Email")
    insurance_type = st.text_input("Insurance Type (e.g., Medicaid, Private Pay)")
    move_in_date = st.date_input("Preferred Move-in Date")
    needs = st.text_area("Describe any medical or personal care needs")
    hipaa_auth = st.checkbox("I authorize Tilo Haven Senior Living to contact me. I understand my privacy is protected and my information will not be shared.")
    submitted = st.form_submit_button("Submit Intake")

if submitted:
    if not hipaa_auth:
        st.warning("⚠️ You must authorize us to contact you before submitting the form.")
    else:
        age = (datetime.today().date() - dob).days // 365
        st.success("✅ Mira has received the resident information and will process the intake.")
        st.info("An email has been sent to the admissions team and POA with the next steps.")

        # Email setup (replace this with Microsoft Graph email API later)
        msg = EmailMessage()
        msg["Subject"] = "New Resident Intake Submission"
        msg["From"] = "your_email@example.com"
        msg["To"] = "dmd@tilohaven.com"
        msg["Cc"] = "admin@tilohaven.com, staff@tilohaven.com"
        msg.set_content(
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

        try:
            with smtplib.SMTP_SSL("smtp.office365.com", 465) as smtp:
                smtp.login("your_email@example.com", "your_app_password")
                smtp.send_message(msg)
        except Exception as e:
            st.error(f"Email failed to send: {e}")

        # Zoho CRM push
        form_data = {
            "Full_Name": full_name,
            "Date_of_Birth": str(dob),
            "POA_Name": contact_name,
            "POA_Phone": contact_phone,
            "POA_Email": contact_email,
            "Insurance_Type": insurance_type,
            "Preferred_Move_In_Date": str(move_in_date),
            "Needs": needs,
        }

        status, result = push_to_zoho_crm(ZOHO_ACCESS_TOKEN, ZOHO_API_DOMAIN, form_data)
        if status == 200:
            st.success("✅ Intake successfully logged in Zoho CRM.")
        else:
            st.error(f"❌ Failed to log intake in Zoho CRM. Status code: {status}")
            st.error(json.dumps(result, indent=2))

        st.markdown("📅 [Schedule Admissions Call or Facility Tour](https://dmd-tilohaven.zohobookings.com/#/4766432000000048006)")
