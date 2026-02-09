import streamlit as st
import pandas as pd
import os

# Set page config
st.set_page_config(page_title="Purchase Management App", layout="wide")

# File path for the data
DATA_FILE = 'cleaned_purchases.csv'

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=['Vendor', 'Item', 'Qty', 'Price', 'Amount'])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Load data into session state
if 'df' not in st.session_state:
    st.session_state.df = load_data()

st.title("🛒 Purchase Management System")

# --- SIDEBAR: ADD NEW DATA ---
st.sidebar.header("➕ Add New Purchase")
with st.sidebar.form("purchase_form", clear_on_submit=True):
    vendor_input = st.text_input("Vendor")
    item_input = st.text_input("Item")
    qty_input = st.number_input("Quantity", min_value=1, step=1)
    price_input = st.number_input("Price", min_value=0.0, step=100.0)
    
    submit = st.form_submit_button("Add Record")
    
    if submit:
        if vendor_input and item_input:
            # Enforcing capitalization rule: First letter of each word
            formatted_item = item_input.title().strip()
            
            new_row = pd.DataFrame([{
                'Vendor': vendor_input.strip(),
                'Item': formatted_item,
                'Qty': qty_input,
                'Price': price_input,
                'Amount': qty_input * price_input
            }])
            st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
            save_data(st.session_state.df)
            st.success(f"Added: {formatted_item}")
            st.rerun()
        else:
            st.error("Please fill in Vendor and Item.")

# --- MAIN DASHBOARD ---
df = st.session_state.df
col1, col2, col3 = st.columns(3)
col1.metric("Total Spending", f"{df['Amount'].sum():,.0f}")
col2.metric("Total Items", len(df))
col3.metric("Vendors", df['Vendor'].nunique())

st.divider()

# --- MANAGE RECORDS ---
st.subheader("📋 Purchase Log")
if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    with st.expander("🗑️ Delete a Record"):
        row_to_delete = st.selectbox("Select row to delete", options=df.index, 
                                     format_func=lambda x: f"Row {x}: {df.iloc[x]['Item']} from {df.iloc[x]['Vendor']}")
        if st.button("Confirm Delete"):
            st.session_state.df = df.drop(row_to_delete).reset_index(drop=True)
            save_data(st.session_state.df)
            st.rerun()
else:
    st.info("The log is currently empty.")

# --- ANALYTICS ---
if not df.empty:
    st.divider()
    st.subheader("💰 Spending by Vendor")
    chart_data = df.groupby('Vendor')['Amount'].sum().sort_values(ascending=False)
    st.bar_chart(chart_data)

# Download Button
csv_data = df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("📥 Export to CSV", csv_data, "purchases_export.csv", "text/csv")