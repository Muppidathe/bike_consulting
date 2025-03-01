import streamlit as st
from streamlit_card import card
import pandas as pd
from datetime import date,datetime
from db import connection
import os
import base64

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def path_to_image_html(path):
    base64_str = image_to_base64(path)
    return f'<img src="data:image/png;base64,{base64_str}" width="100">'

st.set_page_config(layout="wide")
mydb,dbcursor=connection()
inputs = st.columns(2)
with inputs[0]:
    inp_date=st.date_input("enter the date",value=date.today())
with inputs[1]:
    no_of_month=st.number_input("no of months",value=1,min_value=1)

dataframe_query = f"select vehicle_no,image,model,cc,purchase_date,cost_price,fine,sum(amount) as expenses,cost_price+fine+sum(amount) as 'total cost price',sales_date,sales_price from vehicle v left join vehicle_expenses ve on v.vehicle_no=ve.vehicle_num where purchase_date>={inp_date} and purchase_date<=DATE_ADD('{inp_date}', INTERVAL {no_of_month} MONTH)"
df = pd.read_sql(dataframe_query, mydb)
df.index = df.index + 1
if len(df.index)>0:
    df['image']=df['image'].map(path_to_image_html)
    st.write(df.to_html(escape=False), unsafe_allow_html=True)