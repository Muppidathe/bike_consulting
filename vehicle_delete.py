import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'delete_result' not in st.session_state:
    st.session_state['delete_result']=()
if 'delete_exp_result' not in st.session_state:
    st.session_state['delete_exp_result']=[]
mydb,dbcursor=connection()
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model_name,cc,purchase_date,cost_price,fine,buyer_name,ifnull(aadhar_no,0),ifnull(phone_no,0),sales_date,sales_price,received_amount,model_year FROM vehicle  WHERE vehicle_no = %s"

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

def delete_vehicle(vehicle_no):

    try:
        vehicle_delete_query="delete from vehicle where vehicle_no=%s"
        vehicle_delete_query1="delete from vehicle_expenses where vehicle_num=%s "
        dbcursor.execute(vehicle_delete_query1,(vehicle_no,))
        dbcursor.execute(vehicle_delete_query,(vehicle_no,))
        mydb.commit()
        st.success('vehicle deleted')
        st.balloons()
    except Exception as e:
        st.error(f"error while deleting {e}")
def delete_expenses(id):

    try:
        vehicle_delete_query="delete from vehicle_expenses where id=%s "
        dbcursor.execute(vehicle_delete_query,(id,))
        mydb.commit()
        st.success('vehicle expenses deleted')
        st.balloons()
    except Exception as e:
        st.error(f"error while deleting {e}")
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.delete_result=result
        result=fetch_expenses(vehicle_no)
        st.session_state.delete_exp_result=result
#form2
result=st.session_state.delete_result
if result:
    with st.form('Expenses'):
        vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number",value=result[1],disabled=True)
        if result[0]:  # If image exists
                image_path = result[0]  
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        model_name=st.text_input(placeholder="R15",label="Vehicle Name",value=result[2],disabled=True)
        model_year=st.number_input(placeholder="150",label="Model",value=result[13],disabled=True)
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
        submit=st.form_submit_button(label="delete")
        if submit:
            delete_vehicle(vehicle_no)
#form3
st.header("Expenses")
result=st.session_state.delete_exp_result
if result:
    for i in result:
        with st.form(key=str(i[0])):
            id=i[0]
            vehicle_no=i[1]
            expense_date=st.date_input(label="expense date",value=i[2],disabled=True)
            desc=st.text_input(label="Description",value=i[3],disabled=True)
            expense=st.number_input(label="expenses",value=i[4],disabled=True)
            submit=st.form_submit_button(label="delete")
            if submit:
                delete_expenses(id)
else:
    st.info("no Expenses found for this vehicle")