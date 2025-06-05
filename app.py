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
    msg["To"] = "dmd@azauricommunications.net"
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

    except Exception as e:
        st.error(f"Email failed to send: {e}")
