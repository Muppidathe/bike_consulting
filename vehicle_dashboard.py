import streamlit as st
from streamlit_card import card
import pandas as pd
from datetime import date
from db import connection
import base64

# Set responsive layout
st.set_page_config(layout="wide")

def image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def path_to_image_html(path):
    base64_str = image_to_base64(path)
    return f'<img src="data:image/png;base64,{base64_str}" width="100">'

mydb, dbcursor = connection()

inputs = st.columns(2)
with inputs[0]:
    inp_date = st.date_input("enter the date",key='start', value=date.today())
with inputs[1]:
    inp_end_date = st.date_input("enter the date",key='end', value=date.today())


# Queries
cost_price_query = f"select IFNULL(cost_price+fine+sum(amount),0) from vehicle v,vehicle_expenses vv where v.vehicle_no=vv.vehicle_num and purchase_date>='{inp_date}' and purchase_date<='{inp_end_date}'"
balance_query = f"select sum(sales_price-received_amount) from vehicle where sales_date>='{inp_date}' and sales_date<='{inp_end_date}'"
sales_price_query = f"select ifnull(sum(received_amount),0) from vehicle where sales_date>='{inp_date}' and sales_date<='{inp_end_date}'"
#chatgpt query
profit_query=f"select if(ifnull(received_amount,0)=0,0,received_amount-(cost_price+ifnull(sum(amount),0))) as 'profit' from vehicle v left join vehicle_expenses e on vehicle_no=vehicle_num where sales_date>='{inp_date}' and sales_date<='{inp_end_date}' group by vehicle_num"

# Execute queries and get results
dbcursor.execute(cost_price_query)
res = dbcursor.fetchone()
if res[0]:
    cost_price = res[0]
else:
    cost_price = 0
#_________________
dbcursor.execute(balance_query)
res = dbcursor.fetchone()
if res[0]:
    balance= res[0]
else:
    balance = 0
#_________________
dbcursor.execute(sales_price_query)
res = dbcursor.fetchone()
if res[0]:
    sales_price = res[0]
else:
    sales_price = 0
#__________________-
dbcursor.execute(profit_query)
res = dbcursor.fetchall()
profit= 0
if res:
    for i in res:
        profit += i[0]

# CSS for responsive cards
st.markdown("""
<style>
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        width: 100%;
        margin-bottom: 2%;
    }
    .stat-card {
        background-color: #7a7a7a;
        color: white;
        border-radius: 10px;
        padding: 1rem;
        min-width: 220px;
        flex: 1;
        text-align: center;
    }
    .card-title {
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .card-value {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* Responsive adjustments */
    @media (max-width: 1200px) {
        .stat-card {
            min-width: 180px;
        }
    }
    @media (max-width: 768px) {
        .stat-card {
            min-width: 150px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Create responsive cards with HTML/CSS instead of using the card component
st.markdown(f"""
<div class="card-container">
    <div class="stat-card">
        <div class="card-title">Vehicle Cost Amount</div>
        <div class="card-value">{cost_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Sales Amount</div>
        <div class="card-value">{sales_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Balance</div>
        <div class="card-value">{balance}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Profit</div>
        <div class="card-value">{profit}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Table display
dataframe_query = f"select vehicle_no,image,model_name,model_year,purchase_date,cost_price+ifnull(sum(amount),0) as 'total cost price',sales_price,received_amount,sales_price-received_amount as 'balance',if(ifnull(received_amount,0)=0,0,received_amount-(cost_price+fine+ifnull(sum(amount),0))) as 'profit' from vehicle v left join vehicle_expenses ve on v.vehicle_no=ve.vehicle_num where purchase_date >= '{inp_date}' and purchase_date <= '{inp_end_date}' group by vehicle_no"

df = pd.read_sql(dataframe_query, mydb)
df.index = df.index + 1
if len(df.index)>0:
    df['image'] = df['image'].map(path_to_image_html)
    st.write(df.to_html(escape=False), unsafe_allow_html=True)