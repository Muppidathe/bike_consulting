import streamlit as st
from db import connection
from datetime import date

if 'bills_result' not in st.session_state:
    st.session_state['bills_result'] = ()

mydb, dbcursor = connection()

def fetch_bills(name, phone_no):
    try:
        query = "SELECT id, name, phone_no FROM bills_payable WHERE name = %s AND phone_no = %s"
        dbcursor.execute(query, (name, phone_no))
        result = dbcursor.fetchone()
        
        if result:
            return result
        else:
            st.error("No record found for these details.")
            st.stop()
            return None

    except Exception as e:
        st.error(f"Error while fetching user details: {e}")
        st.stop()
        return None

def add_bills(id, bills_date, bills):
    if not bills_date:
        st.error("Please provide an expense date.")
    elif not bills:
        st.error("Please provide an amount.")
    else:
        try:
            query = "INSERT INTO bills (user_id, date, amount,given) VALUES (%s, %s, %s,1);"
            dbcursor.execute(query, (id, bills_date, bills))
            mydb.commit()
            st.success("Bill has been added successfully.")
            st.balloons()
        except Exception as e:
            st.error(f"Error while inserting: {e}")

def less_bills(id, bills_date, bills):
    if not bills_date:
        st.error("Please provide an expense date.")
    elif not bills:
        st.error("Please provide an amount.")
    else:
        try:
            query = "INSERT INTO bills (user_id, date, amount,given) VALUES (%s, %s, %s,0);"
            dbcursor.execute(query, (id, bills_date, bills))
            mydb.commit()
            st.success("Bill has been deducted successfully.")
            st.balloons()
        except Exception as e:
            st.error(f"Error while inserting: {e}")

# Form 1 - Fetch Details
with st.form("fetch_details"):
    name = st.text_input(placeholder="Kannan", label="Name").upper()
    phone_no = st.number_input(placeholder="950037****", label="Number", value=None, min_value=0)
    fetch_submit = st.form_submit_button(label="Get Details")
    
    if fetch_submit:
        result = fetch_bills(name, phone_no)
        st.session_state.bills_result = result

# Form 2 - Add/Deduct Bills
result = st.session_state.bills_result
if result:
    col = st.columns(2)

    with col[0]:
        st.write("**Add Bill**")
        with st.form("add"):
            st.text_input(label="Name", value=result[1], disabled=True)
            st.number_input(label="Phone No", value=int(result[2]), disabled=True)
            bills_date = st.date_input(label="Date", value=date.today())
            bills = st.number_input(label="Amount", value=None, min_value=0)
            submit = st.form_submit_button(label="Add")
            if submit:
                add_bills(result[0], bills_date, bills)

    with col[1]:
        st.write("**Deduct Bill**")
        with st.form("minus"):
            st.text_input(label="Name", value=result[1], disabled=True)
            st.number_input(label="Phone No", value=int(result[2]), disabled=True)
            bills_date = st.date_input(label="Date", value=date.today())
            bills = st.number_input(label="Amount", value=None, min_value=0)
            submit = st.form_submit_button(label="Less")
            if submit:
                less_bills(result[0], bills_date, bills)

