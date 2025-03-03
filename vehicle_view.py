import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'list_result' not in st.session_state:
    st.session_state['list_result']=()
if 'list_exp_result' not in st.session_state:
    st.session_state['list_exp_result']=[]
if 'list_dashboard_result' not in st.session_state:
    st.session_state.list_dashboard_result=()
mydb,dbcursor=connection()
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model,cc,purchase_date,cost_price,fine,buyer_name,ifnull(aadhar_no,0),phone_no,sales_date,ifnull(sales_price,0),ifnull(received_amount,0) FROM vehicle  WHERE vehicle_no = %s"

        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result:
            return result
        else:
            st.error("No Record Found For This Number")
            st.stop()
            return None

    except Exception as e:
        st.error(f'while fetching image {e}')
        st.stop()
        return None
def fetch_expenses(vehicle_no):
    try:
        query="select id,vehicle_num,vehicle_expenses_date,description,amount from vehicle_expenses WHERE vehicle_num = %s;"
        dbcursor.execute(query, (vehicle_no,))
        result = dbcursor.fetchall()
        if result:
            return result
        else:
            return None

    except Exception as e:
        st.error(f'while fetching expenses {e}')
        st.stop()
        return None   
def fetch_dashboard(vehicle_no):
    cost_query="select cost_price+ifnull(fine,0)+ifnull(sum(amount),0) from vehicle left join vehicle_expenses on vehicle_no=vehicle_num where vehicle_no= %s group by vehicle_no;"
    sales_query="select ifnull(sales_price,0) from vehicle where vehicle_no = %s;"
    received_amount_query="select ifnull(received_amount,0) from vehicle where vehicle_no = %s;"
    try:
        dbcursor.execute(cost_query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result[0]:
            cost=result[0]
        else:
            cost=0
        dbcursor.execute(sales_query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result[0]:
            sales=result[0]
        else:
            sales=0
        dbcursor.execute(received_amount_query, (vehicle_no,))
        result = dbcursor.fetchone()
        if result[0]:
            received=result[0]
        else:
            received=0
        return (cost,sales,received)
    except Exception as e:
        st.error(f"error while fetching {e}" )


#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.list_result=result
        result=fetch_expenses(vehicle_no)
        st.session_state.list_exp_result=result
        result=fetch_dashboard(vehicle_no)
        st.session_state.list_dashboard_result=result

#form2
result=st.session_state.list_result
if result:
    with st.form('Expenses'):
        vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number",value=result[1],disabled=True)
        if result[0]:  # If image exists
                image_path = result[0]  
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        model=st.text_input(placeholder="R15",label="Model",value=result[2],disabled=True)
        cc=st.number_input(placeholder="150",label="CC",value=result[3],disabled=True)
        purchase_date=st.date_input(label="Purchasing Date",value=result[4],disabled=True)
        cost_price=st.number_input(placeholder="80000",label="Cost Price",value=result[5],disabled=True)
        fine=st.number_input(placeholder="1500",label="Fine Amount",value=result[6],disabled=True)
        name=st.text_input(placeholder="muppidathi",label='Buyer Name',value=result[7],disabled=True)
        aadhar_no=st.number_input(placeholder='94** **** ****',label='Aadhar no',value=int(result[8]),disabled=True)
        phone_no=st.number_input(placeholder='1234****',label='phone no',value=int(result[9]),disabled=True)
        sales_date=st.date_input(label="sales Date",value=result[10],disabled=True)
        sales_price=st.number_input(placeholder="80000",label="Cost Price",value=result[11],disabled=True)
        received_amount=st.number_input(placeholder="80000",label="received amount",value=result[12],disabled=True)
        balance_amount=st.number_input(placeholder="80000",label="balance amount",value=result[11]-result[12],disabled=True)
        submit=st.form_submit_button(label="view",disabled=True)
#form3
st.header("Expenses")
result=st.session_state.list_exp_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            vehicle_no=i[1]
            expense_date=st.date_input(label="expense date",value=i[2],disabled=True)
            desc=st.text_input(label="Description",value=i[3],disabled=True)
            expense=st.number_input(label="expenses",value=i[4],disabled=True)
            submit=st.form_submit_button(label="view",disabled=True)
else:
    st.info("no Expenses found for this vehicle")



#section 4
result=st.session_state.list_dashboard_result
if result:
    st.header("Insights")
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
        <div class="card-title">Total Cost Price</div>
        <div class="card-value">{result[0]}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Sales Price</div>
        <div class="card-value">{result[1]}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Balance</div>
        <div class="card-value">{result[1]-result[2]}</div>
    </div>
    <div class="stat-card">
        <div class="card-title">Profit</div>
        <div class="card-value">{result[2]-result[0]}</div>
    </div>
</div>
""", unsafe_allow_html=True)