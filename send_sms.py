import streamlit as st
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import pandas as pd
from datetime import datetime
import os

# ---- Twilio credentials ----
ACCOUNT_SID = ''
AUTH_TOKEN = ''
TWILIO_PHONE_NUMBER = ''

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---- Load or initialize message history ----
history_file = 'history.csv'
columns = ['To', 'Message', 'Status', 'Time']

if os.path.exists(history_file):
    history_df = pd.read_csv(history_file)
else:
    history_df = pd.DataFrame(columns=columns)

# ---- Streamlit Page Config ----
st.set_page_config(page_title="📲 Twilio SMS Dashboard", page_icon="📱", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f9f9f9; }
    .stButton>button {
        background-color: #25D366;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 0.5em 2em;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .stTextArea textarea {
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Tabs for navigation ----
tab1, tab2 = st.tabs(["📨 Send Message", "🛠️ Admin Panel"])

# ---- Tab 1: Send Message ----
with tab1:
    st.header("📨 Send SMS via Twilio")

    phone_number = st.text_input("Recipient phone number", value="+92...", help="Include country code (e.g., +923001234567)")
    message_body = st.text_area("Message", value="Hello from Streamlit + Twilio!")

    if st.button("Send SMS"):
        if not phone_number.startswith("+") or len(phone_number) < 10:
            st.warning("⚠ Please enter a valid phone number with '+' and country code.")
        elif not message_body.strip():
            st.warning("⚠ Message body cannot be empty.")
        else:
            try:
                message = client.messages.create(
                    body=message_body.strip(),
                    from_=TWILIO_PHONE_NUMBER,
                    to=phone_number.strip()
                )
                status = 'Successful'
                st.success(f"✅ Message sent! SID: {message.sid}")
            except TwilioRestException as e:
                status = f"Failed ({e.msg})"
                st.error(f"❌ Twilio error: {e.msg}")
            except Exception as e:
                status = f"Failed ({str(e)})"
                st.error(f"❌ Unexpected error: {str(e)}")

            # Save message to history
            new_row = {
                'To': phone_number.strip(),
                'Message': message_body.strip(),
                'Status': status,
                'Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            history_df = pd.concat([history_df, pd.DataFrame([new_row])], ignore_index=True)
            history_df.to_csv(history_file, index=False)

    st.subheader("📜 Recent Message History")
    if not history_df.empty:
        st.dataframe(history_df[::-1].reset_index(drop=True), use_container_width=True)
    else:
        st.info("No messages sent yet.")

# ---- Tab 2: Admin Panel ----
with tab2:
    st.header("🛠️ Admin Panel")
    admin_action = st.selectbox("Choose action", [
        "View full history",
        "Delete all history",
        "Delete history for specific number"
    ])

    if admin_action == "View full history":
        st.subheader("📋 Full SMS History")
        if history_df.empty:
            st.info("📭 No messages in history.")
        else:
            st.dataframe(history_df[::-1].reset_index(drop=True), use_container_width=True)

    elif admin_action == "Delete all history":
        if st.button("❌ Confirm Delete All History"):
            history_df = pd.DataFrame(columns=columns)
            history_df.to_csv(history_file, index=False)
            st.success("✅ All message history deleted.")
            st.info("ℹ️ Please refresh the page to see the update.")

    elif admin_action == "Delete history for specific number":
        specific_number = st.text_input("Enter number to delete (e.g., +923001234567)").strip()

        if st.button("🗑️ Delete for This Number"):
            stripped_numbers = history_df['To'].astype(str).str.strip()

            if specific_number and specific_number in stripped_numbers.values:
                history_df = history_df[stripped_numbers != specific_number]
                history_df.to_csv(history_file, index=False)
                st.success(f"✅ History for {specific_number} deleted.")
                st.info("ℹ️ Please refresh the page to see the update.")
            else:
                st.warning("⚠ Number not found in history.")
