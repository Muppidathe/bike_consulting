import streamlit as st
from db import connection
from datetime import date
if 'delete_bills_payable' not in st.session_state:
    st.session_state['delete_bills_payable']=()
if 'delete_bills_result' not in st.session_state:
    st.session_state['delete_bills_result']=[]
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

def delete_bills(id):
        try:
            vehicle_add_query = """
                delete from  bills where id=%s;
            """
            dbcursor.execute(vehicle_add_query,(id,))
            mydb.commit()
            st.success('bills has deleted')
            st.balloons()
        except Exception as e:
            st.error(f"error while deleting bills {e}")
def delete_bills_payable(id):
        try:
            vehicle_add_query = """
            delete from bills_payable where id=%s;
        """
            dbcursor.execute(vehicle_add_query, (id,))
            mydb.commit()
            st.success('bills payable has deleted')
            st.balloons()
        except Exception as e:
            st.error("error while deleting bills payable ",e)

#form 1
with st.form("fetch_details"):
    name=st.text_input(placeholder="Kannan",label="Name").upper()
    phone_no=st.number_input(placeholder="950037****",label="Number",value=None,min_value=0)
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_bills_payable(name,phone_no)
        st.session_state.delete_bills_payable=result
        result=fetch_bills(result[0])
        st.session_state.delete_bills_result=result
#form 2
result=st.session_state.delete_bills_payable
if result:
    with st.form('edit_payable'):
        name=st.text_input(placeholder="kannan",label="name",value=result[1],disabled=True)
        phone_no=st.number_input(placeholder="956642**",label="phone_no",value=int(result[2]),disabled=True)
        submit=st.form_submit_button(label="delete")
        if submit:
            delete_bills_payable(result[0])
## form 3
st.header("bills")
result=st.session_state.delete_bills_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            bills_date=st.date_input(label="Date",value=i[1],disabled=True)
            amount=st.number_input(label="Given Amount" if i[3]==1 else "Received Amount",value=i[2],disabled=True)
            submit=st.form_submit_button(label="delete")
            if submit:
                delete_bills(id)