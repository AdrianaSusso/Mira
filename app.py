# Streamlit App: Mira – Admissions & Intake Agent
import streamlit as st
from datetime import datetime, date
import smtplib
from email.message import EmailMessage

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
    submitted = st.form_submit_button("Submit Intake")

if submitted:
    st.success("✅ Mira has received the resident information and will process the intake.")
    st.info("An email has been sent to the admissions team and POA with the next steps.")

    msg = EmailMessage()
    msg["Subject"] = "New Resident Intake Submission"
    msg["From"] = "your_email@example.com"
    msg["To"] = "dmd@tilohaven.com"
    msg.set_content(
        f"New Resident Intake Received:\n\n"
        f"Resident Name: {full_name}\n"
        f"Date of Birth: {dob}\n"
        f"Primary Contact (POA): {contact_name}\n"
        f"POA Phone: {contact_phone}\n"
        f"POA Email: {contact_email}\n"
        f"Insurance Type: {insurance_type}\n"
        f"Preferred Move-In Date: {move_in_date}\n"
        f"Needs: {needs}"
    )

    try:
        with smtplib.SMTP_SSL("smtp.yourmailprovider.com", 465) as smtp:
            smtp.login("your_email@example.com", "your_app_password")
            smtp.send_message(msg)
    except Exception as e:
        st.error(f"Email failed to send: {e}")

    # ✅ Push to Zoho CRM
    def push_to_zoho_crm(access_token, api_domain, form_data):
        url = f"{api_domain}/crm/v2/Admissions"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        data = {
            "data": [
                {
                    "Full_Name": full_name,
                    "Date_of_Birth": str(dob),
                    "POA_Name": contact_name,
                    "POA_Phone": contact_phone,
                    "POA_Email": contact_email,
                    "Insurance_Type": insurance_type,
                    "Move_In_Date": str(move_in_date),
                    "Needs": needs
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data)
        return response.status_code, response.json()

    access_token = "YOUR_ACCESS_TOKEN"
    api_domain = "https://www.zohoapis.com"

    form_data = {
        "full_name": full_name,
        "dob": dob,
        "contact_name": contact_name,
        "contact_phone": contact_phone,
        "contact_email": contact_email,
        "insurance_type": insurance_type,
        "move_in_date": move_in_date,
        "needs": needs
    }

    status, result = push_to_zoho_crm(access_token, api_domain, form_data)

    if status == 201:
        st.success("✅ Intake submitted to Zoho CRM successfully!")
    else:
        st.error(f"❌ Zoho CRM submission failed: {result}")
