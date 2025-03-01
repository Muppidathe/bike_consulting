import streamlit as st
from datetime import date,datetime
from db import connection
import os
st.set_page_config(layout="wide")
mydb,dbcursor=connection()
def insert(name,number,date,amount):
    if not name:
        st.error("enter the Name")
    elif not number:
        st.error("enter the Mobile Number")
    elif not date:
        st.error("enter the date")
    elif not amount:
        st.error("Amount required")
    else:
        try:
            vehicle_add_query = """
            INSERT INTO bills_payable (name,phone_no,payable_date,amount) 
            VALUES (%s, %s, %s, %s);
        """
            dbcursor.execute(vehicle_add_query, (name,number,date,amount))
            mydb.commit()
            st.success('vehicle has added')
            st.balloons()
        except Exception as e:
            st.error("error while inserting",e)
with st.form("my_form"):
    name=st.text_input(placeholder="kannan",label="Name").upper()
    number=st.number_input(placeholder="950037****",label="Number",value=None,min_value=0)
    datee=st.date_input(label="Date",value=date.today())
    amount=st.number_input(placeholder="10000",label="Amount",value=None,min_value=0)
    submit=st.form_submit_button(label="submit")
    if submit:
        insert(name,number,datee,amount)