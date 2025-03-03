import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'sold_result' not in st.session_state:
    st.session_state['sold_result']=()
mydb,dbcursor=connection()
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model,cc,purchase_date,cost_price,fine FROM vehicle WHERE vehicle_no = %s"
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

def add_sales(vehicle_no,name,aadhar_no,phone_no,sales_date,sales_price,received_amount):
    if not name:
        st.error('please provide Buyer Name')
    elif not phone_no:
        st.error("please provide Buyer mobile no")
    elif not sales_date:
        st.error("please provide sales date")
    elif not sales_price:
        st.error("please provide sales amount")
    elif not received_amount:
        st.error("please provide received amount")
    else:
        try:
            vehicle_add_query = """
                update vehicle set buyer_name=%s,aadhar_no=%s,phone_no=%s,sales_date=%s,sales_price=%s,received_amount=%s
                where vehicle_no=%s;
            """
            dbcursor.execute(vehicle_add_query,(name,aadhar_no,phone_no,sales_date,sales_price,received_amount,vehicle_no))
            mydb.commit()
            st.success('sales detail has added')
            st.balloons()
        except Exception as e:
            st.error(f"error while inserting {e}")
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.sold_result=result
result=st.session_state.sold_result
if result:
    with st.form('Expenses'):
        if result[0]:  # If image exists
                image_path = result[0] 
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        st.text_input(placeholder="R15",label="Model",value=result[2],disabled=True)
        st.number_input(placeholder="150",label="CC",value=result[3],disabled=True)
        st.date_input(label="Purchasing Date",value=result[4],disabled=True)
        st.number_input(placeholder="80000",label="Cost Price",value=result[5],disabled=True)
        st.number_input(placeholder="1500",label="Fine Amount",value=result[6],disabled=True)
        name=st.text_input(placeholder="muppidathi",label='Buyer Name')
        aadhar_no=st.number_input(placeholder='94** **** ****',label='Aadhar no',value=None,min_value=0)
        phone_no=st.number_input(placeholder='1234****',label='phone no',value=None,min_value=0)
        sales_date=st.date_input(label="Purchasing Date")
        sales_price=st.number_input(placeholder="80000",label="Cost Price",value=None,min_value=0)
        received_amount=st.number_input(placeholder="80000",label="received amount",value=None,min_value=0)
        submit=st.form_submit_button(label="Add sales detail")
        if submit:
            add_sales(result[1],name,aadhar_no,phone_no,sales_date,sales_price,received_amount)