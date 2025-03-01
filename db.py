import streamlit as st
import mysql.connector
@st.cache_resource
def connection():
    try:
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="sasi_kannan"
        )
        dbcursor=mydb.cursor()
        return mydb,dbcursor
    except Exception as e:
        print("connection error",e)
        

# connection()