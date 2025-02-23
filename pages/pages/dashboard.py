import streamlit as st
import pandas as pd
import os
from PIL import Image

st.set_page_config(page_title="Productivity Dashboard", page_icon="📊", layout="wide")


# Check if logged in
if "company_name" not in st.session_state:
    st.warning("❌ Please Login First!")
    st.stop()

company_name = st.session_state["company_name"]
data_file = f"pages/{company_name}.xlsx"
credentials_file = "pages/credentials.xlsx"
logo_folder = "pages/logos/"

# Ensure logo folder exists
os.makedirs(logo_folder, exist_ok=True)

# Load credentials file to get company logo
if os.path.exists(credentials_file):
    df = pd.read_excel(credentials_file)
    company_data = df[df["Company Name"] == company_name]

    if not company_data.empty:
        logo_name = company_data["Logo"].values[0]
        logo_path = os.path.join(logo_folder, logo_name) if pd.notna(logo_name) else None

        # Save logo in session state (for real-time update)
        if logo_path and os.path.exists(logo_path):
            st.session_state["company_logo"] = logo_path
    else:
        logo_path = None
else:
    logo_path = None



# Use session state logo if available
if "company_logo" in st.session_state and st.session_state["company_logo"]:
    st.sidebar.image(st.session_state["company_logo"], caption="Company Logo", use_column_width=True)
else:
    st.sidebar.write("🔴 No Logo Uploaded")



company_name = st.session_state["company_name"]
data_file = f"pages/{company_name}.xlsx"

# Sidebar header with company name
st.sidebar.header(f"🏢 {company_name}")

st.title(f"📊 {company_name} - Productivity Dashboard")

# Check if company data file exists, else create with sheets
if not os.path.exists(data_file):
    with pd.ExcelWriter(data_file) as writer:
        pd.DataFrame(columns=["Product Name", "Input", "Output", "Productivity"]).to_excel(writer, sheet_name="Overall Productivity", index=False)
        pd.DataFrame(columns=["Department", "Input", "Output", "Productivity"]).to_excel(writer, sheet_name="Department Productivity", index=False)
        pd.DataFrame(columns=["Employee", "Department", "Input", "Output", "Productivity"]).to_excel(writer, sheet_name="Employee Productivity", index=False)

# Load data from different sheets
with pd.ExcelFile(data_file) as xls:
    df_overall = pd.read_excel(xls, sheet_name="Overall Productivity")
    df_department = pd.read_excel(xls, sheet_name="Department Productivity")
    df_employee = pd.read_excel(xls, sheet_name="Employee Productivity")

# Sidebar Options
st.sidebar.markdown("### 📌 **Select Calculation**")  # Bold heading
option = st.sidebar.radio("", ["Overall Productivity", "Department Productivity", "Employee Productivity"])


if option == "Overall Productivity":
    st.subheader("📈 Calculate Overall Productivity")
    product_name = st.text_input("Enter Product Name")
    total_input = st.number_input("Enter Total Input", min_value=1)
    total_output = st.number_input("Enter Total Output", min_value=1)
    
    if st.button("Calculate"):
        productivity = total_output / total_input
        st.success(f"✅ Productivity for {product_name}: {productivity:.2f}")

        new_data = pd.DataFrame([[product_name, total_input, total_output, productivity]], 
                                columns=["Product Name", "Input", "Output", "Productivity"])
        
        df_overall = pd.concat([df_overall, new_data], ignore_index=True)
        with pd.ExcelWriter(data_file, mode="a", if_sheet_exists="replace") as writer:
            df_overall.to_excel(writer, sheet_name="Overall Productivity", index=False)

elif option == "Department Productivity":
    st.subheader("🏢 Department Productivity")
    department = st.text_input("Enter Department Name")
    dept_input = st.number_input("Enter Department Input", min_value=1)
    dept_output = st.number_input("Enter Department Output", min_value=1)
    
    if st.button("Calculate"):
        productivity = dept_output / dept_input
        st.success(f"✅ {department} Productivity: {productivity:.2f}")

        new_data = pd.DataFrame([[department, dept_input, dept_output, productivity]], 
                                columns=["Department", "Input", "Output", "Productivity"])

        df_department = pd.concat([df_department, new_data], ignore_index=True)
        with pd.ExcelWriter(data_file, mode="a", if_sheet_exists="replace") as writer:
            df_department.to_excel(writer, sheet_name="Department Productivity", index=False)

elif option == "Employee Productivity":
    st.subheader("👨‍💼 Employee Productivity")
    employee = st.text_input("Enter Employee Name")
    department = st.text_input("Enter Department Name")
    emp_input = st.number_input("Enter Employee Input", min_value=1)
    emp_output = st.number_input("Enter Employee Output", min_value=1)

    if st.button("Calculate"):
        productivity = emp_output / emp_input
        st.success(f"✅ {employee} Productivity: {productivity:.2f}")

        new_data = pd.DataFrame([[employee, department, emp_input, emp_output, productivity]], 
                                columns=["Employee", "Department", "Input", "Output", "Productivity"])

        df_employee = pd.concat([df_employee, new_data], ignore_index=True)
        with pd.ExcelWriter(data_file, mode="a", if_sheet_exists="replace") as writer:
            df_employee.to_excel(writer, sheet_name="Employee Productivity", index=False)
