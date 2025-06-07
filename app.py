import streamlit as st
from datetime import datetime, date
import requests
import json
from email.message import EmailMessage
import msal
import os

# Display the form
dob_default = date(1950, 1, 1)
today = datetime.today().date()

st.title("🏠 Mira – Tilo Haven Admissions Agent")
st.write("Mira helps automate the resident intake process for Tilo Haven Senior Living.")

st.header("📋 New Resident Intake Form")
with st.form("intake_form"):
    full_name = st.text_input("Resident Full Name")
    dob = st.date_input("Date of Birth", value=dob_default, min_value=date(1900, 1, 1), max_value=today)
    contact_name = st.text_input("Primary Contact (POA)")
    contact_phone = st.text_input("POA Phone Number")
    contact_email = st.text_input("POA Email")
    insurance_type = st.selectbox("Insurance Type", ["Medicaid", "Medicare", "Private Pay"])
    move_in_date = st.date_input("Preferred Move-in Date")
    needs = st.text_area("Describe any medical or personal care needs")
    hipaa_agree = st.checkbox("I authorize Tilo Haven Senior Living to contact me. I understand my information is private and will not be shared.", value=True)
    submitted = st.form_submit_button("Submit Intake")

# Configs for Microsoft Graph API (email)
TENANT_ID = st.secrets["TENANT_ID"]
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
SENDER_EMAIL = "adriana@azauricommunications.net"
RECIPIENT_EMAIL = "intake@tilohaven.com"
BCC_EMAIL = "admin@tilohaven.com"
BOOKING_LINK_ADMISSIONS = "https://dmd-tilohaven.zohobookings.com/#/4766432000000046006?serviceId=4766432000000048006"
BOOKING_LINK_TOUR = "https://dmd-tilohaven.zohobookings.com/#/4766432000000046006?serviceId=4766432000000048020"

# Zoho Configs
ZOHO_CLIENT_ID = st.secrets["ZOHO_CLIENT_ID"]
ZOHO_CLIENT_SECRET = st.secrets["ZOHO_CLIENT_SECRET"]
ZOHO_REFRESH_TOKEN = st.secrets["ZOHO_REFRESH_TOKEN"]
ZOHO_API_DOMAIN = "https://www.zohoapis.com"

# Refresh Zoho access token
def refresh_zoho_access_token():
    token_url = f"https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, data=params)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# Send email using Microsoft Graph

def get_graph_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return result.get("access_token")

def send_email(subject, body):
    token = get_graph_access_token()
    if not token:
        st.error("❌ Failed to acquire Microsoft access token.")
        return

    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body
            },
            "toRecipients": [{"emailAddress": {"address": RECIPIENT_EMAIL}}],
            "bccRecipients": [{"emailAddress": {"address": BCC_EMAIL}}]
        }
    }

    graph_url = "https://graph.microsoft.com/v1.0/users/{}/sendMail".format(SENDER_EMAIL)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(graph_url, headers=headers, json=email_msg)
    if response.status_code != 202:
        st.error(f"❌ Email failed to send: {response.status_code} {response.text}")

# Push to Zoho CRM

def push_to_zoho_crm(access_token, form_data):
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Admissions"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }
    data = {"data": [form_data]}
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.text

if submitted:
    if not hipaa_agree:
        st.warning("You must authorize contact to proceed.")
    else:
        age = (today - dob).days // 365
        st.success("✅ Mira has received the resident information and will process the intake.")
        st.info("An email has been sent to the admissions team with next steps.")
        st.markdown(f"[📅 Schedule an Admissions Call]({BOOKING_LINK_ADMISSIONS})")
        st.markdown(f"[🏥 Schedule a Facility Tour]({BOOKING_LINK_TOUR})")

        # Email content
        subject = "New Resident Intake Submission"
        body = (
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

        send_email(subject, body)

        # Prepare data for Zoho CRM
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

        access_token = refresh_zoho_access_token()
        if access_token:
            status, result = push_to_zoho_crm(access_token, form_data)
            if status == 201:
                st.success("✅ Intake logged into Zoho CRM.")
            else:
                st.error(f"❌ Failed to log intake in Zoho CRM. Status code: {status}\n{result}")
        else:
            st.error("❌ Failed to refresh Zoho access token.")
