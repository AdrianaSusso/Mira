import streamlit as st
from datetime import datetime, date
import smtplib
from email.message import EmailMessage
import requests

# ✅ Streamlit Cloud secrets only — not in the file!
ZOHO_CLIENT_ID = st.secrets["ZOHO_CLIENT_ID"]
ZOHO_CLIENT_SECRET = st.secrets["ZOHO_CLIENT_SECRET"]
ZOHO_REFRESH_TOKEN = st.secrets["ZOHO_REFRESH_TOKEN"]
ZOHO_API_DOMAIN = st.secrets["ZOHO_API_DOMAIN"]

def refresh_zoho_access_token():
    token_url = "https://accounts.zoho.com/oauth/v2/token"
    params = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    response = requests.post(token_url, params=params)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        st.error(f"❌ Failed to refresh Zoho token: {response.text}")
        return None

def push_to_zoho_crm(access_token, form_data):
    url = f"{ZOHO_API_DOMAIN}/crm/v2/Admissions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "data": [form_data]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code, response.json()

# 🎯 Streamlit UI
st.title("🏠 Mira – Tilo Haven Admissions Agent")

with st.form("intake_form"):
    full_name = st.text_input("Resident Full Name")
    dob = st.date_input("Date of Birth", value=date(1950, 1, 1), min_value=date(1900, 1, 1))
    contact_name = st.text_input("Primary Contact (POA)")
    contact_phone = st.text_input("POA Phone Number")
    contact_email = st.text_input("POA Email")
    insurance_type = st.selectbox("Insurance Type", ["Medicaid", "Medicare", "Private Pay"])
    move_in_date = st.date_input("Preferred Move-in Date")
    needs = st.text_area("Describe any medical or personal care needs")
    authorize = st.checkbox("✅ I authorize Tilo Haven Senior Living to contact me and agree my information will be kept confidential.")

    submitted = st.form_submit_button("Submit Intake")

if submitted and authorize:
    age = (datetime.today().date() - dob).days // 365
    st.success("✅ Mira has received the resident information and will process the intake.")
    st.info("📅 A team member will follow up soon.")
st.markdown("[📅 Click here to schedule your admissions call or facility tour](https://dmd-tilohaven.zohobookings.com/#/4766432000000048006)")

    # Email alert
    msg = EmailMessage()
    msg["Subject"] = "New Resident Intake Submission"
    msg["From"] = "your_email@example.com"
    msg["To"] = "dmd@tilohaven.com"
    msg.set_content(
        f"New Intake Received:\n\n"
        f"Resident Name: {full_name}\n"
        f"Date of Birth: {dob} (Age: {age})\n"
        f"POA: {contact_name}, Phone: {contact_phone}, Email: {contact_email}\n"
        f"Insurance: {insurance_type}\n"
        f"Move-in: {move_in_date}\n"
        f"Needs: {needs}"
    )

    try:
        with smtplib.SMTP_SSL("smtp.office365.com", 465) as smtp:
            smtp.login("your_email@example.com", "your_app_password")
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"❌ Email failed: {e}")

    # 🔁 Push to Zoho
    access_token = refresh_zoho_access_token()
    if access_token:
        form_data = {
            "Resident_Full_Name": full_name,
            "Date_of_Birth": str(dob),
            "POA_Name": contact_name,
            "POA_Phone": contact_phone,
            "POA_Email": contact_email,
            "Insurance_Type": insurance_type,
            "Move_in_Date": str(move_in_date),
            "Needs": needs
        }
        status, result = push_to_zoho_crm(access_token, form_data)
        if status == 201:
            st.success("✅ Intake sent to Zoho CRM.")
        else:
            st.error(f"❌ Failed to log in Zoho CRM. Status {status}: {result}")
else:
    if submitted:
        st.warning("⚠️ You must authorize contact to submit the form.")


