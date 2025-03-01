import streamlit as st
from db import connection
from datetime import date
import io
from PIL import Image
image=None
if 'delete_result' not in st.session_state:
    st.session_state['delete_result']=()
mydb,dbcursor=connection()
def fetch_vehicle(vehicle_no):
    try:
        query = "SELECT image,vehicle_no,model,cc,purchase_date,cost_price,fine,sales_date,sales_price FROM vehicle  WHERE vehicle_no = %s"

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

def delete(vehicle_no):

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
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.delete_result=result
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
        model=st.text_input(placeholder="R15",label="Model",value=result[2],disabled=True)
        cc=st.number_input(placeholder="150",label="CC",value=result[3],disabled=True)
        purchase_date=st.date_input(label="Purchasing Date",value=result[4],disabled=True)
        cost_price=st.number_input(placeholder="80000",label="Cost Price",value=result[5],disabled=True)
        fine=st.number_input(placeholder="1500",label="Fine Amount",value=result[6],disabled=True)
        sales_date=st.date_input(label="Purchasing Date",value=result[7],disabled=True)
        sales_price=st.number_input(placeholder="80000",label="Cost Price",value=result[8],disabled=True)
        submit=st.form_submit_button(label="delete")
        if submit:
            delete(vehicle_no)