import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'del_office_exp_result' not in st.session_state:
    st.session_state['del_office_exp_result']=[]
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

def delete_info(id):

    try:
        vehicle_delete_query="delete from office_expenses where id=%s "
        dbcursor.execute(vehicle_delete_query,(id,))
        mydb.commit()
        st.success('vehicle expenses deleted')
        st.balloons()
    except Exception as e:
        st.error(f"error while deleting {e}")
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    date=st.date_input(label="expense date",value=date.today())
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(date)
        st.session_state.del_office_exp_result=result
#form2
result=st.session_state.del_office_exp_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            expense_date=st.date_input(label="Expense Date",value=i[1],disabled=True)
            desc=st.text_input(label="Description",value=i[2],disabled=True)
            expense=st.number_input(label="expenses",value=i[3],min_value=0,disabled=True)
            delete=st.form_submit_button(label="delete")
            if delete:
                delete_info(id)