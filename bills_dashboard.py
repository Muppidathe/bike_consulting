import streamlit as st
from streamlit_card import card
import pandas as pd
from datetime import date
from db import connection
import base64

# Set responsive layout
st.set_page_config(layout="wide")

mydb, dbcursor = connection()


# Queries

given="select sum(amount) from bills where given=1;"
taken="select sum(amount) from bills where given=0;"
# Execute queries and get results


dbcursor.execute(given)
res = dbcursor.fetchone()
if res[0]:
    given_price=res[0]
else:
    given_price=0
dbcursor.execute(taken)
res = dbcursor.fetchone()
if res[0]:
    taken_price=res[0]
else:
    taken_price=0
yet_to_come=given_price-taken_price
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
        <div class="card-title">Money Given</div>
        <div class="card-value">{given_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Money taken back</div>
        <div class="card-value">{taken_price}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">money wants to come</div>
        <div class="card-value">{yet_to_come}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Table display
dataframe_query = f"select name,phone_no,date,sum(if(given=1,amount,0)) as 'money given',sum(if(given=0,amount,0)) as 'money taken',sum(if(given=1,amount,0))-sum(if(given=0,amount,0)) as 'balance' from bills_payable bp left join bills b on bp.id=b.user_id;"
df = pd.read_sql(dataframe_query, mydb)
df.index = df.index + 1
if len(df.index)>0:
    st.dataframe(df)