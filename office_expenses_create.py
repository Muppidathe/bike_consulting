import streamlit as st
from datetime import date,datetime
from db import connection
import os
st.set_page_config(layout="wide")
mydb,dbcursor=connection()
def insert(date,description,amount):
    if not date:
        st.error("enter the Expenses date")
    elif not description:
        st.error("enter the description")
    elif not amount:
        st.error("enter the amount")
    else:
        try:
            vehicle_add_query = """
            INSERT INTO office_expenses (date,description,amount) 
            VALUES (%s, %s, %s);
        """
            dbcursor.execute(vehicle_add_query, (date,description,amount))
            mydb.commit()
            st.success('expenses has added')
            st.balloons()
        except Exception as e:
            st.error("error while inserting",e)
with st.form("my_form",clear_on_submit=True):
    date=st.date_input(label="Expenses Date",value=date.today())
    description=st.text_input(placeholder="pathi",label="Description").upper()
    amount=st.number_input(placeholder="12",label="Expenses",value=None,min_value=0)
    submit=st.form_submit_button(label="submit")
    if submit:
        insert(date,description,amount)