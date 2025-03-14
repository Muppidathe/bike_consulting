import streamlit as st
from db import connection
from datetime import date
if 'edit_bills_payable' not in st.session_state:
    st.session_state['edit_bills_payable']=()
if 'edit_bills_result' not in st.session_state:
    st.session_state['edit_bills_result']=[]
mydb,dbcursor=connection()
def fetch_bills_payable(name,phone_no):
    try:
        query = "SELECT id,name,phone_no FROM bills_payable WHERE name= %s and phone_no=%s"
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
def fetch_bills(user_id):
    try:
        query="select id,date,amount,given from bills WHERE user_id = %s;"
        dbcursor.execute(query, (user_id,))
        result = dbcursor.fetchall()
        if result:
            return result
        else:
            return None

    except Exception as e:
        st.error(f'while fetching bills {e}')
        st.stop()
        return None

def edit_bills(id,bills_date,bills):
    if not bills_date:
        st.error('please provide expense Date')
    elif not bills:
        st.error("please provide Amount")
    else:
        try:
            vehicle_add_query = """
                update  bills set date=%s,amount=%s
                where id=%s;
            """
            dbcursor.execute(vehicle_add_query,(bills_date,bills,id))
            mydb.commit()
            st.success('bills has edited')
            st.balloons()
        except Exception as e:
            st.error(f"error while upadating bills {e}")
def edit_bills_payable(id,name,phone_no):
    if not name:
        st.error("enter the Name")
    elif not phone_no:
        st.error("enter the Mobile Number")
    else:
        try:
            vehicle_add_query = """
            update bills_payable set name=%s,phone_no=%s 
            where id=%s;
        """
            dbcursor.execute(vehicle_add_query, (name,phone_no,id))
            mydb.commit()
            st.success('bills payable has edited')
            st.balloons()
        except Exception as e:
            st.error("error while editing bills payable ",e)

#form 1
with st.form("fetch_details"):
    name=st.text_input(placeholder="Kannan",label="Name").upper()
    phone_no=st.number_input(placeholder="950037****",label="Number",value=None,min_value=0)
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_bills_payable(name,phone_no)
        st.session_state.edit_bills_payable=result
        result=fetch_bills(result[0])
        st.session_state.edit_bills_result=result
#form 2
result=st.session_state.edit_bills_payable
if result:
    with st.form('edit_payable'):
        name=st.text_input(placeholder="kannan",label="name",value=result[1])
        phone_no=st.number_input(placeholder="956642**",label="phone_no",value=int(result[2]))
        submit=st.form_submit_button(label="edit")
        if submit:
            edit_bills_payable(result[0],name,phone_no)
## form 3
st.header("bills")
result=st.session_state.edit_bills_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            bills_date=st.date_input(label="Date",value=i[1])
            amount=st.number_input(label="Given Amount" if i[3]==1 else "Received Amount",value=i[2])
            submit=st.form_submit_button(label="Edit")
            if submit:
                edit_bills(id,bills_date,amount)
else:
    st.info("No bills found")