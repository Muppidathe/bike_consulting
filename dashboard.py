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
    inp_date = st.date_input("enter the date", value=date.today())
with inputs[1]:
    no_of_month = st.number_input("no of months", value=0, min_value=0)

def see(vechile_no):
    print(vechile_no)

# Queries
cost_price_query = f"select IFNULL(cost_price+sum(amount),0) from vehicle v,vehicle_expenses vv where v.vehicle_no=vv.vehicle_num and purchase_date>='{inp_date}' and purchase_date<=DATE_ADD('{inp_date}',INTERVAL {no_of_month} MONTH)"
expenses_query = f"select IFNULL(sum(amount),0) from office_expenses where date>='{inp_date}' and date<=DATE_ADD('{inp_date}',INTERVAL {no_of_month} MONTH)"
sales_price_query = f"select IFNULL((sales_price),0) from vehicle where sales_date>='{inp_date}' and sales_date<=DATE_ADD('{inp_date}',INTERVAL {no_of_month} MONTH)"

# Execute queries and get results
dbcursor.execute(cost_price_query)
res = dbcursor.fetchall()
for i in res:
    cost_price = i[0]

dbcursor.execute(expenses_query)
res = dbcursor.fetchall()
for i in res:
    expenses = i[0]

dbcursor.execute(sales_price_query)
res = dbcursor.fetchall()
for i in res:
    sales_price = i[0]
if not res:
    sales_price = 0

# CSS for responsive cards
st.markdown("""
<style>
    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        width: 100%;
        margin-bottom: 2    %;
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
        <div class="card-title">Investment's On Vehicle</div>
        <div class="card-value">{cost_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Office Expenses</div>
        <div class="card-value">{expenses}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Earnings</div>
        <div class="card-value">{sales_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Profit</div>
        <div class="card-value">{sales_price - cost_price}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Table display
dataframe_query = f"select vehicle_no,image,model,cc,purchase_date,cost_price,fine,sum(amount) as expenses,cost_price+fine+sum(amount) as 'total cost price',sales_date,sales_price from vehicle v left join vehicle_expenses ve on v.vehicle_no=ve.vehicle_num where purchase_date>={inp_date} and purchase_date<=DATE_ADD('{inp_date}', INTERVAL {no_of_month} MONTH)"
df = pd.read_sql(dataframe_query, mydb)
df.index = df.index + 1
if len(df.index)>0:
    df['image'] = df['image'].map(path_to_image_html)
    st.write(df.to_html(escape=False), unsafe_allow_html=True)