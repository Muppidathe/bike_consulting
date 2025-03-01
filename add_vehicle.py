import streamlit as st
from datetime import date,datetime
from db import connection
import os
st.set_page_config(layout="wide")
mydb,dbcursor=connection()
def save_uploaded_file(uploaded_file,vehicle_no):
    ext=uploaded_file.name.split('.')[-1]
    filename=str(vehicle_no)+"."+ext
    file_path = os.path.join("static",'vehicle',filename)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path
def insert(vehicle_no,image,model,cc,purchase_date,cost_price,fine):
    if not fine:
        fine=0
    if not vehicle_no:
        st.error("enter the vehicle number")
    elif not model:
        st.error("enter the model name")
    elif not cc:
        st.error("enter the cc")
    elif not purchase_date:
        st.error("purchase date required")
    elif not cost_price:
        st.error("cost price required")
    else:
        if image:
            image_path=save_uploaded_file(image,vehicle_no)
        else:
            image_path='static/vehicle/default_bike.jpg'
        try:
            vehicle_add_query = """
            INSERT INTO vehicle (vehicle_no, image, model, cc, purchase_date,cost_price, fine) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
            dbcursor.execute(vehicle_add_query, (vehicle_no,image_path, model, cc, purchase_date, cost_price, fine))
            mydb.commit()
            st.success('vehicle has added')
            st.balloons()
        except Exception as e:
            st.error("error while inserting",e)
with st.form("my_form"):
    vehicle_no=st.text_input(placeholder="TN10G7871",label="Vehicle Number").upper()
    image=st.file_uploader(label="Vechile Image",type=['png', 'jpg','jpeg'])
    model=st.text_input(placeholder="R15",label="Model").upper()
    cc=st.number_input(placeholder="150",label="CC",value=None,min_value=0)
    purchase_date=st.date_input(label="Purchasing Date",value=date.today())
    cost_price=st.number_input(placeholder="80000",label="Cost Price",value=None,min_value=0)
    fine=st.number_input(placeholder="1500",label="Fine Amount",value=None,min_value=0)
    submit=st.form_submit_button(label="submit")
    if submit:
        insert(vehicle_no,image,model,cc,purchase_date,cost_price,fine)