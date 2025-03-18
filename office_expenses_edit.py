import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'edit_office_exp_result' not in st.session_state:
    st.session_state['edit_office_exp_result']=[]
mydb,dbcursor=connection()
def fetch_vehicle(date):
    try:
        query="select id,date,description,amount from office_expenses WHERE date = %s;"
        dbcursor.execute(query, (date,))
        result = dbcursor.fetchall()
        if result:
            return result
        else:
            st.error("No Record Found For This date")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching office expenses {e}')
        st.stop()
        return None

def edit_info(id,expense_date,desc,expense):
    vehicle_edit_query = """
        UPDATE office_expenses
        SET  date=%s,description=%s,amount=%s
        WHERE id = %s
        """
    values=(expense_date,desc,expense,id)
    try:
        dbcursor.execute(vehicle_edit_query,values)
        mydb.commit()
        st.success('vehicle info edited')
        st.balloons()
    except Exception as e:
        st.error(f"Error While Editing {e}")
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details",clear_on_submit=True):
    date=st.date_input(label="expense date",value=date.today())
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(date)
        st.session_state.edit_office_exp_result=result
#form2
result=st.session_state.edit_office_exp_result
if result:
    for i in result:
        with st.form(key=str(i[0]),clear_on_submit=True):
            id=i[0]
            expense_date=st.date_input(label="Expense Date",value=i[1])
            desc=st.text_input(label="Description",value=i[2])
            expense=st.number_input(label="expenses",value=i[3],min_value=0)
            edit=st.form_submit_button(label="Edit")
            if edit:
                edit_info(id,expense_date,desc,expense)