import streamlit as st
from db import connection
from datetime import date
from streamlit_card import card

if 'office_dashboard_result' not in st.session_state:
    st.session_state['office_dashboard_result']=[]
mydb,dbcursor=connection()
def fetch_vehicle(inp_date,inp_end_date):
    try:
        query="select id,date,description,amount from office_expenses WHERE date >= %s and date <= %s;"
        dbcursor.execute(query, (inp_date,inp_end_date))
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

#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    inputs = st.columns(2)
    with inputs[0]:
        inp_date = st.date_input("enter the date",key='start', value=date.today())
    with inputs[1]:
        inp_end_date = st.date_input("enter the date",key='end', value=date.today())
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(inp_date,inp_end_date)
        st.session_state.office_dashboard_result=result
#form2
result=st.session_state.office_dashboard_result
if result:
    total_expenses=0
    for i in result:
        total_expenses+=i[3]
    card(title='Office Expenses',text=str(total_expenses))
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            expense_date=st.date_input(label="Expense Date",value=i[1],disabled=True)
            desc=st.text_input(label="Description",value=i[2],disabled=True)
            expense=st.number_input(label="expenses",value=i[3],min_value=0,disabled=True)
            delete=st.form_submit_button(label="View",disabled=True)