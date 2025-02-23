import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Company Login", page_icon="🔐", layout="wide")
# Hide default Streamlit elements
st.markdown("""
<style>
.stAppHeader, .st-emotion-cache-6qob1r, .stSidebar { visibility:hidden; }
</style>
""", unsafe_allow_html=True)


st.title("🔐 Company Login / Registration")

credentials_file = "pages/credentials.xlsx"
logo_folder = "pages/logos/"

# Ensure logo folder exists
os.makedirs(logo_folder, exist_ok=True)

# Check if credentials file exists, else create
if not os.path.exists(credentials_file):
    pd.DataFrame(columns=["Company Name", "Email", "Password", "Logo"]).to_excel(credentials_file, index=False)

# Load credentials
df = pd.read_excel(credentials_file)

# Check if user is logged in
if "company_name" in st.session_state:
    st.subheader("🔄 Edit Company Details")
    existing_data = df[df["Company Name"] == st.session_state["company_name"]]

    if not existing_data.empty:
        new_email = st.text_input("📧 Update Email", existing_data["Email"].values[0])
        new_password = st.text_input("🔑 Update Password", existing_data["Password"].values[0], type="password")
        new_logo = st.file_uploader("📂 Update Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])

        if st.button("Update"):
            df.loc[df["Company Name"] == st.session_state["company_name"], "Email"] = new_email
            df.loc[df["Company Name"] == st.session_state["company_name"], "Password"] = new_password
            
            if new_logo:
                logo_filename = f"{st.session_state['company_name']}_{new_logo.name}"
                logo_path = os.path.join(logo_folder, logo_filename)

                # Save logo file
                with open(logo_path, "wb") as f:
                    f.write(new_logo.getbuffer())

                # Save logo filename in Excel
                df.loc[df["Company Name"] == st.session_state["company_name"], "Logo"] = logo_filename

            df.to_excel(credentials_file, index=False)
            st.success("✅ Company Details Updated!")

    # Option to add a new company
    if st.button("Add New Company"):
        del st.session_state["company_name"]
        st.rerun()

else:
    # User Input
    company_name = st.text_input("🏢 Company Name")
    email = st.text_input("📧 Email")
    password = st.text_input("🔑 Password", type="password")
    logo = st.file_uploader("📂 Upload Company Logo (PNG/JPG)", type=["png", "jpg", "jpeg"])
    register = st.checkbox("Register as New Company")

    if st.button("Submit"):
        if not company_name or not email or not password or logo is None:
            st.error("❌ Company Name, Email, Password aur Logo required hain!")
        else:
            if register:  # New Registration
                if company_name in df["Company Name"].values:
                    st.error("❌ Company already exists!")
                else:
                    logo_filename = f"{company_name}_{logo.name}"
                    logo_path = os.path.join(logo_folder, logo_filename)

                    # Save logo file
                    with open(logo_path, "wb") as f:
                        f.write(logo.getbuffer())

                    new_data = pd.DataFrame([[company_name, email, password, logo_filename]], 
                                            columns=["Company Name", "Email", "Password", "Logo"])
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_excel(credentials_file, index=False)
                    st.success("✅ Company Registered! Please login.")
            else:  # Login
                if ((df["Company Name"] == company_name) & (df["Email"] == email) & (df["Password"] == password)).any():
                    st.session_state["company_name"] = company_name
                    st.success("✅ Login Successful! Redirecting...")
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("❌ Incorrect Company Name, Email or Password!")
