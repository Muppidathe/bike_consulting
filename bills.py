import streamlit as st
from db import connection
from datetime import date
if 'bills_result' not in st.session_state:
    st.session_state['bills_result']=()
mydb,dbcursor=connection()
def fetch_bills(name,phone_no):
    try:
        query = "SELECT id,name,phone_no,payable_date,amount FROM bills_payable WHERE name= %s and phone_no=%s"
        dbcursor.execute(query, (name,phone_no))
        result = dbcursor.fetchone()
        if result:
            return result
        else:
            st.error("No Record Found For This details")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching user details {e}')
        st.stop()
        return None

def add_bills(id,bills_date,bills):
    if not bills_date:
        st.error('please provide expense Date')
    elif not bills:
        st.error("please provide Amount")
    else:
        try:
            vehicle_add_query = """
                INSERT INTO bills (user_id,date,amount)
                VALUES (%s, %s, %s);
            """
            dbcursor.execute(vehicle_add_query,(id,bills_date,bills))
            mydb.commit()
            st.success('bills has added')
            st.balloons()
        except Exception as e:
            st.error(f"error while inserting{e}")
with st.form("fetch_details"):
    name=st.text_input(placeholder="Kannan",label="Name").upper()
    phone_no=st.number_input(placeholder="950037****",label="Number",value=None,min_value=0)
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_bills(name,phone_no)
        st.session_state.bills_result=result
result=st.session_state.bills_result
if result:
    with st.form('Expenses'):
        st.text_input(placeholder="kannan",label="name",value=result[1],disabled=True)
        st.number_input(placeholder="956642**",label="phone_no",value=int(result[2]),disabled=True)
        st.date_input(label="bills Date",value=result[3],disabled=True)
        st.number_input(placeholder="800",label="Amount",value=result[4],disabled=True)
        bills_date=st.date_input(label="Date",value=date.today())
        bills=int(st.number_input(placeholder="500",label="Amount",value=None))
        submit=st.form_submit_button(label="add")
        if submit:
            add_bills(result[0],bills_date,bills)