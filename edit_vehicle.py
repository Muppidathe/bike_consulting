import streamlit as st
from db import connection
from datetime import date
import os
image=None
if 'edit_result' not in st.session_state:
    st.session_state['edit_result']=()
mydb,dbcursor=connection()
def save_uploaded_file(uploaded_file,vehicle_no):
    ext=uploaded_file.name.split('.')[-1]
    filename=str(vehicle_no)+"."+ext
    file_path = os.path.join("static",'vehicle',filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
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
        st.error(f'while fetching details {e}')
        st.stop()
        return None

def edit(vehicle_no,images,model,cc,purchase_date,cost_price,fine,sales_date,sales_price):
    if images:
        image_path=save_uploaded_file(images,vehicle_no)
        vehicle_edit_query = """
        UPDATE vehicle
        SET image = %s, model = %s ,cc= %s,purchase_date=%s,cost_price=%s,fine=%s,sales_date=%s,sales_price=%s
        WHERE vehicle_no = %s
        """
        values=(image_path,model,cc,purchase_date,cost_price,fine,sales_date,sales_price,vehicle_no)
    else:
        vehicle_edit_query = """
        UPDATE vehicle
        SET  model = %s ,cc= %s,purchase_date=%s,cost_price=%s,fine=%s,sales_date=%s,sales_price=%s
        WHERE vehicle_no = %s
        """
        values=(model,cc,purchase_date,cost_price,fine,sales_date,sales_price,vehicle_no)
    try:
        dbcursor.execute(vehicle_edit_query,values)
        mydb.commit()
        st.success('vehicle info edited')
        st.balloons()
    except Exception as e:
        st.error(f"error while inserting{e}")
#-------------------------------------------------------------------------------------------------------
#form1
with st.form("fetch_details"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    fetch_submit=st.form_submit_button(label="Get Details")
    if fetch_submit:
        result=fetch_vehicle(vehicle_no)
        st.session_state.edit_result=result
#form2
result=st.session_state.edit_result
if result:
    with st.form('Expenses'):
        vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number",value=result[1],disabled=True)
        if result[0]:  # If image exists
                image_path = result[0]
                col=st.columns(3)
                with col[0]:
                    st.image(image_path,use_container_width=True)
        image_inp=st.file_uploader(label="Vechile Image",type=['png', 'jpg','jpeg'])
        model=st.text_input(placeholder="R15",label="Model",value=result[2])
        cc=st.number_input(placeholder="150",label="CC",value=result[3])
        purchase_date=st.date_input(label="Purchasing Date",value=result[4])
        cost_price=st.number_input(placeholder="80000",label="Cost Price",value=result[5])
        fine=st.number_input(placeholder="1500",label="Fine Amount",value=result[6])
        sales_date=st.date_input(label="Purchasing Date",value=result[7])
        sales_price=st.number_input(placeholder="80000",label="Cost Price",value=result[8])
        submit=st.form_submit_button(label="Edit")
        if submit:
            edit(vehicle_no,image_inp,model,cc,purchase_date,cost_price,fine,sales_date,sales_price)