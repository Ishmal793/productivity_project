import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook

st.set_page_config(page_title="Manage Productivity Data", page_icon="📊", layout="wide")

# Check if logged in
if "company_name" not in st.session_state:
    st.warning("❌ Please Login First!")
    st.stop()

company_name = st.session_state["company_name"]
data_file = f"pages/{company_name}.xlsx"

# Sidebar header with company name
st.sidebar.header(f"🏢 {company_name}")

st.title(f"📊 {company_name} - Manage Productivity Data")

# Check if file exists
if not os.path.exists(data_file):
    st.error("⚠️ No Data Found! Please enter data first.")
    st.stop()

# Select data sheet
sheet_option = st.sidebar.selectbox("📌 Select Data Sheet", ["Overall Productivity", "Department Productivity", "Employee Productivity"])

# **Session State to Keep Edit Mode**
if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False
if "edit_row" not in st.session_state:
    st.session_state.edit_row = None

# Load selected data
df_selected = pd.read_excel(data_file, sheet_name=sheet_option)

if df_selected.empty:
    st.warning("⚠️ No Data Available!")
    st.stop()

# Show data in a table
st.subheader(f"📊 {sheet_option} Data")
st.dataframe(df_selected)

# Download button
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(df_selected)
st.download_button("📥 Download Data", data=csv, file_name=f"{sheet_option}.csv", mime="text/csv")

# Editing and Deleting Section
st.sidebar.subheader("✏️ Edit / ❌ Delete Data")
edit_row = st.sidebar.number_input("Enter Row Number to Edit/Delete", min_value=0, max_value=len(df_selected)-1, step=1)

# **Start Editing**
if st.sidebar.button("✏️ Edit Row"):
    st.session_state.edit_mode = True
    st.session_state.edit_row = edit_row

# **Edit Form Only If Edit Mode is Active**
if st.session_state.edit_mode and st.session_state.edit_row is not None:
    edit_row = st.session_state.edit_row
    st.subheader(f"Editing Row {edit_row}")
    row_data = df_selected.iloc[edit_row].copy()

    updated_values = {}
    for col in df_selected.columns:
        if col.lower() in ["input", "output"]:
            updated_values[col] = st.number_input(f"Update {col}", value=float(row_data[col]), min_value=1.0)
        elif col.lower() == "productivity":
            continue  # Productivity will be recalculated
        else:
            updated_values[col] = st.text_input(f"Update {col}", value=str(row_data[col]))

    # Productivity Calculation
    updated_productivity = updated_values["Output"] / updated_values["Input"] if "Input" in updated_values and "Output" in updated_values else row_data["Productivity"]

    if st.button("✅ Save Changes"):
        for col, value in updated_values.items():
            df_selected.at[edit_row, col] = value  

        df_selected.at[edit_row, "Productivity"] = updated_productivity  

        with pd.ExcelWriter(data_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_selected.to_excel(writer, sheet_name=sheet_option, index=False)

        st.session_state.edit_mode = False  # Exit Edit Mode
        st.success("✅ Row Updated!")
        st.rerun()

# **Delete Row**
if st.sidebar.button("❌ Delete Row"):
    df_selected.drop(index=edit_row, inplace=True)
    df_selected.reset_index(drop=True, inplace=True)  

    with pd.ExcelWriter(data_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df_selected.to_excel(writer, sheet_name=sheet_option, index=False)

    st.session_state.edit_mode = False  # Exit Edit Mode
    st.success("❌ Row Deleted!")
    st.rerun()
