# Streamlit App: Mira – Admissions & Intake Agent
import streamlit as st
from datetime import datetime, date
import requests
import smtplib
from email.message import EmailMessage

# Zoho OAuth and CRM Info (Keep these secure in actual deployment)
ZOHO_ACCESS_TOKEN = "your_zoho_access_token"
ZOHO_API_DOMAIN = "https://www.zohoapis.com"

st.title("🏠 Mira – Tilo Haven Admissions Agent")
st.write("Mira helps automate the resident intake process for Tilo Haven Senior Living.")

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
    authorize = st.checkbox("I authorize Tilo Haven Senior Living to contact me. I understand my privacy is important and my information will not be shared.")
    submitted = st.form_submit_button("Submit Intake")

if submitted and authorize:
    age = (datetime.today().date() - dob).days // 365
    st.success("✅ Mira has received the resident information and will process the intake.")
    st.info("📅 A team member will follow up soon.")
    st.markdown("[Click here to schedule your admissions call or facility tour](https://dmd-tilohaven.zohobookings.com/#/4766432000000048006)")

    # Send Email Notification
    msg = EmailMessage()
    msg["Subject"] = "New Resident Intake Submission"
    msg["From"] = "your_email@example.com"
    msg["To"] = "dmd@tilohaven.com"
    msg["Cc"] = "staff@tilohaven.com"
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
        smtp_server = smtplib.SMTP("smtp.office365.com", 587)
        smtp_server.starttls()
        smtp_server.login("your_email@example.com", "your_app_password")  # Secure this in actual use
        smtp_server.send_message(msg)
        smtp_server.quit()
    except Exception as e:
        st.error(f"❌ Email failed to send: {e}")

    # Push to Zoho CRM
    intake_data = {
        "data": [
            {
                "Full_Name": full_name,
                "Date_of_Birth": str(dob),
                "Primary_Contact": contact_name,
                "POA_Phone": contact_phone,
                "POA_Email": contact_email,
                "Insurance_Type": insurance_type,
                "Move_In_Date": str(move_in_date),
                "Needs": needs
            }
        ]
    }

    crm_url = f"{ZOHO_API_DOMAIN}/crm/v2/Admissions"
    headers = {
        "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(crm_url, headers=headers, json=intake_data)

    if response.status_code == 201:
        st.success("✅ Intake successfully logged in Zoho CRM.")
    else:
        st.error(f"❌ Failed to log intake in Zoho CRM. Status code: {response.status_code}\n{response.text}")



